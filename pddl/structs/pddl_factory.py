
class PDDLFactory:
    """
    Main entry point for creating PDDL objects such as predicates, literals, operators, domains and problems
    """

    @staticmethod
    def PARSE(obj, cls=None, is_filename=False):
        """
        Parse a string
        :param obj: object for which str() must describe a PDDL object of type cls
        :param cls: the class of the expected pddl object. Or None if no class checks should be perofrmed
        :param is_filename: whether obj is a filepath
        :return:
        """
        from pddl.parser import PDDLParser
        obj = str(obj)
        parsed = PDDLParser.parse_file(obj) if is_filename else PDDLParser.parse_string(obj)
        if cls is not None:
            msg = 'A object of class {} was expected as the parser\'s result but got one of class {}'.format(str(cls), str(parsed.__class__))
            assert isinstance(parsed, cls), msg
        return parsed

    @staticmethod
    def PARSE_DOMAIN(obj, is_filename=False):
        from pddl.structs.domain import PDDLDomain
        return PDDLFactory.PARSE(obj, PDDLDomain, is_filename)

    @staticmethod
    def PARSE_PROBLEM(domain, obj, is_filename=False):
        from pddl.structs.domain import PDDLDomain
        from pddl.structs.problem import PDDLProblem
        assert isinstance(domain, PDDLDomain), 'domain must be a PDDLDomain'
        obj = str(obj)
        problem = PDDLFactory.PARSE(obj, PDDLProblem, is_filename)
        problem.domain = domain
        return problem

    @staticmethod
    def PARSE_LITERAL(obj, is_filename=False):
        from pddl.structs.predicate import Literal
        if isinstance(obj, Literal):
            return obj
        return PDDLFactory.PARSE(obj, Literal, is_filename)

    @staticmethod
    def PARSE_TERM(obj, is_filename=False):
        from pddl.structs.predicate import Term
        if isinstance(obj, Term):
            return obj
        return PDDLFactory.PARSE(obj, Term, is_filename)

    @staticmethod
    def PARSE_STRIPS_OP(obj, is_filename=False):
        from pddl.structs.operators import StripsOperator
        if isinstance(obj, StripsOperator):
            return obj
        return PDDLFactory.PARSE(obj, StripsOperator, is_filename)

    @staticmethod
    def DOMAIN(name, requirements=(), types=(), constants=(), functions=(), predicates=(), operators=()):
        from pddl.structs.domain import PDDLDomain
        return PDDLDomain(name, requirements, types, constants, functions, predicates, operators)

    @staticmethod
    def PROBLEM(name, domain, objects=(), init=(), goal=(), metric=None, minimize=True):
        from pddl.structs.problem import PDDLProblem
        from pddl.structs.domain import PDDLDomain
        if not isinstance(domain, PDDLDomain):
            domain = PDDLFactory.PARSE_DOMAIN(domain)
        return PDDLProblem(name, domain, objects, init, goal, metric, minimize)


    @staticmethod
    def STRIPS_OP(name, parameters=(), precond=(), effects=()):
        """
        Creates a StripsOperator object. The passed parameters are unchec
        :param name: String. Name (unique in the domain) of the operator
        :param parameters: List of objects.  str() must return a valid Term description
        :param precond: List of objects.   str() must return a valid Term description
        :param effects: List of objects.  str() must return a valid Term description
        :return: a StripsOperator object
        """
        from pddl.structs.operators import StripsOperator
        return StripsOperator(name, parameters, precond, effects)


    @staticmethod
    def PREDICATE(name, arity=None, types=None):
        """
        Creates a (NAME types) predicate. Literals wraps predicates and must be consistent with them
        :param name: name of the predicate
        :param arity: number of parameters of the predicate. Will be inferred if types is provided
        :param types: list of types of the predicate
        :return:
        """
        from pddl.structs.predicate import Predicate, Term
        if arity is None and types is None:
            arity = 0
        if types is not None:
            types = [str(t.type) if isinstance(t, Term) else t for t in types]
            arity = len(types)
        pred = Predicate(name=name, arity=arity, types=types)
        return pred

    @staticmethod
    def LITERAL(name, args=(), positive=True):
        """
        Creates a (NAME args) literal with its associated wrapped predicate.
        :param name: name of the literal
        :param args: The arguments of the literal. List of Term objects or strings. If strings are given the associated
        Term objects will habe 'object' as type
        :param positive: whether the literal is true or false.
        :return: A Literal object
        """
        from pddl.structs.predicate import Literal, Term
        args = list(iter(args))
        types = list(map(lambda t: str(t.type) if isinstance(t, Term) else None , args))
        args = list(map(lambda a: a if (isinstance(a, Term) or isinstance(a, Literal)) else Term(value=str(a)), args))
        pred = PDDLFactory.PREDICATE(name, types=types)
        literal = Literal(pred, args, positive)
        literal.assert_consistency()
        return literal

    @staticmethod
    def EQUAL(arg0, arg1):
        """
        Creates an (= arg0 arg1) literal
        :param args0: A single or a list of of terms or literals
        :param args1: A single or a list of terms or literals
        """
        if isinstance(arg0, list) or isinstance(arg0, tuple):
            arg0 = PDDLFactory.AND(arg0)
        if isinstance(arg1, list) or isinstance(arg1, tuple):
            arg1 = PDDLFactory.AND(arg1)
        return PDDLFactory.LITERAL('=', [arg0, arg1])

    @staticmethod
    def AND(args):
        """
        Creates an (AND args) literal.
        :param args: List of terms or literals
        """
        return PDDLFactory.LITERAL('and', args)

    @staticmethod
    def OR(args):
        """
        Creates an (OR args) literal
        :param args: List of terms or literals
        """
        return PDDLFactory.LITERAL('or', args)

    @staticmethod
    def WHEN(arg0, arg1):
        """
        Creates a (WHEN arg0 arg1) literal.
        :param args0: A single or a list of of terms or literals
        :param args1: A single or a list of terms or literals
        """
        if isinstance(arg0, list) or isinstance(arg0, tuple):
            arg0 = PDDLFactory.AND(arg0)
        if isinstance(arg1, list) or isinstance(arg1, tuple):
            arg1 = PDDLFactory.AND(arg1)

        return PDDLFactory.LITERAL('when', [arg0, arg1])

    @staticmethod
    def TERM(value, type=None):
        """
        Creates a 'value - type' term which represents either a constant or a variable.
        :param value: value of the term. String
        :param type: type of the term. String
        :return:
        """
        from pddl.structs.predicate import Term
        return Term(value, type)
