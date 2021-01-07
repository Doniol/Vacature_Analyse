class test:
    ''' Class for testing algorithm effectiveness
    '''
    def __init__(self, algorithm, test_data, test_answers):
        ''' Init test

        algorithm: The function that needs to be run, it needs to be a function that only requires input data as an argument
        test_data: The input data for the algorithm
        test_answers: The answers to the give input data
        results: 
        '''
        self.algorithm = algorithm
        self.test_data = test_data
        self.test_answers = test_answers
        self.results = []
    
    def run_algorithm(self):
        ''' Run the algorithm, and store the result in self.results
        '''
        self.results = self.algorithm(self.test_data)
    
    def print_results(self):
        ''' Print self.results
        '''
        print(self.results, type(self.results))

    def get_correct_result_count(self):
        ''' Return how many of the results aren't actual relevant keywords

        return: A integer representing how many of the results aren't actual relevant keywords
        '''
        correct_answers = len([result for result in self.results if result in self.test_answers])
        return correct_answers

    def get_false_positive(self):
        ''' Returns a percentage of how many keywords were found by the algorithm, but weren't actually desired

        return: A float representing a percentage of how many keywords were found by the algorithm, but weren't actually desired
        '''
        false_positives = len(self.results) - self.get_correct_result_count()
        return false_positives / len(self.results) * 100

    def get_false_negative(self):
        ''' Returns a percentage of how many keywords were in the set of answers, but weren't found by the tested algorithm

        return: A float representing a percentage of how many keywords were in the set of answers, but weren't found by the tested algorithm
        '''
        false_negatives = len([answer for answer in self.test_answers if answer not in self.results])
        return false_negatives / len(self.test_answers) * 100
    
    def get_true_positive(self):
        ''' Returns a percentage of how many found keywords are actually relevant keywords

        return: A float representing a percentage of how many found keywords are actually relevant keywords
        '''
        true_positives = self.get_correct_result_count()
        return true_positives / len(self.results) * 100

    def calc_score(self, weight_false_positive, weight_false_negative):
        ''' Return a score based on the false positive- and negatives

        return: A integer representing a score based on the false positive- and negatives
        '''
        false_positive_score = self.get_false_positive() * weight_false_positive
        false_negative_score = self.get_false_negative() * weight_false_negative
        # Calculate score, the higher (closer to 0), the better
        score = -1 * (false_positive_score + false_negative_score)
        return score

    def get_test_results(self, weight_false_positive, weight_false_negative, print_on):
        ''' Either prints or returns a set of different test scores

        return: If selected, 3 different scores representing the effectiveness of the algorithm, if not selected, nothing is returned
        '''
        # Either prints the results of all relevant tests, or returns them
        if print_on:
            print("False Negatives: ", self.get_false_negative(), "%", " of test answers.")
            print("False Positives: ", self.get_false_positive(), "%", " of algorithm results.")
            print("Calculated Score: ", self.calc_score(weight_false_positive, weight_false_negative), ".")
        else:
            return self.get_false_negative(), self.get_false_positive(), self.calc_score(weight_false_positive, weight_false_negative)
            