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


class Coordinate:
    """
    Represents a line number and character position within a line.  Used for
    source mapping to map addresses to ranges within a template.
    """

    def __init__(self, line: int, char_position: int):
        """
        Initializes a Coordinate object.

        Args:
            line: The line number.
            char_position: The character position within the line.
        """
        self.line: int = line
        self.char_position: int = char_position

    def __str__(self) -> str:
        """
        Returns a string representation of the Coordinate in the form "line:charPosition".
        """
        return f"{self.line}:{self.char_position}"

    def __repr__(self) -> str:
        return self.__str__()


"""
Key changes and explanations:

    Constructor: The constructor (__init__) takes the line and char_position as arguments and initializes the instance variables.
    __str__ and __repr__ Methods: The __str__ method provides the "line:charPosition" string representation, and the __repr__ method returns the __str__ representation. f-strings are used for formatting.
    Type Hints: Type hints are used (int).
    Docstrings: Comprehensive docstrings are provided.

This Python class is a very straightforward and accurate translation of the Java Coordinate class.  It's a simple data class representing a line and character position, with a clear string representation.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
