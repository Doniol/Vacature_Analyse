from pipeline_verzamelaar_analyse import pipeline_db_to_analyse as pipeline_in
from pipeline_analyse_interface import pipeline_analyse_to_db as pipeline_out
import spacy
from spacy_langdetect import LanguageDetector
from html import entities
nlp = spacy.load('nl_core_news_sm')
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)


def get_words_at_index(desciptions, index):
    word_dict = {}
    for description in desciptions:
        word_list = nlp(description)
        if word_list[index].text in word_dict:
            word_dict[word_list[index].text][0] += 1
        else:
            word_dict[word_list[index].text] = [1, index]
    return word_dict


def get_is_excluded(token):
    return token.text in ["Ben", "vakantiedagen"]


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
    input_descriptions = db_in.get_descriptions(10) + ["Kurwa pierdzielona", "Petit merde, je ne parle pas anglais", "Avancati!", "Lengyel, Magyar", "Shit, fuck, crapbaskets", "Parlez vous een beetje henk?"]
    # input_descriptions = [desc for desc in input_descriptions if nlp(desc)._.language["language"] == "nl"]  
    # print(input_descriptions)

    # Replace the HTML-chars with UTF-8 chars
    # We're temporary only using the first description
    input_descriptions[0] = input_descriptions[0].replace("&egrave;", entities.html5["egrave;"])    # è
    input_descriptions[0] = input_descriptions[0].replace("&eacute;", entities.html5["eacute;"])    # é
    input_descriptions[0] = input_descriptions[0].replace("&euml;", entities.html5["euml;"])        # ë
    input_descriptions[0] = input_descriptions[0].replace("&ecirc;", entities.html5["ecirc;"])      # ê
    input_descriptions[0] = input_descriptions[0].replace("&ouml;", entities.html5["ouml;"])        # ö
    input_descriptions[0] = input_descriptions[0].replace("&iuml;", entities.html5["iuml;"])        # ï
    input_descriptions[0] = input_descriptions[0].replace("&nbsp;", entities.html5["nbsp;"])        # whitespace
    input_descriptions[0] = input_descriptions[0].replace("&rsquo;", "'")                           # ’ => '

    # "è, é, ë, ê, ö, ï"

    doc = nlp(input_descriptions[0])
    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue
        print(token.text)
    
    # words_at_3 = get_words_at_index(input_descriptions, 2)
    # words_at_4 = get_words_at_index(input_descriptions, 3)

    # db_out.add_dict(words_at_3, "institute_ict")
    # db_out.add_dict(words_at_4, "institute_marketing")


main()