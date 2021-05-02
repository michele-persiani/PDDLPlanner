import numpy as np
from pddl.structs import PDDLProblem, Literal




class Encoder:
    """
    Encoder used to transform set of literals (ie. PDDL states) to binary vectors and vice-versa
    """

    def __init__(self, encoder_dict):
        self.encoder = dict(encoder_dict)
        self.decoder = {v : k for k, v in self.encoder.items()}


    def binary_encode(self, literals):
        """
        Encode to a binary vector a list of literals
        :param literals: Iterables of literals
        :return: a binary vector of size len(self)
        """
        arr = np.zeros(len(self.encoder), dtype='bool')
        for p in literals:
            assert isinstance(p, Literal)
            arr[self.encoder[p]] = True
        return arr


    def binary_decode(self, array):
        """

        :param array:
        :return:
        """

        array = array.reshape(-1).astype('int')
        assert len(array) == len(self)
        pos = np.argwhere(array > 0).reshape(-1)
        positive = [self.decoder[p] for p in pos]
        return set(positive)

    def sorted_literals(self):
        return [self.decoder[i] for i in range(len(self.encoder))]

    def items(self):
        """
        The tuples (literal, id) used to encode-decode states
        :return:
        """
        return self.encoder.items()


    def __getitem__(self, item):
        """

        :param item:
        :return:
        The decoded set of literals through binary_decode() if item is a numpy array.
        The encoded id through encoder[item] if item is a Literal.
        The decoded id through decoder[item] if item is a integer.
        The encoded array through binary_encode() otherwise.
        """
        if isinstance(item, np.ndarray):
            return self.binary_decode(item)
        elif isinstance(item, Literal):
            return self.encoder[item]
        elif isinstance(item, int):
            return self.decoder[item]
        else:
            return self.binary_encode(item)


    def __len__(self):
        return len(self.encoder)


    def __call__(self, *args):
        assert len(args) == 1
        return self[args[0]]

    @staticmethod
    def from_literals(literals):
        d = {}
        for l in literals:
            d[l] = len(d)
        return Encoder(d)

    @staticmethod
    def from_problem(pddl_problem):
        assert isinstance(pddl_problem, PDDLProblem)
        literals = pddl_problem.grounded_predicates
        return Encoder.from_literals(literals)
