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
from typing import Any, TypeVar, Generic
from abc import ABC, abstractmethod

# Assuming these are in the appropriate modules, matching the Java package structure
from org.stringtemplate.v4.interpreter import Interpreter
from org.stringtemplate.v4 import ST
from org.stringtemplate.v4.misc import STNoSuchPropertyException

T = TypeVar("T")


class ModelAdaptor(ABC, Generic[T]):
    """
    An object that knows how to convert property references to appropriate
    actions on a model object. Some models, like JDBC, are interface based (we
    aren't supposed to care about implementation classes). Some other models
    don't follow StringTemplate's getter method naming convention. So, if we have
    an object of type `M` with property method `M.foo()` (as opposed
    to `M.getFoo()`), we can register a model adaptor object, `adap`,
    that converts a lookup for property `foo` into a call to
    `M.foo()`.

    Given `<a.foo>`, we look up `foo` via the adaptor if
    `a instanceof M`.

    Args:
        T: the type of values this adaptor can handle.
    """

    @abstractmethod
    def get_property(
        self,
        interp: Interpreter,
        self_: ST,
        model: T,
        property: Any,
        property_name: str,
    ) -> Any:
        """
        Lookup property name in `o` and return its value.

        `property` is normally a `str` but doesn't have to be.
        E.g., if `o` is `Map`, `property` could be
        any key type. If we need to convert to `str`, then it's done by
        `ST` and passed in here.

        Args:
            interp: The interpreter instance.
            self_: The ST instance.
            model:  The object on which to look up the property.
            property: The property to look up (often a string, but could be other types).
            property_name: The string representation of the property name.

        Returns:
            The value of the property.

        Raises:
            STNoSuchPropertyException: If the property does not exist.
        """
        raise NotImplementedError("Subclasses must implement get_property")


"""
Key Changes and Explanation:

    ABC and @abstractmethod: The ModelAdaptor interface is correctly translated to a Python abstract base class (ABC) using the abc module. The get_property method is marked as abstract using @abstractmethod, ensuring that all concrete implementations of ModelAdaptor must provide an implementation for it.
    Type Hints: Type hints (Interpreter, ST, T, Any, str) are used to specify the types of method parameters and return values. This improves code readability and allows for static analysis. The use of TypeVar and Generic makes the ModelAdaptor generic, mirroring the Java generic type parameter.
    Docstrings: The Javadoc comments are translated into Python docstrings, providing clear documentation for the class and its methods.
    NotImplementedError: The get_property method in the abstract base class raises a NotImplementedError. This is the standard way in Python to indicate that a method must be implemented by subclasses.
    Parameter Names: The Java parameter o is renamed to model which better suits its meaning. self is renamed to self_ to be consistent with previous code and avoid shadowing the class's self.
    No change in Functionality: The code maintains the exact same functionality and purpose of the interface defined in Java, simply translated to a Python-standard interface/abstract class definition.

This Python code provides a clean and accurate representation of the Java ModelAdaptor interface, adhering to Python best practices and conventions. It provides the necessary structure for creating concrete model adaptors that can handle different object types within the StringTemplate engine.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
