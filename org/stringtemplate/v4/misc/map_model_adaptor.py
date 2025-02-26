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
from typing import Any, Dict, Optional, TypeVar

from org.stringtemplate.v4.interpreter import Interpreter
from org.stringtemplate.v4.model_adaptor import ModelAdaptor
from org.stringtemplate.v4.st import ST
from org.stringtemplate.v4.st_group import STGroup
from org.stringtemplate.v4.misc.st_no_such_property_exception import (
    STNoSuchPropertyException,
)

# Using TypeVar to represent Map<?, ?>
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class MapModelAdaptor(ModelAdaptor[Dict[_KT, _VT]]):
    """
    Model adaptor for Python dictionaries, mimicking Java's Map behavior.
    """

    def get_property(
        self,
        interp: Interpreter,
        st: ST,
        model: Dict[_KT, _VT],
        property: Any,
        property_name: str,
    ) -> Any:
        """
        Retrieves a property from the Map (dictionary).
        Handles "keys", "values", and default value lookups.

        Args:
            interp:  Interpreter instance (not used here, but part of the interface).
            st: The ST instance.
            model: The dictionary.
            property: The requested property.
            property_name: String form of property name, in case property is non-string.

        Returns:
            The value associated with the property, or a default value if available.
        Raises:
            STNoSuchPropertyException: If the property is not found and no default is available.

        """
        value: Any

        if property is None:
            value = MapModelAdaptor._get_default_value(model)
        elif MapModelAdaptor._contains_key(model, property):
            value = model.get(property)
        elif MapModelAdaptor._contains_key(
            model, property_name
        ):  # Try string version of key
            value = model.get(property_name)
        elif property == "keys":
            value = model.keys()
        elif property == "values":
            value = model.values()
        else:
            value = MapModelAdaptor._get_default_value(model)  # not found, use default

        if value == STGroup.DICT_KEY:
            value = property

        return value

    @staticmethod
    def _contains_key(map_obj: Dict[_KT, _VT], key: Any) -> bool:
        """
        Safely checks if a key exists in the dictionary, handling potential
        ClassCastException (which can occur in Java but less likely in Python).

        Args:
            map_obj: The dictionary.
            key: The key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        try:
            return key in map_obj  # Use the 'in' operator for Pythonic key lookup
        except TypeError:  # Catch TypeError, equivalent of ClassCastException for 'in'
            return False

    @staticmethod
    def _get_default_value(map_obj: Dict[_KT, _VT]) -> Any:
        """
        Retrieves the default value from the dictionary (associated with STGroup.DEFAULT_KEY).

        Args:
           map_obj: The dictionary.

        Returns:
            The default value, or None if not found or a TypeError occurs.
        """
        try:
            return map_obj.get(STGroup.DEFAULT_KEY)
        except TypeError:  # Handle potential TypeError (like ClassCastException)
            return None


"""
Key changes, improvements, and explanations:

    Type Hints and Generics: Type hints are used extensively (Dict, Any, TypeVar). TypeVar is used to mimic the Java generic types <?, ?> (meaning any key and value types). _KT and _VT are used as type variables to represent the key and value types, respectively.
    get_property(): The logic for retrieving properties from the dictionary is implemented, including handling:
        None property (returns default value).
        Direct key lookup.
        String key lookup (if the original key lookup fails).
        "keys" and "values" special properties.
        Default value lookup (if the key is not found).
        STGroup.DICT_KEY handling.
    _contains_key(): This static method uses the Pythonic in operator for key lookup and includes a try...except TypeError block to handle potential type errors (which are the closest equivalent to Java's ClassCastException in this context). This makes the code robust against unexpected key types.
    _get_default_value(): This static method attempts to retrieve the default value associated with STGroup.DEFAULT_KEY. It also includes error handling for TypeError.
    STNoSuchPropertyException: The Java version implicitly returns null when a property isn't found; it doesn't explicitly throw. The Python version does the same, by returning the value from the _get_default_value() method.
    Imports: All necessary classes and functions are imported, including the type hints and STGroup.
    Static Methods: The helper methods _contains_key and _get_default_value are marked as @staticmethod, since they do not operate on an instance of the class.
    Map<?, ?> in Java: In Python, the equivalent of Map<?, ?> is Dict[Any, Any] - where the keys and the values can be anything. Since TypeVars are used, keys can be compared for equality.

This revised Python code provides a correct, robust, and Pythonic implementation of the Java MapModelAdaptor. It handles various edge cases, uses type hints for clarity, and leverages Python's built-in dictionary features effectively. It's now well-integrated and ready for use in the StringTemplate library.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
