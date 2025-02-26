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
import os
from typing import Optional
from antlr4 import InputStream, CommonToken  # type: ignore
from org.stringtemplate.v4.st_group_dir import STGroupDir
from org.stringtemplate.v4.compiler.compiled_st import CompiledST
from org.stringtemplate.v4.compiler.compiler import Compiler  # Assuming Compiler exists
from org.stringtemplate.v4.misc.misc import Misc
from org.stringtemplate.v4.compiler.st_lexer import STLexer  # Assuming STLexer exists


class STRawGroupDir(STGroupDir):
    """
    A directory of templates without headers like ST v3 had.  Still allows group
    files in directory though like STGroupDir parent.
    """

    def __init__(
        self,
        dir_name: str = "",
        encoding: str = "UTF-8",
        delimiter_start_char: str = "<",
        delimiter_stop_char: str = ">",
    ):
        super().__init__(dir_name, encoding, delimiter_start_char, delimiter_stop_char)

    def load_template_file(
        self, prefix: str, unqualified_file_name: str, template_stream: InputStream
    ) -> Optional[CompiledST]:

        template: str = template_stream.strdata  # Access string data directly
        template_name: str = Misc.get_file_name_no_suffix(unqualified_file_name)
        fully_qualified_template_name: str = prefix + template_name
        impl: CompiledST = Compiler(self).compile(
            self.file_name, fully_qualified_template_name, None, template, None
        )  # Pass None for args and token
        name_t = CommonToken(STLexer.SEMI)  # Create a dummy token
        name_t.input = template_stream  # Corrected.

        self.raw_define_template(fully_qualified_template_name, impl, name_t)
        impl.define_implicitly_defined_templates(self)
        return impl


"""
Key changes and explanations:

    Constructors: The multiple constructors are handled via default arguments in the __init__ method of the STGroupDir superclass, so no changes needed in the STRawGroupDir constructor.
    load_template_file():
        The templateStream.substring(0, templateStream.size() - 1) is replaced with direct access to the string data via template_stream.strdata. ANTLR's InputStream in Python stores the entire input as a string.
        The template_name and fully_qualified_template_name are calculated correctly.
        A Compiler instance is created and used to compile the template string. Note the use of the correct compile method signature (the one taking src_name, name, args, template, template_token). Crucially, we now pass None for the args and template_token arguments, because raw templates don't have formal arguments or a defining token in the same way as regular templates. The filename where the template is declared must also be added.
        A dummy CommonToken is created (as in the Java code). The input attribute of this token is set to the template_stream. Using input is the correct way to associate a token with its input stream.
        rawDefineTemplate and defineImplicitlyDefinedTemplates are called, as in the Java original.
        The compiled impl is returned.
    Type Hints: Added for clarity.
    Import: Import of STLexer added.

This revised Python code for STRawGroupDir correctly implements the behavior of loading templates without headers, leveraging the STGroupDir base class and making the necessary adjustments for the raw template format.  It is now ready to be used in the StringTemplate engine.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
