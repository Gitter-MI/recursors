from collections import defaultdict

from .params import *
from .interactors import Agent, clean_up, to_list, from_text
from .horn_prover import qprove
from .tools import in_stack


def ask_for_clean(agent, g, context):
    answer = agent.ask(g=g, context=context)
    agent.spill()

    xs = from_text(answer)
    res = clean_up(xs)
    return res


def just_ask(agent, g, context):
    answer = agent.ask(g=g, context=context)
    agent.spill()
    return answer


class Unfolder:
    """
    return pair of AND/OR agents
    steering LLM interactions
    """

    def __init__(self, name, prompter, lim):
        pname = prompter['name']
        and_name = f'{name}_{pname}_and_{lim}'
        or_name = f'{name}_{pname}_or_{lim}'

        self.and_ = Agent(and_name)
        self.or_ = Agent(or_name)

        self.and_.set_pattern(prompter['and_p'])
        self.or_.set_pattern(prompter['or_p'])

    def ask_and(self, goal, context):
        return ask_for_clean(self.and_, goal, context)

    def ask_or(self, goal, context):
        return ask_for_clean(self.or_, goal, context)

    def persist(self):
        self.and_.persist()
        self.or_.persist()

    def resume(self):
        self.and_.resume()
        self.or_.resume()

    def costs(self):
        return {'and': self.and_.dollar_cost(), 'or': self.or_.dollar_cost()}


class AndOrExplorer:
    """
    Simple Prolog-inspired recursive descent steering LLMs to
    expand conjunctively or disjunctively while
    staying focussed via a controlled history of
    explored goals while unfolding new ones.
    Besides returning a stream of answers we
    also generate a Prolog program to be further
    explored with logic programming tools.
    """

    def __init__(self, initiator=None, prompter=None, lim=1, strict=False):
        assert initiator is not None
        assert prompter is not None
        self.initiator = " ".join(initiator.replace('.', ' ').strip().split())
        self.name = self.initiator.lower().strip().replace(' ', '_')
        self.prompter = prompter
        self.pname = prompter['name']
        self.lim = lim
        self.strict = strict
        self.unf = Unfolder(self.name, prompter, lim)
        self.clauses = defaultdict(list)
        self.facts = dict()
        self.OUT = None
        PARAMS()(self)

    def new_clause(self, g, trace):
        """
        invents a set of new clauses
        given a goal and the trace of
        the past steps leading to g
        """
        or_context = to_context(trace, self.initiator)
        hs = self.unf.ask_or(g, or_context)
        and_context = to_context((g, trace), self.initiator)
        for h in hs:
            if h == g or in_stack(h, trace): continue
            bs = self.unf.ask_and(h, and_context)  # invent their bodies
            if h in bs: continue
            yield h, bs

    def costs(self):
        return self.unf.costs()

    # end overrides

    def solve(self):

        self.resume()

        def step(g, gs, d):
            if g in gs: return
            self.persist()
            if d >= self.lim:
                if self.appraise(g, gs):
                    self.facts[g] = True
                    yield g, gs
            else:
                hs = []
                for h, bs in self.new_clause(g, gs):
                    if not self.appraise(h, (g, gs)): continue
                    hs.append(h)
                    trace = h, (g, gs)
                    self.clauses[g].append([h])
                    self.clauses[h].append(bs)
                    for b in bs:
                        yield from step(b, trace, d + 1)
                if self.strict and len(hs) > 1: self.clauses['false'].append(hs)

        for gs in step(self.initiator, (), 0):
            yield list(reversed(to_list(gs)))

        self.persist()

        for fact in self.facts: self.clauses[fact].append([])
        css = [(h, bs) for (h, bss) in self.clauses.items() for bs in bss]
        self.logic_model = qprove(css, goal=self.initiator)
        self.trim_clauses()
        self.save_results()

    def save_results(self):
        pro_name = f'{self.OUT}{self.name}_{self.pname}_{self.lim}'
        mo_name = pro_name + "_model"

        to_prolog(self.clauses, pro_name)

        if self.logic_model is None:
            self.logic_model = []
            tprint('\nNO MODEL ENTAILING:', self.initiator)
        else:
            tprint('\nMODEL:', len(self.logic_model), 'facts', '\n')
            for fact in self.logic_model: tprint(fact)
        save_model(self.initiator, self.logic_model, mo_name)

    def run(self):
        yield 'PROMPTER', self.prompter
        for r in self.solve():
            yield 'TRACE', r
        yield 'CLAUSES', dict(self.clauses)
        yield 'MODEL', self.logic_model
        yield 'COSTS', self.costs()

    # -------- begin overrides -------------

    def resume(self):
        self.unf.resume()

    def persist(self):
        self.unf.persist()

    def appraise(self, g, _trace):
        """
        to be overriden by refiners
        """
        return True

    def trim_clauses(self):
        """
        to be overriden : only atoms in the model
        will be kept - no action here as they all are
        """
        pass
        clauses = defaultdict(list)
        if self.logic_model is not None:
            model = set(self.logic_model)
            clauses = defaultdict(list)
            for (h, bss) in self.clauses.items():
                for bs in bss:
                    ok = all(b in model for b in bs)
                    if ok: clauses[h].append(bs)
        self.clauses = clauses


def run_explorer(goal=None, prompter=None, lim=None):
    assert None not in (prompter, goal, lim)
    r = AndOrExplorer(initiator=goal, prompter=prompter, lim=lim)
    seen = dict()
    for a in r.solve():
        print('\nTRACE:')
        # a=sorted(a)
        for x in a: print(x)
        print()
        a = tuple(a)
        if a in seen:
            print('--------------SEEN:', a)
        else:
            seen[a] = True

        if len(a) != len(set(a)):
            print('--------------REPEATED:', a)
    r.unf.persist()
    c1 = r.unf.or_.dollar_cost()
    c2 = r.unf.and_.dollar_cost()
    print('COSTS in $:', {'and': c1, 'or': c2, 'total': c1 + c2})
    return True


def quote(x):
    return "'" + x + "'"


def show_clauses(clauses):
    buf = []

    def p(x):
        buf.append(x)

    for h, bss in clauses.items():
        if bss == []:
            p(f"'{h}'.\n")
            break

        for i, bs in enumerate(bss):
            if i == 0:
                end = ":-" if bs else "."
                p(f"'{h}'{end}\n")

            for j, b in enumerate(bs):
                b = f"'{b}'"
                if j + 1 == len(bs):
                    #print('!!!!', b)
                    b = b + ("." if i + 1 == len(bss) else ";")
                else:
                    b = b + ","
                p("    " + b + "\n")

    return "".join(buf)


def show_model(facts):
    buf = []
    for fact in facts:
        buf.append(f"'{fact}'.")
    return "\n".join(buf)


def save_model(goal, facts, fname, suf='.pro'):
    path = fname + suf
    ensure_path(path)
    with open(path, 'w') as f:
        print(f'% MODEL: {len(facts)} facts', file=f)
        for fact in facts:
            line = quote(fact) + "."
            if fact == goal: line = line + "%" + (10 * " ") + "<==== initiator !"
            print(line, file=f)


def to_prolog(clauses, fname, neck=":-", suf='.pro'):
    suf = '.nat' if neck == ":" else suf

    path = fname + suf
    ensure_path(path)
    with open(path, 'w') as f:
        print('% CLAUSES:', file=f)
        for h, bss in clauses.items():
            for bs in bss:
                if bs == [] or bs == ['fail']: continue
                body = ',\n    '.join(map(quote, bs)) + "."
                print(quote(h), neck + '\n    ' + body, file=f)
        for h, bss in clauses.items():
            if bss == []:
                print(quote(h) + ".", file=f)
            for bs in bss:
                if bs == []:
                    print(quote(h) + ".", file=f)
                elif bs == ['fail']:
                    print(quote(h), neck + ' ' + 'fail.', file=f)


def to_context(trace, topgoal):
    if not trace: return topgoal
    context = ".\n".join(reversed(to_list(trace))) + ".\n"
    # print('!!!! CONTEXT:',context, '!!!!\n')
    return context
