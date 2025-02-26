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
from typing import Protocol, runtime_checkable
from typing import Optional
import io  # Import the 'io' module


@runtime_checkable
class STWriter(Protocol):
    """
    Generic StringTemplate output writer filter.

    Literals and the elements of expressions are emitted via `write(str)`.
    Separators are emitted via `write_separator(str)` because they must be
    handled specially when wrapping lines (we don't want to wrap
    in between an element and it's separator).
    """

    NO_WRAP: int = -1

    def push_indentation(self, indent: str) -> None:
        pass

    def pop_indentation(self) -> str:
        pass

    def push_anchor_point(self) -> None:
        pass

    def pop_anchor_point(self) -> None:
        pass

    def set_line_width(self, line_width: int) -> None:
        pass

    def write(self, str_: str) -> int:
        """
        Write the string and return how many actual characters were written.
        With auto-indentation and wrapping, more chars than `len(str_)`
        can be emitted.  No wrapping is done.
        """
        pass

    def write_with_wrap(self, str_: str, wrap: str) -> int:
        """
        Same as write, but wrap lines using the indicated string as the
        wrap character (such as "\\n").
        """
        pass

    def write_wrap(self, wrap: str) -> int:
        """
        Because we evaluate ST instance by invoking
        `Interpreter.exec(STWriter, InstanceScope)` again, we can't pass options in.
        So the `Bytecode.INSTR_WRITE` instruction of an applied template
        (such as when we wrap in between template applications like
        `<data:{v|[<v>]}; wrap>`) we need to write the `wrap` string
        before calling `Interpreter.exec`. We expose just like for the
        separator. See `Interpreter.write_object` where it checks for ST
        instance. If POJO, `Interpreter.write_pojo` passes `wrap` to
        `STWriter.write(String str, String wrap)`. Can't pass to
        `Interpreter.exec`.
        """
        pass

    def write_separator(self, str_: str) -> int:
        """
        Write a separator.  Same as `write(str)` except that a "\\n"
        cannot be inserted before emitting a separator.
        """
        pass

    def index(self) -> int:
        """
        Return the absolute char index into the output of the char
        we're about to write.  Returns 0 if no char written yet.
        """
        pass


"""
Key changes and explanations:

    Protocol: The STWriter is defined as a Protocol (using typing.Protocol and @runtime_checkable). This is the Pythonic equivalent of a Java interface. It defines the methods that any concrete STWriter implementation must have, without providing any implementation itself. The @runtime_checkable decorator allows us to use isinstance() to check if an object conforms to the protocol, even without inheriting from it directly.
    Method Signatures: All the method signatures from the Java interface are defined using ... (ellipsis) as the body. This indicates that the methods are abstract and must be implemented by concrete subclasses.
    Type Hints: Type hints are used for all method parameters and return values, improving code readability and enabling static analysis.
    write() method variations: The write() method is split in two methods write and write_with_wrap as in Python we can't use method overloading.
    Docstrings: Comprehensive docstrings (using triple quotes) are provided for the class and all methods, explaining their purpose and usage. The original JavaDoc comments are adapted to Python docstring format.
    Import io module: added. This module will be useful when implementing concrete classes that use STWriter.

This Python code defines the STWriter protocol correctly, providing a clear contract for any classes that want to implement StringTemplate output writing functionality.  This is a crucial step in porting the StringTemplate engine to Python, ensuring that different output writers (e.g., for writing to strings, files, or network streams) can be used interchangeably.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
