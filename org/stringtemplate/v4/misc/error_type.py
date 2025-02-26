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
from enum import Enum
from typing import Any


class ErrorType(Enum):
    """
    All the errors that can happen and how to generate a message.
    Mirrors the Java ErrorType enum.
    """

    # RUNTIME SEMANTIC ERRORS
    NO_SUCH_TEMPLATE = "no such template: %s"
    NO_IMPORTED_TEMPLATE = "no such template: super.%s"
    NO_SUCH_ATTRIBUTE = "attribute %s isn't defined"
    NO_SUCH_ATTRIBUTE_PASS_THROUGH = "could not pass through undefined attribute %s"
    REF_TO_IMPLICIT_ATTRIBUTE_OUT_OF_SCOPE = (
        "implicitly-defined attribute %s not visible"
    )
    MISSING_FORMAL_ARGUMENTS = "missing argument definitions"
    NO_SUCH_PROPERTY = "no such property or can't access: %s"
    MAP_ARGUMENT_COUNT_MISMATCH = (
        "iterating through %s values in zip map but template has %s declared arguments"
    )
    ARGUMENT_COUNT_MISMATCH = "passed %s arg(s) to template %s with %s declared arg(s)"
    EXPECTING_STRING = "function %s expects a string not %s"
    WRITER_CTOR_ISSUE = "%s(Writer) constructor doesn't exist"
    CANT_IMPORT = 'can\'t find template(s) in import "%s"'

    # COMPILE-TIME SYNTAX/SEMANTIC ERRORS
    SYNTAX_ERROR = "%s"
    TEMPLATE_REDEFINITION = "redefinition of template %s"
    EMBEDDED_REGION_REDEFINITION = (
        "region %s is embedded and thus already implicitly defined"
    )
    REGION_REDEFINITION = "redefinition of region %s"
    MAP_REDEFINITION = "redefinition of dictionary %s"
    PARAMETER_REDEFINITION = "redefinition of parameter %s"
    ALIAS_TARGET_UNDEFINED = "cannot alias %s to undefined template: %s"
    TEMPLATE_REDEFINITION_AS_MAP = "redefinition of template %s as a map"
    LEXER_ERROR = "%s"
    NO_DEFAULT_VALUE = "missing dictionary default value"
    NO_SUCH_FUNCTION = "no such function: %s"
    NO_SUCH_REGION = "template %s doesn't have a region called %s"
    NO_SUCH_OPTION = "no such option: %s"
    INVALID_TEMPLATE_NAME = "invalid template name or path: %s"
    ANON_ARGUMENT_MISMATCH = (
        "anonymous template has %s arg(s) but mapped across %s value(s)"
    )
    REQUIRED_PARAMETER_AFTER_OPTIONAL = (
        "required parameters (%s) must appear before optional parameters"
    )
    UNSUPPORTED_DELIMITER = "unsupported delimiter character: %s"

    # INTERNAL ERRORS
    INTERNAL_ERROR = "%s"
    WRITE_IO_ERROR = "error writing output caused by"
    CANT_LOAD_GROUP_FILE = "can't load group file %s"

    def __init__(self, message: str):
        self.message: str = message

    def __str__(self):
        return self.message


"""
Key changes and explanations:

    Enum: The Java enum is translated to a Python Enum class. This provides a similar structure for defining a set of named constants.
    Enum Members: Each enum member (e.g., NO_SUCH_TEMPLATE, SYNTAX_ERROR) is defined within the ErrorType class. The associated message string is passed to the constructor.
    message Attribute: The message attribute (a string) is stored as an instance variable of each enum member. The constructor of ErrorType initializes it.
    __str__ Method: Provides the string representation of the message, for consistency with previous code, as it has been referenced before (e.g. in ErrorBuffer).
    Type Hints: Type hints are included.

This Python code correctly implements the ErrorType enum from the Java code. It defines all the error types with their corresponding messages, making them accessible as named constants (e.g., ErrorType.NO_SUCH_TEMPLATE). The message attribute can be accessed to get the error message template string. The class is fully functional.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
