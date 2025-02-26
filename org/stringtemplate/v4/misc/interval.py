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


class Interval:
    """
    An inclusive interval a..b.  Used to track ranges in output and
    template patterns (for debugging).
    """

    def __init__(self, a: int, b: int):
        """
        Initializes an Interval.

        Args:
            a: The start of the interval (inclusive).
            b: The end of the interval (inclusive).
        """
        self.a: int = a
        self.b: int = b

    def __str__(self) -> str:
        """
        Returns a string representation of the interval in the form "a..b".
        """
        return f"{self.a}..{self.b}"

    def __repr__(self) -> str:
        return self.__str__()


"""
Key improvements and explanations:

    Constructor: The constructor (__init__) takes the start (a) and end (b) values of the interval and initializes the instance variables.
    __str__ and __repr__ Methods: The __str__ method provides the "a..b" string representation, and __repr__ method returns the __str__ representation. f-strings are used.
    Type Hints: Added for clarity.
    Docstrings: Comprehensive docstrings added.

This Python code is a straightforward and accurate translation of the Java Interval class, providing a simple data structure for representing an inclusive interval.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
