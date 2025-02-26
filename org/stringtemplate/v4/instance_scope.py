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
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import issues by only importing during type checking
    from org.stringtemplate.v4.debug.eval_template_event import EvalTemplateEvent
    from org.stringtemplate.v4.debug.interp_event import InterpEvent
    from org.stringtemplate.v4.st import ST  # Assuming ST is in st.py


class InstanceScope:
    """
    Represents the execution scope of a single template instance.
    """

    def __init__(self, parent: Optional["InstanceScope"], st: "ST"):
        """
        Initialize the InstanceScope.

        Args:
            parent: The parent InstanceScope (if this is a nested template).
            st: The ST instance being executed.
        """
        self.parent: Optional[InstanceScope] = parent  # Template that invoked us.
        self.st: "ST" = st  # Template we're executing.
        self.ip: int = 0  # Current instruction pointer.

        # Includes the EvalTemplateEvent for this template. This is a
        # subset of Interpreter.events field. The final
        # EvalTemplateEvent is stored in 3 places:
        #
        # 1. In self.parent's self.child_eval_template_events list
        # 2. In this list
        # 3. In the Interpreter.events list
        #
        # The root ST has the final EvalTemplateEvent in its list.
        #
        # All events get added to the parent's event list.

        self.events: List["InterpEvent"] = []

        # All templates evaluated and embedded in this ST. Used
        # for tree view in STViz.
        self.child_eval_template_events: List["EvalTemplateEvent"] = []

        self.early_eval: bool = parent is not None and parent.early_eval


"""
Key Changes and Explanations:

    Type Hints: Extensive use of type hints for clarity and to enable static analysis. Optional['InstanceScope'] indicates that parent can be either an InstanceScope object or None. TYPE_CHECKING is used for the imports of the debug-related classes to avoid circular dependencies, as those classes need to import ST which will eventually need InstanceScope.
    Docstrings: Added a comprehensive docstring to explain the purpose of the class.
    __init__: The constructor closely mirrors the Java version. The initialization of early_eval is identical.
    Removed unnecessary comments: Only the necessary comments have been kept.
    Simplified Member Names: Changed member variable names to be more Pythonic (e.g., childEvalTemplateEvents to child_eval_template_events).
    No Functional Changes: The essential logic and relationships between the members remain the same as in the Java code. This is a straightforward translation that primarily focuses on adapting the code to Python's syntax and conventions.

This Python class is a very close equivalent of the Java InstanceScope class. It's ready for integration into the larger project. It's important that the modules where EvalTemplateEvent, InterpEvent, and ST are defined are also correctly set up for the type hinting and imports to work seamlessly.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
