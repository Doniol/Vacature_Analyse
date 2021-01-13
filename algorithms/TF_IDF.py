import spacy
from spacy.lang.en.stop_words import STOP_WORDS as stop_words
from spacy_langdetect import LanguageDetector
from pipelines.pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
nlp = spacy.load('nl_core_news_sm')
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
from typing import List, Dict

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def TF_IDF_get_results(dataset: List[str]) -> Dict[str, int]:
    ''' This function uses the TF-IDF algorithem to find the most important words.

        dataset: A list containing sentences.
        return: A dict containing the most important words and how much the dataset contains these words.
    '''
    # List for the spacy tokens
    tokens = []

    # List for the word frequency
    freq = {}

    for d in dataset:
        doc = nlp(d)
        tmp = []
        for token in doc:
            # Check if word is either a stopword, interpunction or a bracket...
            if token.is_stop or token.is_punct or token.is_bracket:
                # ...skip this word.
                continue
            # ...else if it's a noun, proper noun or a adjective...
            elif token.pos_ == "NOUN" or token.pos_ == "PROPN" or token.pos_ == "ADJ":
                # ...add it to the temperory list.
                tmp.append(token.text)
                # If the word does not exist...
                if token.text not in freq:
                    # ...add it to the dict, with value 1.
                    freq[token.text.lower()] = 1
                else:
                    # ...else increase the value by 1.    
                    freq[token.text.lower()] += 1
        # Add all the contents from tmp to tokens.
        tokens.append(" ".join(tmp))

    # Init TF-IDF
    tfIdfVectorizer=TfidfVectorizer(use_idf=True)

    # Transform the tokens, so that pandas can work with it.
    tfIdf = tfIdfVectorizer.fit_transform(tokens)

    # Create a dataframe with the words as index and "TF-IDF" as column.
    df = pd.DataFrame(tfIdf[0].T.todense(), index=tfIdfVectorizer.get_feature_names(), columns=["TF-IDF"])
    df = df.sort_values('TF-IDF', ascending=False)
    # Select the Top25 most important words.
    df = df.head(25)
    # Transform the dataframe to a dict.
    tmp = df.to_dict("dict")["TF-IDF"]

    new_freq = {}
    # Copy the word frequency from freq to new_freq using the important words as keys.
    for word in tmp:
        if word in freq:
            new_freq[word] = freq[word]

    return new_freq

if __name__ == "__main__":
    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_in = "pocdb"
    user_in = "pocuser"
    password_in = "pocuser"
    db_in = pipeline_in(host, port, database_in, user_in, password_in)

    dataset = db_in.get_descriptions(1000)
    tmp = TF_IDF_get_results(dataset)
    for i in tmp:
        print(tmp[i], "\t:", i)
