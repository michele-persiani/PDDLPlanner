from pddl.datasets import pucrs_load_dataset, pucrs_get_instance
from pddl.planners import METRIC_FF


if __name__ == '__main__':
    dataset = pucrs_load_dataset()
    domain, problems, observations = pucrs_get_instance(dataset, 'logistics', 0)

    METRIC_FF.verbose = True

    plan, metrics = METRIC_FF.make_plan(domain, problems[0])
