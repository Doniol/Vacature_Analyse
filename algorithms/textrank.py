from pipelines.pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
from pipelines.pipeline_analyse_interface import pipeline_analyse_to_db as pipeline_out
import spacy
from summa import keywords
from summa import summarizer
from spacy import displacy
from spacy_langdetect import LanguageDetector
from html import entities
nlp = spacy.load('nl_core_news_md')

nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
from typing import List, Tuple, Dict


def get_textrank_results(descriptions = List[str])-> Dict[str, int]:
    ''' This function uses the textrank algorithm to get keywords

    descriptions: A list containing the job offer desccriptions
    return: A dictionary with as key the word and as value the amount of times the word
        has been found as a keyword in different offers
    '''
    word_dict = {}
    for description in descriptions:
        description_nlp = nlp(description)
        # check if the job offer is dutch otherwise ignore it 
        if description_nlp._.language["language"] == "nl":
            #get the keywords
            keywords_list = keywords.keywords(description).splitlines()
            # check if keyword should be added
            for key in keywords_list:
                # check if the key contains multiple words
                if " " in key:
                    #apply lemmatization on the key
                    multi_key = nlp(key)
                    lemma_key = ""
                    for token in multi_key:
                        lemma_key += str(token.lemma_) + " "
                    lemma_key.rstrip()
                    # check if it ready was added for this job offer
                    if lemma_key in word_dict:
                        word_dict[lemma_key] += 1
                    else:
                        word_dict[lemma_key] = 1
                # If the keyword is only one word
                else:
                    key_nlp = nlp(key)
                    if key_nlp[0].pos_ == "NOUN" or key_nlp[0].pos_ == "PROPN":
                        if str(key_nlp[0].lemma_) in word_dict:
                            word_dict[str(key_nlp[0].lemma_)] += 1
                        else:
                            word_dict[str(key_nlp[0].lemma_)] = 1

    return word_dict


def add_single_keyword(key: str, already_added: List[str], word_dict: Dict[str, int]) -> None:
    ''' This function is to check if a single keyword has already been added/counted for this job_offer
    When a keyword has already been added it will be ignored, if not, the keyword will be added to list

    key: A string of the keyword
    already_added: A list with the keywords which have already been added for this job offer
    word_dict: The dictionary with the keywords and amount they've been counted in job offers 
    '''
    key_nlp = nlp(key)
    #check if key is already used for this job offer
    if str(key_nlp[0].lemma_) not in already_added and str(key_nlp[0]) not in already_added: 
        #check if key contains words otherwise ignore it
        if all(c.isalpha() or c.isspace() for c in key):
            if key_nlp[0].pos_ == "NOUN" or key_nlp[0].pos_ == "PROPN":
                # check if the key is fully caps
                if str(key_nlp[0].lemma_) in word_dict:
                    word_dict[str(key_nlp[0].lemma_)] += 1
                    already_added.append(str(key_nlp[0].lemma_))
                else:
                    word_dict[str(key_nlp[0].lemma_)] = 1
                    already_added.append(str(key_nlp[0].lemma_))


def get_summarised_textrank_results(descriptions: List[str]) -> Dict[str, int]:
    ''' This function uses the textrank algorithm to get keywords after summarizing the text with textrank summary

    descriptions: A list containing the job offer desccriptions
    return: A dictionary with as key the word and as value the amount of times the word
        has been found as a keyword in different offers
    '''
    word_dict = {}
    for description in descriptions:
        already_added = []
        summary = summarizer.summarize(description)
        description_nlp = nlp(summary)
        # check if the job offer is dutch otherwise ignore it 
        if description_nlp._.language["language"] == "nl":
            #get the keywords
            keywords_list = keywords.keywords(description).splitlines()
            # check if keyword should be added
            for key in keywords_list:
                # check if the key contains multiple words
                if " " in key:
                    #apply lemmatization on the key
                    multi_key = nlp(key)
                    lemma_key = ""
                    for token in multi_key:
                        lemma_key += str(token.lemma_) + " "
                    lemma_key.rstrip()
                    already_added.append(lemma_key)
                    # check if it ready was added for this job offer
                    if lemma_key not in already_added:
                        if lemma_key in word_dict:
                            word_dict[lemma_key] += 1
                        else:
                            word_dict[lemma_key] = 1
                #check if key consists of multiple words
                add_single_keyword(key, already_added, word_dict)
    return word_dict


def main():
    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_in = "pocdb"
    user_in = "pocuser"
    password_in = "pocuser"
    db_in = pipeline_in(host, port, database_in, user_in, password_in)

    database_out = "InnoDB-test"
    user_out = "innouser"
    password_out = "innouser"
    db_out = pipeline_out(host, port, database_out, user_out, password_out)
    print("analysing")
    input_descriptions = db_in.get_descriptions(20)

    keywords = get_summarised_textrank_results(input_descriptions)   

    db_out.clear_entries_institute('textrank')
    print("Uploading...")
    db_out.add_dict(keywords, 'textrank')
    
    

