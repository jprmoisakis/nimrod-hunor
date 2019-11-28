import csv
from nimrod.tools.randoop import Randoop
from nimrod.tools.safira import Safira
from nimrod.tools.junit import JUnit
from collections import namedtuple
from nimrod.project_info.git_project import GitProject
from nimrod.tests.utils import get_config
from nimrod.project_info.merge_scenario import MergeScenario
from nimrod.report.output_report import Output_report
from nimrod.proj.project_dependencies import Project_dependecies
from nimrod.setup_tools.evosuite_setup import Evosuite_setup
from nimrod.setup_tools.evosuite_diff_setup import Evosuite_Diff_setup
from nimrod.setup_tools.randoop_setup import Randoop_setup

NimrodResult = namedtuple('NimrodResult', ['maybe_equivalent', 'not_equivalent',
                                           'coverage', 'differential',
                                           'timeout', 'test_tool', 'is_equal_coverage'])


class evotest:

    def __init__(self, path_local_project="", path_local_module_analysis="", project_name=""):
        config = get_config()
        self.project_dep = Project_dependecies(config, path_local_project, path_local_module_analysis, project_name)

        self.evosuite_setup = Evosuite_setup()
        self.evosuite_diff_setup = Evosuite_Diff_setup()
        self.randoop_setup = Randoop_setup()

        self.suite_evosuite = None
        self.evosuite_params = None

        self.suite_randoop = None
        self.randoop_params = None

        self.output_report = Output_report(config["path_output_csv"])

    def set_git_project(self, path):
        self.project = GitProject(path)


if __name__ == '__main__':

    config = get_config()
    with open(config['path_hash_csv']) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[1] == "true":
                evo = evotest(project_name=row[0])
                merge = MergeScenario(merge_information=row)

                result_evodiff_left = evo.evosuite_diff_setup.exec_evosuite_diff_jar(evo, merge, row[10], row[11], row[13])
                result_evodiff_right = evo.evosuite_diff_setup.exec_evosuite_diff_jar(evo, merge, row[10], row[12], row[13])
                result_evosuite_left = evo.evosuite_setup.exec_evosuite_jar(evo, merge, row[10], row[11], row[13])
                result_evosuite_right = evo.evosuite_setup.exec_evosuite_jar(evo, merge, row[10], row[12], row[13])
                result_randoop_left = evo.randoop_setup.exec_randoop_jar(evo, merge, row[10], row[11], row[13])
                result_randoop_right = evo.randoop_setup.exec_randoop_jar(evo, merge, row[10], row[12], row[13])

                evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge, "evosuite-diff", "left", result_evodiff_left)
                evo.output_report.write_output_results(evo.project_dep.project.get_project_name(),merge, "evosuite-diff", "right", result_evodiff_right)
                evo.output_report.write_output_results(evo.project_dep.project.get_project_name(),merge, "evosuite", "left", result_evosuite_left)
                evo.output_report.write_output_results(evo.project_dep.project.get_project_name(),merge, "evosuite", "right", result_evosuite_right)
                evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge, "randoop", "left", result_randoop_left)
                evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge, "randoop", "right", result_randoop_right)

            else:
                evo = evotest(row[8], row[9], row[0])
                merge = MergeScenario(evo.project_dep.project.get_path_local_project, row)
                evo.project_dep.compile_commits(merge)

                #result_evodiff_left = evo.evosuite_diff_setup.exec_evosuite_diff(evo, merge, "left")
                #result_evodiff_right = evo.evosuite_diff_setup.exec_evosuite_diff(evo, merge, "right")
                #result_evosuite_left = evo.evosuite_setup.exec_evosuite(evo, merge, "left")
                #result_evosuite_right = evo.evosuite_setup.exec_evosuite(evo, merge, "right")
                result_randoop_left = evo.randoop_setup.exec_randoop(evo, merge, "left")
                result_randoop_right = evo.randoop_setup.exec_randoop(evo, merge, "right")

                #evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge, "evosuite-diff", "left", result_evodiff_left)
                #evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge, "evosuite-diff", "right", result_evodiff_right)
                #evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge,"evosuite", "left", result_evosuite_left)
                #evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge,"evosuite", "right", result_evosuite_right)
                evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge,"randoop", "left", result_randoop_left)
                evo.output_report.write_output_results(evo.project_dep.project.get_project_name(), merge,"randoop", "right", result_randoop_right)