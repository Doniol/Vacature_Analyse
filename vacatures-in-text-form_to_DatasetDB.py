import spacy,psycopg2
from spacy import displacy
from spacy_langdetect import LanguageDetector
from html import entities
nlp = spacy.load('nl_core_news_md')
nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)

from typing import List, Tuple, Dict

def execute( output, query):
    # Connect to your postgres DB
    conn = psycopg2.connect(
        host="weert.lucimmerzeel.nl",
        port="5432",
        database="pocdb",
        user="pocuser",
        password="pocuser")

    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    if output:
        return cur.fetchall()
    return


def init(woordenlijsten):
    for lijst in woordenlijsten:
        execute( 0, """ DROP TABLE IF EXISTS vacatures_{};
                        DROP TABLE IF EXISTS vacatures_alle_woorden;
                        DROP TABLE IF EXISTS vacatures_zinnige_woorden;
                    """.format(lijst))

    for lijst in woordenlijsten:
        execute( 0, """ DROP TABLE IF EXISTS vacatures;
                        DROP TABLE IF EXISTS woorden;
                        DROP TABLE IF EXISTS alle_woorden;
                        DROP TABLE IF EXISTS zinnige_woorden;
                        DROP TABLE IF EXISTS {};
                    """.format(lijst))

    execute( 0, """ CREATE TABLE IF NOT EXISTS vacatures (
                        vacature_id SERIAL NOT NULL,
                        "vacature_tekst" VARCHAR(100000) NOT NULL,
                        PRIMARY KEY (vacature_id)
                );""")

    for lijst in woordenlijsten:
        execute( 0, """ CREATE TABLE {} (
                            woord_id SERIAL NOT NULL,
                            "woord" VARCHAR(255) NOT NULL UNIQUE,
                            PRIMARY KEY (woord_id)
                        );

                        CREATE TABLE vacatures_{} (
                            vacature_id integer REFERENCES vacatures,
                            woord_id integer REFERENCES {},
                            PRIMARY KEY (vacature_id, woord_id)
                        );""".format(lijst, lijst, lijst, lijst, lijst, lijst, lijst))


def to_test_database(woordenlijsten, input_rick):
    # Cycle through alle vacatures in input rick
    for vacature in input_rick:
        # INSERT vacature string
        vacature_id = execute( 1, """INSERT INTO vacatures (vacature_tekst) VALUES ('{}') RETURNING vacature_id""".format(vacature[0].replace("'", "''")))[0][0]
        print("Vacature toegevoegd: ID: {} - {}".format(vacature_id, vacature))

        # Voor iedere lijst in woordenlijst
        # Voor iedere lijst in woordenlijst
        for lijst_nr in range(1, len(woordenlijsten) + 1):
            print("Woordwnlijst: {}".format(woordenlijsten[lijst_nr - 1]))
            # Voor ieder woord in de lijst
            for woord in vacature[lijst_nr]:
                # Woord toevoegen aan de de bovengenoemde lijst
                execute( 0, """INSERT INTO {} (woord) VALUES ('{}') ON CONFLICT DO NOTHING""".format(woordenlijsten[lijst_nr - 1] , woord))

                # Selecteer het ID van het bovengenoemde woord
                woord_id = execute( 1, """SELECT woord_id FROM {} WHERE woord = '{}' """.format(woordenlijsten[lijst_nr - 1] , woord))[0][0]

                # Voeg de vacature_id gekoppeld met het woord_id toe aan de goede koppeltabel
                execute(0, """INSERT INTO vacatures_{} VALUES ({}, {}) ON CONFLICT DO NOTHING""".format(woordenlijsten[lijst_nr - 1], vacature_id, woord_id))
                print("Woord-ID: {:4} - Woord: {}".format(woord_id, woord))


def from_test_database(woordenlijsten):
    # Haalt de data uit de database om alles in een list te zetten
    vacatures = execute( 1,   """SELECT vacature_id, vacature_tekst FROM vacatures""".format())
    output = []
    for vacature in vacatures:
        lists = [vacature[1]]
        for woordlijst in woordenlijsten:
            words = []
            for every_word in execute( 1,   """SELECT {}.woord FROM {} WHERE woord_id IN (SELECT woord_id FROM vacatures_{} WHERE vacature_id = {})""".format(woordlijst, woordlijst, woordlijst, vacature[0])):
                words.append(every_word[0])
            lists.append(words)
        output.append(lists)
    print("Data from DATABASE: {}".format(output))
    return output


def apply_lemmanization(keywords: str)-> List[str]:
    ''' This funtion makes from the keyword string a list and applies lemmatization to these keywords
    keywords: The string with the keyword list
    return: a list of the keywords
    '''
    keywords_lemmanized = []
    # loop though every keyword
    keyword_list = keywords.split(",")
    for word in keyword_list:
        to_lemma = nlp(word)
        lemmanized = ""
        # lemmanize the keyword
        for token in to_lemma:
            lemmanized += str(token.lemma_) + " "
        keywords_lemmanized.append(lemmanized.strip())
    return keywords_lemmanized

def format_test_data_with_keywords(offer: str) -> List[List[str]]:
    ''' This function makes from the textfile usable data to store in a database and be used for the tests
    The textfile has both a relevant and all keywords list
    text: a string of the dataset txt file
    return: a list with for every job offer in the dataset a list with the job offer, the relevant keywords,
        the relevant keywords with lemmatization, every keyword, every keyword with lemmatization
    '''
    # split the offers between their categories, single relevevant keywords, relevant keywords, single keywords, keywords and the job offer
    rest_single_relevant_split = offer.split("SINGLE RELEVANTE KERNWOORDEN:")
    rest_relevant_split = rest_single_relevant_split[0].split("RELEVANTE KERNWOORDEN:")
    rest_single_keywords_split = rest_relevant_split[0].split("SINGLE KERNWOORDEN:")
    job_offer_keywords_split = rest_single_keywords_split[0].split("KERNWOORDEN:")

    # assign the list parts to their respective type
    job_offer = job_offer_keywords_split[0]
    keywords_list = job_offer_keywords_split[1]
    single_keywords_list = rest_single_keywords_split[1]
    relevant_keywords_list = rest_relevant_split[1]
    single_relevant_keywords_list =  rest_single_relevant_split[1]

    #turn the strings into lists of words with and without lemmatization
    keywords = [word.strip() for word in keywords_list.replace('\n', '').split(",")]
    lemma_Keywords = apply_lemmanization(keywords_list)
    single_keywords = [word.strip() for word in single_keywords_list.replace('\n', '').split(",")]
    lemma_single_keyword =  apply_lemmanization(single_keywords_list)
    relevant_keywords = [word.strip() for word in relevant_keywords_list.replace('\n', '').split(",")]
    lemma_relevant_keywords = apply_lemmanization(relevant_keywords_list)
    single_relevant_keywords = [word.strip() for word in single_relevant_keywords_list.replace('\n', '').split(",")]
    lemma_single_relevant_keywords = apply_lemmanization(single_relevant_keywords_list)

    #add the whole job offer data set together and add it to the list
    return [job_offer, relevant_keywords, lemma_relevant_keywords, single_relevant_keywords, lemma_single_relevant_keywords, keywords, lemma_Keywords, single_keywords, lemma_single_keyword]


def format_test_data_without_keywords(offer: str) -> List[List[str]]:
    ''' This function makes from the textfile usable data to store in a database and be used for the tests
    The textfile has only a relevant keywords list
    text: a string of the dataset txt file
    return: a list with for every job offer in the dataset a list with the job offer, the relevant keywords,
        the relevant keywords with lemmatization, every keyword, every keyword with lemmatization
    '''
    # split the offers between their categories, single relevevant keywords, relevant keywords and the job offer
    rest_single_relevant_split = offer.split("SINGLE RELEVANTE KERNWOORDEN:")
    job_offer_relevant_split = rest_single_relevant_split[0].split("RELEVANTE KERNWOORDEN:")

    # assign the list parts to their respective type
    job_offer = job_offer_relevant_split[0]
    relevant_keywords_list = job_offer_relevant_split[1]
    single_relevant_keywords_list = rest_single_relevant_split[1]


    #turn the strings into lists of words with and without lemmatization
    relevant_keywords = [word.strip() for word in relevant_keywords_list.replace('\n', '').split(",")]
    lemma_relevant_keywords = apply_lemmanization(relevant_keywords_list)
    single_relevant_keywords = [word.strip() for word in single_relevant_keywords_list.replace('\n', '').split(",")]
    lemma_single_relevant_keywords = apply_lemmanization(single_relevant_keywords_list)

    #add the whole job offer data set together and add it to the list
    return [job_offer, relevant_keywords, lemma_relevant_keywords, single_relevant_keywords, lemma_single_relevant_keywords, [], [], [], []]


def create_dataset(filename: str):
    f = open(filename, encoding="utf-8")
    f_text = f.read()
    job_offer_data_sets = f_text.split("VACATURE:")
    job_offer_data_sets.pop(0)
    formatted_test_data = []

    for data_set in job_offer_data_sets:
        # check if the data set has a piece about every keyword not just the relevant
        if data_set.find("SINGLE KERNWOORDEN") == -1:
            test_data = format_test_data_without_keywords(data_set)
            print(test_data)
            formatted_test_data.append(test_data)
        else:
            test_data = format_test_data_with_keywords(data_set)
            print(test_data)
            formatted_test_data.append(test_data)
    return formatted_test_data


def main():
    # Geeft aan welke tabellen aangemaakt/gecreeerd/verwijderd worden
    vorige_woordenlijsten = ['zinnige_kern_woorden', 'lamanised_woorden', 'zinnige_lamanised_woorden', 'kern_woorden']
    woordenlijsten = ['relevant_keywords', 'lemma_relevant_keywords', 'single_relevant_keywords', 'lemma_single_relevant_keywords', 'keywords', 'lemma_Keywords', 'single_keywords', 'lemma_single_keyword']
    vorige_woordenlijsten += woordenlijsten


    # Als hierboven wordt aangepast MOET de volgende regel geuncomment worden. PAS OP: De tabellen worden leeggemaakt
    #init(vorige_woordenlijsten)

    to_test_database(woordenlijsten, create_dataset("ict vacatures in text form.txt"))
    #from_test_database(woordenlijsten)


main()