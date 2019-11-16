import os
import re
import shutil
import fileinput
from nimrod.tools.java import Java
from nimrod.tools.maven import Maven
from nimrod.project_info.git_project import GitProject


class Project_dependecies:

    def __init__(self, config, path_local_project, path_local_module_analysis, project_name):
        self.config = config

        self.sut_class = None
        self.dRegCp = None  # base
        self.classes_dir = None  # left
        self.mergeDir = None  # merge

        self.java = Java(self.config['java_home'])
        self.maven = Maven(self.java, self.config['maven_home'])
        self.tests_dst = self.config["tests_dst"]
        self.project = GitProject(path_local_project, path_local_module_analysis, project_name)
        self.projects_folder = self.config["projects_folder"]
        self.path_hash_csv = self.config["path_hash_csv"]
        self.path_output_csv = self.config["path_output_csv"]

    def compile_commits(self, scenario):
        java_file = self.find_java_files(self.project.get_path_local_project(), scenario.merge_scenario.get_sut_class())
        data = [(scenario.merge_scenario.get_base_hash(), "base"), (scenario.merge_scenario.get_left_hash(), "left"),
                (scenario.merge_scenario.get_right_hash(), "right"), (scenario.merge_scenario.get_merge_hash(), "merge")]
        self.sut_class = scenario.merge_scenario.get_sut_class()
        for hash in data:
            try:
                self.project.checkout_on_commit(".")
                self.project.checkout_on_commit(hash[0])
                self.project.checkout_on_commit(".")
                self.set_method_public(java_file)
                #self.add_default_constructor(java_file)

                self.maven.compile(self.project.get_path_local_project(), 120, clean=True, install=True)
                self.maven.save_dependencies(self.project.get_path_local_project())
                dst = self.projects_folder + self.project.get_project_name() + "/" + data[3][0] + "/" + hash[1]
                if os.path.exists(dst):
                    shutil.rmtree(dst)

                shutil.copytree(self.project.get_path_local_module_analysis(), dst)
            except:
                print ("The commit "+str(hash) +" was not compilable")

    @staticmethod
    def find_java_files(dir_path, sut_class):
        # dir_path = self.project.get_path_local_project()
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        class_name = sut_class.split('.')[-1]
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.java') and ("Test" not in str(file)) and (class_name in file):
                    return root + '/' + str(file)

    def generate_dependencies_path(self, scenario, commit_type):

        project_folder = self.projects_folder + self.project.get_project_name() + "/" + scenario.merge_scenario.get_merge_hash() + "/"
        dependencies = [(x[0], x[2]) for x in os.walk(project_folder + commit_type + "/target/dependency/")]
        dep_path = dependencies[0][0]
        final_path = ""
        print(dep_path)
        for dependency in dependencies[0][1]:
            final_path = final_path + dep_path + dependency + ":"

        final_path = dep_path + ":" + final_path + project_folder + commit_type + "/target/classes/"

        return final_path

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
            search = re.search("(((|public|final|abstract|private|static|protected)(\\s+))?(class)(\\s+)(\\w+)(<.*>)?(\\s+extends\\s+\\w+)?(<.*>)?(\\s+implements\\s+)?(.*)?(<.*>)?(\\s*))\\{$", line)
            classname = ""
            if re.search("(public) (.*) { this\(null\); }",line):
                pass
            elif search:
                test = search[0].split(" ")
                for word in test:
                    if "public" not in word and "static" not in word and "class" not in word:
                        classname = word
                        #print(classname)
                        break

                print(line.rstrip()+"\npublic "+classname +"(){}\n") #ajust this later

            elif re.search(".*?private final.*", line):
                print(line.replace("private final", "private").rstrip())
            else:
                print(line.rstrip())