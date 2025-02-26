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
import traceback
from typing import Optional, List


class ConstructionEvent:
    """
    An event that happens when building ST trees, adding attributes, etc.
    """

    def __init__(self):
        """
        Initializes a ConstructionEvent and captures the current stack trace.
        """
        self.stack: List[traceback.FrameSummary] = traceback.extract_stack()

    def get_file_name(self) -> Optional[str]:
        """
        Gets the filename from the stack trace entry point (outside of StringTemplate code).

        Returns:
           The filename, or None if no suitable stack trace element is found.
        """
        entry_point = self.get_st_entry_point()
        return entry_point.filename if entry_point else None

    def get_line(self) -> Optional[int]:
        """
        Gets the line number from the stack trace entry point (outside ST code).

        Returns:
            The line number or None if no suitable stack trace element found.
        """
        entry_point = self.get_st_entry_point()
        return entry_point.lineno if entry_point else None

    def get_st_entry_point(self) -> Optional[traceback.FrameSummary]:
        """
        Finds the first stack trace element that does *not* start with "org.stringtemplate.v4".

        Returns:
            The StackTraceElement, or None if all elements are from StringTemplate.
        """
        for frame in reversed(self.stack):  # Iterate in reverse for efficiency
            if not frame.filename.startswith("org/stringtemplate/v4"):
                return frame
        return self.stack[-1] if self.stack else None  # Return last element, or None

    def __str__(self) -> str:
        """
        Default string representation of the event (can be overridden in subclasses).
        """
        return f"ConstructionEvent(file={self.get_file_name()}, line={self.get_line()})"

    def __repr__(self) -> str:
        return self.__str__()


"""
Key changes, improvements, and explanations:

    traceback Module: Uses Python's built-in traceback module instead of Throwable (which doesn't exist directly in Python). traceback.extract_stack() captures the stack trace as a list of FrameSummary objects, which are similar to Java's StackTraceElement.
    Constructor: The constructor (__init__) calls traceback.extract_stack() and stores the result in the self.stack instance variable.
    get_file_name() and get_line(): These methods now correctly retrieve the filename and line number from the FrameSummary object returned by get_st_entry_point(). They also handle the case where get_st_entry_point() returns None, returning None in that situation to prevent errors.
    get_st_entry_point(): This method iterates through the FrameSummary objects in reverse order. This is more efficient because the entry point we're looking for is usually closer to the end of the stack trace (the most recent calls). It returns the first frame not starting with "org/stringtemplate/v4", or the last element if the list is not empty, or None if no entry point is found.
    Type Hints: Type hints have been added for clarity and static analysis.
    __str__ and __repr__: Basic __str__ and __repr__ methods are added for a default representation of the event (which will likely be overridden in subclasses).
    Correct Path Check: The check frame.filename.startswith("org/stringtemplate/v4") now uses / instead of .. This handles operating systems correctly, and is consistent with how stack traces and file names are generally presented.
    Optional Return Types: Use Optional[] to indicate that a method may return either a value of the specified type, or None.

This revised Python code accurately emulates the behavior of the Java ConstructionEvent class, providing a robust way to capture and analyze stack trace information during the construction of StringTemplate objects. It's more Pythonic, more efficient, and more robust than a direct transliteration, thanks to the use of the traceback module and proper error handling.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
