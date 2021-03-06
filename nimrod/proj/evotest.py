import os
import shutil
import time
import re
import csv
import threading
import subprocess
from nimrod.tools.randoop import Randoop
from nimrod.tools.mujava import MuJava
from nimrod.mutant import Mutant
from nimrod.tools.safira import Safira
from nimrod.tools.junit import JUnit, JUnitResult, Coverage
from nimrod.tools.evosuite import Evosuite
from nimrod.utils import package_to_dir
from nimrod.project_info import commit, git_project, merge_scenario, report_directory
from collections import namedtuple
from nimrod.project_info.git_project import GitProject
import shutil
from nimrod.tools.java import Java
from nimrod.tools.maven import Maven
from nimrod.tests.utils import get_config
from nimrod.project_info.merge_scenario import MergeScenario
from tempfile import mkstemp
import fileinput

from shutil import move

from os import fdopen, remove
NimrodResult = namedtuple('NimrodResult', ['maybe_equivalent', 'not_equivalent',
                                           'coverage', 'differential',
                                           'timeout', 'test_tool', 'is_equal_coverage'])


class evotest:

    def __init__(self):

        self.config = get_config()
        self.dRegCp = None  # base
        self.classes_dir = None  # left
        self.mergeDir = None  # merge

        self.evosuite_diff_params = None
        self.suite_evosuite_diff = None

        self.sut_class = None
        self.java = Java(self.config['java_home'])
        self.maven = Maven(self.java, self.config['maven_home'])
        self.tests_dst = self.config["tests_dst"]
        self.project = GitProject(self.config["repo_dir"])
        self.projects_folder = self.config["projects_folder"]
        self.path_hash_csv = self.config["path_hash_csv"]
        self.path_output_csv = self.config["path_output_csv"]

    def gen_evosuite_diff(self, scenario):

        evosuite = Evosuite(
            java=self.java,
            classpath=self.classes_dir,
            sut_class=self.sut_class,
            params=self.evosuite_diff_params,
            tests_src=self.tests_dst + '/' + self.project.get_project_name() + '/' + scenario.get_merge_hash()
        )
        self.suite_evosuite_diff = evosuite.generate_differential(self.dRegCp)
        return self.suite_evosuite_diff

    def try_evosuite_diff(self, classes_dir, sut_class, mutant_dir):

        junit = JUnit(java=self.java, classpath=classes_dir)
        res = junit.run_with_mutant(self.suite_evosuite_diff, sut_class, mutant_dir)
        return res

    def compile_commits(self, scenario):
        java_file = self.find_java_files(self.project.get_path_local_project())
        data = [(scenario.get_base_hash(), "base"), (scenario.get_left_hash(), "left"),
                (scenario.get_right_hash(), "right"), (scenario.get_merge_hash(), "merge")]
        self.sut_class = scenario.get_sut_class()
        for hash in data:
            self.project.checkout_on_commit(".")
            self.project.checkout_on_commit(hash[0])
            self.project.checkout_on_commit(".")
            self.set_method_public(java_file)
            self.add_default_constructor(java_file)

            self.maven.compile(self.project.get_path_local_project(), 120, clean=True, install=True)
            self.maven.save_dependencies(self.project.get_path_local_project())
            dst = self.projects_folder + self.project.get_project_name() + "/" + data[3][0] + "/" + hash[1]
            if os.path.exists(dst):
                shutil.rmtree(dst)

            shutil.copytree(self.project.get_path_local_project(), dst)

    def generate_dependencies_path(self, scenario, commit_type):

        project_folder = self.projects_folder + self.project.get_project_name() + "/" + scenario.get_merge_hash() + "/"
        dependencies = [(x[0], x[2]) for x in os.walk(project_folder + commit_type + "/target/dependency/")]
        dep_path = dependencies[0][0]
        final_path = ""
        print(dep_path)
        for dependency in dependencies[0][1]:
            final_path = final_path + dep_path + dependency + ":"

        final_path = dep_path + ":" + final_path + project_folder + commit_type + "/target/classes/"

        return final_path

    def write_output_csv(self, output_base, output_left, output_merge, scenario):

        output = [self.project.get_project_name(), scenario.get_merge_hash(), "False"]
        if output_base[1] and not output_left[1] and output_merge[1]:
            output = [self.project.get_project_name(), scenario.get_merge_hash(), "True"]

        with open(self.path_output_csv, 'a') as fd:
            writer = csv.writer(fd)
            writer.writerow(output)

    @staticmethod
    def set_method_public(file):

        for line in fileinput.input(file, inplace=1):
            if re.search(r'(protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])', line):
                print(line.replace("protected", "public").rstrip())
            elif re.search(r'(private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])', line):
                print(line.replace("private", "public").rstrip())
            else:
                print(line.rstrip())

    @staticmethod
    def add_default_constructor(file):
        for line in fileinput.input(file, inplace=1):
            if re.search("(((|public|final|abstract|private|static|protected)(\\s+))?(class)(\\s+)(\\w+)(<.*>)?(\\s+extends\\s+\\w+)?(<.*>)?(\\s+implements\\s+)?(.*)?(<.*>)?(\\s*))\\{$", line):
                print(line.rstrip()+"\npublic Ball(){}\n")

            elif re.search(".*?private final.*", line):
                print(line.replace("private final", "private").rstrip())
            else:
                print(line.rstrip())

    @staticmethod
    def find_java_files(dir_path):
        #dir_path = self.project.get_path_local_project()
        #dir_path = os.path.dirname(os.path.realpath(__file__))
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.java') and ("Test" not in str(file)):
                    return root + '/' + str(file)





if __name__ == '__main__':

    evo = evotest()
    #evo.add_default_constructor("/home/ines/Documents/ic/Project-stuff/example-project-evosuite/src/main/java/br/com/Ball.java")
    java_file = evo.find_java_files(evo.project.get_path_local_project())

    merge = MergeScenario(evo.project.get_path_local_project, evo.path_hash_csv)
    merge_scenarios = merge.get_merge_scenarios()

    for scenario in merge_scenarios:
        evo.compile_commits(scenario)

        evo.dRegCp = evo.generate_dependencies_path(scenario, "base")
        evo.classes_dir = evo.generate_dependencies_path(scenario, "left")
        evo.mergeDir = evo.generate_dependencies_path(scenario, "merge")

        # thread_evosuite_diff = threading.Thread(target=evo.gen_evosuite_diff)

        print("waiting analisys finish")
        evo.gen_evosuite_diff(scenario)

        # thread_evosuite_diff.start()
        # thread_evosuite_diff.join()

        print("ended")

        # time.sleep(5)

        test_result = evo.try_evosuite_diff(evo.classes_dir, evo.sut_class, evo.dRegCp)  # fail on base

        # time.sleep(4)

        test_result2 = evo.try_evosuite_diff(evo.classes_dir, evo.sut_class, evo.classes_dir)  # pass on left

        # time.sleep(4)

        test_result3 = evo.try_evosuite_diff(evo.classes_dir, evo.sut_class, evo.mergeDir)  # fail on merge

        # test_result = evo.try_evosuite_diff(evo.dRegCp, evo.sut_class, evo.classes_dir) #ok

        # test_result = evo.try_evosuite_diff(evo.classes_dir, evo.sut_class, evo.classes_dir) #ok

        # test_result = evo.try_evosuite_diff(evo.dRegCp, evo.sut_class, evo.dRegCp) #notok ----

        # test_result = evo.try_evosuite_diff(evo.mergeDir, evo.sut_class, evo.mergeDir) #ok

        # test_result = evo.try_evosuite_diff(evo.classes_dir, evo.sut_class, evo.mergeDir)#ok

        # test_result = evo.try_evosuite_diff(evo.dRegCp, evo.sut_class, evo.mergeDir)#ok

        # test_result = evo.try_evosuite_diff(evo.mergeDir, evo.sut_class, evo.dRegCp)#notok ----

        # test_result = evo.try_evosuite_diff(evo.mergeDir, evo.sut_class, evo.classes_dir)#ok

        print(test_result)
        print(test_result2)
        print(test_result3)
        evo.write_output_csv(test_result, test_result2, test_result3, scenario)
