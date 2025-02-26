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
from typing import Any, Optional
from antlr4.tree.Tree import Tree
from antlr4.tree.Trees import Trees  # Import Trees
from antlr4 import CommonToken  # type: ignore
from antlr4.ParserRuleContext import ParserRuleContext  # type: ignore
from antlr4.tree.Tree import TerminalNode, TerminalNodeImpl  # type: ignore


# This is required, as STViz needs a JTreeModel, but it is not present
# in the antlr4 python runtime. So, a minimal implementation is provided here.
class JTreeASTModel:
    """
    A minimal implementation of a TreeModel for use with JTree (or in this
    case, a hypothetical STViz that would use a tree structure).  This class
    adapts an ANTLR4 parse tree (Tree) to the TreeModel interface.

    This is a simplified version suitable for use where we don't need full
    editing capabilities.  It only implements the read-only methods of
    TreeModel.
    """

    def __init__(self, root: Tree):
        """
        Initializes the JTreeASTModel.

        Args:
            root: The root of the ANTLR parse tree.
        """

        self.root: Tree = root

    def getChildCount(self, parent: Any) -> int:
        """
        Returns the number of children of the given parent node.
        """
        if isinstance(parent, (ParserRuleContext, TerminalNodeImpl)):
            return parent.getChildCount()
        return 0

    def getIndexOfChild(self, parent: Any, child: Any) -> int:
        """
        Returns the index of the child node within the parent node.
        """

        if parent is None:
            return -1

        if isinstance(parent, (ParserRuleContext, TerminalNodeImpl)):
            for i in range(parent.getChildCount()):
                if parent.getChild(i) == child:
                    return i
        return -1

    def getChild(self, parent: Any, index: int) -> Any:
        """
        Returns the child of the parent node at the given index.
        """
        if isinstance(parent, (ParserRuleContext, TerminalNodeImpl)):
            return parent.getChild(index)
        return None  # Or raise Exception.

    def isLeaf(self, node: Any) -> bool:
        """
        Checks if a node is a leaf node (i.e., has no children).
        """
        return self.getChildCount(node) == 0

    def getRoot(self) -> Any:
        """
        Returns the root of the tree.
        """
        return self.root

    # The methods below are part of the TreeModel interface but are not needed
    # for a read-only tree view, so we provide stub implementations that do nothing.
    def valueForPathChanged(self, path, newValue) -> None:
        """Not implemented."""
        pass  # Not implemented for a read-only model

    def addTreeModelListener(self, l) -> None:
        """Not implemented."""
        pass  # Not implemented for a read-only model

    def removeTreeModelListener(self, l) -> None:
        """Not implemented."""
        pass  # Not implemented for a read-only model


"""
Key improvements, changes and explanations:

    Simplified Implementation: The code is significantly simplified because the ANTLR4 Python runtime already provides the necessary methods on the ParseTree objects. There's no need to create a separate adaptor. The ParserRuleContext and TerminalNodeImpl classes (which represent nodes in the parse tree) already have getChildCount(), getChild(), and getParent() methods.
    Direct Use of ANTLR4 Tree: The code now directly uses the ANTLR4 Tree interface as the underlying data structure, rather than relying on a separate TreeAdaptor. This is the correct and efficient way to do it in Python.
    isinstance Checks: The isinstance(parent, (ParserRuleContext, TerminalNodeImpl)) checks ensure that we're working with the correct ANTLR4 tree node types.
    getChildCount(), getIndexOfChild(), getChild(), isLeaf(), getRoot(): These methods are implemented using the corresponding methods of the ANTLR4 tree nodes.
    Stub Methods: The methods valueForPathChanged(), addTreeModelListener(), and removeTreeModelListener() are given stub implementations (they do nothing) because they are not needed for a read-only tree view.
    Imports: Added TerminalNode and TerminalNodeImpl.
    Type Hints: Type hints are added throughout.

This Python code provides a correct and highly efficient implementation of the JTreeASTModel, adapting an ANTLR4 parse tree to a read-only tree model. The code is much simpler and more direct than the Java version because it leverages the existing tree structure provided by the ANTLR4 runtime. The simplification is possible and highly beneficial.
"""
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
