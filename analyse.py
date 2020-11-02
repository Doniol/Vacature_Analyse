from pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
from pipeline_analyse_interface import pipeline_analyse_to_db as pipeline_out
import spacy
from spacy import displacy
from spacy_langdetect import LanguageDetector
from html import entities
nlp = spacy.load('nl_core_news_sm')
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)


''' This functions calculates the word frequencies in each descriptions. It only
    calculates if the POS of the token is a NOUN, a PROPN or a ADJ.

descriptions:   A list of strings
return:         A dict, containing words (str) as keys and word frequency (int) as values
'''
def get_words_at_index(descriptions: list) -> dict:
    word_dict = {}
    unworthy = {}
    for description in descriptions:
        word_list = nlp(description)
        if word_list._.language["language"] == "nl":
            for token in word_list:
                if token.is_punct or token.is_bracket or token.is_currency or token.shape_ == "X" or token.shape_ == "x" or token.is_space:
                    continue
                # print(token.text, token.lemma_, token.pos_, token.tag_)
                if token.pos_ == "NOUN" or token.pos_ == "PROPN" or token.pos_ == "ADJ":
                    # print("Worthy")
                    if token.lemma_ in word_dict:
                        word_dict[token.lemma_] += 1
                    else:
                        word_dict[token.lemma_] = 1
                # print()
    # word_dict = []
    # for description in descriptions:
    #     word_list = nlp(description)
    #     if word_list._.language["language"] == "nl":
    #         for token in word_list:
    #             if token.is_punct or token.is_bracket or token.is_currency or token.shape_ == "X" or token.shape_ == "x" or token.is_space or token.is_stop:
    #                 continue
    #             elif token not in word_dict:
    #                 word_dict.append(token)

    return word_dict


''' This functions prints the lemma, the POS and the tag of a token, but only if it's
    the desired word.

inputs:         A dict, containing words (str) as keys and word frequency (int) as values
'''
def checker(inputs: dict):
    words = []
    for key in inputs:
        print(key.lemma_)
        ans = input("Is this a desired word? y/n")
        if ans == "y":
            words.append(key)
    print("\n\n\n")
    for word in words:
        print(word.lemma_, word.pos_, word.tag_)


''' This functions prints the 'text' and the label of the entity annotations from the tokens.
    It also explains what the label means.

things:         A list of strings
'''
def get_details(things: list):
    for text in things:
        doc = nlp(text)
        for ent in doc.ents:
            print(ent.text, ent.label_, spacy.explain(ent.label_))


''' This functions initializes the pipelines, grabs the descriptions from the
    database, analyses them and sends the output of the analyse to the
    INNO-database.
'''
def main():
    host = "weert.lucimmerzeel.nl"
    port = "5432"
    database_in = "pocdb"
    user_in = "pocuser"
    password_in = "pocuser"
    db_in = pipeline_in(host, port, database_in, user_in, password_in)

    database_out = "innodb"
    user_out = "innouser"
    password_out = "innouser"
    db_out = pipeline_out(host, port, database_out, user_out, password_out)
    print("analysing")
    input_descriptions = db_in.get_descriptions(-1)
    # input_descriptions = [desc for desc in input_descriptions if nlp(desc)._.language["language"] == "nl"]
    # # print(input_descriptions)

    # for desc in input_descriptions:
    #     doc = nlp(desc)
    #     for token in doc:
    #         if token.is_stop or token.is_punct or token.is_space:
    #             continue
    #         elif token.is_digit or token.is_alpha:
    #             print(token.text)

    words_at_3 = get_words_at_index(input_descriptions[0:2000])
    # checker(words_at_3)

    db_out.clear_all_tables()

    affirmation = input("Continue?")

    print("Uploading...")
    db_out.add_dict(words_at_3, "institute_ict")

    # get_details(input_descriptions)


main()
