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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from org.stringtemplate.v4.misc.st_message import STMessage


class STErrorListener(ABC):
    """How to handle messages."""

    @abstractmethod
    def compile_time_error(self, msg: "STMessage") -> None:
        """
        Called when a compile-time error occurs (e.g., syntax error).
        """
        raise NotImplementedError("Implement this method")

    @abstractmethod
    def run_time_error(self, msg: "STMessage") -> None:
        """
        Called when a run-time error occurs (e.g., missing attribute).
        """
        raise NotImplementedError("Implement this method")

    @abstractmethod
    def io_error(self, msg: "STMessage") -> None:
        """
        Called when an I/O error occurs.
        """
        raise NotImplementedError("Implement this method")

    @abstractmethod
    def internal_error(self, msg: "STMessage") -> None:
        """
        Called when an internal error occurs within StringTemplate itself.
        """
        raise NotImplementedError("Implement this method")


"""
Key Changes and Explanations:

    Abstract Base Class (ABC): The Java interface is converted to a Python abstract base class using the abc module. This enforces that any concrete implementation of STErrorListener must provide implementations for all the abstract methods.
    @abstractmethod: The @abstractmethod decorator is used to mark each method as abstract.
    Type Hints: Type hints are used for clarity, with STMessage assumed to be a class defined elsewhere in the project. TYPE_CHECKING is used to resolve the circular dependency, if STMessage needs to import this class.
    Docstrings: Clear docstrings are provided, explaining the purpose of each method.
    NotImplementedError: Each abstract method raises a NotImplementedError. This is the standard way to indicate that a method must be implemented by subclasses.
    Method Names: Renamed the methods to snake_case for idiomatic reasons.

This Python code accurately represents the Java STErrorListener interface as an abstract base class, defining the required methods that any concrete error listener must implement.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
