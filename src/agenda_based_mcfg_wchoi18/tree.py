import pyparsing
from agenda_based_mcfg_wchoi18.grammar import MCFGRule as Rule
from typing import TypeVar, Optional
from collections.abc import Hashable, Callable

DataType = Hashable
TreeList = list[str, Optional[list['TreeList']]]
TreeTuple = tuple[DataType, Optional[tuple['TreeTuple', ...]]]

class Tree:

    LPAR = pyparsing.Suppress('(')
    RPAR = pyparsing.Suppress(')')
    DATA = pyparsing.Regex(r'[^\(\)\s]+')

    PARSER = pyparsing.Forward()
    SUBTREE = pyparsing.ZeroOrMore(PARSER)
    PARSERLIST = pyparsing.Group(LPAR + DATA + SUBTREE + RPAR)
    PARSER <<= DATA | PARSERLIST

    """
    A class representing a tree structure.
    
    Parameters
    ----------
    data : DataType
    children : list[Tree], optional

    Attributes
    ----------
    data : DataType
    children : list[Tree]
    """
    
    def __init__(self, data: DataType, children: list['Tree'] = []):
        self._data = data
        self._children = children
        
        self._validate()
  
    def to_tuple(self) -> TreeTuple:
        """
        Convert the tree to a tuple.

        Returns
        -------
        TreeTuple
            A tuple representation of the tree.
        """
        return self._data, tuple(c.to_tuple() for c in self._children)

    def __hash__(self) -> int:
        """
        Return a hash value for the tree.

        Returns
        -------
        int
            Hash value for the tree.
        """
        return hash(self.to_tuple())
    
    def __eq__(self, other: 'Tree') -> bool:
        """
        Check if two trees are equivalent.

        Parameters
        ----------
        other : Tree
            The other tree to compare with.

        Returns
        -------
        bool
            True if the trees are equal, False otherwise.
        """
        return self.to_tuple() == other.to_tuple()

    def __str__(self) -> str:
        """
        Return a string representation of the tree.

        Returns
        -------
        str
            String representation of the tree.
        """
        return ' '.join(self.terminals)
        
    def __repr__(self) -> str:
        """
        Return a string representation of the tree.

        Returns
        -------
        str
            String representation of the tree.
        """
        return self.to_string()
     
    def to_string(self, depth=0) -> str:
        """
        Return a string representation of the tree with indentation.

        Parameters
        ----------
        depth : int, optional
            The current depth of the tree for indentation.

        Returns
        -------
        str
            String representation of the tree with indentation.
        """
        s = (depth - 1) * '  ' +\
            int(depth > 0) * '--' +\
            self._data + '\n'
        s += ''.join(c.to_string(depth+1)
                     for c in self._children)
        
        return s
    
    def __contains__(self, data: DataType) -> bool:
        """
        Check if the tree contains a specific data value.

        Parameters
        ----------
        data : DataType
            The data value to check for.

        Returns
        -------
        bool
            True if the data value is found in the tree, False otherwise.
        """
        # pre-order depth-first search
        if self._data == data:
            return True
        else:
            for child in self._children:
                if data in child:
                    return True
                
            return False
        
    def __getitem__(self, idx: int | tuple[int, ...]) -> 'Tree':
        """
        Get a child tree by index or a path of indices.

        Parameters
        ----------
        idx : int or tuple[int, ...]
            The index or path of indices to access the child tree.

        Returns
        -------
        Tree
            The child tree at the specified index or path.
        """
        if isinstance(idx, int):
            return self._children[idx]
        elif len(idx) == 1:
            return self._children[idx[0]]
        elif idx:
            return self._children[idx[0]].__getitem__(idx[1:])
        else:
            return self
        
    @property
    def data(self) -> DataType:
        """
        Return the data of the tree.

        Returns
        -------
        DataType
            The data of the tree.
        """
        return self._data 
    
    @property
    def children(self) -> list['Tree']:
        """
        Return the children of the tree.

        Returns
        -------
        list[Tree]
            The children of the tree.
        """
        return self._children
     
    @property
    def terminals(self) -> list[str]:
        """
        Return the terminal symbols of the tree.

        Returns
        -------
        list[str]
            The terminal symbols of the tree.
        """
        if self._children:
            return [w for c in self._children 
                    for w in c.terminals]
        else:
            return [str(self._data)]
        
    @property
    def nonterminals(self) -> list[str]:
        """
        Return the non-terminal symbols of the tree.

        Returns
        -------
        list[str]
            The non-terminal symbols of the tree.
        """
        nts = []
        if self._children:
            nts.append(str(self._data))
            for child in self._children:
                nts.extend(child.nonterminals)
        return nts
        
    def _validate(self) -> None:
        try:
            assert all(isinstance(c, Tree)
                       for c in self._children)
        except AssertionError:
            msg = 'all children must be trees'
            raise TypeError(msg)
            
    def index(self, data: DataType, index_path: tuple[int, ...] = tuple()) -> list[tuple[int, ...]]:
        """
        Return the indices of the tree that match the given data.

        Parameters
        ----------
        data : DataType
            The data value to search for.
        index_path : tuple[int, ...], optional
            The path of indices to access the child tree.

        Returns
        -------
        list[tuple[int, ...]]
            A list of indices that match the given data.
        """
        indices = [index_path] if self._data==data else []
        root_path = [] if index_path == -1 else index_path
        
        indices += [j 
                    for i, c in enumerate(self._children) 
                    for j in c.index(data, root_path+(i,))]

        return indices
    
    def relabel(self, label_map: Callable[[DataType], DataType], 
                nonterminals_only: bool = False, terminals_only: bool = False) -> 'Tree':
        """
        Relabel the tree using the provided label_map function.

        Parameters
        ----------
        label_map : Callable[[DataType], DataType]
            A function that takes a data value and returns a new data value.
        nonterminals_only : bool, optional
            If True, only non-terminal symbols will be relabeled.
        terminals_only : bool, optional
            If True, only terminal symbols will be relabeled.

        Returns
        -------
        Tree
            A new tree with relabeled data.
        """
        if not nonterminals_only and not terminals_only:
            data = label_map(self._data)
        elif nonterminals_only and self._children:
            data = label_map(self._data)
        elif terminals_only and not self._children:
            data = label_map(self._data)
        else:
            data = self._data
        
        children = [c.relabel(label_map, nonterminals_only, terminals_only) 
                    for c in self._children]
        
        return self.__class__(data, children)
    
    @classmethod
    def from_string(cls, treestr: str) -> 'Tree':
        """
        Create a tree from a string representation.
        
        Parameters
        ----------
        treestr : str
            The string representation of the tree.

        Returns
        -------
        Tree
            A tree object created from the string representation.
        """
        treelist = cls.PARSER.parseString(treestr[2:-2])[0]
        
        return cls.from_list(treelist)
    
    @classmethod
    def from_list(cls, treelist: TreeList) -> 'Tree':
        """
        Create a tree from a list representation.

        Parameters
        ----------
        treelist : TreeList
            The list representation of the tree.

        Returns
        -------
        Tree
            A tree object created from the list representation.
        """
        if isinstance(treelist, str):
            return cls(treelist[0])
        elif len(treelist) == 1:
            return cls(treelist[0])
        elif isinstance(treelist[1], str):
            return cls(treelist[0], [cls(treelist[1])])
        else:
            return cls(treelist[0], [cls.from_list(l) for l in treelist[1:]])
        
    @property
    def rules(self) -> set[Rule]:
        """
        Return the rules of the tree.

        Returns
        -------
        set[Rule]
            A set of rules generated from the tree structure.
        """
        current_rhs = tuple(child.data for child in self._children)
        rules = set()
        for child in self._children:
            if child.children:
                rules |= child.rules
        rules.add(Rule(self.data, *current_rhs))

        return rules