from pipelines.pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
from pipelines.pipeline_analyse_interface import pipeline_analyse_to_db as pipeline_out
import spacy
from rake_spacy import Rake
from summa import keywords
from summa import summarizer
from spacy import displacy
from spacy_langdetect import LanguageDetector
from html import entities
nlp = spacy.load('nl_core_news_md')
r = Rake(max_length = 3, nlp=nlp)


nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
from typing import List, Tuple, Dict

def get_combo_results(descriptions: List[str]) -> Dict[str, int]:
    ''' This function uses the rake algorithm to get keywords and the summary function of textrank

    descriptions: A list containing the job offer desccriptions
    return: A dictionary with as key the word and as value the amount of times the word
        has been found as a keyword in different offers
    '''
    word_dict = {}
    for description in descriptions:
        summary = summarizer.summarize(description)
        word_list = nlp(summary)
        # check if the job offer is dutch otherwise ignore it 
        if word_list._.language["language"] == "nl":
            words = r.apply(description)
            for word in words:
                if all(c.isalpha() or c.isspace() for c in str(word[1])):
                    #ignore non nouns, proper noun and adjectives
                    if len(word[1]) >1 or (word[1][0].pos_ == "NOUN" or word[1][0].pos_ == "PROPN"):
                    #check if a word, wordgroup contains only capitals, in which case it's probably an acronym, save that acronym in caps
                        if str(word[1]).isupper():
                            if str(word[1]) in word_dict:
                                word_dict[str(word[1])] += 1
                            else:
                                word_dict[str(word[1])] = 1
                        else:
                            if str(word[1].lemma_) in word_dict:
                                word_dict[str(word[1].lemma_)] += 1
                            else:
                                word_dict[str(word[1].lemma_)] = 1
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

    keywords = get_combo_results(input_descriptions)

    #db_out.clear_entries_institute('combo')
    #for keyword in keywords:
    #    print(keyword)
    print("Uploading...")
    db_out.add_dict(keywords, 'combo')
    
    
