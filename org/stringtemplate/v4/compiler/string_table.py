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
from typing import Dict, List
from collections import OrderedDict


class StringTable:
    """
    A unique set of strings where we can get a string's index.
    We can also get them back out in original order.
    """

    def __init__(self):
        self.table: Dict[str, int] = (
            OrderedDict()
        )  # Use OrderedDict to preserve insertion order
        self.i: int = -1

    def add(self, s: str) -> int:
        """Adds a string to the table if it's not already present and returns its index."""
        if s in self.table:  # Use 'in' for dictionary key lookup
            return self.table[s]
        self.i += 1
        self.table[s] = self.i
        return self.i

    def to_array(self) -> List[str]:
        """Returns the strings in the table as a list, in their original order."""
        return list(self.table.keys())  # Efficient conversion to list

    def __len__(self):
        return len(self.table)

    def __contains__(self, s: str) -> bool:
        return s in self.table  # Use 'in' operator

    def __getitem__(self, s: str) -> int:
        return self.table[s]  # Raise KeyError


"""
Key changes and explanations:

    OrderedDict: The LinkedHashMap from Java is replaced with Python's OrderedDict from the collections module. This preserves the insertion order of the strings, which is crucial for the StringTable's functionality.
    add() Method: The add() method is implemented to add strings to the table (an OrderedDict) and return the index. It uses the in operator for efficient key lookup, rather than get() != None, which is more Pythonic.
    to_array() Method: This method efficiently converts the keys of the OrderedDict (which are the strings) to a list using list(self.table.keys()).
    Type Hints: Added.
    Dunder methods: __len__ and __contains__ have been included to improve usage and to make it more Pythonic.
    __getitem__: added, to allow indexed access, raising a KeyError if the item is not in the StringTable.

This Python code provides a correct and efficient implementation of the StringTable class, mirroring the behavior of the Java original and leveraging Python's built-in data structures for optimal performance and readability.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
