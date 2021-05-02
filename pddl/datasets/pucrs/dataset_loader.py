import os
import re
from pddl.structs.pddl_factory import PDDLFactory
from pddl.structs.operators import OperatorToken
from pddl.structs.predicate import Term

dataset_folder = os.path.join(os.path.dirname(__file__), 'dataset')



line_filter = lambda lines: map(str.strip, filter(lambda l: not l.startswith(';'), lines))

def perc_filter(folder_name):
    try:
        int(folder_name)
        return True
    except:
        return False



'''
Structure of the dataset
domain
    - perc obs
        - problem instance
'''


def pucrs_generate_dataset(folder=dataset_folder):
    """
    Generate the PUCRS dataset from its source folder
    :param folder:
    :return:
    """
    dataset = {}

    for domain_name in os.listdir(folder):
        path_domain = os.path.join(folder, domain_name)

        dataset[domain_name] = {}

        for perc in map(int, filter(perc_filter, os.listdir(path_domain))):
            path = os.path.join(path_domain, str(perc))

            dataset[domain_name][perc] = []

            for problem in os.listdir(path):
                path_problem = os.path.join(path, problem)

                os.system('tar -xvf {}'.format(path_problem))

                with open('./domain.pddl', 'r') as fin:
                    pr_domain = os.linesep.join(line_filter(fin.readlines())).lower()
                    dm = PDDLFactory.PARSE_DOMAIN(pr_domain)



                with open('./template.pddl', 'r') as fin:
                    pr_problem = os.linesep.join(map(lambda l: re.sub('<HYPOTHESIS>', '(false)', l), line_filter(fin.readlines()))).lower()
                    pr = PDDLFactory.PARSE_PROBLEM(pr_problem)


                with open('./hyps.dat', 'r') as fin:
                    hyps = [[p.strip() for p in l.split(',')] for l in line_filter(fin.readlines())]

                with open('./real_hyp.dat', 'r') as fin:
                    real_hyp = [[p.strip() for p in l.split(',')] for l in line_filter(fin.readlines())][0]

                with open('./obs.dat', 'r') as fin:
                    obs = [l.strip(')(').split(' ') for l in line_filter(fin.readlines())]

                dataset[domain_name][perc].append_child([pr_domain, pr_problem, hyps, real_hyp, obs])


    with open(os.path.join(os.path.dirname(__file__), 'dataset.dat'), 'w') as fout:
        fout.write(str(dataset))


def pucrs_load_dataset():
    '''
    Loads a previously generated dataset.
    The dataset is a nested dictionary
        dataset[domain_name][perc_obs][problem]


    :return: the dataset.
    Every dataset entry is the tuple
    [
    pr_domain,
    pr_problem,
    hyps,
    real_hyp,
    obs
    ]

    '''


    with open(os.path.join(os.path.dirname(__file__), 'dataset.dat'), 'r') as fin:
        dataset = fin.read()
    return eval(dataset)


def pucrs_available_domains(dataset, noisy=False):
    def _filter(name):
        _t = str(name).endswith('-noisy')
        return (noisy and _t) or not (noisy or _t)
    return list(filter(lambda n: _filter(n), dataset.keys()))


def pucrs_num_instances(dataset, domain_name):
    return len(dataset[domain_name][100])


def __create_operator_token(domain, name, params):
    _op = domain.find_operator(name)
    assert _op is not None
    types = list(map(lambda p: p.type, _op.params))
    assert len(params) == len(types)
    values_types = list(zip(params, types))
    _params = [Term(value=x[0]) for x in values_types]
    return OperatorToken(name, _params)


def pucrs_get_instance(dataset, domain_name, num_instance, percentage_obs=100, noisy=False):
    """
    Load an instance from the PUCRS dataset
    :param dataset: The dataset obtained by load_pucrs_dataset()
    :param domain_name: a domain name amongst the ones returned from available_domains()
    :param num_instance: the instance number to use. See num_instances()
    :param percentage_obs: The percentage of obs to use
    :param noisy: Whther to use the noisy version of the observations
    :return: (domain, problems, observations,) triple
    """
    if noisy:
        domain_name += '-noisy'

    domain, problem, candidate_goals, true_goal, observations = dataset[domain_name][100][num_instance]

    domain = PDDLFactory.PARSE_DOMAIN(domain.lower())
    problem = PDDLFactory.PARSE_PROBLEM(domain, problem.lower())

    problems = []

    true_goal = set(true_goal)

    true_goal_idx = -1
    for i, g in enumerate(candidate_goals):
        pr = problem.shallowcopy()
        pr.goal = tuple(map(lambda x: PDDLFactory.PARSE_LITERAL(x), g))
        problems.append(pr)
        if all([str(p) in true_goal for p in pr.goal]):
            true_goal_idx = i
    assert true_goal_idx >= 0

    tmp = problems[true_goal_idx]
    del problems[true_goal_idx]
    problems.insert(0, tmp)


    enum_obs = enumerate(observations[:max(1, int(percentage_obs*len(observations)))])
    observations = [__create_operator_token(domain, name=o[0].lower(), params=[x.lower() for x in o[1:]]) for i, o in enum_obs]



    return domain, problems, observations


if __name__ == '__main__':
    #generate_dataset()
    dataset = pucrs_load_dataset()
    domains = pucrs_available_domains(dataset)
    print(domains)
    instances = pucrs_num_instances(dataset, domains[0])
    print(instances)
    instance = pucrs_get_instance(dataset, domains[0], 0)
