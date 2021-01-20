from pipelines.pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
from pipelines.pipeline_analyse_interface import pipeline_analyse_to_db as pipeline_out
import spacy
from spacy import displacy
from spacy_langdetect import LanguageDetector
from html import entities
nlp = spacy.load('nl_core_news_md')
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)

from typing import List, Tuple, Dict

def get_baseline_results(descriptions: List[str]) -> Dict[str, int]:
    ''' This functions gets a baseline, every noun and pronoun are seen as keywords

    descriptions: A list of strings containing the descriptions of the job offers
    return: A dict, containing words (str) as keys and word frequency (int) as values
    '''
    word_dict = {}
    for description in descriptions:
        word_list = nlp(description)
        # Check if the job offer is dutch
        if word_list._.language["language"] == "nl":
            for token in word_list:
                # Check if token (word) is a noun or pronoun
                if token.pos_ == "NOUN" or token.pos_ == "PROPN":
                    if token.lemma_ in word_dict:
                        word_dict[token.lemma_] += 1
                    else:
                        word_dict[token.lemma_] = 1
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
    input_descriptions = db_in.get_descriptions(10)
    clear_institue = False
    baseline_results = get_baseline_results(input_descriptions)

    if(clear_institue):
        db_out.clear_entries_institute('baseline')

    print("Uploading...")
    db_out.add_dict(baseline_results, "baseline")

