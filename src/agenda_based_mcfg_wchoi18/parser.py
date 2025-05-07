### parser/agenda_parser.py

from collections import deque, defaultdict
from agenda_based_mcfg_wchoi18.grammar import MCFGRuleElementInstance, MCFGGrammar, MCFGRule
from agenda_based_mcfg_wchoi18.tree import Tree
from typing import Tuple

StringVariables = Tuple[int, ...]
SpanIndices = Tuple[int, ...]
SpanMap = dict[int, SpanIndices]

class MCFGChartEntry:
    def __init__(self, instance, rule=None, backpointers=None):
        self.instance = instance
        self.rule = rule
        self.backpointers = backpointers or []

    def __hash__(self):
        return hash(self.instance)

    def __eq__(self, other):
        return self.instance == other.instance

    @property
    def symbol(self):
        return self.instance.variable

    @property
    def spans(self):
        return self.instance.string_spans

    def to_tree(self) -> Tree:
        children = [d.to_tree() for d in self.backpointers]
        return Tree(self.symbol, children)


class MCFGChart:
    def __init__(self):
        self._entries = defaultdict(set)

    def _key(self, entry: MCFGChartEntry):
        return (entry.symbol, entry.spans)

    def add(self, entry: MCFGChartEntry):
        key = self._key(entry)
        self._entries[key].add(entry)

    def get_by_symbol(self, symbol: str):
        return [entry for (sym, _), entries in self._entries.items() if sym == symbol for entry in entries]
    
    @property
    def parses(self):
        return {
            entry.to_tree()
            for (sym, _), entries in self._entries.items()
            if sym == "S"
            for entry in entries
        }


class AgendaBasedMCFGParser:
    def __init__(self, grammar: MCFGGrammar):
        self.grammar = grammar
        self.chart = MCFGChart()
        self.agenda = deque()

    def parse(self, tokens: list[str]):
        self.tokens = tokens
        self._initialize_agenda()

        while self.agenda:
            trigger = self.agenda.popleft()
            self.chart.add(trigger)
            for consequence in self._infer(trigger):
                self.agenda.append(consequence)

        return self.chart.parses

    def _initialize_agenda(self):
        # Step 1: Add all terminal epsilon rules matching tokens as axioms
        for i, token in enumerate(self.tokens):
            # print(f"Processing token: {token} at position {i}")
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
