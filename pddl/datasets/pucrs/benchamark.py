from .dataset_loader import pucrs_load_dataset, pucrs_num_instances, pucrs_get_instance, pucrs_available_domains
import pandas as pd
import itertools

class PUCRSBenchmark:
    """
    Class to perform benchmarks on the PUCRS dataset
    """


    def __init__(self):
        self.dataset = pucrs_load_dataset()

        config = self.__class__._default_config()
        config.update(self.config())

        self.noisy       = config['noisy']
        self.verbose     = config['verbose']
        self.output_file = config['dataframe_file']
        self.autosave    = config['autosave']
        self.params      = config['params']
        self.num_insts   = config['num_instances']
        self.num_goals   = config['num_goals']
        domains          = config['domains']
        self.domains = domains if domains else pucrs_available_domains(self.dataset, self.noisy)

        self.dataframe = pd.DataFrame()

    @staticmethod
    def _default_config():
        return {
            'noisy' : False,
            'domains' : None,        # If specified list of names of the tested domains. Use all of them if None
            'num_instances' : 100,   # If specified take only the first n instances from the tested datasets
            'num_goals' : None,      # If specified take only the first n goals from the tested instances. Use all of them if None
            'verbose' : False,       # Whenever adding rows to the dataframe print stored values
            'dataframe_file' : None, # Filepath to store the dataframe. Can't save to file if unspecified
            'autosave' : True,       # Save the dataframe whenever adding rows to it
            'params' : {},           # Parameters to forward to each individual benchmark. Dictionary { string : [n0, n1,...,] }
        }


    def config(self):
        return {}


    def run(self):

        for dom_name in self.domains:
            num_inst = min(pucrs_num_instances(self.dataset, dom_name), self.num_insts)

            for inst in range(num_inst):
                comb_params = list(self._parameters_to_list({'instance' : inst, 'domain' : dom_name}))
                comb_params = comb_params if len(comb_params) > 0 else [{},]

                for param_comb in comb_params:
                    domain, problems, observations = pucrs_get_instance(self.dataset, dom_name, inst, noisy=self.noisy)
                    if self.num_goals:
                        problems = problems[:self.num_goals]
                    self.benchmark(domain, problems, observations, param_comb)

        self.save_dataframe()
        return self.dataframe


    def benchmark(self, domain, problems, observations, params):
        """
        Ovverride with user behavior.
        :param domain: A PDDLDomain object
        :param problems: A list of PDDLProblem objects
        :param observations: List of OperatorToken for the instance's observations
        :param params: Parameters combination. See config()
        :return:
        """
        pass


    def store_dataframe_row(self, values):
        """
        Used to store a row in the current results dataframe
        :param values: A dictionary of column-value pairs
        :return:
        """
        self.dataframe = self.dataframe.append(values, ignore_index=True)
        if self.verbose:
            self.print_values(values)
        if self.autosave:
            self.save_dataframe()


    def save_dataframe(self):
        """
        Save the current dataframe on the hard drive
        :return:
        """
        if self.output_file is not None:
            self.dataframe.to_csv(str(self.output_file))


    def print_values(self, values):
        """
        Logging function.
        :param values:
        :return:
        """
        strings = []
        for k, v in values.items():
            strings.append('{}: {}'.format(str(k), str(v)))
        print('    '.join(strings))


    def _parameters_to_list(self, elems):
        params = self.params
        if params is None or len(params) == 0:
            return

        l = [(k, v) for k, v in self.params.items()]
        names, values = list(zip(*l))

        comb = itertools.product(*values)

        for c in comb:
            cc = {k : v for k, v in zip(names, c)}
            cc.update(elems)
            yield cc
