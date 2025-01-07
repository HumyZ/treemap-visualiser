from __future__ import annotations
import os
from random import randint
import math

from typing import Tuple, List, Optional


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    === Public Attributes ===
    data_size: the total size of all leaves of this tree.
    colour: The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    _root: the root value of this tree, or None if this tree is empty.
    _subtrees: the subtrees of this tree.
    _parent_tree: the parent tree of this tree; i.e., the tree that contains
        this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    data_size: int
    colour: (int, int, int)
    _root: Optional[object]
    _subtrees: List[AbstractTree]
    _parent_tree: Optional[AbstractTree]

    def __init__(self: AbstractTree, root: Optional[object],
                 subtrees: List[AbstractTree], data_size: int = 0) -> None:
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this
        tree's data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None

        self.colour = (randint(0, 255), randint(0, 255), randint(0, 225))
        if not self._subtrees:
            self.data_size = data_size
        else:
            self.data_size = 0
            for tree in self._subtrees:
                self.data_size += tree.data_size
                tree._parent_tree = self

    def is_empty(self: AbstractTree) -> bool:
        """Return True if this tree is empty."""
        return self._root is None

    def generate_treemap(self: AbstractTree, rect: Tuple[int, int, int, int]) \
            -> List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]]:
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        """
        x, y, width, height = rect
        lst = []
        if self.data_size == 0:
            return []
        if not self._subtrees and self.data_size > 0:
            return [(rect, self.colour)]
        if width > height:
            curr_widths = 0
            for tree in self._subtrees:
                new_width = tree.data_size / tree._parent_tree.data_size * width
                new_width = math.floor(new_width)
                curr_widths += new_width
                if tree is self._subtrees[-1] and curr_widths != 0:
                    diff = width % curr_widths
                    new_width += diff
                lst.extend(tree.generate_treemap((x, y, new_width, height)))
                x += new_width
        elif height >= width:
            curr_heights = 0
            for tree in self._subtrees:
                size = tree.data_size / tree._parent_tree.data_size
                new_height = size * height
                new_height = math.floor(new_height)
                curr_heights += new_height
                if tree is self._subtrees[-1] and curr_heights != 0:
                    diff = height % curr_heights
                    new_height += diff
                lst.extend(tree.generate_treemap((x, y, width, new_height)))
                y += new_height
        return lst

    def get_leaf(self: AbstractTree, pos: Tuple[int, int], rects: List[Tuple])\
            -> Optional[AbstractTree]:
        """Given a position where the user clicks and the list of the
        rectangle descriptions, return which leaf this user has interacted with,
        or None if no such tree exists.
        """
        index = 0
        for rect in rects:
            if self._within_bounds(pos, rect):
                return self._get_leaves()[index]
            index += 1
        return None

    def _get_leaves(self: AbstractTree) -> List[AbstractTree]:
        """Given an AbstractTree, return the leaves of this tree.
        """
        if self.is_empty() or self.data_size == 0:
            return []
        if not self._subtrees:
            return [self]
        leaves = []
        for tree in self._subtrees:
            leaves.extend(tree._get_leaves())
        return leaves

    def _within_bounds(self, pos: Tuple[int, int], rect: Tuple[int, int, int,
                                                               int]) -> bool:
        """Determine if pos is within rect
        """
        x = self
        if x is self:
            return rect[0] <= pos[0] <= rect[2] + rect[0] and \
                rect[1] <= pos[1] <= rect[3] + rect[1]
        return rect[0] <= pos[0] <= rect[2] + rect[0] and \
            rect[1] <= pos[1] <= rect[3] + rect[1]

    def get_pathname(self: AbstractTree) -> str:
        """Given this tree, return the full path from first parent to self.
        """
        if self._parent_tree is None:
            return str(self._root)
        return self._parent_tree.get_pathname() + self.get_separator() + \
            str(self._root)

    def remove_leaf(self: AbstractTree) -> None:
        """Remove this leaf from this tree. Also update ancestors.
        Precondition: self is a leaf.
        """
        self._parent_tree._subtrees.remove(self)
        self.update_ancestors_deletion()

    def update_ancestors_deletion(self: AbstractTree) -> None:
        """Update the ancestors of this leaf to not include this leaf's
         data_size.
        """
        curr = self
        while curr._parent_tree is not None:
            curr = curr._parent_tree
            curr.data_size -= self.data_size
        return None

    def increase_datasize(self: AbstractTree) -> None:
        """Increase this tree's data_size by 1% of its datasize.
        Also update ancestor's data_size.
        """
        increment = math.ceil(self.data_size * 0.01)
        self.data_size += increment
        curr = self
        while curr._parent_tree is not None:
            curr = curr._parent_tree
            curr.data_size += increment
        return None

    def decrease_datasize(self: AbstractTree) -> None:
        """Decrease this tree's data size by 1% of its datasize only if
        that decrease will not result in a datasize below 1. Also update
        ancestor's data_size.
        """
        decrement = math.ceil(self.data_size * 0.01)
        if not (self.data_size - decrement) < 1:
            self.data_size -= decrement
            curr = self
            while curr._parent_tree is not None:
                curr = curr._parent_tree
                curr.data_size -= decrement
        return None

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.
        """
        raise NotImplementedError


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path.

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self: FileSystemTree, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        name = os.path.basename(path)
        if not os.path.isdir(path):
            AbstractTree.__init__(self, name, [], os.path.getsize(path))
        elif os.path.isdir(path):
            trees = []
            for obj in os.listdir(path):
                if obj != '.DS_Store':
                    trees.append(FileSystemTree(os.path.join(path, obj)))
            AbstractTree.__init__(self, name, trees)

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.
        """
        return os.path.sep
