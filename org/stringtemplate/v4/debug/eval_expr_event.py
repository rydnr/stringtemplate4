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
from typing import Optional

from org.stringtemplate.v4.debug.interp_event import InterpEvent
from org.stringtemplate.v4.instance_scope import InstanceScope


class EvalExprEvent(InterpEvent):
    """
    Represents an event that occurs when an expression is evaluated.
    """

    def __init__(
        self,
        scope: InstanceScope,
        start: int,
        stop: int,
        expr_start_char: int,
        expr_stop_char: int,
    ):
        """
        Initializes an EvalExprEvent.

        Args:
            scope: The InstanceScope.
            start: Start char index in output.
            stop: Stop char index in output.
            expr_start_char: Index of the first character in the template.
            expr_stop_char: Index of the last character in the template (inclusive).
        """
        super().__init__(scope, start, stop)
        self.expr_start_char: int = expr_start_char  # Index of first char in template
        self.expr_stop_char: int = (
            expr_stop_char  # Index of last char in template (inclusive)
        )
        self.expr: str
        if expr_start_char >= 0 and expr_stop_char >= 0:
            self.expr = scope.st.impl.template[expr_start_char : expr_stop_char + 1]
        else:
            self.expr = ""

    def __str__(self) -> str:
        """Returns a string representation of the event."""
        return (
            f"{self.__class__.__name__}{{self={self.scope.st}, "
            f"expr='{self.expr}', exprStartChar={self.expr_start_char}, "
            f"exprStopChar={self.expr_stop_char}, start={self.output_start_char}, "
            f"stop={self.output_stop_char}}}"
        )

    def __repr__(self):
        return self.__str__()


"""
Key changes and explanations:

    Inheritance: EvalExprEvent inherits from InterpEvent (which is assumed to be defined elsewhere, and you've already provided its Java code).
    Constructor: The constructor takes all the necessary parameters, calls the superclass constructor, and initializes the instance variables. The logic for extracting the expression substring from the template is correctly implemented.
    __str__: The __str__ method provides a user-friendly string representation of the event, similar to the Java toString() method. f-strings are used for formatting. Added a __repr__ method.
    Type Hints: Type hints are used throughout.
    Imports: Added necessary imports, including InstanceScope.

This Python class accurately represents the EvalExprEvent from the Java code. It stores information about the expression being evaluated, its location in the template, and its location in the output.  It's a simple data class with a helpful string representation for debugging.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
