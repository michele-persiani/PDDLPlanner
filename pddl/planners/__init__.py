from . import metricff_v21
from os.path import dirname, realpath, join


_tmp_folder = join(dirname(realpath(__file__)), 'tmp')
_planners_folder = join(dirname(realpath(__file__)), 'ext_planners')




METRIC_FF = metricff_v21.FF(tmp_folder=_tmp_folder,
                                planner_folder=join(_planners_folder, 'Metric-FF-v2.1'),
                                max_plan_secs=5,
                                search_config=2)





def clear_tmp_folder():
    from shutil import rmtree
    from os import mkdir

    folder = _tmp_folder
    rmtree(folder)
    mkdir(folder)
