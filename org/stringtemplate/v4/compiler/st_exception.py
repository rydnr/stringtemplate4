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


class STException(Exception):
    """
    A custom exception class for StringTemplate errors.
    Extends the built-in Exception class.
    """

    def __init__(
        self, message: Optional[str] = None, cause: Optional[Exception] = None
    ):
        """
        Initializes the STException.

        Args:
            message: The error message.
            cause:  The underlying cause of the exception.
        """
        super().__init__(message)  # Call superclass constructor with the message
        self.cause = cause

    def __str__(self) -> str:
        """
        Provides a string representation of the exception, including the cause if present.
        """
        if self.cause:
            return f"{super().__str__()} (caused by: {self.cause})"
        return super().__str__()


"""
Key changes and explanations:

    Inheritance: The STException class now inherits directly from Python's built-in Exception class. This is the standard way to create custom exceptions in Python, and it's more concise than extending RuntimeException (which doesn't exist directly in Python).
    Constructor: The constructor (__init__) takes an optional message and an optional cause (the underlying exception). This matches the Java constructors. The super().__init__(message) call is crucial; it properly initializes the base Exception class with the error message. The cause is stored as an instance variable.
    __str__ Method: Overriding the __str__ method gives control to the format of the printed exception. In this case, a check for cause is performed, and the cause information is concatenated in the string format, with the super().__str__() method call.
    Type Hints: Type hints are used for clarity.
    No need to getCause(): in python is better to check directly for the attribute self.cause.

This Python code provides a clean and correct implementation of the STException class, mirroring the functionality of the Java version and adhering to Python best practices for custom exceptions. The use of super() ensures proper initialization, and the optional cause parameter allows for chaining exceptions, preserving the original error information.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
