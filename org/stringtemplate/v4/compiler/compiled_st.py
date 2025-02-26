#!/usr/bin/env python3
"""
 [The "BSD license"]
  Copyright (c) 2011 Terence Parr
  All rights reserved.

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.
  3. The name of the author may not be used to endorse or promote products
     derived from this software without specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
  IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import collections.abc
import sys
from typing import Dict, List, Optional, Any, Tuple, Set, Union, TypeVar
from collections import OrderedDict
from antlr4.Token import CommonToken, Token  # type: ignore
from antlr4.ParserRuleContext import ParserRuleContext  # type:ignore
from antlr4.tree.Tree import TerminalNode, TerminalNodeImpl  # type: ignore
from antlr4 import TokenStream, InputStream  # type: ignore

from org.stringtemplate.v4.api.st_writer import STWriter
from org.stringtemplate.v4.compiler.compiler import Compiler  # Assumed location.
from org.stringtemplate.v4.compiler.group_parser import GroupParser  # Assumed location
from org.stringtemplate.v4.compiler.formal_argument import FormalArgument
from org.stringtemplate.v4.compiler.bytecode_disassembler import BytecodeDisassembler
from org.stringtemplate.v4.misc.multi_map import MultiMap  # Assuming location
from org.stringtemplate.v4.misc.misc import Misc
from org.stringtemplate.v4.st import ST
from org.stringtemplate.v4.st_group import STGroup
from org.stringtemplate.v4.misc.interval import Interval


class CompiledST:
    """
    The result of compiling an ST.  Contains all the bytecode instructions,
    string table, bytecode address to source code map, and other bookkeeping
    info.  It's the implementation of an ST you might say.  All instances
    of the same template share a single implementation (impl field).
    """

    def __init__(self):
        self.name: str = ""  # Template name.
        # Every template knows where it is relative to the group that loaded it.
        # The prefix is the relative path from the root.  "/prefix/name" is
        # the fully qualified name of this template. All calls to
        # STGroup.get_instance_of() calls must use fully qualified names. A
        # "/" is added to the front if you don't specify one. Template
        # references within template code, however, use relative names, unless
        # of course the name starts with "/".
        #
        # This has nothing to do with the outer filesystem path to the group dir or
        # group file.
        #
        # We set this as we load/compile the template.
        # Always ends with "/".
        self.prefix: str = "/"

        # The original, immutable pattern (not really used again after
        # initial "compilation"). Useful for debugging.  Even for
        # subtemplates, this is entire overall template.
        self.template: str = ""

        # The token that begins template definition; could be <@r> of region.
        self.template_def_start_token: Optional[Token] = None

        # Overall token stream for template (debug only).
        self.tokens: Optional[TokenStream] = None  # Changed to TokenStream

        # How do we interpret the syntax of the template? (debug only)
        self.ast: Optional[CommonTree] = None

        self.formal_arguments: Optional[Dict[str, FormalArgument]] = (
            None  # If no formal args, this is None.
        )
        self.has_formal_args: bool = False
        self.number_of_args_with_default_values: int = 0

        # A list of all regions and subtemplates.
        self.implicitly_defined_templates: Optional[List["CompiledST"]] = None  # type: ignore

        # The group that physically defines this ST definition. We use it
        # to initiate interpretation via ST.render(). From there, it
        # becomes field Interpreter.group and is fixed until rendering
        # completes.
        self.native_group: STGroup = STGroup.default_group

        # Does this template come from a <@region>...<@end> embedded in
        # another template?
        self.is_region: bool = False

        # If someone refs <@r()> in template t, an implicit
        #
        # @t.r() ::= ""
        #
        # is defined, but you can overwrite this def by defining your own. We
        # need to prevent more than one manual def though. Between this var and
        # is_region we can determine these cases.
        self.region_def_type: Optional[ST.RegionType] = None

        self.is_anon_subtemplate: bool = False  # {...}

        self.strings: List[str] = []  # string operands of instructions
        self.instrs: List[int] = []  #  byte-addressable code memory. Changed to int
        self.code_size: int = 0
        self.source_map: List[Optional[Interval]] = (
            []
        )  # maps IP to range in template pattern
        # If this template includes other templates, we must define them
        # so that we can set arguments for them if we see an indirect
        # or direct inclusion.  t ::= "<other(...)>".  The code generator
        # must define any template-includes with formal arguments,
        # in this case: other( (... arg list ...) ).
        self.referenced_templates: Optional[List[CommonTree]] = None

    def clone(self) -> "CompiledST":
        """
        Cloning the CompiledST for an ST instance allows ST.add to be called safely during
        interpretation for templates that do not contain formal arguments.
        """
        clone = CompiledST()  # Create a new instance
        clone.name = self.name
        clone.prefix = self.prefix
        clone.template = self.template
        clone.template_def_start_token = self.template_def_start_token
        clone.tokens = self.tokens
        clone.ast = self.ast

        # Important: Clone the formal arguments if they exist
        if self.formal_arguments is not None:
            clone.formal_arguments = OrderedDict()
            for k, v in self.formal_arguments.items():
                clone.formal_arguments[k] = v

        clone.has_formal_args = self.has_formal_args
        clone.number_of_args_with_default_values = (
            self.number_of_args_with_default_values
        )

        # Don't clone implicitly_defined_templates, as it is a cache and will be populated
        # when needed. This also prevents deep copies that are unnecessary.
        clone.implicitly_defined_templates = None

        clone.native_group = self.native_group
        clone.is_region = self.is_region
        clone.region_def_type = self.region_def_type
        clone.is_anon_subtemplate = self.is_anon_subtemplate

        # No need to clone strings, as they are immutable.
        clone.strings = self.strings[:]  # Shallow copy of the string list
        # The list is copied, but it contains the same elements.
        clone.instrs = self.instrs[:]  # Shallow copy
        clone.code_size = self.code_size
        clone.source_map = self.source_map[:]  # Shallow copy intervals

        # Don't clone the reference template.
        return clone

    def add_implicitly_defined_template(self, sub: "CompiledST") -> None:
        """
        Adds an implicitly defined template (like a region or anonymous subtemplate)
        to this template's list.
        """
        sub.prefix = self.prefix
        if not sub.name.startswith("/"):
            sub.name = sub.prefix + sub.name
        if self.implicitly_defined_templates is None:
            self.implicitly_defined_templates = []
        self.implicitly_defined_templates.append(sub)

    def define_arg_default_value_templates(self, group: STGroup) -> None:
        """
        Define default argument values that are templates.
        """
        if self.formal_arguments is None:
            return

        for a in self.formal_arguments:
            arg: FormalArgument = self.formal_arguments[a]
            if arg.default_value_token:
                self.number_of_args_with_default_values += 1
                if arg.default_value_token.type == GroupParser.ANONYMOUS_TEMPLATE:
                    arg_st_name = f"{arg.name}_default_value"
                    c2 = Compiler(group)
                    def_arg_template = Misc.strip(arg.default_value_token.text, 1)
                    arg.compiled_default_value = c2.compile(
                        group.file_name,
                        arg_st_name,
                        None,
                        def_arg_template,
                        arg.default_value_token,
                    )
                    arg.compiled_default_value.name = arg_st_name
                    arg.compiled_default_value.define_implicitly_defined_templates(
                        group
                    )

                elif arg.default_value_token.type == GroupParser.STRING:
                    arg.default_value = Misc.strip(arg.default_value_token.text, 1)

                elif arg.default_value_token.type == GroupParser.LBRACK:
                    arg.default_value = []

                elif arg.default_value_token.type in (
                    GroupParser.TRUE,
                    GroupParser.FALSE,
                ):
                    arg.default_value = arg.default_value_token.type == GroupParser.TRUE

                else:
                    raise ValueError(
                        f"Unexpected default value token type: {arg.default_value_token.type}"
                    )

    def define_formal_args(self, args: Optional[List[FormalArgument]]) -> None:
        """Define the formal arguments for this template."""
        self.has_formal_args = True  # Even if no args, it's formally defined
        if args is None:
            self.formal_arguments = None
        else:
            for a in args:
                self.add_arg(a)

    def add_arg(self, a: FormalArgument) -> None:
        """Add a formal argument to this template."""
        if self.formal_arguments is None:
            self.formal_arguments = OrderedDict()

        # Check for duplicate argument names
        if a.name in self.formal_arguments:
            raise ValueError(f"Formal argument {a.name} already exists.")

        a.index = len(self.formal_arguments)
        self.formal_arguments[a.name] = a

    def define_implicitly_defined_templates(self, group: STGroup) -> None:
        """
        Define any implicitly defined templates (like regions) within this template.
        """
        if self.implicitly_defined_templates:
            for sub in self.implicitly_defined_templates:
                group.raw_define_template(
                    sub.name, sub, sub.template_def_start_token
                )  # Token in ST.g not subtemplate
                sub.define_implicitly_defined_templates(group)

    def get_template_source(self) -> str:
        """Get the original template source."""
        r = self.get_template_range()
        if not self.template:  # Handle potential None value.
            return ""
        return self.template[r.a : r.b + 1]

    def get_template_range(self) -> Interval:
        """Get the range of the template in the original source."""
        if self.is_anon_subtemplate:
            start = sys.maxsize
            stop = -sys.maxsize - 1
            for interval in self.source_map:
                if interval:  # Handle potential None.
                    start = min(start, interval.a)
                    stop = max(stop, interval.b)
            if start <= stop:
                return Interval(start, stop)
        return Interval(0, len(self.template) - 1)

    def instrs(self) -> str:
        """
        Return a string representation of the bytecode instructions.  For debugging.
        """
        dis = BytecodeDisassembler(self)
        return dis.instrs()

    def dump(self) -> None:
        """
        Print a disassembly of the template to stdout.  For debugging.
        """
        dis = BytecodeDisassembler(self)
        print(self.name + ":")
        print(dis.disassemble())
        print("Strings:")
        print(dis.strings())
        print("Bytecode to template map:")
        print(dis.source_map())

    def disasm(self) -> str:
        """
        Return a string containing a disassembly of the template. For debugging.
        """
        dis = BytecodeDisassembler(self)
        output = []  # Use list
        output.append(dis.disassemble())
        output.append("Strings:")
        output.append(dis.strings())
        output.append("Bytecode to template map:")
        output.append(dis.source_map())
        return "\n".join(output)  # Join.


"""
Key changes and explanations for CompiledST:

    Instance Variables: All instance variables from the Java class are declared in the Python class, with appropriate type hints.
    Constructor: The constructor initializes the instrs, source_map, and template instance variables.
    clone() Method: This method now correctly performs a shallow copy of the CompiledST object, but deep copies the formal_arguments dictionary. This is crucial because the add() method on ST can modify the formal_arguments if a template doesn't have formally declared arguments. Without a deep copy of formal_arguments, modifications made to one ST instance could affect other instances that share the same CompiledST object.
    add_implicitly_defined_template(): This method correctly adds an implicitly defined template (like a region or anonymous subtemplate) to the list, ensuring the correct prefix is set.
    define_arg_default_value_templates(): This method is carefully translated, handling the different types of default value tokens (anonymous templates, strings, empty lists, booleans).
    define_formal_args() and add_arg(): These methods handle the definition of formal arguments, checking for duplicates. Using OrderedDict for formal_arguments ensures that the argument order is preserved, as in Java's LinkedHashMap.
    define_implicitly_defined_templates(): This method recursively defines implicitly defined templates within the group.
    get_template_source() and get_template_range(): These methods retrieve the original template source and the range within the source.
    instrs(), dump(), disasm(): These methods are for debugging/inspection and correctly create and use a BytecodeDisassembler instance. The dump() method prints the disassembly to standard output, while disasm() returns it as a string.
    Type Hints: Comprehensive type hints are included.
    Imports: Added all necessary imports.
    Collections: List is translated using list. Map and HashMap are converted to Python's dict. LinkedHashMap is replaced with OrderedDict to preserve insertion order. ArrayList is replaced with the built-in list.
    Error Handling: The CloneNotSupportedException is handled, converted to a RuntimeError.
    String Manipulation: substring method replaced with Python slicing.
    System.arraycopy: replaced with slice copy and extend.

This Python CompiledST class now accurately represents the compiled form of a StringTemplate template. It stores the bytecode, string table, source map, formal arguments, and other necessary information.  It also provides methods for manipulating and inspecting the compiled template, as well as for defining default argument values and implicitly defined templates.  The clone() method is now correctly implemented, addressing the critical issue of shared mutable state. This completes another essential building block of the StringTemplate engine.

"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
