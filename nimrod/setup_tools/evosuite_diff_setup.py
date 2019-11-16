from nimrod.tools.junit import JUnit, JUnitResult, Coverage
from nimrod.tools.evosuite import Evosuite
from nimrod.setup_tools.behaviour_check import Behaviour_change


class Evosuite_Diff_setup:

    def __init__(self):
        self.suite_evosuite_diff = None
        self.evosuite_diff_params = None
        self.behaviour_change = Behaviour_change()

    def gen_evosuite_diff(self, scenario, project_dep):

        evosuite = Evosuite(
            java=project_dep.java,
            classpath=project_dep.classes_dir,
            sut_class=project_dep.sut_class,
            params=self.evosuite_diff_params,
            tests_src=project_dep.tests_dst + '/' + project_dep.project.get_project_name() + '/' + scenario.merge_scenario.get_merge_hash()
        )
        self.suite_evosuite_diff = evosuite.generate_differential(project_dep.dRegCp)
        return self.suite_evosuite_diff

    def try_evosuite_diff(self, classes_dir, sut_class, mutant_dir, project_dep):

        junit = JUnit(java=project_dep.java, classpath=classes_dir)
        res = junit.run_with_mutant(self.suite_evosuite_diff, sut_class, mutant_dir)
        return res

    def exec_evosuite_diff(self, evo, scenario, parent):
        conflict_info = []
        try:
            evo.project_dep.dRegCp = evo.project_dep.generate_dependencies_path(scenario, "base")
            evo.project_dep.classes_dir = evo.project_dep.generate_dependencies_path(scenario, parent)
            evo.project_dep.mergeDir = evo.project_dep.generate_dependencies_path(scenario, "merge")
            evo.project_dep.sut_class = scenario.merge_scenario.get_sut_class()

            conflict_info = self.exec_evosuite_diff_all(evo, scenario)

        except:
            print("Some project versions could not be evaluated")

        return conflict_info

    def exec_evosuite_diff_jar(self, evo, scenario, jarBase, jarParent, jarMerge):
        conflict_info = []
        try:
            evo.project_dep.dRegCp = jarBase
            evo.project_dep.classes_dir = jarParent
            evo.project_dep.mergeDir = jarMerge
            evo.project_dep.sut_class = scenario.merge_scenario.get_sut_class()

            conflict_info = self.exec_evosuite_diff_all(evo, scenario)

        except:
            print("Some project versions could not be evaluated")

        return conflict_info

    def exec_evosuite_diff_all(self, evo, scenario):
        conflict_info = []
        try:
            path_suite = self.gen_evosuite_diff(scenario, evo.project_dep)

            test_result_base = self.try_evosuite_diff(evo.project_dep.classes_dir, evo.project_dep.sut_class, evo.project_dep.dRegCp, evo.project_dep)  # fail on base
            test_result_parent = self.try_evosuite_diff(evo.project_dep.classes_dir, evo.project_dep.sut_class, evo.project_dep.classes_dir, evo.project_dep)  # pass on left
            test_result_merge = self.try_evosuite_diff(evo.project_dep.classes_dir, evo.project_dep.sut_class, evo.project_dep.mergeDir, evo.project_dep)  # fail on merge

            conflict_info.append(
                self.behaviour_change.check_different_test_results_for_commit_pair(test_result_base, test_result_parent, path_suite))
            conflict_info.append(
                self.behaviour_change.check_different_test_results_for_commit_pair(test_result_merge, test_result_parent, path_suite))
            conflict_info.append(self.behaviour_change.check_different_test_results_for_merge_scenario(test_result_base, test_result_parent,
                                                                                      test_result_merge, path_suite))

        except:
            print("Some project versions could not be evaluated")

        return conflict_info