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
from typing import Any, Optional
from org.stringtemplate.v4.debug.construction_event import ConstructionEvent


class AddAttributeEvent(ConstructionEvent):
    """
    Represents an event where an attribute is added to a template.
    """

    def __init__(self, name: str, value: Any):
        """
        Initializes an AddAttributeEvent.

        Args:
            name: The name of the attribute being added.
            value: The value of the attribute being added.
        """
        super().__init__()  # Call the superclass constructor
        self.name: str = name
        self.value: Any = value  # Reserved for future use

    def __str__(self) -> str:
        """
        Returns a string representation of the event.
        """
        return (
            f"addEvent{{, name='{self.name}', value={self.value}, "
            f"location={self.file_name}:{self.line}}}"
        )

    def __repr__(self) -> str:
        return self.__str__()


"""
Key changes and explanations:

    Inheritance: AddAttributeEvent inherits from ConstructionEvent (which is assumed to be defined elsewhere, corresponding to the Java inheritance).
    Constructor: The constructor (__init__) takes the attribute name and value as arguments and initializes the instance variables. It calls the superclass constructor (super().__init__()) to properly initialize the base class part of the object.
    __str__ and __repr__: The __str__ method is implemented to provide a user-friendly string representation of the event, similar to the Java toString() method. Added __repr__ to return the __str__ representation.
    Type Hints: Type hints are included for clarity and static analysis.
    Imports: Added import for the ConstructionEvent super class.

This Python class accurately represents the AddAttributeEvent from the Java code, providing a way to track attribute addition events during template construction/evaluation. It's a simple data class, storing the attribute name and value, and providing a string representation for debugging purposes. The inheritance from ConstructionEvent is correctly handled.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
