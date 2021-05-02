from pddl.datasets.pucrs import pucrs_load_dataset, pucrs_get_instance
from numpy.random import uniform
from random import choice
from pddl.datasets.generator import PlanGenerator


class PUCRSPlanGenerator(PlanGenerator):
    """
    PlanGenerator for the PUCRS dataset
    """

    def __init__(self, planner, params={}):
        super(PUCRSPlanGenerator, self).__init__(planner, params)
        self.dataset = pucrs_load_dataset()
        self.domain, problems, _ = pucrs_get_instance(self.dataset, self.params['domain'], self.params['instance'])
        self.base_problem = problems[0]
        self.goals = [p.goal for p in problems]
        self.grounded_predicates = self.base_problem.grounded_predicates
        if self.params['add_operators_suffix']:
            self.__add_operators_suffix()

    def __add_operators_suffix(self):
        for i, op in enumerate(self.domain.operators):
            op.name += f'_{i}'

    def default_params(self):
        p = super(PUCRSPlanGenerator, self).default_params()
        p.update({
            'domain' : 'ferry',
            'instance' : 0,
            'proba_add_init' : .1,  # Probability of adding a ground predicate to a sampled problem's original init
            'proba_drop_init' : .1, # Probability of dropping a predicate from a sampled problem's original init
            'proba_drop_goal' : .1, # Probability of dropping a predicate from a sampled problem's original goal
            'add_operators_suffix' : True
        })
        return p


    def sample_domain(self):
        return self.domain


    def sample_problem(self, domain):
        bernoulli = lambda p: uniform() < p
        problem = self.base_problem.shallowcopy()

        grounded_predicates = self.grounded_predicates

        p_drop = self.params['proba_drop_init']
        p_add = self.params['proba_add_init'] * (len(problem.init) / len(grounded_predicates))

        keep = tuple(filter(lambda x: bernoulli(1-p_drop), problem.init))
        add = tuple(filter(lambda x: bernoulli(p_add) and x.name != '=', grounded_predicates))

        init = set(keep + add)
        goal = choice(self.goals)

        problem.domain = domain
        problem.init = init
        problem.goal = tuple(filter(lambda x: bernoulli(1-self.params['proba_drop_goal']), goal))
        if len(problem.goal) == 0:
            problem.goal = goal


        return problem



if __name__ == '__main__':
    from pddl.planners import METRIC_FF_V21

    params = {
        'domain' : 'ferry',
        'instance' : 0,
        'verbose' : True,
        'max_plan_secs' : 1.,
        'log_every' : 40,
        'proba_add_init' : .1,
        'proba_drop_init' : .1,
    }

    datagen = PUCRSPlanGenerator(METRIC_FF_V21, params=params)

    res = datagen.sample_X_recurrent(20)


    exit(0)