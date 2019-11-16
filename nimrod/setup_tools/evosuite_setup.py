from nimrod.tools.safira import Safira
from nimrod.tools.junit import JUnit, JUnitResult, Coverage
from nimrod.tools.evosuite import Evosuite
from nimrod.setup_tools.behaviour_check import Behaviour_change


class Evosuite_setup:

    def __init__(self):
        self.suite_evosuite = None
        self.evosuite_params = None
        self.behaviour_change = Behaviour_change()

    def gen_evosuite(self, scenario, project_dep):
        evosuite = Evosuite(
            java=project_dep.java,
            classpath=project_dep.classes_dir,
            tests_src=project_dep.tests_dst + '/' + project_dep.project.get_project_name() + '/' + scenario.merge_scenario.get_merge_hash(),
            sut_class=project_dep.sut_class,
            params=self.evosuite_params
        )
        # suite = evosuite.generate()
        safira = Safira(java=project_dep.java, classes_dir=project_dep.classes_dir,
                        mutant_dir=project_dep.dRegCp)
        self.suite_evosuite = evosuite.generate_with_impact_analysis(safira)
        if "Simulator" in project_dep.sut_class:
            import distutils.dir_util
            distutils.dir_util.copy_tree("./config/", evosuite.suite_dir + "/config/")

        return self.suite_evosuite

    def try_evosuite(self, classes_dir, sut_class, mutant_dir, project_dep):
        junit = JUnit(java=project_dep.java, classpath=classes_dir)
        return (junit.run_with_mutant(self.suite_evosuite, sut_class, mutant_dir)
                if self.suite_evosuite else None)

    def exec_evosuite(self, evo, scenario, parent):

        conflict_info = []
        try:
            evo.project_dep.dRegCp = evo.project_dep.generate_dependencies_path(scenario, "base")
            evo.project_dep.classes_dir = evo.project_dep.generate_dependencies_path(scenario, parent)
            evo.project_dep.mergeDir = evo.project_dep.generate_dependencies_path(scenario, "merge")

            conflict_info = self.exec_evosuite_all(evo, scenario)

        except:
            print("Some project versions could not be evaluated")

        return conflict_info

    def exec_evosuite_jar(self, evo, scenario, jarBase, jarParent, jarMerge):
        conflict_info = []
        try:
            evo.project_dep.dRegCp = jarBase
            evo.project_dep.classes_dir = jarParent
            evo.project_dep.mergeDir = jarMerge
            evo.project_dep.sut_class = scenario.merge_scenario.get_sut_class()

            conflict_info = self.exec_evosuite_all(evo, scenario)
        except:
            print("Some project versions could not be evaluated")

        return conflict_info

    def exec_evosuite_all(self, evo, scenario):
        conflict_info = []
        try:
            path_suite = self.gen_evosuite(scenario, evo.project_dep)

            test_result_base = self.try_evosuite(evo.project_dep.classes_dir, evo.project_dep.sut_class,
                                                evo.project_dep.dRegCp, evo.project_dep)  # fail on base - passing tests 0 2 7
            test_result_parent = self.try_evosuite(evo.project_dep.classes_dir, evo.project_dep.sut_class, evo.project_dep.classes_dir, evo.project_dep)  # pass on left
            test_result_merge = self.try_evosuite(evo.project_dep.classes_dir, evo.project_dep.sut_class,
                                                 evo.project_dep.mergeDir, evo.project_dep)  # fail on merge - passing tests 0 2 7

            conflict_info.append(
                self.behaviour_change.check_different_test_results_for_commit_pair(test_result_base, test_result_parent, path_suite))
            conflict_info.append(
                self.behaviour_change.check_different_test_results_for_commit_pair(test_result_merge, test_result_parent, path_suite))
            conflict_info.append(self.behaviour_change.check_different_test_results_for_merge_scenario(test_result_base, test_result_parent,
                                                                                      test_result_merge, path_suite))

        except:
            print("Some project versions could not be evaluated")

        return conflict_info