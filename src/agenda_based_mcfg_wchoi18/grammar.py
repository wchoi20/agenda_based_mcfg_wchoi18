from typing import Tuple
from functools import lru_cache
import re

StringVariables = Tuple[int, ...]
SpanIndices = Tuple[int, ...]
SpanMap = dict[int, SpanIndices]


class MCFGRuleElement:

    """A multiple context free grammar rule element

    Parameters
    ----------
    variable
    string_variables

    Attributes
    ----------
    symbol
    string_variables
    """

    def __init__(self, variable: str, *string_variables: StringVariables):
        self._variable = variable
        self._string_variables = string_variables

    def __str__(self) -> str:
        """
        Return a string representation of the MCFGRuleElement.

        Returns
        -------
        str
            String representation of the MCFGRuleElement.
        """
        strvars = ', '.join(
            ''.join(str(v) for v in vtup)
            for vtup in self._string_variables
        )
        
        return f"{self._variable}({strvars})"

    def __eq__(self, other) -> bool:
        """
        Check if two MCFGRuleElements are equivalent.

        Parameters
        ----------
        other : MCFGRuleElement
            The other MCFGRuleElement to compare with.

        Returns
        -------
        bool
            True if the two MCFGRuleElements are equivalent, False otherwise.
        """
        vareq = self._variable == other._variable
        strvareq = self._string_variables == other._string_variables
        
        return vareq and strvareq
        
    def to_tuple(self) -> tuple[str, tuple[StringVariables, ...]]:
        """
        Convert the rule element to a tuple.

        Returns
        -------
        tuple
            A tuple containing the variable and its string variable tuples.
        """
        return (self._variable, self._string_variables)

    def __hash__(self) -> int:
        """
        Return a hash value for the rule element.

        Returns
        -------
        int
            Hash value of the MCFGRuleElement.
        """
        return hash(self.to_tuple())
        
    @property
    def variable(self) -> str:
        """
        Return the variable of the rule element.

        Returns
        -------
        str
            The variable of the rule element.
        """
        return self._variable

    @property
    def string_variables(self) -> tuple[StringVariables, ...]:
        """
        Return string variables used in the rule.

        Returns
        -------
        tuple of string variables
            Grouped index positions of substrings.
        """
        return self._string_variables

    @property    
    def unique_string_variables(self) -> set[int]:
        """
        Return unique string variable indices.

        Returns
        -------
        set of int
        """
        return {
            i
            for tup in self.string_variables
            for i in tup
        }


class MCFGRuleElementInstance:
    """An instantiated multiple context free grammar rule element

    Parameters
    ----------
    symbol
    string_spans

    Attributes
    ----------
    symbol
    string_spans
    """
    def __init__(self, variable: str, *string_spans: SpanIndices):
        self._variable = variable
        self._string_spans = string_spans

    def __eq__(self, other: 'MCFGRuleElementInstance') -> bool:
        """
        Check if two MCFGRuleElementInstances are equivalent.

        Parameters
        ----------
        other : MCFGRuleElementInstance
            The other MCFGRuleElementInstance to compare with.
        Returns
        -------
        bool
            True if the two MCFGRuleElementInstances are equivalent, False otherwise.
        """
        vareq = self._variable == other._variable
        strspaneq = self._string_spans == other._string_spans
        
        return vareq and strspaneq
        
    def to_tuple(self) -> tuple[str, tuple[SpanIndices, ...]]:
        """
        Convert the rule element instance to a tuple.

        Returns
        -------
        tuple
            A tuple containing the variable and its string spans.
        """
        return (self._variable, self._string_spans)

    def __hash__(self) -> int:
        """
        Return a hash value for the rule element instance.

        Returns
        -------
        int
            Hash value of the MCFGRuleElementInstance.
        """
        return hash(self.to_tuple())

    def __str__(self):
        """
        Return a string representation.
        
        Returns
        -------
        str
            String representation of the MCFGRuleElementInstance.
        """
        strspans = ', '.join(
            str(list(stup))
            for stup in self._string_spans
        )
        
        return f"{self._variable}({strspans})"

    def __repr__(self) -> str:
        """
        Return a string representation of the MCFGRuleElementInstance.

        Returns
        -------
        str
            String representation of the MCFGRuleElementInstance.
        """
        return self.__str__()
    
    @property
    def variable(self) -> str:
        """
        Return the variable of the rule element instance.

        Returns
        -------
        str
        """
        return self._variable

    @property
    def string_spans(self) -> tuple[SpanIndices, ...]:
        """
        Return string spans used in the rule element instance.

        Returns
        -------
        tuple of tuple of int
            Grouped index positions of substrings.
        """
        return self._string_spans


class MCFGRule:
    """A linear multiple context free grammar rule

    Parameters
    ----------
    left_side 
    right_side

    Attributes
    ----------
    left_side
    right_side
    """

    def __init__(self, left_side: MCFGRuleElement, *right_side: MCFGRuleElement):
        self._left_side = left_side
        self._right_side = right_side

        self._validate()

    def to_tuple(self) -> tuple[MCFGRuleElement, tuple[MCFGRuleElement, ...]]:
        """
        Convert the rule to a tuple.

        Returns
        -------
        tuple
            A tuple containing the left side and right side elements.
        """
        return (self._left_side, self._right_side)

    def __hash__(self) -> int:
        """
        Return a hash value for the rule.

        Returns
        -------
        int
            Hash value of the MCFGRule.
        """
        return hash(self.to_tuple())
    
    def __repr__(self) -> str:
        """
        Return a string representation of the rule.

        Returns
        -------
        str
            String representation of the MCFGRule.
        """
        return '<Rule: '+str(self)+'>'
        
    def __str__(self) -> str:
        """
        Return a string representation of the rule.

        Returns
        -------
        str
            String representation of the MCFGRule.
        """
        if self.is_epsilon:
            return str(self._left_side)                

        else:
            return str(self._left_side) +\
                ' -> ' +\
                ' '.join(str(el) for el in self._right_side)

    def __eq__(self, other: 'MCFGRule') -> bool:
        """
        Check if two MCFGRules are equivalent.

        Parameters
        ----------
        other : MCFGRule
            The other MCFGRule to compare with.

        Returns
        -------
        bool
            True if the two MCFGRules are equivalent, False otherwise.
        """
        left_side_equal = self._left_side == other._left_side
        right_side_equal = self._right_side == other._right_side

        return left_side_equal and right_side_equal

    def _validate(self):
        """Validate the rule"""
        vs = [
            el.unique_string_variables
            for el in self.right_side
        ]
        sharing = any(
            vs1.intersection(vs2)
            for i, vs1 in enumerate(vs)
            for j, vs2 in enumerate(vs)
            if i < j
        )

        if sharing:
            raise ValueError(
                'right side variables cannot share '
                'string variables'
            )

        if not self.is_epsilon:
            left_vars = self.left_side.unique_string_variables
            right_vars = {
                var for el in self.right_side
                for var in el.unique_string_variables
            }
            if left_vars != right_vars:
                raise ValueError(
                    'number of arguments to instantiate must '
                    'be equal to number of unique string_variables'
                )
        
    @property
    def left_side(self) -> MCFGRuleElement:
        """The left side of the rule"""
        return self._left_side

    @property
    def right_side(self) -> tuple[MCFGRuleElement, ...]:
        """The right side of the rule"""
        return self._right_side

    @property
    def is_epsilon(self) -> bool:
        """Check if the rule is an epsilon rule"""
        return len(self._right_side) == 0

    @property
    def unique_variables(self) -> set[str]:
        """Get the unique variables in the rule"""
        return {
            el.variable
            for el in [self._left_side]+list(self._right_side)
        }

    def instantiate_left_side(self, *right_side: MCFGRuleElementInstance) -> MCFGRuleElementInstance:
        """Instantiate the left side of the rule given an instantiated right side

        Parameters
        ----------
        right_side
            The instantiated right side of the rule.
        """
        
        if self.is_epsilon:
            strvars = tuple(v[0] for v in self._left_side.string_variables)
            strconst = tuple(el.variable for el in right_side)
            
            if strconst == strvars:
                return MCFGRuleElementInstance(
                    self._left_side.variable,
                    *[s for el in right_side for s in el.string_spans]
                )

        new_spans = []
        span_map = self._build_span_map(right_side)
        
        for vs in self._left_side.string_variables:
            for i in range(1,len(vs)):
                end_prev = span_map[vs[i-1]][1]
                begin_curr = span_map[vs[i]][0]

                if end_prev != begin_curr:
                    raise ValueError(
                        f"Spans {span_map[vs[i-1]]} and {span_map[vs[i]]} "
                        f"must be adjacent according to {self} but they "
                        "are not."
                    )
                
            begin_span = span_map[vs[0]][0]
            end_span = span_map[vs[-1]][1]

            new_spans.append((begin_span, end_span))

        return MCFGRuleElementInstance(
            self._left_side.variable, *new_spans
        )

    
    def _build_span_map(self, right_side: tuple[MCFGRuleElementInstance, ...]) -> SpanMap:
        """Construct a mapping from string variables to string spans"""
        
        if self._right_side_aligns(right_side):
            return {
                strvar[0]: strspan
                for elem, eleminst in zip(
                    self._right_side,
                    right_side
                )
                for strvar, strspan in zip(
                    elem.string_variables,
                    eleminst.string_spans
                )
            }
        else:
            raise ValueError(
                f"Instantiated right side {right_side} do not "
                f"align with rule's right side {self._right_side}"
            )

    def _right_side_aligns(self, right_side: tuple[MCFGRuleElementInstance, ...]) -> bool:
        """Check whether the right side aligns"""

        if len(right_side) == len(self._right_side):
            vars_match = all(
                elem.variable == eleminst.variable
                for elem, eleminst in zip(self._right_side, right_side)
            )
            strvars_match = all(
                len(elem.string_variables) == len(eleminst.string_spans)
                for elem, eleminst in zip(self._right_side, right_side)
            )

            return vars_match and strvars_match
        else:
            return False 

    @classmethod
    def from_string(cls, rule_string) -> 'MCFGRule':
        """
        Create a rule from a string representation.

        Parameters
        ----------
        rule_string : str
            The string representation of the rule.

        Returns
        -------
        MCFGRule
            The MCFGRule object created from the string.
        """
        elem_strs = re.findall(r'(\w+)\(((?:\w+,? ?)+?)\)', rule_string)

        elem_tuples = [(var, [v.strip()
                              for v in svs.split(',')])
                       for var, svs in elem_strs]

        if len(elem_tuples) == 1:
            return cls(MCFGRuleElement(elem_tuples[0][0],
                                   tuple(w for w in elem_tuples[0][1])))

        else:
            strvars = [v for _, sv in elem_tuples[1:] for v in sv]

            # no duplicate string variables
            try:
                assert len(strvars) == len(set(strvars))
            except AssertionError:
                msg = 'variables duplicated on right side of '+rule_string
                raise ValueError(msg)

            
            elem_left = MCFGRuleElement(elem_tuples[0][0],
                                    *[tuple([strvars.index(v)
                                             for v in re.findall('('+'|'.join(strvars)+')', vs)])
                                      for vs in elem_tuples[0][1]])

            elems_right = [MCFGRuleElement(var, *[(strvars.index(sv),)
                                              for sv in svs])
                           for var, svs in elem_tuples[1:]]

            return cls(elem_left, *elems_right)
        
    def string_yield(self):
        """
        Get the string yield of the rule.

        Returns
        -------
        str
            The string yield of the rule.
        """
        if self.is_epsilon:
            return self._left_side.variable
        else:
            raise ValueError(
                'string_yield is only implemented for epsilon rules'
            )


class MCFGGrammar:

    """"
    A multiple context free grammar

    Parameters
    ----------
    alphabet: set[str]
    variables: set[str]
    rules: set[MCFGRule]
    start_variable: str

    Attributes
    ----------
    alphabet: set[str]
    variables: set[str]
    rules: set[MCFGRule]
    start_variable: str
    """
    
    def __init__(self, alphabet: set[str], variables: set[str], rules: set[MCFGRule], start_variable: str):
        self._alphabet = alphabet
        self._variables = variables
        self._rules = rules
        self._start_variable = start_variable

        self._validate_variables()
        self._validate_rules()

    def _validate_variables(self):
        if self._alphabet & self._variables:
            raise ValueError('alphabet and variables must not share elements')
        
        if self._start_variable not in self._variables:
            raise ValueError('start variable must be in set of variables')

    def _validate_rules(self):
        for r in self._rules:
            r._validate()
                
    @property            
    def alphabet(self) -> set[str]:
        """
        The alphabet of the grammar.

        Returns
        -------
        set of str
            The alphabet of the grammar.
        """
        return self._alphabet

    @property    
    def variables(self) -> set[str]:
        """
        The variables of the grammar.

        Returns
        -------
        set of str
            The variables of the grammar.
        """
        return self._variables
    
    @property
    def start_variable(self) -> str:
        """
        The start variable of the grammar.

        Returns
        -------
        str
            The start variable of the grammar.
        """
        return self._start_variable

    @property
    def rules(self):
        """
        The rules of the grammar.

        Returns
        -------
        set of MCFGRule
            The rules of the grammar.
        """
        return self._rules