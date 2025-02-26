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
from typing import List
from org.stringtemplate.v4.st_error_listener import STErrorListener
from org.stringtemplate.v4.misc.st_message import STMessage
from org.stringtemplate.v4.misc.error_type import (
    ErrorType,
)  # Assuming ErrorType enum is defined
from org.stringtemplate.v4.misc.misc import Misc


class ErrorBuffer(STErrorListener):
    """
    Used during tests to track all errors.  Implements the STErrorListener
    interface.
    """

    def __init__(self):
        self.errors: List[STMessage] = []

    def compile_time_error(self, msg: STMessage) -> None:
        """
        Records a compile-time error.
        """
        self.errors.append(msg)

    def run_time_error(self, msg: STMessage) -> None:
        """
        Records a runtime error, excluding NO_SUCH_PROPERTY errors.
        """
        if msg.error != ErrorType.NO_SUCH_PROPERTY:  # type: ignore # Assuming ErrorType is an Enum
            self.errors.append(msg)

    def io_error(self, msg: STMessage) -> None:
        """
        Records an I/O error.
        """
        self.errors.append(msg)

    def internal_error(self, msg: STMessage) -> None:
        """
        Records an internal error.
        """
        self.errors.append(msg)

    def __str__(self) -> str:
        """
        Returns a string representation of all recorded errors, each on a new line.
        """
        buf = []
        for m in self.errors:
            buf.append(str(m) + Misc.newline)
        return "".join(buf)

    def __repr__(self):
        return self.__str__()


"""
Key changes, improvements and explanations:

    Inheritance: ErrorBuffer implements (inherits from) STErrorListener, as in the Java code.
    errors List: The errors list is initialized in the constructor.
    Error Handling Methods: The compile_time_error, run_time_error, io_error, and internal_error methods are implemented to add the received STMessage to the errors list. The run_time_error method correctly ignores NO_SUCH_PROPERTY errors.
    __str__ and __repr__ Methods: The __str__ method concatenates the string representations of all errors in the errors list, separated by newlines (using Misc.newline as in the Java). __repr__ added.
    Type Hints: Type hints are used extensively.
    Imports: Added all the required imports.
    ErrorType: Added an import of ErrorType.

This Python class accurately mirrors the functionality of the Java ErrorBuffer class. It's a simple error listener that stores all received error messages in a list, providing a way to collect and inspect errors during testing or debugging. The conditional check in run_time_error() is correctly implemented, and the toString() (now __str__()) method provides a combined string of all error messages.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
