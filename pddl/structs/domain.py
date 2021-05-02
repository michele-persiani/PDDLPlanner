from os import linesep
from collections import defaultdict
from copy import deepcopy



class PDDLDomain(object):

    def __init__(self, name, requirements, types, constants, functions, predicates, operators):
        """
        :param name: string. Name of the domain.
        :param requirements:  list(string). List of requirements such as [':typing']
        :param types: Dictionary {string : list(string)}
        :param constants: tuple(Term)
        :param functions: tuple(Predicate)
        :param predicates: tuple(Predicate)
        :param operators: tuple(Operator)
        """
        self.name = name
        self.requirements = tuple(requirements)
        self.types = tuple(types)
        self.constants = tuple(constants)
        self.functions = tuple(functions)
        self.predicates = tuple(predicates)
        self.operators = tuple(operators)


    def find_operator(self, name):
        """
        Returns the operator with the given name
        :param name:
        :return:
        """
        for a in self.operators:
            if a.name == name:
                return a
        return None


    def deepcopy(self):
        return deepcopy(self)

    def shallowcopy(self):
        return PDDLDomain(
                    self.name,
                    tuple(self.requirements),
                    tuple(self.types),
                    tuple(self.constants),
                    tuple(self.functions),
                    tuple(self.predicates),
                    tuple(op.shallowcopy() for op in self.operators),
                    )


    def get_types_dictionary(self):
        d = defaultdict(lambda : [])
        for obj in self.types:
            type = str(obj.type) if obj.is_typed else 'object'
            value = str(obj.value)
            d[type].append(value)

        # Populate recursively the dictionary
        changed = True
        while changed:
            changed = False
            for k0, v0 in d.items():
                for k1, v1 in d.items():
                    sv0, sv1 = set(v0), set(v1)
                    lv0, lv1 = len(sv0), len(sv1)
                    if k1 in v0 and len(sv0.intersection(sv1)) < min(lv0, lv1):
                        v0.clear()
                        sv0 = sv0.union(sv1)
                        v0 += sv0
                        changed = True
        return d


    def get_constants_dictionary(self, type_hierarchy=False):

        # Compute shallow object dictionary
        d = defaultdict(lambda : [])
        for obj in self.constants:
            type = str(obj.type) if obj.is_typed else 'object'
            value = str(obj.value)
            d[type].append(value)

        if type_hierarchy:
            # Add inferred subtypes
            types_dict = self.get_types_dictionary()
            for type, subtypes in types_dict.items():
                for subtype in subtypes:
                    d[type] += d[subtype]

        return d

    def pddl_str(self):
        req_str   = '(:requirements {})\n\n'.format(' '.join(map(str, self.requirements))) if len(self.requirements) > 0 else ''
        types_str = '(:types {})\n\n'.format(' '.join(map(str, self.types))) if len(self.types) > 0 else ''
        const_str = '(:constants {})\n\n'.format(' '.join(map(str, self.constants))) if len(self.constants) > 0 else ''
        func_str  = '(:functions {})\n\n'.format(' '.join(map(str, self.functions))) if len(self.functions) > 0 else ''
        pred_str  = '(:predicates\n{}\n)\n\n'.format('\n'.join(map(str, self.predicates)))
        op_str    = '\n\n'.join(map(str, self.operators))
        domain_str = '(define (domain {})\n\n' \
                     '{}' \
                     '{}' \
                     '{}' \
                     '{}' \
                     '{}' \
                     '{}' \
                     '\n)'.format(self.name,
                                  req_str,
                                  types_str,
                                  const_str,
                                  func_str,
                                  pred_str,
                                  op_str
                                  )

        domain_str.replace('\n', linesep)

        return domain_str


    def __repr__(self):
        return '(domain {})'.format(self.name)


    def __str__(self):
        return self.pddl_str()


    def __eq__(self, other):
        return str(other) == str(self)


    def __hash__(self):
        return str(self).__hash__()
