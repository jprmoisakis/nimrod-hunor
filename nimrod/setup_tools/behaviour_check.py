class Behaviour_change:

    def check_different_test_results_for_commit_pair(self, parent_one, parent_two, path_suite):
        if len(parent_one[2].difference(parent_two[2])) > 0 or len(parent_two[2].difference(parent_one[2])) > 0:
            return [True, parent_one[2].difference(parent_two[2]).union(parent_two[2].difference(parent_one[2])), path_suite[1]]
        else:
            return [False, parent_one[2].difference(parent_two[2]).union(parent_two[2].difference(parent_one[2])), path_suite[1]]

    def check_different_test_results_for_merge_scenario(self, parent_one, parent_two, parent_tree, path_suite):
        if len(parent_one[2].intersection(parent_tree[2]).difference(parent_two[2])) > 0 or len(parent_two[2].difference(parent_one[2].intersection(parent_tree[2]))) > 0:
            return [True, parent_one[2].intersection(parent_tree[2]).difference(parent_two[2]).union(parent_two[2].difference(parent_one[2].intersection(parent_tree[2]))), path_suite[1]]
        else:
            return [False, parent_one[2].intersection(parent_tree[2]).difference(parent_two[2]).union(parent_two[2].difference(parent_one[2].intersection(parent_tree[2]))), path_suite[1]]