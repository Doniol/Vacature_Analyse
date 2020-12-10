import spacy
from spacy.lang.en.stop_words import STOP_WORDS as stop_words
from spacy_langdetect import LanguageDetector
from pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
nlp = spacy.load('nl_core_news_sm')
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def TF_IDF_get_results(dataset):
    # host = "weert.lucimmerzeel.nl"
    # port = "5432"
    # database_in = "pocdb"
    # user_in = "pocuser"
    # password_in = "pocuser"
    # db_in = pipeline_in(host, port, database_in, user_in, password_in)

    # dataset = db_in.get_descriptions(1000)
    # dataset = [
    #     "Dit is een test.",
    #     "In deze test zitten strings.",
    #     "Ik weet niet meer wat ik in deze test moet zetten."
    # ]

    tokens = []
    for d in dataset:
        doc = nlp(d)
        tmp = []
        for token in doc:
            if token.is_stop or token.is_punct or token.is_bracket:
                continue
            elif token.pos_ == "NOUN" or token.pos_ == "PROPN" or token.pos_ == "ADJ":
                tmp.append(token.text)
        tokens.append(" ".join(tmp))


    tfIdfVectorizer=TfidfVectorizer(use_idf=True)
    tfIdf = tfIdfVectorizer.fit_transform(tokens)
    df = pd.DataFrame(tfIdf[0].T.todense(), index=tfIdfVectorizer.get_feature_names(), columns=["TF-IDF"])
    df = df.sort_values('TF-IDF', ascending=False)
    df = df.head(25)
    return df.to_dict("dict")["TF-IDF"]
