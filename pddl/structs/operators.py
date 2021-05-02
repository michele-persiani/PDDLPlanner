from pddl.structs.predicate import Term
from pddl.structs.pddl_factory import PDDLFactory
from os import linesep
from copy import deepcopy



class Operator(object):
    """
    Base class for operators
    """

    def __init__(self, name, params, precond, effects):
        """
        :param name: name of the operator. String
        :param params: parameters. List of Term
        :param precond: operator preconditions. List of Literals
        :param effects: operator effects. List of literals.
        """
        self.name    = str(name)
        self.params  = tuple(p if isinstance(p, Term) else PDDLFactory.TERM(value=str(p)) for p in params)
        self.precond = tuple(precond)
        self.effects = tuple(effects)


    def param_values(self):
        return tuple(map(lambda p:p.value, self.params))


    def param_types(self):
        return tuple(map(lambda p:p.type, self.params))


    def as_literal(self):
        args = self.param_values()
        return PDDLFactory.LITERAL(self.name, args)


    def shallowcopy(self):
        raise NotImplementedError


    def deepcopy(self):
        return deepcopy(self)


    def __str__(self):
        raise NotImplementedError


    def __repr__(self):
        return str(self.as_literal())


    def __eq__(self, other):
        return str(other) == str(self)


    def __hash__(self):
        return str(self).__hash__()


class OperatorToken(Operator):
    """
    Operator token that contains name and parameters
    """

    def __init__(self, name, params):
        super(OperatorToken, self).__init__(name, params, [], [])


    def shallowcopy(self):
        return OperatorToken(self.name, list(self.params))

    def __str__(self):
        return str(self.as_literal())


class StripsOperator(Operator):
    """
    STRIPS operator with name, parameters, preconditions and effects
    """

    def __init__(self, name, params, precond, effects):
        super(StripsOperator, self).__init__(name, params, precond, effects)

    @property
    def positive_effects(self):
        return tuple(filter(lambda x: x.is_positive, self.effects))

    @property
    def negative_effects(self):
        """
        Returns the negative effects in positive form.
        :return:  List of literals
        """
        neg_eff = filter(lambda x: x.is_negative, self.effects)
        neg_eff = tuple(map(lambda l: PDDLFactory.LITERAL(l.name, l.args, positive=True), neg_eff))
        return neg_eff


    def get_grounded(self, values):
        """
        Returns a grounded version copy of the operator
        :param values: The values to substitute the variables with. List of strings
        :return:
        """
        values = tuple(map(str, values))
        assert len(values) == len(self.params), 'Number of variables must be the same of parameters'

        vd = {self.params[i].value : v for i, v in enumerate(values)}

        op = self.deepcopy()
        for p in op.params:
            p.value = vd[p.value] if p.value in vd else p.value
        for p in op.precond:
            p.substitute_args(vd)
        for p in op.effects:
            p.substitute_args(vd)
        return op


    def shallowcopy(self):

        return StripsOperator(self.name,
                              list(self.params),
                              list(self.precond),
                              list(self.effects)
                              )


    def pddl_str(self):
        effects = self.effects
        param_str   = '({})'.format(' '.join(map(str, self.params)))
        precond_str = '(and {})'.format(' '.join(map(str, self.precond))) if len(self.precond) > 0 else '(and )'
        effects_str = '(and {})'.format(' '.join(map(str, effects))) if len(effects) > 0 else '(and )'
        action_str = '(:action {}\n' \
                     ':parameters {}\n' \
                     ':precondition {}\n' \
                     ':effect {}\n' \
                     ')'.format(self.name,
                                param_str,
                                precond_str,
                                effects_str
                                )

        action_str.replace('\n', linesep)
        return action_str


    def __str__(self):
        return self.pddl_str()