class test:
    def __init__(self, algorithm, test_data, test_answers):
        self.algorithm = algorithm
        self.test_data = test_data
        self.test_answers = test_answers
        self.results = []
    
    def run_algorithm(self):
        self.results = algorithm(self.test_data)
    
    def get_correct_result_count(self):
        correct_results = 0
        for result in self.results:
            if result in self.test_answers:
                correct_results += 1
        return correct_results

    def calc_success_rate(self):
        # Calculate percentage of how many of the resulting words actually appear in given the set of answers
        return self.get_correct_result_count() / len(self.results) * 100
    
    def calc_score(self, answers, incorrect_weight, missing_weight):
        # Calculate score of results
        # Score is based on both the resulting words that are contained with the answers
        # But also takes into consideration test_answers that didn't appear in the results
        unnecessary_results = len(self.results) - self.get_correct_result_count()
        missing_answers = len([[answer] if answer not in self.results for answer in self.test_answers])

        return 100 - (incorrect_weight * unnecessary_results + missing_weight * missing_answers)