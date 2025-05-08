from collections import deque, defaultdict
from agenda_based_mcfg_wchoi18.grammar import MCFGRuleElementInstance, MCFGGrammar, MCFGRule
from agenda_based_mcfg_wchoi18.tree import Tree
from typing import Tuple

StringVariables = Tuple[int, ...]
SpanIndices = Tuple[int, ...]
SpanMap = dict[int, SpanIndices]

class MCFGChartEntry:
    """
    Represents a single entry in the MCFG chart.
    
    Parameters
    ----------
    instance : MCFGRuleElementInstance
    rule : MCFGRule, optional
    backpointers : list[MCFGChartEntry], optional
    
    Attributes
    ----------
    instance : MCFGRuleElementInstance
    rule : MCFGRule
    backpointers : list[MCFGChartEntry]
    """
    def __init__(self, instance, rule=None, backpointers=None):
        self.instance = instance
        self.rule = rule
        self.backpointers = backpointers or []

    def __hash__(self) -> int:
        """
        Return a hash value of the instance.

        Returns
        -------
        int
            The hash value of the instance.
        """
        return hash(self.instance)

    def __eq__(self, other) -> bool:
        """
        Check if two entries are equal based on their instance.
        
        Parameters
        ----------
        other : MCFGChartEntry
            The other entry to compare with.

        Returns
        -------
        bool
            True if the entries are equal, False otherwise.
        """
        return self.instance == other.instance

    @property
    def symbol(self) -> str:
        """
        Return the symbol of the entry.

        Returns
        -------
        str
            The symbol of the entry.
        """
        return self.instance.variable

    @property
    def spans(self) -> SpanIndices:
        """
        Return the spans of the entry.
        
        Returns
        -------
        SpanIndices
            The spans of the entry.
        """
        return self.instance.string_spans

    def to_tree(self) -> Tree:
        """
        Convert the entry to a tree representation.
        
        Returns
        -------
        Tree
            A tree representation of the entry.
        """
        children = [d.to_tree() for d in self.backpointers]
        return Tree(self.symbol, children)


class MCFGChart:
    """
    Represents the MCFG chart, which stores entries and allows for retrieval.

    Attributes
    ----------
    entries : dict, optional
        A dictionary of entries, default is an empty dictionary.
    """
    def __init__(self):
        self._entries = defaultdict(set)

    def _key(self, entry: MCFGChartEntry) -> Tuple[str, SpanIndices]:
        return (entry.symbol, entry.spans)

    def add(self, entry: MCFGChartEntry):
        """
        Add an entry to the chart.
        """
        key = self._key(entry)
        self._entries[key].add(entry)

    def get_by_symbol(self, symbol: str) -> list[MCFGChartEntry]:
        """
        Get entries by symbol.
        
        Parameters
        ----------
        symbol : str
            The symbol to search for in the chart.

        Returns
        -------
        list[MCFGChartEntry]
            A list of entries that match the given symbol.
        """
        return [entry for (sym, _), entries in self._entries.items() if sym == symbol for entry in entries]
    
    @property
    def parses(self) -> set[Tree]:
        """
        Get all parses in the chart.

        Returns
        -------
        set[Tree]
            A set of trees representing the parses in the chart.
        """
        return {
            entry.to_tree()
            for (sym, _), entries in self._entries.items()
            if sym == "S"
            for entry in entries
        }


class AgendaBasedMCFGParser:
    """
    Implements the agenda-based MCFG parser.

    Parameters
    ----------
    grammar : MCFGGrammar

    Attributes
    ----------
    grammar : MCFGGrammar
    chart : MCFGChart
    agenda : deque
    """

    def __init__(self, grammar: MCFGGrammar):
        self.grammar = grammar
        self.chart = MCFGChart()
        self.agenda = deque()

    def parse(self, tokens: list[str]) -> set[Tree]:
        """
        Parse the input tokens using the MCFG grammar.

        Parameters
        ----------
        tokens : list[str]
            The input tokens to be parsed.

        Returns
        -------
        set[Tree]
            A set of trees representing the parses of the input tokens.
        """

        self.tokens = tokens
        self._initialize_agenda()

        while self.agenda:
            trigger = self.agenda.popleft()
            self.chart.add(trigger)
            for consequence in self._infer(trigger):
                self.agenda.append(consequence)

        return self.chart.parses

    def _initialize_agenda(self):

        for i, token in enumerate(self.tokens):
            for rule in self.grammar.rules:
                if rule.is_epsilon:
                    terminal = rule.left_side.string_variables[0][0]
                    if terminal == token:
                        instance = MCFGRuleElementInstance(terminal, (i, i + 1))
                        lhs_instance = rule.instantiate_left_side(instance)
                        entry = MCFGChartEntry(lhs_instance, rule, [MCFGChartEntry(instance)])
                        self.agenda.append(entry)
                        self.chart.add(entry)

    def _infer(self, trigger: MCFGChartEntry):
        new_entries = []

        for rule in self.grammar.rules:
            if len(rule.right_side) == 2:
                B, C = rule.right_side

                if trigger.symbol == B.variable:
                    for c_entry in self.chart.get_by_symbol(C.variable):
                        try:
                            inst = rule.instantiate_left_side(trigger.instance, c_entry.instance)
                            new_entries.append(MCFGChartEntry(inst, rule, [trigger, c_entry]))
                        except ValueError:
                            continue

                if trigger.symbol == C.variable:
                    for b_entry in self.chart.get_by_symbol(B.variable):
                        try:
                            inst = rule.instantiate_left_side(b_entry.instance, trigger.instance)
                            new_entries.append(MCFGChartEntry(inst, rule, [b_entry, trigger]))
                        except ValueError:
                            continue

        return new_entries
