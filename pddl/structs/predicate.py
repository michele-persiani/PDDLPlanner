


class Predicate(object):

    variables = '?a ?b ?c ?d ?e ?f ?g ?h ?i ?l ?m ?n ?o ?p ?q ?r ?s ?t ?u ?v ?z'.split(' ')

    def __init__(self, name, arity, types=None):
        """

        :param name: name of the predicate
        :param arity: number of arguments of the predicate
        :param types: list of string of same length of arity
        """
        self.name = name
        self.arity = arity
        if types is not None:
            assert len(types) == self.arity
            self.types = list(map(lambda x: str(x) if x is not None else x, types))
        else:
            self.types = ['object' for _ in range(self.arity)]
        assert self.arity <= len(Predicate.variables)


    def get_grounded(self, values, positive=True):
        assert len(values) == self.arity
        args = [Term(values[i], t) for i, t in enumerate(self.types)]
        lit = Literal(self, args, positive)
        return lit


    def pddl_str(self):
        var_types = zip(Predicate.variables[:len(self.types)], self.types)
        vars = list(map(lambda x: '{} - {}'.format(x[0], x[1]), var_types))
        if self.arity == 0:
            return '({})'.format(self.name)
        return '({} {})'.format(self.name, ' '.join(vars))


    def __repr__(self):
        return self.pddl_str()


    def __str__(self):
        return self.pddl_str()


    def __eq__(self, other):
        return isinstance(other, type(self)) and (hash(other) == hash(self))

    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return str(self).__hash__()


class Literal:


    def __init__(self, predicate, args, positive):
        """

        :param predicate: A Predicate object
        :param args: List of arguments. Must be consistent with the provided predicate.
        :param positive: Whther the literal is positive
        """
        self.predicate = predicate
        self.args = tuple(args)
        self._positive = positive
        self.assert_consistency()

    def assert_consistency(self):
        assert self.predicate.arity >= 0
        assert len(self.args) == self.predicate.arity
        for i, arg in enumerate(self._args):
            assert isinstance(arg, Term) or isinstance(arg, Literal)
            if isinstance(arg, Term) and arg.is_typed:
                assert arg.type == self.predicate.types[i]
            if isinstance(arg, Literal):
                arg.assert_consistency()

    @property
    def name(self):
        return self.predicate.name

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, v):
        self._args = tuple(v)
        self.assert_consistency()

    @property
    def is_positive(self):
        return self._positive

    @is_positive.setter
    def is_positive(self, v):
        self._positive = bool(v)

    @property
    def is_negative(self):
        return not self.is_positive

    @is_negative.setter
    def is_negative(self, v):
        self._positive = not bool(v)

    @property
    def as_positive(self):
        return Literal(self.predicate, self._args, True)

    @property
    def as_negative(self):
        return Literal(self.predicate, self._args, False)

    @property
    def is_grounded(self):
        terms = filter(lambda x: isinstance(x, Term), self._args)
        lit = filter(lambda x: isinstance(x, Literal), self._args)

        return all([t.is_constant for t in terms] + [l.is_grounded for l in lit])


    def shallowcopy(self):
        return Literal(self.predicate, self.args, self.is_positive)


    def substitute_args(self, substitutions):
        """
        Substitute terms values with those specified in substitutions
        :param substitutions: A {old_value : new_value} dictionary.
        :return: 
        """
        terms = filter(lambda x: isinstance(x, Term), self._args)
        lit = filter(lambda x: isinstance(x, Literal), self._args)
        for p in terms:
            if p.value in substitutions:
                p.value = substitutions[p.value]
        for l in lit:
            l.substitute_args(substitutions)


    def pddl_str(self):
        s0 = '{}' if self.is_positive else '(not {})'
        if self.predicate.arity == 0:
            s1 = '({})'.format(self.predicate.name)
        else:
            str_x = lambda x: str(x.value if isinstance(x, Term) else x)
            s1 = '({} {})'.format(self.predicate.name, ' '.join(map(str_x, self.args)))
        return s0.format(s1)


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        return self.pddl_str()


    def __eq__(self, other):
        return isinstance(other, type(self)) and (hash(other) == hash(self))

    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return str(self).__hash__()


class Term(object):

    def __init__(self, value, type=None):
        """
        :param value: a string. If value begins with '?' the term will be interpreted as being a variable, a constant otherwise
        :param type: optional type. When specified terms will print as 'value - type', only with 'value' otherwise.
        """
        self.type  = type
        self.value = value


    @property
    def is_variable(self):
        return str(self.value).startswith('?')

    @property
    def is_constant(self):
        return not self.is_variable

    @property
    def is_typed(self):
        return self.type is not None


    @staticmethod
    def variable(name, type=None):
        return Term(value=name, type=type)

    @staticmethod
    def constant(value, type=None):
        return Term(value=value, type=type)

    def pddl_str(self):
        if self.is_typed:
            return '{0} - {1}'.format(self.value, self.type)
        else:
            return '{0}'.format(self.value)

    def __str__(self):
        return self.pddl_str()

    def __repr__(self):
        return self.pddl_str()


    def __eq__(self, other):
        return isinstance(other, type(self)) and (hash(other) == hash(self))

    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return str(self).__hash__()