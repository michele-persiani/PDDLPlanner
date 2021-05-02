from .base import SubprocessPlanner, PlannerOutcome
import os


class FF(SubprocessPlanner):

    def __init__(self, tmp_folder, planner_folder, exec_name='ff', max_plan_secs=5, search_config=4, h_weight=1):
        self.search_config = search_config
        self.h_weight = h_weight
        super(FF, self).__init__(
            tmp_folder,
            os.path.join(planner_folder, exec_name),
            max_plan_secs
        )

    def get_subprocess_config(self, script, domain_path, problem_path, result_path):
        config = super(FF, self).get_subprocess_config(script, domain_path, problem_path, result_path)
        config.update({'stdout' : open('{}.1'.format(result_path), 'w')})
        config.update({'args' : [script,
                                 '-o', domain_path,
                                 '-f', problem_path,
                                 '-s', str(self.search_config),
                                 '-w', str(self.h_weight),
                                 ]})
        return config



    def get_outcome(self, planner_output):

        lines = planner_output.split(os.linesep)

        # Very probably this list of conditions is incomplete
        for l in map(str.lower, lines):
            if 'no plan will solve it' in l:
                return PlannerOutcome.SOLUTION_IMPOSSIBLE

            if 'problem proven unsolvable' in l:
                return PlannerOutcome.SOLUTION_IMPOSSIBLE

            if 'found legal plan as follows' in l:
                return PlannerOutcome.PLAN_FOUND

            if 'goal can be simplified to true' in l:
                return PlannerOutcome.PLAN_FOUND

            if 'undeclared predicate' in l:
                return PlannerOutcome.ERROR

            if 'too many' in l:
                return PlannerOutcome.ERROR

        # Default outcome if none of the above are true
        return PlannerOutcome.ERROR



    def yield_plan(self, planner_output):

        lines = planner_output.split(os.linesep)


        def _get_action_from_line(line):
            a_l = line.split(':')

            if len(a_l) == 1:
                return self.create_action(name='noop', params=[])

            assert len(a_l) == 2
            a_l = str(a_l[1]).lower()

            name_args = a_l.strip(')(\n ').split(' ', 1)
            if len(name_args) > 1:
                name, args = name_args
                name = str(name).lower()
                args = str(args).lower()
                args = args.split(' ')
            else:
                name = str(name_args[0]).lower()
                args = []

            return self.create_action(name=name, params=args)


        plan_line = False
        for l in map(str.lower, map(str.strip, lines)):
            if 'goal can be simplified to true' in l:
                yield self.create_action(name='noop', params=[])
                break

            if 'step' in l:
                plan_line = True
                yield _get_action_from_line(l)
                continue

            if l == '' or 'plan cost' in l:
                plan_line = False
                continue

            if plan_line:
                yield _get_action_from_line(l)



    def get_metrics(self, planner_output):
        lines = planner_output.split(os.linesep)
        metrics = super(FF, self).get_metrics(planner_output)

        for l in map(str.lower, lines):
            if 'plan cost' in l:
                cost = float(l.split(' ')[2])
                metrics.update({'plan_cost': cost})

        return metrics


