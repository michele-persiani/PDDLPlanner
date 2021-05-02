from pddl.structs.pddl_factory import PDDLFactory
from pddl.structs.predicate import Literal, Term, Predicate
from os import linesep
from collections import defaultdict
from itertools import product
from copy import deepcopy


class PDDLProblem(object):

    planner = None

    def __init__(self, name, domain, objects, init, goal, metric=None, minimize=True):
        """

        :param name: Name of the problem. String
        :param domain: PDDLDomain object. String
        :param objects: Objects in the problem instance. Either a dictionary {type: [Sobject,]} or a list [Tobject].
        Sobject is a string, Tobject is a Term object
        :param init: Tuple of ground literals
        :param goal: Tuple of ground literals
        :param metric: Name of the metric to minimize or maximize
        :param minimize: Wehther the metric is to be minimized
        """
        self.name = str(name)
        self.domain = domain
        self._objects = tuple(objects)

        self._init   = tuple(init)
        self._goal   = tuple(goal)
        self.minimize = bool(minimize)
        self.metric = str(metric) if metric else None

    @staticmethod
    def set_planner(planner):
        PDDLProblem.planner = planner

    @property
    def init(self):
        return self._init

    @init.setter
    def init(self, v):
        self._init = tuple(l if isinstance(l, Literal) else PDDLFactory.PARSE_LITERAL(str(l)) for l in v)

    @property
    def goal(self):
        return self._goal

    @goal.setter
    def goal(self, v):
        self._goal = tuple(l if isinstance(l, Literal) else PDDLFactory.PARSE_LITERAL(str(l)) for l in v)

    @property
    def objects(self):
        return self._objects

    @objects.setter
    def objects(self, v):
        self._objects = tuple(l if isinstance(l, Term) else PDDLFactory.PARSE_TERM(str(l)) for l in v)

    @property
    def grounded_operators(self):
        found_operators = []
        d = self.get_objects_dictionary(type_hierarchy=True)
        for op in self.domain.operators:
            types = tuple(map(lambda x: str(x.type) if x.type else 'object', op.params))
            objects = tuple(d[t] for t in types)
            values = product(*objects)
            for v in values:
                found_operators += [op.get_grounded(v),]
        return found_operators

    @property
    def grounded_predicates(self):
        """
        # TODO add numerical predicates
        :return: The set of predicates grounded using the problem's objects
        """
        found_predicates = set()
        d = self.get_objects_dictionary(type_hierarchy=True)
        for pr in self.domain.predicates:
            types = tuple(map(lambda x: str(x) if x else 'object', pr.types))
            objects = tuple(d[t] for t in types)
            values = product(*objects)
            for v in values:
                found_predicates.add(pr.get_grounded(v))

        eq_pr = Predicate('=', arity=2, types=None)
        for o0, o1 in product(d['object'], d['object']):
            found_predicates.add(eq_pr.get_grounded([o0, o1]))

        return found_predicates

    @property
    def done(self):
        """
        Get whether the goal state is in init
        :return: Boolean
        """
        sm = lambda y, pos: set(map(str, filter(lambda y: y.is_positive == pos, y)))
        positive_goal = sm(self.goal, True)
        negative_goal = sm(self.goal, False)

        pos_x = len(sm(self.init, True).intersection(positive_goal)) == len(positive_goal)
        neg_x = len(sm(self.init, True).intersection(negative_goal)) == 0

        return pos_x and neg_x


    def find_type(self, object_name):
        """
        Finds the type for the object
        :param object_name: object name. String
        :return: object type. String
        """
        object_name = str(object_name)
        for obj in self._objects:
            if obj.value == object_name:
                return str(obj.type)
        return None


    def deepcopy(self):
        return deepcopy(self)


    def shallowcopy(self):
        prob = PDDLProblem(self.name,
                           self.domain.shallowcopy(),
                           tuple(self.objects),
                           tuple(self.init),
                           tuple(self.goal),
                           self.metric
                           )
        return prob


    def get_objects_dictionary(self, type_hierarchy=False, with_constants=True):
        """
        Returns a dictionary, organized by type, containing all the problem's objects
        :param type_hierarchy: add objects over the type hierarchy as well. Superclasses will have all of the subclasses objects
        :param with_constants: comprehend also the constants from the domain in the result
        :return:
        """
        # Compute shallow object dictionary
        d = defaultdict(lambda : [])
        for obj in self.objects:
            type = str(obj.type) if obj.is_typed else 'object'
            value = str(obj.value)
            d[type].append(value)

        constants = self.domain.get_constants_dictionary(type_hierarchy) if with_constants else dict()
        for k, v in constants.items():
            d[k] += v

        if type_hierarchy:
            # Add inferred subtypes
            types_dict = self.domain.get_types_dictionary()
            for type, subtypes in types_dict.items():
                for subtype in subtypes:
                    d[type] += d[subtype]
        return d


    def apply_operator(self, operator, force=False):
        """
        See apply_plan().
        :param operator:
        :param force:
        :return:
        """
        return self.apply_plan([operator, ], force)


    def apply_plan(self, plan, force=False):
        """
        Applies the plan to the problem and returns another problem with the updated init.
        the force argument determine whether to check for the operators preconditions
        :param plan: A list of operators
        :param force: If true the operators' preconditions will be added whenever missing. If false, whenever a
        precondition is missing an exception will be raised
        :return:
        """
        state = set(self.init)
        for x in plan:
            op = self.domain.find_operator(x.name)
            op_gr = op.get_grounded(list(map(lambda x: x.value, x.params)))

            pos_precond = set(filter(lambda l: l.is_positive, op_gr.precond))
            neg_precond = set(map(lambda l: l.as_positive, filter(lambda l: l.is_negative, op_gr.precond)))

            if force:
                state = state.union(pos_precond)
                state = state.difference(neg_precond)
            else:
                assert len(state.intersection(pos_precond)) == len(pos_precond)
                assert len(state.intersection(neg_precond)) == 0

            state = state.difference(op_gr.negative_effects)
            state = state.union(op_gr.positive_effects)

        prob = self.shallowcopy()
        prob.init = state
        return prob


    def make_plan(self, planner=None, params={}):
        """
        Make a plan using the PDDLProblem.planner planner.
        :param planner: PDDL planner to use, or None to use the default PDDLProblem.planner
        :param params: optional dictionary of parameters. Ignored for hte moment
        :return: A tuple (plan, metrics, )
        """
        planner = planner if planner is not None else PDDLProblem.planner
        assert planner is not None, 'You must set a PDDLProblem.planner before planning. Or pass the planner to use as an argument'
        plan, metrics = planner.make_plan(self.domain, self)
        return plan, metrics


    def without_action_costs(self, metric_name='total-cost'):
        """
        Creates a copy problem instance with action costs predicates being removed.
        Removes :action-costs from the domain requirements, and any predicates containing 'metric_name' from the
        operators, predicates, init or goal, such as (increase (total-cost) 1). Removes the problem's minimized metric
        :param metric_name: plan cost metric
        :return: The new problem instance without action costs related predicates
        """
        filter_literals = lambda predicates, s: tuple(filter(lambda p: s not in str(p), predicates))

        copy = self.shallowcopy()
        domain = self.domain.shallowcopy()

        domain.requirements = filter_literals(domain.requirements, ':action-costs')

        for op in domain.operators:
            op.effects = filter_literals(op.effects, metric_name)

        domain.functions = filter_literals(domain.functions, metric_name)

        copy.init = filter_literals(self.init, metric_name)
        copy.goal = filter_literals(self.goal, metric_name)

        copy.domain = domain
        copy.metric = None
        return copy


    def pddl_str(self):
        d = self.get_objects_dictionary(type_hierarchy=False, with_constants=False)

        objs = '\n'.join([' '.join([str(o) for o in d[t]]) + ' - {}'.format(t) for t in d.keys() if len(d[t]) > 0])

        if len(self.goal) > 0:
            goal_str = '(and {})'.format( ' '.join([str(p) for p in self.goal]))
        else:
            goal_str = ''

        if self.metric:
            metric_str = '(:metric {} {})'.format('minimize' if self.minimize else 'maximize', self.metric)
        else:
            metric_str = ''

        o = '(define (problem {})\n' \
            '(:domain {})\n' \
            '(:objects \n{}\n)\n\n' \
            '(:init \n{})\n\n' \
            '(:goal \n{})\n\n' \
            '{}\n\n' \
            ')'.format(self.name,
                       self.domain.name,
                       objs,
                       '\n'.join(map(str, self.init)),
                       goal_str,
                       metric_str
                       )

        o.replace('\n', linesep)
        return o


    def __str__(self):
        return self.pddl_str()


    def __repr__(self):
        return '(problem {} {})'.format(self.domain.name, self.name)


    def __eq__(self, other):
        return str(other) == str(self)


    def __hash__(self):
        return str(self).__hash__()
