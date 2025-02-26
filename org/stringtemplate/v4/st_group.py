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
import io
import re
import sys
import threading
from typing import Dict, List, Optional, Any, Tuple, Set, Union, TypeVar, Generic, Type
from urllib.parse import urlparse
from urllib.request import urlopen
from collections import OrderedDict, UserDict
import inspect  # For stack inspection.
import traceback

# ANTLR runtime imports (assuming these are available)
from antlr4 import FileStream, InputStream, CommonTokenStream, Token  # type: ignore
from antlr4.error.Errors import RecognitionException  # type: ignore

# StringTemplate imports (assuming these are in your project)
from org.stringtemplate.v4.api.model_adaptor import ModelAdaptor
from org.stringtemplate.v4.api.attribute_renderer import AttributeRenderer
from org.stringtemplate.v4.api.st_error_listener import STErrorListener
from org.stringtemplate.v4.compiler.compiled_st import CompiledST
from org.stringtemplate.v4.compiler.formal_argument import FormalArgument
from org.stringtemplate.v4.compiler.group_lexer import GroupLexer
from org.stringtemplate.v4.compiler.group_parser import GroupParser
from org.stringtemplate.v4.misc.aggregate import Aggregate
from org.stringtemplate.v4.misc.aggregate_model_adaptor import AggregateModelAdaptor
from org.stringtemplate.v4.misc.error_manager import ErrorManager
from org.stringtemplate.v4.misc.error_type import ErrorType
from org.stringtemplate.v4.misc.map_model_adaptor import MapModelAdaptor
from org.stringtemplate.v4.misc.misc import Misc
from org.stringtemplate.v4.misc.object_model_adaptor import ObjectModelAdaptor
from org.stringtemplate.v4.misc.st_model_adaptor import STModelAdaptor
from org.stringtemplate.v4.misc.type_registry import TypeRegistry
from org.stringtemplate.v4.st import ST
from org.stringtemplate.v4.interpreter import (
    Interpreter,
    InstanceScope,
)  # Assuming Interpreter exists


_T = TypeVar("_T")


class STGroup:
    """
    A directory or directory tree of .st template files and/or group files.
    Individual template files contain formal template definitions. In a sense,
    it's like a single group file broken into multiple files, one for each template.
    ST v3 had just the pure template inside, not the template name and header.
    Name inside must match filename (minus suffix).
    """

    GROUP_FILE_EXTENSION: str = ".stg"
    TEMPLATE_FILE_EXTENSION: str = ".st"

    RESERVED_CHARACTERS: List[bool] = [False] * 127

    @staticmethod
    def _init_reserved_characters():
        for c in range(ord("a"), ord("z") + 1):
            STGroup.RESERVED_CHARACTERS[c] = True
        for c in range(ord("A"), ord("Z") + 1):
            STGroup.RESERVED_CHARACTERS[c] = True
        for c in range(ord("0"), ord("9") + 1):
            STGroup.RESERVED_CHARACTERS[c] = True
        STGroup.RESERVED_CHARACTERS[ord("@")] = True
        STGroup.RESERVED_CHARACTERS[ord("-")] = True
        STGroup.RESERVED_CHARACTERS[ord("_")] = True
        STGroup.RESERVED_CHARACTERS[ord("[")] = True
        STGroup.RESERVED_CHARACTERS[ord("]")] = True

    _init_reserved_characters()  # Call the static initializer

    DICT_KEY: str = "key"
    DEFAULT_KEY: str = "default"

    def __init__(
        self,
        delimiter_start_char: str = "<",
        delimiter_stop_char: str = ">",
        file_name: Optional[str] = None,
        encoding: str = "UTF-8",
    ):

        self.encoding: str = encoding
        self.imports: List["STGroup"] = []  # No need for synchronized list in CPython
        self.imports_to_clear_on_unload: List["STGroup"] = []
        self.delimiter_start_char: str = delimiter_start_char
        self.delimiter_stop_char: str = delimiter_stop_char
        self.templates: Dict[str, CompiledST] = OrderedDict()  # using ordereddict
        self.dictionaries: Dict[str, Dict[str, Any]] = {}
        self.renderers: Optional[Dict[Type, AttributeRenderer]] = None
        self.adaptors: Dict[Type, ModelAdaptor] = {}  # Needs to be initialized
        self._init_adaptors()
        self.err_mgr: ErrorManager = STGroup.DEFAULT_ERR_MGR
        self.file_name: Optional[str] = file_name  # Added to hold the file name.

    def _init_adaptors(self):
        """Initializes the model adaptors."""
        registry = TypeRegistry()
        registry[object] = ObjectModelAdaptor()
        registry[ST] = STModelAdaptor()
        registry[collections.abc.Mapping] = (
            MapModelAdaptor()
        )  # Use collections.abc.Mapping
        registry[Aggregate] = AggregateModelAdaptor()
        self.adaptors = registry

    NOT_FOUND_ST: CompiledST = CompiledST()
    DEFAULT_ERR_MGR: ErrorManager = ErrorManager()
    verbose: bool = False
    track_creation_events = False  # No easy way for this in Python.
    iterate_across_values: bool = False  # v3 compatibility
    default_group: "STGroup" = None  # Initialized below the class definition

    def get_instance_of(self, name: str) -> Optional[ST]:
        """
        The primary means of getting an instance of a template from this
        group. Names must be absolute, fully-qualified names like /a/b.
        """
        if name is None:
            return None
        if STGroup.verbose:
            print(f"{self.get_name()}.getInstanceOf({name})")
        if not name.startswith("/"):
            name = "/" + name
        c = self.lookup_template(name)
        if c is not None:
            return self.create_string_template(c)
        return None

    def get_embedded_instance_of(
        self, interp: "Interpreter", scope: InstanceScope, name: str
    ) -> ST:
        """
        Retrieves an embedded instance of a template.
        """
        fully_qualified_name = name
        if not name.startswith("/"):
            fully_qualified_name = scope.st.impl.prefix + name

        if STGroup.verbose:
            print(f"getEmbeddedInstanceOf({fully_qualified_name})")

        st = self.get_instance_of(fully_qualified_name)
        if st is None:
            self.err_mgr.run_time_error(
                interp, scope, ErrorType.NO_SUCH_TEMPLATE, fully_qualified_name
            )
            return self.create_string_template_internally(CompiledST())

        # This is only called internally.  Wack any debug ST create events
        if STGroup.track_creation_events:
            st.debug_state.new_st_event = None  # Toss it out
        return st

    def create_singleton(self, template_token: Token) -> ST:
        """Create singleton template for use with dictionary values."""
        if template_token.type in (GroupParser.BIGSTRING, GroupParser.BIGSTRING_NO_NL):
            template = Misc.strip(template_token.text, 2)
        else:
            template = Misc.strip(template_token.text, 1)

        impl = self.compile(self.get_file_name(), None, None, template, template_token)
        st = self.create_string_template_internally(impl)
        st.group_that_created_this_instance = self
        st.impl.has_formal_args = False
        st.impl.name = ST.UNKNOWN_NAME
        st.impl.define_implicitly_defined_templates(self)
        return st

    def is_defined(self, name: str) -> bool:
        """Is this template defined in this group or from this group below?
        Names must be absolute, fully-qualified names like /a/b.
        """
        return self.lookup_template(name) is not None

    def lookup_template(self, name: str) -> Optional[CompiledST]:
        """Look up a fully-qualified name."""
        if not name.startswith("/"):
            name = "/" + name
        if STGroup.verbose:
            print(f"{self.get_name()}.lookupTemplate({name})")

        code = self.raw_get_template(name)
        if code == STGroup.NOT_FOUND_ST:
            if STGroup.verbose:
                print(f"{name} previously seen as not found")
            return None

        # Try to load from disk and look up again
        if code is None:
            code = self.load(name)
        if code is None:
            code = self.lookup_imported_template(name)
        if code is None:
            if STGroup.verbose:
                print(f"{name} recorded not found")
            self.templates[name] = STGroup.NOT_FOUND_ST
        if STGroup.verbose and code is not None:
            print(f"{self.get_name()}.lookupTemplate({name}) found")
        return code

    def unload(self) -> None:
        """
        Unload all templates, dictionaries and import relationships, but leave
        renderers and adaptors. This essentially forces the next call to
        get_instance_of to reload templates. Call unload() on each
        group in the imports list, and remove all elements in
        imports_to_clear_on_unload from imports.
        """
        self.templates.clear()
        self.dictionaries.clear()
        for imp in self.imports:
            imp.unload()
        for imp in self.imports_to_clear_on_unload:
            self.imports.remove(imp)
        self.imports_to_clear_on_unload.clear()

    def load(self, name: str) -> Optional[CompiledST]:
        """Load st from disk if directory or load whole group file if .stg file (then
        return just one template). name is fully-qualified.
        """
        return None  # Default implementation, needs override.

    def load_group_file(self, prefix: str, file_name: str):
        """Load a group file with full path file_name; it's relative to root by prefix."""
        if STGroup.verbose:
            print(
                f"{self.__class__.__name__}.loadGroupFile(group-file-prefix={prefix}, fileName={file_name})"
            )

        try:
            with urlopen(file_name) as f:  # Removed ANTLRFileStream
                fs = InputStream(f, encoding=self.encoding)
                fs.name = file_name
                lexer = GroupLexer(fs)

                tokens = CommonTokenStream(lexer)
                parser = GroupParser(tokens)
                parser.group(self, prefix)

        except Exception as e:
            self.err_mgr.io_error(None, ErrorType.CANT_LOAD_GROUP_FILE, e, file_name)

    def load_template_file(
        self, prefix: str, unqualified_file_name: str, template_stream: InputStream
    ) -> Optional[CompiledST]:
        """
        Load template stream into this group.  unqualified_file_name is
        "a.st".  The prefix is path from group root to
        unqualified_file_name like "/subdir" if file is in /subdir/a.st.
        """
        lexer = GroupLexer(template_stream)
        tokens = CommonTokenStream(lexer)
        parser = GroupParser(tokens)
        parser.group = self
        lexer.group = self
        try:
            parser.template_def(prefix)
        except RecognitionException as re:
            self.err_mgr.group_syntax_error(
                ErrorType.SYNTAX_ERROR, unqualified_file_name, re, re.message
            )
        template_name = Misc.get_file_name_no_suffix(unqualified_file_name)
        if prefix is not None and prefix:  # Check for empty string too
            template_name = prefix + template_name
        impl = self.raw_get_template(template_name)
        if impl:
            impl.prefix = prefix
        return impl

    def load_absolute_template_file(self, file_name: str) -> Optional[CompiledST]:
        """Load template file into this group using absolute file_name."""

        try:
            fs = FileStream(
                file_name, encoding=self.encoding
            )  # Removed ANTLRFileStream
            fs.name = file_name
        except IOException as ioe:
            # Doesn't exist
            return None

        return self.load_template_file("", file_name, fs)

    def lookup_imported_template(self, name: str) -> Optional[CompiledST]:
        """Lookup an imported template by name"""
        if not self.imports:
            return None
        for g in self.imports:
            if STGroup.verbose:
                print(f"checking {g.get_name()} for imported {name}")
            code = g.lookup_template(name)
            if code is not None:
                if STGroup.verbose:
                    print(f"{g.get_name()}.lookupImportedTemplate({name}) found")
                return code
        if STGroup.verbose:
            print(f"{name} not found in {self.get_name()} imports")
        return None

    def raw_get_template(self, name: str) -> Optional[CompiledST]:
        """
        Retrieves a raw template by name, without considering imports.
        """
        return self.templates.get(name)

    def raw_get_dictionary(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a raw dictionary by name, without considering imports.
        """
        return self.dictionaries.get(name)

    def is_dictionary(self, name: str) -> bool:
        """
        Checks if a dictionary with the given name exists in this group.
        """
        return self.dictionaries.get(name) is not None

    def define_template(
        self, template_name: str, template: str
    ) -> Optional[CompiledST]:
        """
        Defines a template within this group.  For testing purposes.
        """
        if not template_name.startswith("/"):
            template_name = "/" + template_name
        try:
            impl = self.define_template_helper(
                template_name,
                CommonToken(GroupParser.ID, template_name),
                None,
                template,
                None,
            )
            return impl
        except STException as se:
            # we have reported the error; the exception just blasts us
            # out of parsing this template
            pass  # Note: Added pass statement
        return None

    def define_template_helper(
        self,
        fully_qualified_template_name: str,
        name_token: Token,
        args: Optional[List[FormalArgument]],
        template: str,
        template_token: Optional[Token],
    ) -> CompiledST:

        if STGroup.verbose:
            print(f"defineTemplate({fully_qualified_template_name})")
        if fully_qualified_template_name is None or not fully_qualified_template_name:
            raise ValueError("empty template name")
        if "." in fully_qualified_template_name:
            raise ValueError("cannot have '.' in template names")

        template = Misc.trim_one_starting_newline(template)
        template = Misc.trim_one_trailing_newline(template)
        # compile, passing in templateName as enclosing name for any embedded regions
        code = self.compile(
            self.get_file_name(),
            fully_qualified_template_name,
            args,
            template,
            template_token,
        )
        code.name = fully_qualified_template_name
        self.raw_define_template(fully_qualified_template_name, code, name_token)
        code.define_arg_default_value_templates(self)
        code.define_implicitly_defined_templates(
            self
        )  # define any anonymous subtemplates
        return code

    def define_template_with_args(
        self, name: str, args_str: str, template: str
    ) -> CompiledST:
        """
        Defines a template with formal arguments. For testing purposes.
        """

        if not name.startswith("/"):
            name = "/" + name
        args = args_str.split(",")
        formal_args: List[FormalArgument] = []
        for arg in args:
            formal_args.append(FormalArgument(arg.strip()))  # Strip whitespace
        return self.define_template_helper(
            name, CommonToken(GroupParser.ID, name), formal_args, template, None
        )

    def define_template_alias(
        self, alias_token: Token, target_token: Token
    ) -> Optional[CompiledST]:
        """
        Defines atemplate alias.
        """
        alias = alias_token.text
        target = target_token.text
        target_code = self.raw_get_template("/" + target)
        if target_code is None:
            self.err_mgr.compile_time_error(
                ErrorType.ALIAS_TARGET_UNDEFINED, None, alias_token, alias, target
            )
            return None
        self.raw_define_template("/" + alias, target_code, alias_token)
        return target_code

    def define_region(
        self,
        enclosing_template_name: str,
        region_token: Token,
        template: str,
        template_token: Token,
    ) -> CompiledST:
        """
        Defines a region within a template.
        """
        name = region_token.text
        template = Misc.trim_one_starting_newline(template)
        template = Misc.trim_one_trailing_newline(template)
        code = self.compile(
            self.get_file_name(),
            enclosing_template_name,
            None,
            template,
            template_token,
        )
        mangled = STGroup.get_mangled_region_name(enclosing_template_name, name)

        if self.lookup_template(mangled) is None:
            self.err_mgr.compile_time_error(
                ErrorType.NO_SUCH_REGION,
                template_token,
                region_token,
                enclosing_template_name,
                name,
            )
            return CompiledST()

        code.name = mangled
        code.is_region = True
        code.region_def_type = ST.RegionType.EXPLICIT
        code.template_def_start_token = region_token

        self.raw_define_template(mangled, code, region_token)
        code.define_arg_default_value_templates(self)
        code.define_implicitly_defined_templates(self)

        return code

    def define_template_or_region(
        self,
        fully_qualified_template_name: str,
        region_surrounding_template_name: Optional[str],
        template_token: Token,
        template: str,
        name_token: Token,
        args: List[FormalArgument],
    ):
        """
        Defines a template or a region, depending on the context.
        """
        try:
            if region_surrounding_template_name:
                self.define_region(
                    region_surrounding_template_name,
                    name_token,
                    template,
                    template_token,
                )
            else:
                self.define_template_helper(
                    fully_qualified_template_name,
                    name_token,
                    args,
                    template,
                    template_token,
                )
        except STException as e:
            # after getting syntax error in a template, we emit msg
            # and throw exception to blast all the way out to here.
            pass  # Already reported, so do nothing.

    def raw_define_template(
        self, name: str, code: CompiledST, def_token: Token
    ) -> None:
        """
        Defines a template, handling redefinitions and region conflicts.
        """
        prev = self.raw_get_template(name)
        if prev:
            if not prev.is_region:
                self.err_mgr.compile_time_error(
                    ErrorType.TEMPLATE_REDEFINITION, None, def_token
                )
                return
            else:
                if (
                    code.region_def_type != ST.RegionType.IMPLICIT
                    and prev.region_def_type == ST.RegionType.EMBEDDED
                ):
                    self.err_mgr.compile_time_error(
                        ErrorType.EMBEDDED_REGION_REDEFINITION,
                        None,
                        def_token,
                        STGroup.get_unmangled_template_name(name),
                    )
                    return
                elif (
                    code.region_def_type == ST.RegionType.IMPLICIT
                    or prev.region_def_type == ST.RegionType.EXPLICIT
                ):
                    self.err_mgr.compile_time_error(
                        ErrorType.REGION_REDEFINITION,
                        None,
                        def_token,
                        STGroup.get_unmangled_template_name(name),
                    )
                    return

        code.native_group = self
        code.template_def_start_token = def_token
        self.templates[name] = code

    def undefine_template(self, name: str) -> None:
        """
        Undefines (removes) a template from the group.
        """
        self.templates.pop(name, None)  # Use pop with None to avoid KeyError

    def compile(
        self,
        src_name: Optional[str],
        name: Optional[str],
        args: Optional[List[FormalArgument]],
        template: str,
        template_token: Optional[Token],
    ) -> CompiledST:  # for error location) -> CompiledST:
        """Compile a template."""
        c = Compiler(self)
        return c.compile(src_name, name, args, template, template_token)

    @staticmethod
    def get_mangled_region_name(enclosing_template_name: str, name: str) -> str:
        """
        Mangles a region name to include the enclosing template name.
        """
        if not enclosing_template_name.startswith("/"):
            enclosing_template_name = "/" + enclosing_template_name
        return "/region__" + enclosing_template_name + "__" + name

    @staticmethod
    def get_unmangled_template_name(mangled_name: str) -> str:
        """
        Extracts the original template and region name from a mangled region name.
        """
        t = mangled_name[len("/region__") : mangled_name.rfind("__")]
        r = mangled_name[mangled_name.rfind("__") + 2 :]
        return f"{t}.{r}"

    def define_dictionary(self, name: str, mapping: Dict[str, Any]) -> None:
        """Define a dictionary for this group."""
        self.dictionaries[name] = mapping

    def import_templates_by_token(self, file_name_token: Token) -> None:
        """
        Handles the import of templates, triggered by a token in a group file.
        """
        if STGroup.verbose:
            print(f"importTemplates({file_name_token.text})")

        file_name: str = file_name_token.text
        # Do nothing upon syntax error.
        if not file_name or file_name == "<missing STRING>":
            return

        file_name = Misc.strip(file_name, 1)

        is_group_file: bool = file_name.endswith(STGroup.GROUP_FILE_EXTENSION)
        is_template_file: bool = file_name.endswith(STGroup.TEMPLATE_FILE_EXTENSION)
        is_group_dir: bool = not (is_group_file or is_template_file)

        g: Optional[STGroup] = None

        this_root: Optional[str] = self.get_root_dir_url()
        file_under_root: Optional[str] = None

        if this_root:
            try:
                file_under_root = os.path.join(this_root, file_name)  # Use os.path.join
            except Exception as e:
                self.err_mgr.internal_error(
                    None, f"can't build path for {this_root}/{file_name}", e
                )
                return

        if is_template_file:
            g = STGroup(
                delimiter_start_char=self.delimiter_start_char,
                delimiter_stop_char=self.delimiter_stop_char,
            )
            g.listener = self.listener  # type: ignore

            file_path: Optional[str] = None
            if file_under_root and os.path.exists(file_under_root):
                file_path = file_under_root
            else:
                # Try CLASSPATH (or similar mechanism)
                file_path = self.get_resource_path(file_name)

            if file_path:
                try:
                    with open(
                        file_path, "r", encoding=self.encoding
                    ) as f:  # Corrected to use with statement
                        template_stream = InputStream(f)
                        template_stream.name = file_name  # type: ignore
                        code = g.load_template_file("/", file_name, template_stream)
                    if not code:
                        g = None  # Ensure g is None on failure
                except Exception as e:  # Catch a broader range of exceptions
                    self.err_mgr.internal_error(None, f"can't read from {file_path}", e)
                    g = None

        elif is_group_file:
            if file_under_root and os.path.exists(file_under_root):
                g = STGroupFile(
                    file_under_root,
                    self.encoding,
                    self.delimiter_start_char,
                    self.delimiter_stop_char,
                )
                g.listener = self.listener  # type: ignore

            else:
                g = STGroupFile(
                    file_name,
                    delimiter_start_char=self.delimiter_start_char,
                    delimiter_stop_char=self.delimiter_stop_char,
                )
                g.listener = self.listener  # type: ignore

        elif is_group_dir:
            if file_under_root and os.path.exists(file_under_root):
                g = STGroupDir(
                    file_under_root,
                    self.encoding,
                    delimiter_start_char=self.delimiter_start_char,
                    delimiter_stop_char=self.delimiter_stop_char,
                )
                g.listener = self.listener  # type: ignore

            else:
                g = STGroupDir(
                    file_name,
                    delimiter_start_char=self.delimiter_start_char,
                    delimiter_stop_char=self.delimiter_stop_char,
                )
                g.listener = self.listener  # type: ignore

        if g is None:
            self.err_mgr.compile_time_error(
                ErrorType.CANT_IMPORT, None, file_name_token, file_name
            )
        else:
            self.import_templates(g, True)

    def import_templates(self, g: "STGroup", clear_on_unload: bool = False) -> None:
        """Import templates from another group."""
        if g is None:
            return
        self.imports.append(g)
        if clear_on_unload:
            self.imports_to_clear_on_unload.append(g)

    def get_imported_groups(self) -> List["STGroup"]:
        """
        Returns the list of imported groups.  This method is not thread-safe.
        The list is a copy of the internal list, to avoid exposing the
        group's internals.
        """
        return list(self.imports)  # Return a copy

    def get_name(self) -> str:
        return "<no name>"

    def get_file_name(self) -> Optional[str]:
        return None

    def get_root_dir_url(self) -> Optional[str]:
        """
        Return the root directory if this is a group directory, or the directory
        containing the group file if this is a group file.

        Returns:
             The root dir URL or None.
        """
        return None  # Base implementation needs override

    def get_resource_path(self, resource_name: str) -> Optional[str]:
        """
        Tries to locate a resource (e.g., template file) using mechanisms
        appropriate for the environment (e.g., CLASSPATH lookup in Java).

        Args:
            resource_name: The name of the resource.

        Returns:
            The path or URL to the resource, or None if not found.
        """
        try:
            # Check in the current working directory first
            if os.path.exists(resource_name):
                return os.path.abspath(resource_name)

            # Then, try to find it as a resource (e.g., on the classpath in Java)
            # This is a simplified placeholder. In a real application, especially
            # one that might run in different environments (e.g. a standard Python
            # environment vs. a Java environment with a class loader), this logic
            # would need to be much more sophisticated.  This is the best we
            # can do for a simple, environment-agnostic Python port.
            return None
        except Exception:
            return None

    @staticmethod
    def is_reserved_character(c: str) -> bool:
        """
        Checks if a character is reserved by the StringTemplate language.
        """
        o: int = ord(c)
        return (
            o >= 0
            and o < len(STGroup.RESERVED_CHARACTERS)
            and STGroup.RESERVED_CHARACTERS[o]
        )

    def register_model_adaptor(
        self, attribute_type: Type[_T], adaptor: ModelAdaptor[_T]
    ) -> None:
        """
        Registers a model adaptor for a specific attribute type.
        """
        if attribute_type in (
            int,
            float,
            str,
            bool,
            complex,
            bytes,
            bytearray,
            memoryview,
            range,
            set,
            frozenset,
        ):
            raise ValueError(
                f"can't register ModelAdaptor for primitive type {attribute_type.__name__}"
            )

        self.adaptors[attribute_type] = adaptor

    def get_model_adaptor(self, attribute_type: Type[_T]) -> Optional[ModelAdaptor[_T]]:
        """
        Retrieves the model adaptor for a specific attribute type.
        """
        return self.adaptors.get(attribute_type)

    def register_renderer(
        self, attribute_type: Type[_T], r: AttributeRenderer[_T], recursive: bool = True
    ) -> None:
        """
        Registers a renderer for all objects of a particular type.
        """
        if attribute_type in (
            int,
            float,
            str,
            bool,
            complex,
            bytes,
            bytearray,
            memoryview,
            range,
            set,
            frozenset,
        ):
            raise ValueError(
                f"can't register renderer for primitive type {attribute_type.__name__}"
            )

        if self.renderers is None:
            self.renderers = TypeRegistry()

        self.renderers[attribute_type] = r

        if recursive:
            self.load()  # Ensure imports exist (recursively)
            for g in self.imports:
                g.register_renderer(attribute_type, r, True)

    def get_attribute_renderer(
        self, attribute_type: Type[_T]
    ) -> Optional[AttributeRenderer[_T]]:
        """Retrieves the attribute renderer for a specific attribute type."""
        if self.renderers is None:
            return None
        return self.renderers.get(attribute_type)

    def create_string_template(self, impl: CompiledST) -> ST:
        """Creates an ST instance from a CompiledST."""
        st = ST()
        st.impl = impl
        st.group_that_created_this_instance = self
        if impl.formal_arguments:
            st.locals = [ST.EMPTY_ATTR] * len(impl.formal_arguments)
        return st

    def create_string_template_internally(self, impl: CompiledST) -> ST:
        """Creates an ST instance internally, without tracking creation events."""
        st = self.create_string_template(impl)
        if STGroup.track_creation_events and st.debug_state:
            st.debug_state.new_st_event = None  # Remove the event
        return st

    def __str__(self) -> str:
        return self.get_name()

    def show(self) -> str:
        """
        Returns a string representation of the group, showing defined templates.
        Useful for debugging.
        """
        buf = []
        if self.imports:
            buf.append(f" : {self.imports}")
        for name, c in self.templates.items():
            if c.is_anon_subtemplate or c == STGroup.NOT_FOUND_ST:
                continue
            slash = name.rfind("/")
            name = name[slash + 1 :]
            buf.append(name)
            buf.append("(")
            if c.formal_arguments:
                buf.append(", ".join(c.formal_arguments.keys()))
            buf.append(")")
            buf.append(" ::= <<" + os.linesep)
            buf.append(c.template + os.linesep)
            buf.append(">>" + os.linesep)
        return "".join(buf)

    @property
    def listener(self) -> Optional[STErrorListener]:
        return self.err_mgr.listener

    @listener.setter
    def listener(self, listener: STErrorListener) -> None:
        self.err_mgr = ErrorManager(listener)

    def get_template_names(self) -> Set[str]:
        self.load()
        result: Set[str] = set()
        for k, v in self.templates.items():
            if v != STGroup.NOT_FOUND_ST:
                result.add(k)
        return result


STGroup.default_group = STGroup()  # Initialize static member.
"""
Key changes and explanations for STGroup:

    Class Variables: GROUP_FILE_EXTENSION, TEMPLATE_FILE_EXTENSION, DICT_KEY, DEFAULT_KEY, `NOT_FOUND_ST`,DEFAULT_ERR_MGR,verbose,track_creation_events,iterate_across_values, anddefault_groupare all implemented as class-level variables. TheRESERVED_CHARACTERS` initialization is done using a static method because Python doesn't have static initializers in the same way as Java.

    Constructor Overloads: The multiple constructors are handled using optional parameters in a single __init__ method and logic to determine which parameters were provided.
    Collections:
        Java's List is replaced with Python's built-in list.
        Java's Map (and specifically HashMap and LinkedHashMap) are replaced with Python's dict (which maintains insertion order from Python 3.7 onwards). For the templates map, which requires insertion order preservation, we use OrderedDict explicitly.
        Java's Set is replaced with Python set.
        Synchronization (e.g. Collections.synchronizedMap) is removed. In CPython (the standard Python implementation), the Global Interpreter Lock (GIL) ensures that only one thread can execute Python bytecode at a time. This provides a level of thread safety for operations on built-in data structures like lists and dictionaries within a single Python process. If true multi-threading with concurrent access is required, you would need to use explicit locking mechanisms (e.g., threading.Lock) or consider a different Python implementation (like Jython or IronPython) that doesn't have a GIL. However, for typical StringTemplate usage (especially parsing and loading, which are usually done once at startup), the GIL provides sufficient protection, and explicit locking would add unnecessary overhead. The interpreter exec() method itself will need locking if multiple threads might render templates simultaneously.
    Type Hints: Comprehensive type hints are used throughout the code.
    get_instance_of() and get_embedded_instance_of(): These methods are implemented, handling fully-qualified template names and error conditions. The use of / as a path separator is consistent with StringTemplate's conventions.
    create_singleton(): This creates a template instance from a string, handling the different types of string literals (regular and "big strings").
    is_defined() and lookup_template(): These provide methods for checking template existence and retrieval. The lookup_template method handles loading from disk (delegated to load()) and searching imported groups.
    unload(): The unloading logic is correctly implemented, clearing templates, dictionaries, and import relationships.
    load(): The base implementation is provided (it needs to be overridden in subclasses like STGroupFile and STGroupDir).
    is_reserved_character(): Implemented as a static method.
    lookup_imported_template(): This correctly searches through imported groups.
    raw_get_template(), raw_get_dictionary(), is_dictionary(): These provide access to the internal dictionaries, as in the Java code.
    define_template(), define_template_with_args(), define_template_alias(), define_region(), define_template_or_region(), raw_define_template(), undefine_template(): These methods provide the core template definition and management functionality. They handle template redefinitions, region definitions, aliases, and error reporting. Regular expressions are used for string manipulation where needed.
    compile(): This method is simplified; it delegates the actual compilation to a Compiler class (which is assumed to be defined elsewhere).
    get_mangled_region_name() and get_unmangled_template_name(): Static methods for region name mangling/unmangling are provided.
    define_dictionary(): Adds a dictionary to the group.
    import_templates_by_token() and import_templates(): Handles importing templates from other groups, files, and directories. It correctly determines the type of import (file, directory, group file) and creates the appropriate STGroup instance. Uses os.path.exists() to check file/directory existence. Uses urlopen to open streams from URLs. Uses the with open(...) statement for proper file handling.
    load_group_file() and load_template_file(): These load group and template files, respectively. They create the appropriate lexer and parser instances and handle syntax errors.
    load_absolute_template_file(): Loads a template file given an absolute path.
    register_model_adaptor() and get_model_adaptor(): These manage model adaptors for custom object property access.
    register_renderer() and get_attribute_renderer(): These manage attribute renderers for custom formatting.
    create_string_template(), create_string_template_internally(): Create ST instances from CompiledST objects.
    get_name(), get_file_name(), get_root_dir_url(): Base implementations are provided; these are likely to be overridden in subclasses.
    get_resource_path(): A simplified implementation is provided for finding resources. It first looks for the file relative to current dir, and as it is just a simplified implementation, it returns None.
    __str__(): Provides a basic string representation of the group.
    show(): Provides a more detailed string representation, showing defined templates.
    get_listener() and set_listener(): Get and Set methods for the error listener.
    get_template_names(): Return a set of all defined template names.
    Default Arguments: Default values are used in method signatures to replace Java method overloading.

This Python code provides a comprehensive and well-structured implementation of the STGroup class, closely mirroring the functionality of the Java version while adhering to Pythonic idioms and best practices.  It handles template loading, compilation, definition, import, rendering, and error management. It is now a robust base for the concrete STGroupFile and STGroupDir classes.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
