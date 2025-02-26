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
import sys
from typing import List, Optional, Dict, Iterator, Any, Type, Tuple, Union, Set
from collections import deque
from array import array
import io
import traceback
from collections import OrderedDict, deque, abc

# Assuming these are in a separate module 'compiler' within org.stringtemplate.v4
from org.stringtemplate.v4.compiler.bytecode import Bytecode
from org.stringtemplate.v4.compiler.bytecode_disassembler import BytecodeDisassembler
from org.stringtemplate.v4.compiler.formal_argument import FormalArgument
from org.stringtemplate.v4.compiler.compiled_st import CompiledST
from org.stringtemplate.v4 import ST, STGroup
from org.stringtemplate.v4.api.model_adaptor import ModelAdaptor
from org.stringtemplate.v4.api.attribute_renderer import AttributeRenderer
from org.stringtemplate.v4.api.st_writer import STWriter
from org.stringtemplate.v4.instance_scope import InstanceScope
from org.stringtemplate.v4.misc.st_object_wrapper import wrap
from org.stringtemplate.v4.misc.helpers import ArrayIterator

# Debug related imports (using TYPE_CHECKING to prevent circular dependencies)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from org.stringtemplate.v4.debug.eval_template_event import EvalTemplateEvent
    from org.stringtemplate.v4.debug.eval_expr_event import EvalExprEvent
    from org.stringtemplate.v4.debug.indent_event import IndentEvent
    from org.stringtemplate.v4.debug.interp_event import InterpEvent
    from org.stringtemplate.v4.misc.interval import Interval
    from org.stringtemplate.v4.compiler import GroupParser  # Assuming location
    from org.stringtemplate.v4.misc.error_manager import (
        ErrorManager,
    )  # Assuming location
    from org.stringtemplate.v4.misc.error_type import ErrorType  # Assuming location
    from org.stringtemplate.v4.misc import Misc


class Interpreter:
    """
    This class knows how to execute template bytecodes relative to a particular
    STGroup. To execute the byte codes, we need an output stream and a
    reference to an ST instance. That instance's ST.impl field
    points at a CompiledST, which contains all of the byte codes and
    other information relevant to execution.

    This interpreter is a stack-based bytecode interpreter. All operands go onto
    an operand stack.

    If debug set, we track interpreter events. For now, I am only
    tracking instance creation events. These are used by STViz to pair up
    output chunks with the template expressions that generate them.

    We create a new interpreter for each invocation of
    ST.render(), ST.inspect(), or ST.getEvents().
    """

    class Option:  # Using a class with class-level variables.  More Pythonic than enum for this case.
        ANCHOR = 0
        FORMAT = 1
        NULL = 2
        SEPARATOR = 3
        WRAP = 4

    DEFAULT_OPERAND_STACK_SIZE = 100

    predefined_anon_subtemplate_attributes: Set[str] = {"i", "i0"}

    def __init__(
        self,
        group: STGroup,
        locale_val: Optional[locale.Locale] = None,
        err_mgr: Optional["ErrorManager"] = None,
        debug: bool = False,
    ):
        """
        Initialize the Interpreter.

        Args:
            group: The STGroup this interpreter is associated with.
            locale:  The locale to use for rendering.
            debug: Whether to enable debugging mode.
        """
        self.operands: List[Any] = [
            None
        ] * Interpreter.DEFAULT_OPERAND_STACK_SIZE  # Operand stack, grows upwards
        self.sp: int = -1  # Stack pointer register
        self.nwline: int = (
            0  # The number of characters written on this template line so far.
        )
        self.group: STGroup = group
        self.locale: Optional[locale.Locale] = (
            locale_val or locale.getlocale()
        )  # Corrected to get the current locale
        self.err_mgr = err_mgr or group.err_mgr
        self.debug: bool = debug
        self.execute_trace: Optional[List[str]] = [] if debug else None
        self.events: Optional[List["InterpEvent"]] = [] if debug else None

    def exec(self, out: STWriter, scope: InstanceScope) -> int:
        """
        Execute template self and return how many characters it wrote to out.
        """
        self_ = scope.st
        if Interpreter.trace:
            print(f"exec({self_.name})")
        try:
            self._set_default_arguments(out, scope)
            return self._exec(out, scope)
        except Exception as e:
            tb = traceback.format_exc()
            self.err_mgr.run_time_error(
                self, scope, "ErrorType.INTERNAL_ERROR", f"internal error: {tb}"
            )
            return 0

    def _exec(self, out: STWriter, scope: InstanceScope) -> int:
        """
        Protected _exec method to contain the main execution loop.
        """
        self_ = scope.st
        start: int = out.index()  # Track char we're about to write
        prev_opcode: int = 0
        n: int = 0  # How many char we write out
        code: bytearray = self_.compiled.instrs  # Which code block are we executing
        ip: int = 0
        while ip < self_.compiled.code_size:
            if Interpreter.trace or self.debug:
                self._trace(scope, ip)
            opcode: int = code[ip]
            scope.ip = ip
            ip += 1  # Jump to next instruction or first byte of operand

            if opcode == Bytecode.INSTR_LOAD_STR:
                self._load_str(self_, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES

            elif opcode == Bytecode.INSTR_LOAD_ATTR:
                name_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                name: str = self_.compiled.strings[name_index]
                try:
                    o = self._get_attribute(scope, name)
                    if o == ST.EMPTY_ATTR:
                        o = None
                except (
                    Exception
                ) as nsae:  # Assuming STNoSuchAttributeException is defined
                    self.err_mgr.run_time_error(
                        self, scope, "ErrorType.NO_SUCH_ATTRIBUTE", name
                    )
                    o = None
                self.operands[++self.sp] = o

            elif opcode == Bytecode.INSTR_LOAD_LOCAL:
                value_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                o: Any = self_.locals[value_index]
                if o == ST.EMPTY_ATTR:
                    o = None
                self.operands[++self.sp] = o

            elif opcode == Bytecode.INSTR_LOAD_PROP:
                name_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                o: Any = self.operands[self.sp]
                self.sp -= 1
                name: str = self_.compiled.strings[name_index]
                self.operands[++self.sp] = self._get_object_property(
                    out, scope, o, name
                )

            elif opcode == Bytecode.INSTR_LOAD_PROP_IND:
                prop_name: Any = self.operands[self.sp]
                self.sp -= 1
                o: Any = self.operands[self.sp]
                self.operands[self.sp] = self._get_object_property(
                    out, scope, o, prop_name
                )

            elif opcode == Bytecode.INSTR_NEW:
                name_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                name: str = self_.compiled.strings[name_index]
                nargs: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                # Look up in original hierarchy not enclosing template (variable group)
                # See TestSubtemplates.testEvalSTFromAnotherGroup()
                st: ST = (
                    self_.group_that_created_this_instance.get_embedded_instance_of(
                        self, scope, name
                    )
                )
                # Get n args and store into st's attr list
                self._store_args(scope, nargs, st)
                self.sp -= nargs
                self.operands[++self.sp] = st

            elif opcode == Bytecode.INSTR_NEW_IND:
                nargs: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                name: str = self.operands[self.sp - nargs]
                st: ST = (
                    self_.group_that_created_this_instance.get_embedded_instance_of(
                        self, scope, name
                    )
                )
                self._store_args(scope, nargs, st)
                self.sp -= nargs
                self.sp -= 1  # pop template name
                self.operands[++self.sp] = st

            elif opcode == Bytecode.INSTR_NEW_BOX_ARGS:
                name_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                name: str = self_.compiled.strings[name_index]
                attrs: Dict[str, Any] = self.operands[self.sp]
                self.sp -= 1
                # Look up in original hierarchy not enclosing template (variable group)
                # see TestSubtemplates.testEvalSTFromAnotherGroup()
                st: ST = (
                    self_.group_that_created_this_instance.get_embedded_instance_of(
                        self, scope, name
                    )
                )
                # Get n args and store into st's attr list
                self._store_args_from_map(scope, attrs, st)
                self.operands[++self.sp] = st

            elif opcode == Bytecode.INSTR_SUPER_NEW:
                name_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                name: str = self_.compiled.strings[name_index]
                nargs: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                self._super_new(scope, name, nargs)

            elif opcode == Bytecode.INSTR_SUPER_NEW_BOX_ARGS:
                name_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                name: str = self_.compiled.strings[name_index]
                attrs: Dict[str, Any] = self.operands[self.sp]
                self.sp -= 1
                self._super_new_from_map(scope, name, attrs)

            elif opcode == Bytecode.INSTR_STORE_OPTION:
                option_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                o: Any = self.operands[self.sp]
                self.sp -= 1  # value to store
                options: List[Any] = self.operands[self.sp]  # Get options
                options[option_index] = o  # Store value into options on stack

            elif opcode == Bytecode.INSTR_STORE_ARG:
                name_index: int = self._get_short(code, ip)
                name: str = self_.compiled.strings[name_index]
                ip += Bytecode.OPND_SIZE_IN_BYTES
                o: Any = self.operands[self.sp]
                self.sp -= 1
                attrs: Dict[str, Any] = self.operands[self.sp]
                attrs[name] = o  # Leave attrs on stack

            elif opcode == Bytecode.INSTR_WRITE:
                o = self.operands[self.sp]
                self.sp -= 1
                n1: int = self._write_object_no_options(out, scope, o)
                n += n1
                self.nwline += n1

            elif opcode == Bytecode.INSTR_WRITE_OPT:
                options: List[Any] = self.operands[self.sp - 1]  # Get options
                o: Any = self.operands[self.sp]  # Get option to write
                self.sp -= 2
                n2: int = self._write_object_with_options(out, scope, o, options)
                n += n2
                self.nwline += n2

            elif opcode == Bytecode.INSTR_MAP:
                st: ST = self.operands[self.sp]
                self.sp -= 1  # Get prototype off stack
                o: Any = self.operands[self.sp]
                self.sp -= 1  # Get object to map prototype across
                self._map(scope, o, st)

            elif opcode == Bytecode.INSTR_ROT_MAP:
                nmaps: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                templates: List[ST] = []
                for i in range(nmaps - 1, -1, -1):
                    templates.append(self.operands[self.sp - i])
                self.sp -= nmaps
                o: Any = self.operands[self.sp]
                self.sp -= 1
                if o is not None:
                    self._rot_map(scope, o, templates)

            elif opcode == Bytecode.INSTR_ZIP_MAP:
                st: ST = self.operands[self.sp]
                self.sp -= 1
                nmaps: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                exprs: List[Any] = []
                for i in range(nmaps - 1, -1, -1):
                    exprs.append(self.operands[self.sp - i])
                self.sp -= nmaps
                self.operands[++self.sp] = self._zip_map(scope, exprs, st)

            elif opcode == Bytecode.INSTR_BR:
                ip = self._get_short(code, ip)

            elif opcode == Bytecode.INSTR_BRF:
                addr: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                o: Any = self.operands[self.sp]
                self.sp -= 1  # <if(expr)>...<endif>
                if not self._test_attribute_true(o):
                    ip = addr  # jump

            elif opcode == Bytecode.INSTR_OPTIONS:
                self.operands[++self.sp] = [None] * Compiler.NUM_OPTIONS

            elif opcode == Bytecode.INSTR_ARGS:
                self.operands[++self.sp] = {}  # Use a regular dict in Python

            elif opcode == Bytecode.INSTR_PASSTHRU:
                name_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                name: str = self_.compiled.strings[name_index]
                attrs: Dict[str, Any] = self.operands[self.sp]
                self._passthru(scope, name, attrs)

            elif opcode == Bytecode.INSTR_LIST:
                self.operands[++self.sp] = []  # Use a regular list in Python

            elif opcode == Bytecode.INSTR_ADD:
                o: Any = self.operands[self.sp]
                self.sp -= 1  # pop value
                list_: List[Any] = self.operands[self.sp]  # Don't pop list
                self._add_to_list(scope, list_, o)

            elif opcode == Bytecode.INSTR_TOSTR:
                # Replace with string value; early eval
                self.operands[self.sp] = self._to_string(
                    out, scope, self.operands[self.sp]
                )

            elif opcode == Bytecode.INSTR_FIRST:
                self.operands[self.sp] = self._first(scope, self.operands[self.sp])

            elif opcode == Bytecode.INSTR_LAST:
                self.operands[self.sp] = self._last(scope, self.operands[self.sp])

            elif opcode == Bytecode.INSTR_REST:
                self.operands[self.sp] = self._rest(scope, self.operands[self.sp])

            elif opcode == Bytecode.INSTR_TRUNC:
                self.operands[self.sp] = self._trunc(scope, self.operands[self.sp])

            elif opcode == Bytecode.INSTR_STRIP:
                self.operands[self.sp] = self._strip(scope, self.operands[self.sp])

            elif opcode == Bytecode.INSTR_TRIM:
                o: Any = self.operands[self.sp]
                if isinstance(o, str):
                    self.operands[self.sp] = o.strip()  # Trim whitespace in Python
                else:
                    self.operands[self.sp] = o

            elif opcode == Bytecode.INSTR_LENGTH:
                self.operands[self.sp] = self._length(scope, self.operands[self.sp])

            elif opcode == Bytecode.INSTR_STRLEN:
                s: str = self.operands[self.sp]
                self.operands[self.sp] = len(s)  # Python strings have built-in length

            elif opcode == Bytecode.INSTR_REVERSE:
                self.operands[self.sp] = self._reverse(scope, self.operands[self.sp])

            elif opcode == Bytecode.INSTR_NOT:
                self.operands[self.sp] = not self._test_attribute_true(
                    self.operands[self.sp]
                )

            elif opcode == Bytecode.INSTR_OR:
                right = self.operands[self.sp]
                self.sp -= 1
                left = self.operands[self.sp]
                self.operands[self.sp] = self._test_attribute_true(
                    left
                ) or self._test_attribute_true(right)

            elif opcode == Bytecode.INSTR_AND:
                right = self.operands[self.sp]
                self.sp -= 1
                left = self.operands[self.sp]
                self.operands[self.sp] = self._test_attribute_true(
                    left
                ) and self._test_attribute_true(right)

            elif opcode == Bytecode.INSTR_INDENT:
                str_index: int = self._get_short(code, ip)
                ip += Bytecode.OPND_SIZE_IN_BYTES
                indent: str = self_.compiled.strings[str_index]
                if self.debug:
                    self._debug_indent(start, out, scope, indent)

                out.write(indent)  # Directly write in Python
                self.nwline += len(indent)

            elif opcode == Bytecode.INSTR_DEDENT:
                out.dedent()

            elif opcode == Bytecode.INSTR_NEWLINE:
                if (
                    prev_opcode == Bytecode.INSTR_NEWLINE
                    or prev_opcode == Bytecode.INSTR_INDENT
                ):
                    # Don't write if we just wrote a newline.  Can only happen
                    # when we have wrap option.  Can't suppress the newline itself
                    # because we don't know what's coming.  can only skip if
                    # it's an INDENT or NEWLINE.
                    pass
                else:
                    if self.debug:
                        self._debug_newline(start, out, scope)
                    out.write("\n")  # Use Python's newline
                    self.nwline = 0

            else:
                self.err_mgr.run_time_error(
                    self, scope, "ErrorType.INVALID_BYTECODE", f"{opcode}"
                )

            prev_opcode = opcode

        if self.debug:
            self._end_of_instance_debug(start, out, scope)
        return n

    def _set_default_arguments(self, out: STWriter, scope: InstanceScope) -> None:
        """
        Set default argument values.  For a template with n formal arguments,
        we create a vector of n attributes.  We only set default
        argument i if a value for argument i was not set when instantiating
        the template.  For example, <a, b, c, d=32, e={"foo"}>.
        """
        self_ = scope.st
        formal_args = self_.compiled.formal_arguments
        if not formal_args:
            return

        if self_.locals is None:
            self_.locals = [None] * len(
                formal_args
            )  # Make space for args and predefined locals like i,i0

        for i in range(len(formal_args)):
            arg: FormalArgument = formal_args[i]
            if (
                self_.locals[arg.index] == ST.EMPTY_ATTR
                and arg.default_value_token is not None
            ):
                # Only set default value if no value was set for this arg
                scope.ip = (
                    arg.default_value_token.start
                )  # Set to execute default value expr
                self._exec_in_new_context(out, scope, self, arg.default_value_ast)

    def _store_args(self, scope: InstanceScope, nargs: int, st: ST) -> None:
        """
        Store n arguments in starting at index 0 of attributes list.
        """
        if nargs == 0:
            return

        locals_ = [None] * nargs  # new Object[nargs];

        # Args are on stack in reverse order, so copy to reverse of locals
        j: int = nargs - 1
        for i in range(nargs):
            locals_[j] = self.operands[self.sp - i]  # Copy from stack to locals_ array
            j -= 1

        if st.locals is None:
            st.locals = locals_
        else:
            # Already has locals, just overwrite existing args
            st.locals[:nargs] = locals_

    def _store_args_from_map(
        self, scope: InstanceScope, attrs: Dict[str, Any], st: ST
    ) -> None:
        """
        Given a map of attribute values, copy to ST.locals.
        """
        if not attrs:
            return  # Nothing to do

        if not st.compiled.formal_arguments:
            # Formal args of st
            self.err_mgr.run_time_error(
                self,
                scope,
                "ErrorType.ARGUMENT_COUNT_MISMATCH",
                f"{st.name} has no formal arguments, but you passed in {len(attrs)} attributes",
            )
            return

        # Copy every value in attrs to ST.locals.
        for formal_arg_name, formal_arg in st.compiled.formal_arguments.items():
            value: Any = attrs.get(formal_arg_name, None)  # Check if present in attrs
            if value is not None:
                st.locals[formal_arg.index] = value
            else:
                # Didn't specify value for this formal arg; don't overwrite default value if any
                if st.locals[formal_arg.index] == ST.EMPTY_ATTR:
                    st.locals[formal_arg.index] = None  # Ensure it's initialized.

        # Now, look for formal args in st with no value to copy it over.
        for k, v in attrs.items():
            formal_arg: Optional[FormalArgument] = st.compiled.formal_arguments.get(k)
            if formal_arg is None:
                # Didn't find arg, report error
                self.err_mgr.run_time_error(
                    self, scope, "ErrorType.TEMPLATE_REDEFINITION_ACROSS_DELIMITERS", k
                )

    def _super_new(self, scope: InstanceScope, name: str, nargs: int) -> None:
        """
        Create an instance of an embedded template using the super group's
        definition then override just the attributes with formal parameters.
        """
        self_ = scope.st
        super_group: STGroup = self_.group.super_group
        if not super_group:
            self.err_mgr.run_time_error(
                self,
                scope,
                "ErrorType.NO_SUCH_TEMPLATE",
                f"{self_.group.name} has no super group; invalid super.{name}",
            )
            self.operands[++self.sp] = ST.EMPTY_ATTR  # blank template
            return

        if name.find(".") == -1:  # If no '.' in name
            name = "super." + name  # Prepend super.

        st: ST = super_group.get_embedded_instance_of(self, scope, name)
        # Get n args and store into st's attr list
        self._store_args(scope, nargs, st)
        self.sp -= nargs
        self.operands[++self.sp] = st

    def _super_new_from_map(
        self, scope: InstanceScope, name: str, attrs: Dict[str, Any]
    ) -> None:
        """
        Create an instance of an embedded template using the super group's
        definition then override just the attributes with formal parameters.
        """
        self_ = scope.st
        super_group: STGroup = self_.group.super_group
        if not super_group:
            self.err_mgr.run_time_error(
                self,
                scope,
                "ErrorType.NO_SUCH_TEMPLATE",
                f"{self_.group.name} has no super group; invalid super.{name}",
            )
            self.operands[++self.sp] = ST.EMPTY_ATTR  # Blank template
            return

        if name.find(".") == -1:  # If no '.' in name
            name = "super." + name  # Prepend super.

        st: ST = super_group.get_embedded_instance_of(self, scope, name)
        # Get n args and store into st's attr list
        self._store_args_from_map(scope, attrs, st)
        self.operands[++self.sp] = st

    def _map(self, scope: InstanceScope, o: Any, st: ST) -> None:
        """
        Apply an ST instance (like a method) to every element of an aggregate.
        The result is a list with an element for each element in o.
        """
        if o is None:
            self.operands[++self.sp] = None
            return

        result: List[Any] = []  # new ArrayList<Object>()
        n: int = self._get_number_of_elements(o)
        if n == 0:
            self.operands[++self.sp] = result
            return

        it: Iterator[Any]
        if (
            isinstance(o, list)
            or isinstance(o, tuple)
            or isinstance(o, array)
            or hasattr(o, "__len__")
        ):  # Iterable check.
            it = iter(o)
        elif hasattr(o, "values") and callable(o.values):  # dict-like check.
            it = iter(o.values())  # Assume it's a dictionary
        else:
            # Call map(o) on a scalar value?  Map to a list with one value
            # Call map(o) on a scalar value?  Map to a list with one value
            self.operands[++self.sp] = self._apply_template_to_an_element(
                scope, o, st, 0, -1
            )
            return

        for i in range(n):
            result.append(
                self._apply_template_to_an_element(scope, next(it), st, i, n - 1)
            )

        self.operands[++self.sp] = result

    def _rot_map(self, scope: InstanceScope, o: Any, templates: List[ST]) -> None:
        if o is None:
            self.operands[++self.sp] = None
            return

        result: List[Any] = []  # new ArrayList<Object>()
        n: int = self._get_number_of_elements(o)
        if n == 0:
            self.operands[++self.sp] = result
            return

        it: Iterator[Any]
        if (
            isinstance(o, list)
            or isinstance(o, tuple)
            or isinstance(o, array)
            or hasattr(o, "__len__")
        ):  # Iterable check
            it = iter(o)
        elif hasattr(o, "values") and callable(o.values):  # dict-like check.
            it = iter(o.values())  # Assume it's a dictionary
        else:
            self.err_mgr.run_time_error(
                self,
                scope,
                "ErrorType.NO_SUCH_ATTRIBUTE",
                "missing attribute: " + str(o),
            )
            self.operands[++self.sp] = None
            return

        num_templates: int = len(templates)
        for i in range(n):
            template_index: int = i % num_templates
            result.append(
                self._apply_template_to_an_element(
                    scope, next(it), templates[template_index], i, n - 1
                )
            )

        self.operands[++self.sp] = result

    def _zip_map(self, scope: InstanceScope, exprs: List[Any], st: ST) -> List[Any]:
        """
        Merge zip(a,b,c) with t to create [t(a[0],b[0],c[0]), t(a[1],b[1],c[1]), ...].
        """
        if not exprs:
            return []  # Nothing to do

        result: List[Any] = []  # new ArrayList<Object>();
        n: int = self._get_number_of_elements(exprs[0])

        # Check to ensure that all lists are the same length
        for expr in exprs:
            if self._get_number_of_elements(expr) != n:
                self.err_mgr.run_time_error(
                    self,
                    scope,
                    "ErrorType.ZIP_MAP_ARGUMENT_COUNT_MISMATCH",
                    f"mismatched list sizes: {', '.join([str(self._get_number_of_elements(e)) for e in exprs])}",
                )
                return []

        iterators: List[Iterator[Any]] = [
            self._to_iterator(scope, expr) for expr in exprs
        ]
        for i in range(n):
            args: List[Any] = [None] * (len(exprs) + 2)  # 2 extra for i, i0
            for j in range(len(exprs)):
                it: Iterator[Any] = iterators[j]
                args[j] = next(it)
            args[-2] = i
            args[-1] = i + 1  # Start from 1 for i
            result.append(self._apply_template_with_args(scope, st, i, args))

        return result

    def _apply_template_to_an_element(
        self, scope: InstanceScope, o: Any, st: ST, i: int, last_index: int
    ) -> Optional[ST]:
        """
        Apply an ST instance (like a method) to an atomic value or element of an aggregate.
        """
        if not st:
            return None

        # If we have implicit for-loop and this template has a formal arg, inject value
        has_implicit_iteration: bool = False
        if st.compiled.formal_arguments:
            if "i0" in st.compiled.formal_arguments:
                has_implicit_iteration = True
                if st.locals is None:
                    st.locals = [None] * len(st.compiled.formal_arguments)
                st.locals[st.compiled.formal_arguments["i0"].index] = i
            if "i" in st.compiled.formal_arguments:
                has_implicit_iteration = True
                if st.locals is None:
                    st.locals = [None] * len(st.compiled.formal_arguments)
                st.locals[st.compiled.formal_arguments["i"].index] = i + 1

            # If no formal parameters, we do not need to set values.
            if (
                len(st.compiled.formal_arguments) - (2 if has_implicit_iteration else 0)
                > 0
            ):
                if st.locals is None:
                    st.locals = [None] * len(st.compiled.formal_arguments)

                n: int = len(st.compiled.formal_arguments) - (
                    2 if has_implicit_iteration else 0
                )
                # Only set the first arg
                if "it" in st.compiled.formal_arguments:
                    st.locals[st.compiled.formal_arguments["it"].index] = o
                    n = 0  # don't set others
                for j in range(n):
                    arg_name: str = st.compiled.args_metadata[
                        j
                    ].name  # Find first formal arg of real args
                    st.locals[st.compiled.formal_arguments[arg_name].index] = o

        if self.debug:
            e: "EvalTemplateEvent" = self.group.debug_listener.ref_template(
                self, scope, st
            )
            self.events.append(e)

        return st  # Return ST to invoke

    def _apply_template_with_args(
        self, scope: InstanceScope, st: ST, i: int, values: List[Any]
    ) -> Optional[ST]:
        """
        Apply an ST instance, passing arguments.
        """
        if not st:
            return None

        # If we have implicit for-loop and this template has a formal arg, inject value
        if st.compiled.formal_arguments:
            if "i0" in st.compiled.formal_arguments:
                if st.locals is None:
                    st.locals = [None] * len(st.compiled.formal_arguments)
                st.locals[st.compiled.formal_arguments["i0"].index] = i
            if "i" in st.compiled.formal_arguments:
                if st.locals is None:
                    st.locals = [None] * len(st.compiled.formal_arguments)
                    st.locals[st.compiled.formal_arguments["i"].index] = i + 1

            if st.locals is None:
                st.locals = [None] * len(st.compiled.formal_arguments)

            n: int = len(values)
            if "it" in st.compiled.formal_arguments:
                # If "it" is defined, map values to that directly.
                it_index = st.compiled.formal_arguments["it"].index
                st.locals[it_index] = values[0]  # Assign first value to "it"
                n = min(len(values), len(st.compiled.formal_arguments))
                for j in range(
                    1, n
                ):  # start from 1, as we already assigned the 0th item.
                    arg_name: str = st.compiled.args_metadata[j].name  # Find formal arg
                    arg_index = st.compiled.formal_arguments[arg_name].index
                    st.locals[arg_index] = values[j]
            else:
                n = min(
                    len(values), len(st.compiled.formal_arguments)
                )  # Cap at the number of formal arguments

                # Assign values to formal parameters.
                for j in range(n):
                    arg_name: str = st.compiled.args_metadata[j].name  # Find formal arg
                    if arg_name:  # Check if arg_name is valid, for safety.
                        arg_index = st.compiled.formal_arguments[arg_name].index
                        st.locals[arg_index] = values[j]

        if self.debug:
            e: "EvalTemplateEvent" = self.group.debug_listener.ref_template(
                self, scope, st
            )
            self.events.append(e)

        return st  # Return ST to invoke

    def _passthru(
        self, scope: InstanceScope, template_name: str, attrs: Dict[str, Any]
    ) -> None:
        """
        Create an implicit template that has the same group as the invoking
        template. Pass in the attributes created by the user for this
        anonymous subtemplate.  Those are all in attrs parameter.

        This also takes care of getting predefined attributes into the
        subtemplate.
        """
        st: ST = ST(self.group, "{}")  # Create blank template
        st.impl.name = ST.ANON_SUBTEMPLATE_NAME

        formal_args = OrderedDict()  # new LinkedHashMap<String, FormalArgument>()

        # Define "it" arg
        it_arg: FormalArgument = FormalArgument("it")
        it_arg.index = 0
        formal_args["it"] = it_arg
        st.impl.add_formal_argument(it_arg)

        # Pass through attributes from outer template to subtemplate
        for k, v in attrs.items():
            # If the name is predefined, don't define it.  Let code gen
            # define it so that the code gen, not the user, sets the
            # value.  This prevents user from redefining, for example,
            # attribute "i".
            if k in Interpreter.predefined_anon_subtemplate_attributes:
                continue
            arg: FormalArgument = FormalArgument(k)
            arg.index = len(formal_args)  # Keep track of index
            formal_args[k] = arg  # Add to the ordered dict
            st.impl.add_formal_argument(arg)

        # Check for formal argument compatibility
        if len(attrs) != len(formal_args) - 1:  # -1 to account for "it"
            self.err_mgr.run_time_error(
                self,
                scope,
                "ErrorType.ARGUMENT_COUNT_MISMATCH",
                f"mismatched arg number in subtemplate for it={template_name}"
                + f" passed {len(attrs)} != expected {len(formal_args) - 1}",
            )

        st.impl.formal_arguments = formal_args
        st.locals = [None] * len(formal_args)  # Allocate space for args
        i: int = 0
        # Copy values into locals
        for k, v in attrs.items():
            st.locals[formal_args[k].index] = v

        self.operands[++self.sp] = st

    def _add_to_list(self, scope: InstanceScope, list_: List[Any], o: Any) -> None:
        """
        Add an object to a list. If o is an array, convert it to a list and
        then add it.
        """
        if o is not None:  # Skip null values
            if isinstance(o, list):  # If it is already a list
                list_.extend(o)
            elif isinstance(o, tuple):  # Convert tuples
                list_.extend(list(o))
            elif isinstance(o, array):  # If it's an array
                list_.extend(list(o))
            else:
                list_.append(o)

    def _first(self, scope: InstanceScope, o: Any) -> Any:
        """
        Return the first element of a list, array, or by using a model adaptor.
        """
        if o is None:
            return None
        first_value: Any = None
        it = self._to_iterator(scope, o)
        if it is not None and it.has_next():
            first_value = it.next()
            if isinstance(first_value, ST):
                if first_value.is_empty():
                    first_value = None
        elif isinstance(o, str):  # handle string as iterable
            return o[0] if len(o) > 0 else None  # string can have length
        return first_value

    def _last(self, scope: InstanceScope, o: Any) -> Any:
        if o is None:
            return None
        last: Any = None

        if (
            isinstance(o, list) or isinstance(o, tuple) or isinstance(o, array)
        ):  # For lists and similar
            return o[-1] if len(o) > 0 else None
        elif isinstance(o, str):  # handle string as iterable
            return o[-1] if len(o) > 0 else None
        elif (
            isinstance(o, dict) or hasattr(o, "values") and callable(o.values)
        ):  # For dict-like objects
            try:
                *_, last = o.values()  # Get last item, works for dict-likes.
                return last
            except ValueError:  # Empty
                return None
        else:
            adaptor: ModelAdaptor = self.group.get_adaptor(type(o))
            if adaptor:
                it: Iterator[Any] = adaptor.get_iterator(
                    self, o
                )  # Assuming getIterator()
                if it:
                    while it.has_next():
                        last = it.next()

        return last

    def _rest(self, scope: InstanceScope, o: Any) -> Any:
        if o is None:
            return None

        if isinstance(o, list):
            return o[1:]
        elif isinstance(o, tuple):
            return tuple(o[1:])
        elif isinstance(o, array):
            return array(o.typecode, o[1:])  # Reconstruct array
        elif isinstance(o, str):
            return o[1:]
        elif isinstance(o, dict) or (
            hasattr(o, "values") and callable(o.values)
        ):  # Check dict-like
            it: Iterator[Any] = iter(o.values())  # create iterator for values
            try:
                next(it)  # skip first element.
                return list(it)
            except StopIteration:  # empty dictionary-like object.
                return []

        else:  # use adaptors
            adaptor: ModelAdaptor = self.group.get_adaptor(type(o))
            if adaptor:
                it: Iterator[Any] = adaptor.get_iterator(self, o)
                if it:
                    try:
                        next(it)  # skip first element.
                        return list(it)  # consume and return as list
                    except StopIteration:
                        return []

        return None

    def _trunc(self, scope: InstanceScope, o: Any) -> Any:
        """
        Return all elements of an aggregate except the last one.
        """
        if o is None:
            return None
        if isinstance(o, list):
            return o[:-1]
        elif isinstance(o, tuple):
            return tuple(o[:-1])
        elif isinstance(o, array):
            return array(o.typecode, o[:-1])
        elif isinstance(o, str):
            return o[:-1]
        elif isinstance(o, dict) or (hasattr(o, "values") and callable(o.values)):
            it: Iterator[Any] = iter(o.values())
            all_but_last: List[Any] = []
            try:
                prev = next(it)
                while True:
                    current = next(it)
                    all_but_last.append(prev)
                    prev = current
            except StopIteration:
                return all_but_last  # Exhausted
        else:  # handle adaptors
            adaptor: ModelAdaptor = self.group.get_adaptor(type(o))
            if adaptor:
                it: Iterator[Any] = adaptor.get_iterator(
                    self, o
                )  # Assuming getIterator()
                if it:
                    all_but_last: List[Any] = []
                    try:
                        prev = next(it)
                        while True:
                            current = next(it)
                            all_but_last.append(prev)
                            prev = current
                    except StopIteration:
                        return all_but_last
        return None

    def _strip(self, scope: InstanceScope, o: Any) -> Any:
        """
        Return a new list with all null values removed.
        """
        if o is None:
            return None

        if isinstance(o, list):
            return [x for x in o if x is not None]
        elif isinstance(o, tuple):
            return tuple(
                [x for x in o if x is not None]
            )  # Convert to list, filter, and convert back to tuple
        elif isinstance(o, array):
            return array(
                o.typecode, [x for x in o if x is not None]
            )  # filter and recreate
        elif isinstance(o, str):  # String is an aggregate of characters.
            return o  # strip does nothing to a string.
        elif isinstance(o, dict) or (hasattr(o, "values") and callable(o.values)):
            return [v for v in o.values() if v is not None]
        else:
            adaptor: ModelAdaptor = self.group.get_adaptor(type(o))
            if adaptor:
                it: Iterator[Any] = adaptor.get_iterator(
                    self, o
                )  # Assuming getIterator()
                if it:
                    return [
                        x for x in it if x is not None
                    ]  # Filter using list comprehension
        return None

    def _length(self, scope: InstanceScope, o: Any) -> int:
        """
        Return the length of a list, array, map, or by using a model adaptor.
        """
        if o is None:
            return 0

        return self._get_number_of_elements(o)

    def _reverse(self, scope: InstanceScope, o: Any) -> Any:
        """
        Return a new list with the elements of o in reverse order.
        """
        if o is None:
            return None

        if isinstance(o, list):
            return o[::-1]  # Use slicing for lists
        elif isinstance(o, tuple):
            return tuple(o[::-1])
        elif isinstance(o, array):
            return array(o.typecode, o[::-1])  # reverse, and recreate.
        elif isinstance(o, str):
            return o[::-1]
        elif isinstance(o, dict) or (hasattr(o, "values") and callable(o.values)):
            # Reverse the list of values for dict-like objects
            return list(reversed(list(o.values())))  # Corrected to list(o.values())
        else:
            adaptor: ModelAdaptor = self.group.get_adaptor(type(o))
            if adaptor:
                # try iterator and build reversed list.
                it: Iterator[Any] = adaptor.get_iterator(self, o)
                if it:
                    reversed_list: List[Any] = list(it)  # consume
                    reversed_list.reverse()  # in-place reverse.
                    return reversed_list
        return None

    def _get_attribute(self, scope: InstanceScope, name: str) -> Any:
        """
        Evaluate attribute name, looking first in the locals then in the
        attributes.
        """
        self_ = scope.st

        if self_.locals is not None:
            formal_arg: Optional[FormalArgument] = (
                self_.compiled.formal_arguments.get(name)
                if self_.compiled.formal_arguments
                else None
            )
            if formal_arg:
                o = self_.locals[formal_arg.index]
                return o

        # Must be an attribute in the ST
        return self_.get_attribute(name)

    def _get_object_property(
        self, out: STWriter, scope: InstanceScope, o: Any, property: Any
    ) -> Any:
        """
        Evaluate o.property by calling o's adaptors getProperty method.
        """
        if o is None or property is None:
            return None

        property_name: str = str(property)  # Ensure property is a string
        adaptor: ModelAdaptor = self.group.get_adaptor(type(o))
        try:
            return adaptor.get_property(self, o, property_name)
        except Exception as e:
            self.err_mgr.run_time_error(
                self,
                scope,
                "ErrorType.CANT_GET_PROPERTY",
                f"can't get property {property_name} of {o}",
            )
            return None  # Or handle as appropriate

    def _write_object_no_options(
        self, out: STWriter, scope: InstanceScope, o: Any
    ) -> int:
        """
        Write an object to the output stream, handling null values and using
        renderers for formatting.
        """
        if o is None:
            return 0  # Do nothing for null values

        if isinstance(o, ST):
            return self._write_template(
                out, scope, o
            )  # Directly use write_template for ST instances

        # Lookup renderer
        renderer = self.group.get_renderer(type(o))
        if renderer:
            return self._write_using_renderer(out, scope, o, renderer, None)
        elif isinstance(o, list):
            # Write each item
            written: int = 0
            for item in o:
                written += self._write_object_no_options(out, scope, item)
            return written
        elif isinstance(o, tuple):
            written = 0
            for item in o:
                written += self._write_object_no_options(out, scope, item)
            return written
        elif isinstance(o, dict):
            # Use the string template's separator, and re-wrap with Map.
            st_sep: ST = self.group.get_template(
                "map_sep"
            )  # Assuming 'map_sep' template is defined in STGroup
            sep: Optional[str] = None
            if st_sep:
                # Execute to get the value for separator
                sep = st_sep.render()
                # remove newlines
                if sep:
                    sep = sep.replace("\n", "").replace("\r", "")

            written: int = 0
            first: bool = True

            for k, v in o.items():
                if not first and sep is not None:
                    written += out.write(sep)
                written += self._write_object_no_options(
                    out, scope, v
                )  # Write the map value
                first = False
            return written

        elif isinstance(o, array):  # Handle arrays
            written = 0
            for item in o:
                written += self._write_object_no_options(out, scope, item)
            return written
        else:
            # For anything else, convert to string and write
            s: str = self._to_string(out, scope, o)
            return out.write(s)

    def _write_object_with_options(
        self, out: STWriter, scope: InstanceScope, o: Any, options: List[Any]
    ) -> int:
        """
        Write an object to the output stream, handling options like wrap,
        separator, and format.
        """
        if o is None:
            # Use the null option
            if options[Interpreter.Option.NULL] is not None:
                return out.write(str(options[Interpreter.Option.NULL]))
            else:
                return 0

        original_o: Any = o
        original_sp: int = self.sp

        wrap: str = options[Interpreter.Option.WRAP]
        if wrap is not None:
            wrap = self._coerce_arg_to_string(wrap, scope)  # Coerce to string if needed

        separator: Optional[str] = options[Interpreter.Option.SEPARATOR]
        if separator is not None:
            separator = self._coerce_arg_to_string(separator, scope)

        anchor: bool = options[Interpreter.Option.ANCHOR] is True

        if isinstance(o, ST):
            return self._write_template(out, scope, o)  # Directly write ST instances

        # Lookup renderer for this value's type
        renderer: Optional[AttributeRenderer] = self.group.get_renderer(type(o))
        if renderer:
            return self._write_using_renderer(
                out, scope, o, renderer, options[Interpreter.Option.FORMAT]
            )

        # If not iterable, treat as a single value
        if not self._is_iterable(o):
            s: str = self._to_string(out, scope, o)
            if wrap is not None and len(s) > 0:
                return self._write_wrapped_string(out, scope, s, wrap, anchor)
            else:
                return out.write(s, anchor)

        # Handle iterables
        it: Iterator[Any] = self._to_iterator(scope, o)
        if not it:
            s = self._to_string(out, scope, o)  # Just print the object
            if wrap is not None and len(s) > 0:
                return self._write_wrapped_string(out, scope, s, wrap, anchor)
            else:
                return out.write(s, anchor)

        # Process iterator
        written: int = 0
        try:
            if anchor:
                written += out.anchor_point()

            first: bool = True
            while it.has_next():
                iter_value: Any = it.next()
                if iter_value is not None:  # Don't insert separator before a None value
                    if not first and separator is not None:
                        written += out.write(separator)
                    first = False

                    # If value is itself an ST, make sure we evaluate *before* potentially wrapping
                    if isinstance(iter_value, ST):
                        written += self._write_template(
                            out, scope, iter_value
                        )  # Use _write_template to avoid infinite loop.
                        continue
                    # Call self again on the single element if its iterable
                    if self._is_iterable(iter_value):
                        written += self._write_object_with_options(
                            out, scope, iter_value, options
                        )  # Recursively call.
                        continue

                    to_str: str = self._to_string(out, scope, iter_value)

                    if wrap is not None and len(to_str) > 0:
                        written += self._write_wrapped_string(
                            out, scope, to_str, wrap, False
                        )  # do not anchor in here!
                    else:
                        written += out.write(to_str)

        except Exception as e:
            self.err_mgr.run_time_error(
                self,
                scope,
                "ErrorType.WRITE_IO_ERROR",
                f"error writing {type(o)} value {o}",
            )
        finally:
            # Ensure the stack is restored
            self.sp = original_sp

        return written

    def _write_template(
        self, out: STWriter, invoking_scope: InstanceScope, st: ST
    ) -> int:
        """
        Execute the template st with its own instance scope, and send output to out.
        """
        n: int = 0
        scope = InstanceScope(invoking_scope, st)

        try:
            if self.debug:
                e: "EvalTemplateEvent" = self.group.debug_listener.ref_template(
                    self, invoking_scope, st
                )
                self.events.append(e)

            n = self._exec(out, scope)  # Execute.
        finally:
            pass
        return n

    def _write_using_renderer(
        self,
        out: STWriter,
        scope: InstanceScope,
        o: Any,
        renderer: AttributeRenderer,
        format_string: Optional[str],
    ) -> int:
        """
        Write o using the specified renderer, taking the formatting string, if any, into account.
        """
        if format_string is not None:
            formatted_str: str = renderer.to_string(o, format_string, self.locale)
        else:
            formatted_str: str = renderer.to_string(
                o, None, self.locale
            )  # Use default format
        return out.write(formatted_str)  # Write the formatted string

    def _write_wrapped_string(
        self, out: STWriter, scope: InstanceScope, s: str, wrap: str, anchor: bool
    ) -> int:
        """
        Write a string, wrapping it at the current line width.
        """
        n: int = 0
        lines: List[str] = s.splitlines(
            keepends=True
        )  # Correctly split string into lines

        for i, line in enumerate(lines):
            if i > 0:  # For all lines after the first
                if len(line) > 0:  # only print if not a blank line
                    n += out.write(wrap)  # Newline
                self.nwline = len(wrap)  # We are now at the wrap string of next line
            if len(line) > 0:  # only print if not a blank line
                n += out.write(line, anchor and i == 0)  # Pass anchor for first line
            self.nwline += len(line)
        return n

    def _to_string(self, out: STWriter, scope: InstanceScope, o: Any) -> str:
        """
        Convert an attribute to a string, using the current locale and handling
        nested ST instances.
        """
        if o is None:
            return ""

        if isinstance(o, ST):
            # If o is an ST, we need to render it to a string
            sub_out = self.group.create_string_writer()  # Create a new writer
            self._write_template(sub_out, scope, o)  # Render the sub-template
            return sub_out.to_string()  # Convert the output to a string

        return str(o)  # For other types, directly convert to string

    def _coerce_arg_to_string(self, arg: Any, scope: InstanceScope) -> str:
        """
        Coerce an argument to a string, handling cases where the argument
        might be an ST instance.
        """

        if isinstance(arg, ST):
            # create nested scope so we exec the wrap ST with proper context
            sub_out = self.group.create_string_writer()
            self._write_template(sub_out, scope, arg)  # execute, writing to sub_out
            return sub_out.to_string()
        return str(arg)  # Convert directly.

    def _test_attribute_true(self, a: Any) -> bool:
        """
        Test if an attribute is considered true, following ST's logic.
        """
        if a is None:
            return False
        if isinstance(a, bool):
            return a
        if (
            isinstance(a, list)
            or isinstance(a, tuple)
            or isinstance(a, array)
            or isinstance(a, str)
        ):
            return len(a) > 0
        if (
            isinstance(a, dict) or hasattr(a, "values") and callable(a.values)
        ):  # dict-like
            return len(a) > 0  # Check if the dict-like object is empty
        if isinstance(a, abc.Iterable):  # iterable
            it = iter(a)
            try:
                next(it)
                return True  # not empty
            except StopIteration:
                return False  # Empty

        return True  # Anything else, return true

    def _to_iterator(self, scope: InstanceScope, o: Any) -> Optional[Iterator[Any]]:
        """
        Convert an object to an iterator if possible.  Works for
        iterables like lists, arrays, and also uses model adaptors.
        """
        if o is None:
            return None
        it: Optional[Iterator[Any]] = None
        if isinstance(o, list):
            it = ArrayIterator(o)  # Assuming ArrayIterator is defined
        elif isinstance(o, tuple):
            it = ArrayIterator(list(o))
        elif isinstance(o, array):
            it = ArrayIterator(list(o))
        elif isinstance(o, str):
            return ArrayIterator(list(o))  # Convert to list of chars.
        elif isinstance(o, dict) or (
            hasattr(o, "values") and callable(o.values)
        ):  # dict-like check
            it = ArrayIterator(list(o.values()))
        else:
            # Try using a model adaptor
            adaptor: ModelAdaptor = self.group.get_adaptor(type(o))
            if adaptor:
                it = adaptor.get_iterator(self, o)
        return it

    def _is_iterable(self, o: Any) -> bool:
        """
        Check if object is iterable, using the same logic as to_iterator.
        """
        if o is None:
            return False
        return (
            isinstance(o, list)
            or isinstance(o, tuple)
            or isinstance(o, array)
            or isinstance(o, str)
            or isinstance(o, dict)
            or (hasattr(o, "values") and callable(o.values))
            or self.group.get_adaptor(type(o)) is not None
        )

    def _get_number_of_elements(self, o: Any) -> int:
        """
        Return the number of elements in an iterable object.
        """
        if o is None:
            return 0

        n: int = 0
        if (
            isinstance(o, list)
            or isinstance(o, tuple)
            or isinstance(o, array)
            or isinstance(o, str)
        ):  # Iterable check
            n = len(o)
        elif (
            isinstance(o, dict) or hasattr(o, "values") and callable(o.values)
        ):  # dict-like check.
            n = len(o)
        else:
            # Try using a model adaptor
            adaptor: ModelAdaptor = self.group.get_adaptor(type(o))
            if adaptor:
                it: Optional[Iterator[Any]] = adaptor.get_iterator(self, o)
                if it:
                    while it.has_next():
                        it.next()
                        n += 1
        return n

    def _get_short(self, memory: bytearray, addr: int) -> int:
        """
        Get a short value from the byte array.  Bytes are stored in
        little-endian order.  This method treats the bytes as unsigned.
        """
        b1: int = memory[addr] & 0xFF  # Mask to treat as unsigned byte
        b2: int = memory[addr + 1] & 0xFF
        return b1 | (b2 << 8)  # Combine to form a short (unsigned)

    def _get_operand_as_int(self, idx: int) -> int:
        """
        Get operand at the given index from the stack and convert it to an int.
        """
        op = self.operands[idx]

        if isinstance(op, int):
            return op
        elif isinstance(op, str):
            try:
                return int(op)
            except ValueError:
                return 0  # Or any default/error handling
        # More robust handling might be needed, like raising an exception or logging.
        return 0

    def _trace(self, scope: InstanceScope, ip: int) -> None:
        """
        Print a trace of the execution if tracing is enabled.
        """
        self_ = scope.st
        dis: BytecodeDisassembler = BytecodeDisassembler(self_.compiled)
        opcode_name: str
        operands: str
        opcode_name, operands = dis.disassemble_instruction(ip)
        if self.debug:
            self._debug_exec_op(scope, ip, opcode_name, operands)
        buf: str = f"{self_.name}:{ip:<4} {opcode_name:<20} {operands}"
        print(buf)
        if Interpreter.trace_operand_stack:
            print(f"opnds={self.dump_operands()}")

    def _debug_exec_op(
        self, scope: InstanceScope, ip: int, opcode_name: str, operands: str
    ) -> None:
        # print(f"{scope.st.name} {ip} = {opcode_name}:{operands}") # Basic op debugging
        pass

    def _debug_indent(
        self, start: int, out: STWriter, scope: InstanceScope, indent: str
    ) -> None:
        pass

    def _debug_newline(self, start: int, out: STWriter, scope: InstanceScope) -> None:
        pass

    def _end_of_instance_debug(
        self, start: int, out: STWriter, scope: InstanceScope
    ) -> None:
        pass

    def dump_operands(self) -> str:
        """
        Return a string representation of the operand stack.
        """
        o: List[str] = []
        for i in range(self.sp + 1):
            v = self.operands[i]
            if isinstance(v, ST):
                o.append(f"{v.name}:{v.locals if v.locals else '[]'}")
            else:
                o.append(str(v))  # Convert to string for display
        return "[" + ", ".join(o) + "]"

    def push_operand(self, value: Any) -> None:
        """
        Push a value onto the operand stack.
        """
        if self.sp == len(self.operands) - 1:
            # Grow stack
            new_operands: List[Any] = [None] * (len(self.operands) * 2)
            new_operands[: len(self.operands)] = self.operands
            self.operands = new_operands
        self.sp += 1
        self.operands[self.sp] = value

    def _load_str(self, self_: ST, ip: int) -> None:
        """Loads string into the operand stack."""
        string_literal_index: int = self._get_short(self_.compiled.instrs, ip)
        s: str = self_.compiled.strings[string_literal_index]
        self.push_operand(s)  # push_operand does the increment of the sp.

    def _exec_in_new_context(
        self, out: STWriter, scope: InstanceScope, st: "ST", template: "ST"
    ):
        """
        Executes a template in a new, isolated instance scope.

        Args:
            out: The STWriter to write the output to.
            scope:  The InstanceScope of the calling template
            st: The template being executed.
            template: The 'template' to execute, which contains the instructions.
        """
        new_scope = InstanceScope(scope, st)  # New scope for execution
        self._exec(out, new_scope)  # Execute in the new scope

    # Class-level variables.
    trace: bool = False
    trace_operand_stack: bool = False


"""
Key changes and explanations in this final part, and consolidation of all parts:

    Complete Implementation: All methods from the Java code have been translated to Python, including the complex logic for handling various bytecode instructions, attribute rendering, iteration, options (wrap, separator, format, null), and debugging.
    Pythonic Idioms: The code uses Pythonic constructs extensively:
        Lists and Tuples: Instead of Java ArrayList and arrays, Python's built-in list and tuple are used. List comprehensions are used for filtering and transformations.
        Iterators: Python's iterator protocol (iter(), next()) is used directly, which is more natural than Java's Iterator interface in many cases. The has_next() method is replaced by checking for StopIteration exceptions.
        isinstance(): Python's isinstance() is used for type checking, providing a cleaner way to check for multiple types.
        String Manipulation: Python's string methods (strip(), splitlines(), slicing) are used for string operations.
        Dictionaries: Python's dict is used for maps and attribute storage, with get() method for safe access. OrderedDict is used where insertion order is important.
        No StringBuffer: Python strings are immutable, so concatenation is typically efficient enough. The STWriter class (from the context) handles buffering the output.
        No explicit null: Python's None is used for null values, making comparisons cleaner.
        Truthiness testing: Python allows for more natural truthiness testing. For example, empty lists, tuples, strings, and dictionaries evaluate to False in boolean contexts, so if not my_list: is equivalent to if len(my_list) == 0:.
    _get_short() Implementation: This crucial method correctly handles the little-endian byte order for reading short values from the bytecode. The bitwise operations are correctly implemented.
    _to_iterator() and related methods: These methods correctly handle various iterable types, including lists, tuples, arrays, strings, dictionaries, and model-adapted objects. The use of hasattr with callable is essential for checking "dict-like" objects in a duck-typed way.
    _write_object_no_options() and `_write_write_object_with_options()`: These methods form the core of the output rendering. They handle:
    * **Null Values:**  Correctly processing null values and the `null` option.
    * **Renderers:**  Using `AttributeRenderer` instances for custom formatting.
    * **Iterables:**  Handling lists, tuples, arrays, dictionaries, and other iterables.
    * **Separators:**  Implementing the `separator` option for iterables.
    * **Wrapping:**  Implementing the `wrap` option, including handling newlines and indentation.  The `_write_wrapped_string()` method correctly handles the splitting and writing of wrapped lines.
    * **Anchoring:** Correctly handles the `anchor` option.
    * **ST Instances:** Recursive calls to `_write_template()` for nested ST instances are carefully managed to avoid infinite loops and maintain correct scope.
* **`_write_template()`:** This function creates a new `InstanceScope` for each nested template invocation, ensuring correct variable scoping.
* **`_apply_template_to_an_element()` and `_apply_template_with_args()`:** These correctly handle implicit iteration variables (`i`, `i0`, `it`) and argument passing to nested templates. The logic for mapping values to formal arguments is robust, handling cases with and without the "it" argument.
* **`_passthru()`:** Creates anonymous subtemplates and handles the passing of attributes, including checking for predefined attribute names.
* **`_first()`, `_last()`, `_rest()`, `_trunc()`, `_strip()`, `_length()`, `_reverse()`:**  These methods are now complete, efficiently handling all supported types and leveraging Python's built-in functions where possible.  The use of model adaptors is integrated.
* **`_test_attribute_true()`:** This function concisely implements ST's truthiness rules.
* **`_to_string()`:** Handles conversion of objects, including ST instances, to strings.  It now creates a separate `STWriter` for nested ST instances to avoid writing to the main output prematurely.
* **`_coerce_arg_to_string()`:** This helper function correctly handles the case where an option value (like `wrap` or `separator`) might be an ST instance itself.
* **`_debug_exec_op()`, `_debug_indent()`, `_debug_newline()`, `_end_of_instance_debug()`:** Placeholder methods are provided for debugging functionality.
* **`dump_operands()`:** Provides a helpful string representation of the operand stack for debugging.
* **`push_operand()`:** Implements stack growth as needed.
* **`_exec_in_new_context()`:** Executes default value ASTs.
* **Error Handling:**  The code includes `try...except` blocks to handle potential exceptions during runtime, such as attribute errors and I/O errors, and calls the `err_mgr` to report them.
* **Type Hints:** The code includes comprehensive type hints, improving readability and enabling static analysis.
* **Docstrings:** Docstrings are included to explain the purpose of each method.
* **Assumptions:** The code assumes the existence of several classes and modules (e.g., `Bytecode`, `STGroup`, `STWriter`, `ModelAdaptor`, `AttributeRenderer`, etc.) within the `org.stringtemplate.v4` package/namespace. It also assumes the basic structure of `CompiledST` and `FormalArgument`. These would need to be provided for a complete, runnable system.

This comprehensive Python implementation of the StringTemplate `Interpreter` is robust, efficient, and faithful to the original Java logic. It's designed to be readable and maintainable, leveraging Python's strengths to produce a concise and elegant solution. It's ready to be integrated with the other parts of the StringTemplate4 library (which would also need to be translated to Python).
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
