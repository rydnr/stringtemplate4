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
from org.stringtemplate.v4.debug.eval_expr_event import EvalExprEvent
from org.stringtemplate.v4.instance_scope import InstanceScope


class IndentEvent(EvalExprEvent):
    """
    Represents an event that occurs when indentation is added during template rendering.
    It's a subclass of EvalExprEvent since indentation is treated as a type of expression.
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
        Initializes an IndentEvent.

        Args:
            scope: The InstanceScope of the template evaluation.
            start: The start index in the output string.
            stop:  The stop index in the output string.
            expr_start_char: Start char index in template.
            expr_stop_char: Stop char index in template.
        """
        super().__init__(scope, start, stop, expr_start_char, expr_stop_char)

    def __str__(self) -> str:
        return super().__str__()  # Use super class's str method.

    def __repr__(self) -> str:
        return self.__str__()


"""
Key changes and explanations:

    Inheritance: IndentEvent correctly inherits from EvalExprEvent.
    Constructor: The constructor takes the same arguments as the Java version and passes them to the superclass constructor using super().__init__().
    __str__ and __repr__: The __str__ method calls the superclass's implementation to reuse the string representation logic, and __repr__ is added.
    Type Hints: Included for clarity.
    Imports: Added.

This Python IndentEvent class is a straightforward and accurate translation of the Java class. Since it doesn't add any new fields or significantly different logic compared to EvalExprEvent, it can simply inherit the string representation from its parent class.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
