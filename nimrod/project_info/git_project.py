from git import Repo

class GitProject():

    def __init__(self,path_local_project):
        self.path_local_project = path_local_project
        self.project_name = path_local_project.split("/")[-1]
        self.analysis_directory_path = path_local_project.split("subjects")[0]
        self.repo = Repo(self.path_local_project)

    def get_path_local_project(self):
        return self.path_local_project

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
