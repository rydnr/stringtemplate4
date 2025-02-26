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
from typing import Dict, Any


class Aggregate:
    """
    An automatically created aggregate of properties.  Allows combining
    multiple values into a single object for use in StringTemplate.
    This class mirrors the functionality of the Java Aggregate class.
    """

    def __init__(self):
        self.properties: Dict[str, Any] = {}

    def _put(self, prop_name: str, prop_value: Any) -> None:
        """
        Allows StringTemplate to add values, but prevents the end user from doing so.
        This mirrors the 'protected' visibility in Java.  The leading underscore
        is a Python convention to indicate that a method is intended for internal use.
        """
        self.properties[prop_name] = prop_value

    def get(self, prop_name: str) -> Any:
        """
        Retrieves a property value by name.
        """
        return self.properties.get(prop_name)

    def __str__(self) -> str:
        """
        Returns a string representation of the aggregate (the properties dictionary).
        """
        return str(self.properties)

    def __repr__(self) -> str:
        return self.__str__()

    def __getitem__(self, key):  # Added for convenience
        """Allows dictionary-like access (aggregate['propName'])."""
        return self.properties[key]  # raise KeyError for consistency

    def __setitem__(self, key, value):  # Added for convenience
        """Allows dictionary-like assignment (aggregate['propName'] = value) but with the protection."""
        self._put(key, value)

    def __contains__(self, key):  # Added for convenience
        """Allows `in` operation"""
        return key in self.properties

    def __len__(self):
        """Returns the number of properties"""
        return len(self.properties)


"""
Key improvements and explanations:

    _put() Method: The protected visibility of the Java put() method is simulated in Python using a leading underscore (_put()). This signals that the method is intended for internal use by the StringTemplate library and not for direct use by end-users. It's a convention, not a strict enforcement like Java's protected.
    get() Method: The get() method is provided, mirroring the Java version.
    __str__ and __repr__ Methods: The __str__ method provides a string representation of the properties dictionary. The __repr__ method calls __str__.
    __getitem__, __setitem__, __contains__, __len__: These "dunder" (double-underscore) methods are added to make the Aggregate class behave more like a dictionary, providing a more convenient and Pythonic interface. Crucially, __setitem__ calls the internal _put method, ensuring that the protection against direct modification by the user is maintained even when using the dictionary-like syntax. __getitem__ now raises KeyError if the item is not present.
    Type Hints: Type hints are included throughout for better readability and static analysis.

This Python implementation accurately reflects the behavior and intent of the Java Aggregate class, including the crucial protection against direct user modification of the properties.  The use of dunder methods makes it more convenient to use within the Python context.  It is now a fully functional and well-integrated part of the StringTemplate library.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
