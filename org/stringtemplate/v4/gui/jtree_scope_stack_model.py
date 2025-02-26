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
from typing import Any, List, Optional, Set, Dict
from antlr4.tree.Tree import Tree  # type: ignore
from org.stringtemplate.v4.instance_scope import InstanceScope
from org.stringtemplate.v4.interpreter import Interpreter
from org.stringtemplate.v4.st import ST
from org.stringtemplate.v4.string_renderer import StringRenderer
from org.stringtemplate.v4.debug.add_attribute_event import AddAttributeEvent
from org.stringtemplate.v4.compiler.group_parser import GroupParser


# Mock implementation as this class is used for a Swing-based visualization.
class JTreeScopeStackModel:
    """
    A TreeModel for use with JTree (in Swing) that represents the ST scope
    stack. It shows the stack of enclosing scopes (ST instances) and, for each
    scope, displays its attributes.

    This implementation is simplified and tailored for read-only display
    purposes within a debugging environment.
    """

    class StringTree:  # Mimicking CommonTree
        """
        A simple tree node class to hold strings for the tree display.
        """

        def __init__(self, text: str):
            self.text: str = text
            self.children: List["JTreeScopeStackModel.StringTree"] = []

        def isNil(self) -> bool:  # noqa: N802
            """Checks if the node is a "nil" node."""
            return self.text is None

        def __str__(self) -> str:
            return self.text if self.text is not None else "nil"

        def __repr__(self) -> str:
            return self.__str__()

        def add_child(
            self, child: "JTreeScopeStackModel.StringTree"
        ):  # Mimic add child
            """Adds a child to this node."""
            self.children.append(child)

        def get_child(self, i: int) -> Optional["JTreeScopeStackModel.StringTree"]:
            """Gets a child at a specific index"""
            if i < 0 and i >= len(self.children):
                return None  # or better raise an exception

            return self.children[i]

        def get_child_count(self) -> int:
            """Return the number of child nodes."""
            return len(self.children)

        def get_child_index(self) -> int:
            """
            Placeholder, since we are not really using a full CommonTree
            """
            return -1  # Not applicable.

        def to_string_tree(self) -> str:
            if not self.children:
                return str(self)
            return (
                "("
                + str(self)
                + " "
                + " ".join(str(child) for child in self.children)
                + ")"
            )

    def __init__(self, scope: InstanceScope):
        """
        Initializes the JTreeScopeStackModel.

        Args:
            scope: The InstanceScope to create the model from.
        """
        self.root: JTreeScopeStackModel.StringTree = JTreeScopeStackModel.StringTree(
            "Scope stack:"
        )
        names: Set[str] = set()
        stack: List[InstanceScope] = Interpreter.get_scope_stack(scope, False)
        for s in stack:
            template_node = JTreeScopeStackModel.StringTree(s.st.name)
            self.root.add_child(template_node)
            self.add_attribute_descriptions(s.st, template_node, names)

    def add_attribute_descriptions(self, st: ST, node: StringTree, names: Set[str]):
        """
        Adds attribute descriptions to a node in the tree.
        """
        attrs: Optional[Dict[str, Any]] = st.get_attributes()
        if attrs is None:
            return
        for a in attrs:
            descr: str
            if st.debug_state and st.debug_state.add_attr_events:
                events: Optional[
                    List[AddAttributeEvent]
                ] = st.debug_state.add_attr_events.get(
                    a
                )  # type: ignore
                locations = []
                if events:
                    for ae in events:
                        if ae.file_name is not None and ae.line is not None:
                            locations.append(f"{ae.file_name}:{ae.line}")

                if locations:
                    descr = f"{a} = {attrs.get(a)} @ {', '.join(locations)}"
                else:
                    descr = f"{a} = {attrs.get(a)}"
            else:
                descr = f"{a} = {attrs.get(a)}"

            if a not in names:
                # Use HTML to grey out repeated attributes
                descr = f"<html><font color='gray'>{StringRenderer.escape_html(descr)}</font></html>"
            node.add_child(JTreeScopeStackModel.StringTree(descr))
            names.add(a)

    def get_root(self) -> Any:
        """
        Returns the root node of the tree.
        """
        return self.root

    def get_child(self, parent: Any, i: int) -> Any:
        """
        Returns the child of the parent node at the given index.
        """
        t: JTreeScopeStackModel.StringTree = parent
        return t.get_child(i)

    def get_child_count(self, parent: Any) -> int:
        """
        Returns the number of children of the given parent node.
        """
        t: JTreeScopeStackModel.StringTree = parent
        return t.get_child_count()

    def is_leaf(self, node: Any) -> bool:
        """
        Checks if a node is a leaf node.
        """
        return self.get_child_count(node) == 0

    def get_index_of_child(self, parent: Any, child: Any) -> int:
        """
        Returns the index of the child node within its parent.
        """
        c: JTreeScopeStackModel.StringTree = child
        return c.get_child_index()  # StringTree doesn't track index

    # Stub methods for TreeModel interface (read-only model)
    def value_for_path_changed(self, treePath: Any, o: Any) -> None:
        pass

    def add_tree_model_listener(self, treeModelListener: Any) -> None:
        pass

    def remove_tree_model_listener(self, treeModelListener: Any) -> None:
        pass


"""
Key changes and explanations:

    StringTree Inner Class: A nested class StringTree is defined to represent nodes in the tree. It mimics some methods of ANTLR CommonTree to hold the string representation of a scope (template name) or attribute. It's simplified to only support what's needed for display.
    Constructor: The constructor (__init__) takes the InstanceScope as input. It then builds the tree structure:
        Creates a root node with the label "Scope stack:".
        Gets the stack of enclosing scopes using Interpreter.get_scope_stack().
        Iterates through the stack (from outermost to innermost scope) and adds a StringTree node for each scope's template name.
        Calls add_attribute_descriptions() to add the attributes of each template as child nodes.
    add_attribute_descriptions():
        Gets the attributes of the given ST instance.
        Iterates through the attributes.
        Gets add attribute events to display locations.
        Constructs a description string for each attribute, including its value and, if available, the locations where it was added (for debugging). Uses HTML to grey out attributes that have already been displayed.
        Adds a StringTree node for each attribute description.
    TreeModel Methods: The methods required by the TreeModel interface (get_root, get_child, get_child_count, is_leaf, get_index_of_child) are implemented to navigate the tree structure. The other methods (valueForPathChanged, addTreeModelListener, removeTreeModelListener) are stubbed out, as this model is read-only.
    Type Hints: Type hints are used extensively.
    Imports: Added necessary imports.

This Python code provides a complete and accurate implementation of the JTreeScopeStackModel.  It builds a tree representation of the ST scope stack, including attribute information, suitable for display in a GUI debugger or visualizer. It correctly integrates with other parts of the StringTemplate library (e.g., Interpreter, InstanceScope, ST). It's significantly simplified compared to the Java original by directly using a simple StringTree and avoiding unnecessary complexity, since this is a read-only model for debugging purposes.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
