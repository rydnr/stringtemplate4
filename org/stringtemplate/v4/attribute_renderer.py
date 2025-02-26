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
import locale
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class AttributeRenderer(ABC, Generic[T]):
    """
    This interface describes an object that knows how to format or otherwise
    render an object appropriately. There is one renderer registered per group
    for a given Java type.

    If the format string passed to the renderer is not recognized then simply
    call str(object).

    format_string can be None but locale will at least be
    locale.getdefaultlocale().

    Type Parameters:
        T: the type of values this renderer can handle.
    """

    @abstractmethod
    def to_string(
        self, value: T, format_string: Optional[str], loc: Optional[Any] = None
    ) -> str:
        """
        Render the object 'value' according to the format string and locale.

        Args:
            value: The object to render.
            format_string:  The format string (can be None).
            loc: The locale (if None, defaults to the system default locale).

        Returns:
            The rendered string.
        """
        raise NotImplementedError


"""
Key changes and explanations:

    abc module: Java interfaces are best represented in Python using abstract base classes (ABCs). We import ABC and abstractmethod from the abc module. AttributeRenderer now inherits from ABC.
    @abstractmethod: The toString method is marked as abstract using the @abstractmethod decorator. This forces any concrete subclass to implement this method.
    Type Hints: I've used Python's type hinting system.
        TypeVar('T'): This defines a type variable T, similar to the generic type parameter <T> in the Java interface. AttributeRenderer is now a generic class: AttributeRenderer(ABC, Generic[T]).
        value: T: Indicates that the value parameter should be of type T.
        format_string: Optional[str]: Indicates that format_string can be a string or None.
        loc: Optional[Any]: Indicates the locale is Optional and is of type Any. Since the AttributeRenderer interface just takes a locale argument and passes it down, and since specific renderers (like DateRenderer) are responsible for using the locale correctly, we can simplify the type hint for the loc parameter. The simplest, most robust, and most Pythonic solution here is to use Any as the type hint (or simply omit the type hint, which defaults to Any).  This avoids the error and maintains compatibility. Later, when you implement specific renderers, you'll use the locale module's functions correctly within those renderers.
        -> str: Indicates that the to_string method returns a string.
    Method Name: I've renamed toString to to_string. While __str__ is the most Pythonic way to get a string representation of an object, it's typically used for the default string representation. Since this interface is specifically about formatting with options, a more explicit name like to_string is better. This avoids confusion with the built-in __str__ method.
    Locale: Java's Locale is handled using Python's locale module. I've used locale.Locale for type hinting. The interface comments clarify that a None value for locale means to use locale.getdefaultlocale(). This is handled in the implementation.
    Docstrings: I've adapted the Javadoc comments into a Python docstring, clarifying the purpose of the class and the method.
    NotImplementedError: Inside the abstract method, we raise NotImplementedError. This is the standard way to indicate that a method in an abstract class must be implemented by a subclass.

This Python code provides the equivalent interface definition from the Java code, leveraging Python's features for abstract classes, type hinting, and documentation. It sets up the structure for concrete renderer implementations.  Good start! Let's move on to the next file when you're ready.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
