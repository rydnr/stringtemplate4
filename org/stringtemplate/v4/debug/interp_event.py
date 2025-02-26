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

from org.stringtemplate.v4.instance_scope import InstanceScope


class InterpEvent:
    """
    A base class for events that occur during template interpretation.
    """

    def __init__(
        self, scope: InstanceScope, output_start_char: int, output_stop_char: int
    ):
        """
        Initializes an InterpEvent.

        Args:
            scope: The InstanceScope of the template evaluation.
            output_start_char: Index of the first character in the output stream.
            output_stop_char: Index of the last character in the output stream (inclusive).
        """
        self.scope: InstanceScope = scope
        self.output_start_char: int = output_start_char
        self.output_stop_char: int = output_stop_char

    def __str__(self) -> str:
        """Returns a string representation of the event."""
        return (
            f"{self.__class__.__name__}{{self={self.scope.st}, "
            f"start={self.output_start_char}, stop={self.output_stop_char}}}"
        )

    def __repr__(self) -> str:
        return self.__str__()


"""
Key changes and explanations:

    Constructor: The constructor (__init__) takes the scope, output_start_char, and output_stop_char as arguments and initializes the corresponding instance variables.
    __str__ and __repr__: The __str__ method provides a user-friendly string representation of the event. __repr__ has been added and calls __str__. f-strings are used for formatting.
    Type Hints: Type hints are added for clarity.
    Imports: Added the import for InstanceScope.
    Instance Variables: Instance variables are created with type hints.

This Python class accurately represents the base InterpEvent from the Java code.  It stores the InstanceScope and the start/stop character positions in the output. It provides a basic string representation, which will likely be extended by subclasses.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
