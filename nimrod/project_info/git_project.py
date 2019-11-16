from git import Repo

class GitProject:

    def __init__(self,path_local_project, path_local_module_analysis, project_name):
        self.path_local_project = path_local_project
        self.path_local_module_analysis = path_local_module_analysis
        self.project_name = project_name
        self.analysis_directory_path = path_local_project.split("subjects")[0]
        if (path_local_project != ""):
            self.repo = Repo(self.path_local_project)

    def get_path_local_project(self):
        return self.path_local_project

    def get_path_local_module_analysis(self):
        return self.path_local_module_analysis

    def get_project_name(self):
        return self.project_name

    def get_analysis_directory_path(self):
        return self.analysis_directory_path

    def checkout_on_commit(self, hash):

        self.repo.git.checkout(hash)
        sha = self.repo.head.object.hexsha

        if sha[:7] == hash[:7]:
            return True
        else:
            return False
