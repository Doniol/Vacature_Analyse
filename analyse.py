from pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
from pipeline_analyse_interface import pipeline_analyse_to_db as pipeline_out
import spacy
nlp = spacy.load('nl_core_news_sm')


def get_words_at_index(desciptions, index):
    word_dict = {}
    for description in desciptions:
        word_list = nlp(description)
        if word_list[index].text in word_dict:
            word_dict[word_list[index].text][0] += 1
        else:
            word_dict[word_list[index].text] = [1, index]
    return word_dict

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
    input_descriptions = db_in.get_descriptions()[:10]
    words_at_3 = get_words_at_index(input_descriptions, 2)
    words_at_4 = get_words_at_index(input_descriptions, 3)

    db_out.add_dict(words_at_3, "institute_ict")
    db_out.add_dict(words_at_4, "institute_marketing")
    print("donerio")


main()