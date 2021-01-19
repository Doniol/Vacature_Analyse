import spacy
from spacy.lang.nl.stop_words import STOP_WORDS
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
from typing import List, Dict
nlp = spacy.load('nl_core_news_sm')


def read_article(file_name):
    file = open(file_name, "r", encoding='utf-8')
    article = file.readlines()

    #article = filedata.split(". ")
    sentences = []

    for sentence in article:
        if sentence[-1] == "\n":
            sentence = sentence[:-1]
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop() 
    
    return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    ''' This function depends on Cosine similarity
     is a measure of similarity between two non-zero vectors of an inner product space that measures the cosine 
     of the angle between them. Since we will be representing our sentences as the bunch of vectors,
     we can use it to find the similarity among sentences.
     Its measures cosine of the angle between vectors. Angle will be 0 if sentences are similar.
    '''

    #Check is the word is not in the stop word 
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # This is where we will be using cosine similarity to find similarity between sentences
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix
  

def word_count(descriptions: List[str])-> Dict[str,int]:
    ''' This function counts the words of the sentences that were summerized with simmilarity matrix algorithm.

        descriptions: A list containing words.
        return: A dict containing the most important words and how much those words are appeerd in the text.
    '''
    new_list = nlp("".join(descriptions))
    word_counter = {}

    for token in new_list:
        # Check if word is either a stopword, interpunction or a bracket...
        if token.is_stop or token.is_punct or token.is_bracket or token.is_currency:
            # skip the world
            continue
        # ...else if it's a noun, proper noun or a adjective...
        elif token.pos_ == "NOUN" or token.pos_ == "PROPN" or token.pos_ == "ADJ":
            # if the world does not exit
            if token.text not in word_counter:
                # add it to the word counter with value 1 
                word_counter[token.text] = 1
            else:
                # else increase the value with 1
                word_counter[token.text] += 1
    return word_counter


def generate_summary(sentences, top_n=15):
    summarize_text = []

 
    # Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, STOP_WORDS)

    # Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    

    for i in range(top_n):
     # add the summarized text to the list
      summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Count words
    return word_count(summarize_text)

if __name__ == "__main__":
    import os
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "../dataset/similarity_vacature.txt")
    print(generate_summary(read_article(filename), top_n=30))
