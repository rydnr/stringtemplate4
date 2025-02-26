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


class AmbiguousMatchException(Exception):
    """
    Custom exception class for ambiguous matches, inheriting from the built-in Exception.
    This mirrors the Java AmbiguousMatchException which extends RuntimeException.
    """

    def __init__(self, message: str = "", cause: Exception = None):
        """
        Initializes an AmbiguousMatchException.

        Args:
            message: The error message.
            cause: The underlying cause of the exception.
        """
        super().__init__(message)  # Pass the message to the base Exception class
        self.cause = cause  # Store the cause (if any)

    def __str__(self):
        """Returns string with message and cause."""
        if self.cause:
            return f"{super().__str__()}, caused by {self.cause}"
        return super().__str__()


"""
Key changes and explanations:

    Inheritance: The AmbiguousMatchException class now inherits directly from Python's built-in Exception class. This is the most appropriate base class for custom exceptions in Python, and it mirrors the behavior of Java's RuntimeException.
    Constructor: The constructor takes an optional message and cause argument, similar to the Java version. It calls super().__init__(message) to properly initialize the base Exception class with the error message. It also stores the cause for later inspection, if provided.
    __str__: This method presents both the message and the cause (if available).
    No need for type hints on cause: Although Exception is used, this covers Throwable and is the common approach for specifying an exception as the cause.

This Python code provides a clean and accurate equivalent of the Java AmbiguousMatchException class, following best practices for custom exceptions in Python.  It allows for both a message and a cause, making it suitable for handling and reporting ambiguous match errors within the StringTemplate library.  It's a fully functional and well-integrated part of the ported library.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
