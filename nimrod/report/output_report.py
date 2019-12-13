import csv
import os

class Output_report():

    def __init__(self, output_path):
        self.path_output_csv = output_path

    def write_output_results(self, project_name, scenario, tool, which_parent, criteria_validation, class_information, method_information):
        if (os.path.isfile(self.path_output_csv) == False):
            output = ["project_name", "merge_scenario", "tool", "evaluated_parent", "commit_pair", "criteria_validation", "failed_tests", "class_information", "method_information"]
            with open('persons.csv', 'wb') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow(output) #
                                            #self.write_each_result(output)

        self.write_each_result(self.formate_output_line(project_name, scenario.merge_scenario.get_merge_hash(), tool, which_parent, "base-parent", criteria_validation, 0, class_information, method_information))
        self.write_each_result(self.formate_output_line(project_name, scenario.merge_scenario.get_merge_hash(), tool, which_parent, "parent-merge", criteria_validation, 1, class_information, method_information))
        self.write_each_result(self.formate_output_line(project_name, scenario.merge_scenario.get_merge_hash(), tool, which_parent, "base-merge", criteria_validation, 2, class_information, method_information))

    def write_each_result(self, output):
        with open(self.path_output_csv, 'a') as fd:
            writer = csv.writer(fd)
            writer.writerow(output)

    def formate_output_line(self, project_name, merge, tool, which_parent, commit_pair, criteria_validation, id_information, class_information, method_information):
        if (len(criteria_validation) > 0 and criteria_validation[id_information] != None):
            return [project_name, merge, tool, which_parent, commit_pair, criteria_validation[id_information][0], criteria_validation[id_information][1], criteria_validation[id_information][2], class_information, method_information]
        else:
            return [project_name, merge, tool,
                                  which_parent, commit_pair, "NO_INFORMATION", "", "","",""]