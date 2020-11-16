from pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
from pipeline_analyse_interface import pipeline_analyse_to_db as pipeline_out
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keybert import KeyBERT
import spacy
from spacy_langdetect import LanguageDetector
nlp = spacy.load('nl_core_news_md')
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
import torch
from torch import nn
import torch.nn.functional as F


# https://towardsdatascience.com/transformers-from-scratch-in-pytorch-8777e346ca51 Implementation incoming


def clean_input(doc):
    cleaned_doc = ""
    nlp_doc = nlp(doc)
    for token in nlp_doc:
        if token.is_punct or token.is_bracket or token.is_currency or token.shape_ == "X" or token.shape_ == "x" or token.is_space:
            continue
        if token.pos_ == "NOUN" or token.pos_ == "PROPN" or token.pos_ == "ADJ":
            cleaned_doc += " " + token.lemma_
    return cleaned_doc

def main():
    # Wat is the input?
        # 1. TF-IDF results, words connected to a value between 0 and 1 that shows its relevance within multiple different texts
        # 2. Sentences
            # 2.1. Full sentences, containing stop-words
            # 2.2. Cleaned sentences, stripped of stop-words
            # 2.3. Lemmanized sentences, each word is lemmanized
            # 2.4. Processed sentences, stripped of stop-words and lemmanized
        # 3. List of words (adjectives, nouns and names) with associated data
        # 4. List of named entities and associated data
        # 5. List of noun chunks and associated data
        # 6. Other kind of preprocessing?
    
    # For testing purposes, we choose to research whether 2.4 would work
    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_in = "pocdb"
    user_in = "pocuser"
    password_in = "pocuser"
    db_in = pipeline_in(host, port, database_in, user_in, password_in)

    # How to fix the problem with a varying amount of inputs? (Each sentence/list contains a different amount of words)
        # 1. Recurrent NNs
        # 2. Recursive NNs
        # 3. Sequence2sequence, word embeddings
        # 4. Transformers, bijv Google BERT
        # 5. Ready to use libraries, bijv keyBERT
    # Currently being researched
    # PyTorch checken
    
    # Test 1: keyBERT
    # input_descriptions = db_in.get_descriptions(20)
    # for desc in input_descriptions:
    #     desc_nlp = nlp(desc)
    #     if desc_nlp._.language["language"] == "en":
    #         input_descriptions = desc
    #         break
    # input_descriptions = clean_input(input_descriptions)
    # print(input_descriptions)
    # model = KeyBERT('distilbert-base-nli-mean-tokens')
    # keywords = model.extract_keywords(input_descriptions, keyphrase_length=1, stop_words='english', top_n=10)
    # print(keywords)

    # Test 2: pyTorch

    # Test 3: RNN
    



main()