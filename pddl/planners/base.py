from __future__ import print_function
import subprocess
from random import choice
from datetime import datetime
from shutil import rmtree
from os import mkdir, listdir, linesep
from os.path import join, abspath, split
from threading import Timer, Semaphore
from pddl.structs import OperatorToken


class PlannerOutcome:
    PLAN_FOUND          = 'plan-found'           # A valid plan is found
    SOLUTION_IMPOSSIBLE = 'solution-impossbible' # No plan can be found
    ERROR               = 'planner-error'        # Error while executing the planner eg. planner wrong arguments
    TIMEOUT             = 'timeout'              # The planner didn't find any plan in the timeout frame



class Planner(object):


    def __init__(self):
        self.verbose = False


    def make_plan(self, domain, problem):
        '''

        :param domain: PDDL domain object. str(domain) method must return a valid PDDL domain
        :param problem: PDDL problem object. str(problem) method must return a valid PDDL problem
        :return: A tuple ([plan], {metrics})
        '''

        planner_output, done = self.run_planner(domain, problem)


        assert planner_output is not None, 'Error: planner_output is None'


        self.print(planner_output, 'Planner Output')



        outcome = self.get_outcome(planner_output)
        metrics = {
            'outcome' : str(outcome),
            'message' : 'OK',
            'planner_output' : str(planner_output),
        }

        if outcome == PlannerOutcome.PLAN_FOUND:
            plan = list(self.yield_plan(planner_output))
            self.print(linesep.join(map(str, plan)), 'Found Plan')
            metrics['plan_length']    = len(plan)
            metrics['plan_cost']      = len(plan)

            metrics.update(self.get_metrics(planner_output))
            return plan, metrics

        metrics.update(self.get_metrics(planner_output))

        if outcome == PlannerOutcome.ERROR:
            self.print('Error while running the planner.')
            metrics['message'] = 'Error encountered while running planner.'
            return None, metrics

        elif outcome == PlannerOutcome.SOLUTION_IMPOSSIBLE:
            self.print('Solution impossible!')
            metrics['message'] = 'The planner could not find any solution.'
            return None, metrics

        elif outcome == PlannerOutcome.TIMEOUT or not done:
            self.print('Planner reached timeout.')
            metrics['message'] = 'Planner timeout. Try to increase the maximum plan time.'
            return None, metrics

        assert False, 'Invalid planner outcome'


    def print(self, message, tag=None):
        if self.verbose:
            if tag:
                print('--- Begin {} ---'.format(tag), end=linesep)
            print(str(message), end=linesep)
            if tag:
                print('--- End {} ---'.format(tag), end=linesep)


    def create_action(self, name, params):
        '''
        Use to instantiate an action given its name and parameters.

        :param name: name of the action
        :param params: parameters of the action
        :return: An action object
        '''
        return OperatorToken(name, params)


    def run_planner(self, domain, problem):
        '''
        Run the planner on the given domain and problem.

        :param domain: PDDL domain object. str(domain) method must return a valid PDDL domain
        :param problem: PDDL problem object. str(problem) method must return a valid PDDL problem
        :return: The output of the planner, or None if an error occured
        '''
        raise NotImplementedError


    def get_outcome(self, planner_output):
        '''

        :param planner_output: The content of the file containing the found solution. The content depends
        on what run_planner() returns
        :return: A value from the enumeration class PlannerOutcome
        '''
        raise NotImplementedError


    def yield_plan(self, planner_output):
        '''
        Retrieve the plan from the given planner_output.
        planner_output is assumed to contain a valid solution.

        :param planner_output: The content of the file containing the found solution. The content depends
        on what run_planner() returns
        :return: A list of InstantiatedAction objects representing the found plan. Use self._create_action()
        '''
        raise NotImplementedError


    def get_metrics(self, planner_output):
        '''
        Retrieve relevant metrics from planner_output.
        planner_output is assumed to contain a valid solution.
        Should be overridden by each subclass that have custom metrics. plan_length and plan_cost with
        plan_cost = plan_length can be omitted as are added by default .


        :param planner_output: The content of the file containing the found solution. The content depends
        on what run_planner() returns
        :return: A dictionary containing all the metrics expressed in the file
        '''
        return {}



class SubprocessPlanner(Planner):



    def __init__(self, tmp_folder, plan_script, max_plan_secs=5, remove_tmp_folder=True):
        super(SubprocessPlanner, self).__init__()
        self.tmp    = abspath(tmp_folder)
        self.script = abspath(plan_script)
        assert max_plan_secs > 0
        self.max_plan_secs = max_plan_secs
        self.remove_tmp_folder = remove_tmp_folder


    def get_subprocess_config(self, script, domain_path, problem_path, result_path):
        config = {
            'args' : [script, domain_path, problem_path, result_path],
            'stdin' : None,
            'stdout' : None,
            'stderr' : None,
            'cwd' : None
        }
        return config


    def create_subprocess(self, script, domain_path, problem_path, result_path):
        '''
        Create Popen to call external planner.
        Use get_subprocess_config() to set the Popen arguments

        :param script:
        :param domain_path:
        :param problem_path:
        :param result_path:
        :return: (Popen object, config)
        '''

        config = self.get_subprocess_config(script, domain_path, problem_path, result_path)

        p = subprocess.Popen(args=config['args'], cwd=config['cwd'], stdin=config['stdin'],
                             stdout=config['stdout'], stderr=config['stderr'])
        return p, config


    def run_planner(self, domain, problem):
        '''
        Runs the planner for the given domain and problem
        :param domain: an object with str() returning a valid PDDL domain. Case-insensitive
        :param problem: an object with str() returning a valid PDDL problem. Case-insensitive
        :return: the output of the planner, or None if a plan could not be found with the given self.max_plan_secs
        '''

        # ------ Save structs files in a temporary folder
        plan_folder = self._mkdir_tmp_folder()
        domain_file = join(plan_folder, 'domain.pddl')
        problem_file = join(plan_folder, 'problem.pddl')
        result_file = join(plan_folder, 'solution')

        with open(domain_file, 'w') as dout, open(problem_file, 'w') as pout:
            dout.write(str(domain).lower())
            pout.write(str(problem).lower())


        # ------ Run subprocess
        p, stdout = self.create_subprocess(self.script, domain_file, problem_file, result_file)

        done = self._handle_subprocess(p, stdout)


        # ------ Read solution files from the temporary folder
        planner_output = self.read_planner_output(result_file)

        if self.remove_tmp_folder:
            rmtree(plan_folder)


        return planner_output, done

    def _handle_subprocess(self, p, config):
        sem = Semaphore()
        _timeout = False
        _done = False

        def kill_subprocess():
            _timeout = True
            try:
                p.kill()
            except OSError as e:
                self.print('Couldn\'t kill subprocess: {}'.format(str(e)))
            sem.acquire(True)
            sem.release()

        t = Timer(self.max_plan_secs, kill_subprocess)
        t.start()
        p.wait()

        sem.acquire(True)
        _done = True - _timeout
        sem.release()
        t.cancel()

        for v in map(lambda k: config[k], ['stdin', 'stdout', 'stderr']):
            if v is not None and not isinstance(v, int):
                v.flush()
                v.close()


        return bool(_done)


    def _mkdir_tmp_folder(self):
        now = str(datetime.now().time())
        rnd_id = now + '-' + ''.join(choice('ABCDEFGHILMNOPQRSTUVZ') for _ in range(3))
        rnd_id = rnd_id.replace(':', '-')
        plan_folder = join(self.tmp, rnd_id)

        plan_folder = plan_folder
        mkdir(plan_folder)
        return plan_folder


    def read_planner_output(self, base_result_file):
        '''
        Finds the file containing the best solution and returns its content.
        This default implementation goes though incremental quality solutions with files solution.1 solution.2 etc.
        :param base_result_file: path of the result file without incremental number suffix
        :return: planner output for the best solution
        '''
        curr_file, curr_ver = None, -1

        solution_folder, result_filename = split(base_result_file)


        append_tmp_file = lambda fn: join(solution_folder, fn)


        for filename in listdir(solution_folder):

            if filename.startswith(result_filename):

                if '.' in result_filename:
                    ver = int(filename.split('.')[-1])
                else:
                    ver = 0

                if ver > curr_ver:
                    curr_ver = ver
                    curr_file = append_tmp_file(filename)

        if curr_file is None:
            return None

        with open(curr_file, 'r') as fin:
            planner_result = fin.read()

        return planner_result

