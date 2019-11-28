from nimrod.tools.randoop import Randoop
from nimrod.tools.safira import Safira
from nimrod.tools.junit import JUnit
from nimrod.setup_tools.behaviour_check import Behaviour_change

class Randoop_setup:

    def __init__(self):
        self.suite_randoop = None
        self.randoop_params = None
        self.behaviour_change = Behaviour_change()

    def gen_randoop(self, scenario, project_dep):
        randoop = Randoop(
            java=project_dep.java,
            classpath=project_dep.classes_dir,
            tests_src=project_dep.tests_dst + '/' + project_dep.project.get_project_name() + '/' + scenario.merge_scenario.get_merge_hash(),
            sut_class=project_dep.sut_class,
            params=self.randoop_params
        )
        safira = Safira(java=project_dep.java, classes_dir=project_dep.classes_dir, mutant_dir=project_dep.dRegCp)
        if "Bisect" in project_dep.sut_class:
            self.suite_randoop = randoop.generate()
        else:
            self.suite_randoop = randoop.generate_with_impact_analysis(safira)
            if "Simulator" in project_dep.sut_class:
                import distutils.dir_util
                distutils.dir_util.copy_tree("./config/", randoop.suite_dir + "/config/")
        return self.suite_randoop

    def try_randoop(self, classes_dir, sut_class, mutant_dir, project_dep):
        junit = JUnit(java=project_dep.java, classpath=classes_dir)
        return (junit.run_with_mutant(self.suite_randoop, sut_class, mutant_dir)
                if self.suite_randoop else None)

    def exec_randoop(self, evo, scenario, parent):
        conflict_info = []
        try:
            evo.project_dep.dRegCp = evo.project_dep.generate_dependencies_path(scenario, "base")
            evo.project_dep.classes_dir = evo.project_dep.generate_dependencies_path(scenario, parent)
            evo.project_dep.mergeDir = evo.project_dep.generate_dependencies_path(scenario, "merge")

            conflict_info = self.exec_randoop_all(evo, scenario)
        except:
            print("Some project versions could not be evaluated")

        return conflict_info

    def exec_randoop_jar(self, evo, scenario, jarBase, jarParent, jarMerge):
        conflict_info = []
        try:
            evo.project_dep.dRegCp = jarBase
            evo.project_dep.classes_dir = jarParent
            evo.project_dep.mergeDir = jarMerge
            evo.project_dep.sut_class = scenario.merge_scenario.get_sut_class()

            conflict_info = self.exec_randoop_all(evo, scenario)
        except:
            print("Some project versions could not be evaluated")

        return conflict_info

    def exec_randoop_all(self, evo, scenario):
        conflict_info = []
        try:
            path_suite = self.gen_randoop(scenario, evo.project_dep)

            test_result_base = self.try_randoop(evo.project_dep.classes_dir, evo.project_dep.sut_class,
                                                evo.project_dep.dRegCp, evo.project_dep)  # fail on base - passing tests 0 2 7
            test_result_parent = self.try_randoop(evo.project_dep.classes_dir, evo.project_dep.sut_class, evo.project_dep.classes_dir, evo.project_dep)  # pass on left
            test_result_merge = self.try_randoop(evo.project_dep.classes_dir, evo.project_dep.sut_class,
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