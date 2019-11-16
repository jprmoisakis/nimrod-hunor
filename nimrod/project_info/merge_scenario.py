from nimrod.project_info.commit import Commit
import csv


class MergeScenario:

    def __init__(self, path_local_clone="", merge_information=""):
        self.path_local_clone = path_local_clone
        self.path_merge_scenarios = merge_information
        self.merge_scenario = self.identify_merge_scenarios(merge_information)

    def get_merge_scenarios(self):
        return self.merge_scenarios

    def identify_merge_scenarios(self, merge_information):
        merge_scenarios = []
        commit = Commit(merge_information[5], merge_information[3], merge_information[4], merge_information[2], merge_information[6])#, merge_information[5])#, merge_information[6], merge_information[7])
        return commit
