from pddl.structs import PDDLProblem
import numpy as np
from random import choice
from pddl.encoder import Encoder


class PlanGenerator:
    """
    Used to create datasets of plans.
    The user must override the methods sample_domain() and sample_problem().
    """

    def __init__(self, planner, params={}):
        self.planner = planner
        pr = self.default_params()
        pr.update(params)
        self.params = pr


    def default_params(self):
        return {'verbose' : True,
                'log_every' : 100,
                'max_plan_secs' : 1.,
                }


    def sample_domain(self):
        """
        :return: A sampled PDDLDomain
        """
        raise NotImplementedError


    def sample_problem(self, domain):
        """
        Sample a problem for the given domain.
        :param domain: The PDDLDomain to which the sampled problem belongs.
        :return: A sampled PDDLProblem
        """
        raise NotImplementedError


    def make_plans(self, problem):
        """
        Computes the plans for the given problem. By default the planner's make_plan() output is used to return a
        single optimal for the problem
        :param problem: PDDLProblem instance
        :return: a list of plans or None if any plan couldn't be computed
        """
        if hasattr(self.planner, 'max_plan_secs'):
            self.planner.max_plan_secs = float(self.params['max_plan_secs'])
        plan, metrics = self.planner.make_plan(problem.domain, problem)
        if plan is None:
            return None
        return [plan,]

    @staticmethod
    def get_states(problem, plan, force=False):
        """
        Get the states associated with the provided trajectory starting from problem.init and performing plan
        :param problem: a PDDLProblem
        :param plan: a sequence of Operator
        :param force: whether to force the application of operator. If false, every operator's preconditions must be
        present in the state it is allied on
        :return:
        """
        states = [problem.init, ]
        for op in plan:
            problem = problem.apply_operator(op, force=force)
            states += [problem.init, ]
        states += [problem.goal, ]
        return states

    @staticmethod
    def make_encoder_dictionary(problems_plans):
        """
        Create an encoder dictionary. Used by Encoder objects to encode states
        :param problems_plans: a list of tuples (problem, plans)
        :return: a dictionary d = {literal : id} with max(d) = len(d)
        """
        predicates_dict = {}
        for problem, plan in problems_plans:
            states = PlanGenerator.get_states(problem, plan)
            for state in states:
                for literal in state:
                    if literal not in predicates_dict:
                        predicates_dict[literal] = len(predicates_dict)

        return predicates_dict


    def sample(self):
        """
        :return: A randomly sampled problem-plan instance.
        """
        plans = None
        problem = None
        while plans is None:
            domain = self.sample_domain()
            problem = self.sample_problem(domain)
            plans = self.make_plans(problem)
        return problem, choice(plans)


    def sample_n(self, n, plan_filter=None):
        """
        Sample a given amount of plans
        :param plan_filter:
        :param n: the number of plans to sample
        :return: a list of PDDL plans
        """
        found_plans = []
        epoch = 0
        if plan_filter is None:
            plan_filter = lambda x: True

        while len(found_plans) < n:
            epoch += 1
            domain = self.sample_domain()
            problem = self.sample_problem(domain)
            plans = self.make_plans(problem)

            if plans is not None:
                found_plans += [(problem, p) for p in plans if plan_filter(p)]

            if self.params['verbose'] and (epoch & self.params['log_every'] == 0):
                print(f'Sampling plans... {len(found_plans):>5}/{n}')
        if self.params['verbose']:
            print(f'Sampling plans... {n}/{n}')

        return found_plans[:n]


    def make_encoder(self, problems_plans):
        """
        Create an encoder object
        :param problems_plans: a list of tuples (problem, plans)
        :return:
        """
        d = self.make_encoder_dictionary(problems_plans)
        return Encoder(d)


    def sample_X_recurrent(self, n, plan_filter=None):
        """
        Sample plans to obtain a numpy array.
        :param n:
        :param plan_filter: filter function for sampled plans
        :return: A tuple (X, G), encoder.
        X is the array of the encoded plans. G the array of the encoded goals. encoder is the encode that was used
        to encode the plans.
        Size of the array:
        X: (n, max_len, max_state_size)
        G: (n, max_state_size)
        """
        problems_plans = self.sample_n(n, plan_filter)
        encoder = self.make_encoder(problems_plans)

        def concat(problem):
            return np.concatenate([encoder(problem.init), encoder(problem.goal)])

        max_plan_len = max(list(map(lambda x: len(x[1]), problems_plans)))
        X = np.zeros((len(problems_plans), max_plan_len+1, len(encoder)*2))

        for i, pp in enumerate(problems_plans):
            problem, plan = pp

            states = [concat(problem),]
            for op in plan:
                problem = problem.apply_operator(op)
                states += [concat(problem),]
            states = np.vstack(states)
            X[i, -len(plan)-1:, :] = states

        Xr = X[:, :, :int(X.shape[-1]/2)]
        Gr = X[:, :, int(X.shape[-1]/2):]
        G = Gr[:, -1, :]
        return [Xr, G], encoder


    def sample_X_classification(self, n, plan_filter=None):
        """
        Sample plans to obtain a numpy array. Size of the array: (n * plan_len, max_state_size)
        :param n:
        :param plan_filter: filter function for sampled plans
        :return: A tuple (X, G), encoder.
        X is the array of the encoded plans. G the array of the encoded goals. encoder is the encode that was used
        to encode the plans
        X: (n * plan_len, max_state_size)
        G: (n, max_state_size)
        """
        X, encoder = self.sample_X_recurrent(n, plan_filter)
        X, _ = X
        X = X.reshape(-1, len(encoder)*2)
        X = np.delete(X, np.argwhere(np.all(X==0, 1)), 0)
        X0, G = X[:, :len(encoder)], X[:, len(encoder):]
        del X

        return [X0, G, ], encoder

    @staticmethod
    def save_X(filename, X, encoder):
        """
        Save to the hard drive a list of encoded arrays and their corresponding encoder
        :param filename: target filename
        :param X: either a single numpy array or an iterable of arrays
        :param encoder: the associated encoder
        """
        s = list()
        if isinstance(X, np.ndarray):
            X = [X,]
        s += X
        s += [encoder.encoder,]
        np.savez(filename, *s)

    @staticmethod
    def load_X(filename):
        """
        Load from the hard drive a list of encoded arrays and their corresponding encoder. Dual of save_X().
        :param filename: target filename
        :return: a tuple (X, encoder)
        X is a list of numpy arrays
        """
        r = np.load(filename, allow_pickle=True)
        items = [r[k] for k in r]
        items[-1] = items[-1].item()
        assert isinstance(items[-1], dict)
        items[-1] = Encoder(items[-1])
        return items[:-1], items[-1]