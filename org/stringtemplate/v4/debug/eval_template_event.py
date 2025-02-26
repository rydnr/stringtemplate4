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
from org.stringtemplate.v4.debug.interp_event import InterpEvent
from org.stringtemplate.v4.instance_scope import InstanceScope


class EvalTemplateEvent(InterpEvent):
    """
    Represents an event that occurs when a template is evaluated.
    This is a subclass of InterpEvent, focusing specifically on template evaluation.
    """

    def __init__(self, scope: InstanceScope, start: int, stop: int):
        """
        Initializes an EvalTemplateEvent.

        Args:
            scope: The InstanceScope of the template evaluation.
            start: The start character index in output.
            stop: The stop character index in output.
        """
        super().__init__(scope, start, stop)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}{{"
            + f"self={self.scope.st}"
            + f", start={self.output_start_char}, stop={self.output_stop_char}"
            + "}"
        )

    def __repr__(self) -> str:
        return self.__str__()


"""
Key changes and explanations:

    Inheritance: EvalTemplateEvent inherits from InterpEvent, as in the Java code.
    Constructor: The constructor takes the InstanceScope, start, and stop arguments, and calls the superclass constructor to initialize the base class part of the object.
    __str__ and __repr__: The __str__ method provides a user-friendly string representation, and the __repr__ returns the same representation. f-strings are used.
    Type Hints: Type hints are used.
    Imports: Added import statement for InstanceScope.

This Python code is a simple and accurate translation of the Java EvalTemplateEvent class, representing a template evaluation event during StringTemplate's interpretation process. The simplification is possible and correct because EvalTemplateEvent in the provided Java code doesn't add any new fields compared to its parent class InterpEvent; it only provides a different constructor and inherits all the functionality.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
