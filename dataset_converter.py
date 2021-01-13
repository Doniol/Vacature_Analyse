import spacy
from spacy import displacy
from spacy_langdetect import LanguageDetector
from html import entities
nlp = spacy.load('nl_core_news_md')
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)

from typing import List, Tuple, Dict

def apply_lemmatization(keywords: str) -> List[str]:
    ''' This funtion turns the keywords string into a list and applies lemmatization to these keywords

    keywords: The string with the keyword list
    return: A list of the keywords
    '''
    keywords_lemmatized = []
    # loop though every keyword
    keyword_list = keywords.split(",")
    for word in keyword_list:
        to_lemma = nlp(word)
        lemmatized = ""
        # lemmanize the keyword
        for token in to_lemma:
            lemmatized += str(token.lemma_) + " "
        keywords_lemmanized.append(lemmatized.strip())
    return keywords_lemmatized

def format_test_data_with_keywords(offer: str) -> List[str, List[str], List[str], List[str], List[str], List[str], List[str], List[str], List[str]]:
    ''' This function turns a textfile into usable data to be stored in a database and used for the tests
    The textfile has both a relevant and all keywords lists

    text: A string of the dataset txt file
    return: A list with for every job offer in the dataset: a list with the job offer, the relevant keywords, 
        the relevant keywords with lemmatization, every keyword, every keyword with lemmatization
    '''
    # split the offers between their categories, single relevevant keywords, relevant keywords, single keywords, keywords and the job offer
    rest_single_relevant_split = offer.split("SINGLE RELEVANTE KERNWOORDEN:")
    rest_relevant_split = rest_single_relevant_split[0].split("RELEVANTE KERNWOORDEN:")
    rest_single_keywords_split = rest_relevant_split[0].split("SINGLE KERNWOORDEN:")
    job_offer_keywords_split = rest_single_keywords_split[0].split("KERNWOORDEN:")
    
    # assign the list parts to their respective type 
    job_offer = job_offer_keywords_split[0]
    keywords_list = job_offer_keywords_split[1]
    single_keywords_list = rest_single_keywords_split[1]
    relevant_keywords_list = rest_relevant_split[1]
    single_relevant_keywords_list =  rest_single_relevant_split[1]
    
    #turn the strings into lists of words with and without lemmatization
    keywords = [word.strip() for word in keywords_list.replace('\n', '').split(",")]
    lemma_Keywords = apply_lemmanization(keywords_list)
    single_keywords = [word.strip() for word in single_keywords_list.replace('\n', '').split(",")]
    lemma_single_keyword =  apply_lemmanization(single_keywords_list)
    relevant_keywords = [word.strip() for word in relevant_keywords_list.replace('\n', '').split(",")]
    lemma_relevant_keywords = apply_lemmanization(relevant_keywords_list)
    single_relevant_keywords = [word.strip() for word in single_relevant_keywords_list.replace('\n', '').split(",")]
    lemma_single_relevant_keywords = apply_lemmanization(single_relevant_keywords_list)
    
    #add the whole job offer data set together and add it to the list
    return [job_offer, relevant_keywords, lemma_relevant_keywords, single_relevant_keywords, lemma_single_relevant_keywords, keywords, lemma_Keywords, single_keywords, lemma_single_keyword]


def format_test_data_without_keywords(offer: str) -> List[str, List[str], List[str], List[str], List[str], List[str], List[str], List[str], List[str]]:
    ''' This function makes from the textfile usable data to store in a database and be used for the tests
    The textfile has only a relevant keywords list

    text: a string of the dataset txt file
    return: a list with for every job offer in the dataset a list with the job offer, the relevant keywords, 
        the relevant keywords with lemmatization, every keyword, every keyword with lemmatization
    '''
    # split the offers between their categories, single relevevant keywords, relevant keywords and the job offer
    rest_single_relevant_split = offer.split("SINGLE RELEVANTE KERNWOORDEN:")
    job_offer_relevant_split = rest_single_relevant_split[0].split("RELEVANTE KERNWOORDEN:")

    # assign the list parts to their respective type 
    job_offer = job_offer_relevant_split[0]
    relevant_keywords_list = job_offer_relevant_split[1]
    single_relevant_keywords_list = rest_single_relevant_split[1]


    #turn the strings into lists of words with and without lemmatization
    relevant_keywords = [word.strip() for word in relevant_keywords_list.replace('\n', '').split(",")]
    lemma_relevant_keywords = apply_lemmanization(relevant_keywords_list)
    single_relevant_keywords = [word.strip() for word in single_relevant_keywords_list.replace('\n', '').split(",")]
    lemma_single_relevant_keywords = apply_lemmanization(single_relevant_keywords_list)
    
    #add the whole job offer data set together and add it to the list
    return [job_offer, relevant_keywords, lemma_relevant_keywords, single_relevant_keywords, lemma_single_relevant_keywords, [], [], [], []] 


def create_dataset(filename: str) -> List[str, List[str], List[str], List[str], List[str], List[str], List[str], List[str], List[str]]:
    ''' This function creates the dataset by calling the requiered function

    filename: The name of the file you want to get data from
    return: The formatted version which can be uploaded to the database  
    '''
    f = open(filename, encoding="utf-8")
    f_text = f.read()
    job_offer_data_sets = f_text.split("VACATURE:")
    job_offer_data_sets.pop(0)
    formatted_test_data = []
    
    for data_set in job_offer_data_sets:
        # check if the data set has a piece about every keyword not just the relevant
        if data_set.find("SINGLE KERNWOORDEN") == -1:
            test_data = format_test_data_without_keywords(data_set)
            print(test_data)
            formatted_test_data.append(test_data)
        else:
            test_data = format_test_data_with_keywords(data_set)
            print(test_data)
            formatted_test_data.append(test_data)
    return formatted_test_data


def main():
    create_dataset("ict vacatures in text form.txt")


main()