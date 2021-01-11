import spacy
import codecs

nlp = spacy.load('nl_core_news_md')

# All the code in this file is old, probably inefficient, and will most likely become obsolete quite quickly.
# Or faulty, stuff like non-words not entirely being filtered out.


def get_word_data(file: str):
    ''' Returns all kinds of data gained from the given file
    Returns 4 lists containing different kinds of information about the words in the file.
    The first list contains all of the individual words within the file.
    The second list contains the Part Of Speach (POS) tags for each of the abovementioned words.
    The third list contains the details POS tags for each of the abovementioned words.
    The fourth list contains the Suntactic Dependency for each of the abovementioned words.

    file: A already opened file that contains the to be analysed text
    '''
    # Tokenize a lowercased version of the file
    tokens = nlp(file.lower())
    words = []
    POSs = []
    tags = []
    deps = []
    for token in tokens:
        if token.is_punct or token.is_bracket or token.is_currency or token.shape_ == "X" or token.shape_ == "x" or token.is_space:
            # If a token is useless, don't bother doing anything with it
            continue
        else:
            # Otherwise, store all desired data from current token
            words.append(token.text)
            POSs.append(token.pos_)
            tags.append(token.tag_)
            deps.append(token.dep_)
    return words, POSs, tags, deps


def add_uniques(existing_list: List[str], entry_list: List[str]):
    #TODO: Useless? Probably, should check to make sure
    ''' Returns a list of unique entries

    existing_list: A list of datapoints, among which duplicates
    entry_list: Another list of datapoints, among which duplicates
    return: A list filled with unique entries
    '''
    # I genuinely don't know why I did this, I'd change it if we weren't so close to the deadline and I weren't so afraid of breaking something
    # My condolences to whoever has to decipher why I did what I did here
    # I am not responsible for any aneurisms caused by this
    uniques = set(existing_list)
    for entry in entry_list:
        uniques.add(entry)
    return list(uniques)


def load_datasets(dataset_names: List[str]):
    ''' Returns all relevant data from a list of given datasets
    Returns 3 different lists filled with data used in the training/running of AI
    The first list is one filled with 4 lists corresponding to the 4 types of information gained from
     get_word_data(). Each of those 4 lists contains a list of said type of data for each given dataset.
    The second list is one filled with lists that contain the desired answers to the corresponding datasets.
    The third list is, once again, a list filled with 4 lists corresponding to the 4 types of information
     gained from get_word_data(). Except these are filled with unique words from all the different datasets
     combined into 1 list.
    
    Example:
    List 1: [[[dataset_1.words], [dataset_2.words]], [[dataset_1.POSs], [dataset_2.POSs]], 
             [[dataset_1.tags], [dataset_2.tags]], [[dataset_1.deps], [dataset_2.deps]]]
    List 2: [[dataset_1.answers], [dataset_2.answers]]
    List 3: [[unique words], [unique POSs], [unique tags], [unique deps]]

    dataset_names: A list containing the names of the desired datasets
    return: A tuple of above explained lists
    '''
    input_sets = []
    answer_sets = []
    unique_words = []
    unique_POSs = []
    unique_tags = []
    unique_deps = []
    # Loop through all datasets
    for name in dataset_names:
        # Read the dataset in- and outputs
        text = codecs.open("dataset\\{0}.txt".format(name), "r", encoding="utf8").read()
        ans = codecs.open("dataset\\{0}_keywords.txt".format(name), "r", encoding="utf8").read()
        # Get lists of words, POSs, tags and deps from selected dataset
        processed_text = get_word_data(text)
        # Append data and answers to corresponding lists
        input_sets.append(processed_text)
        answer_sets.append(get_word_data(ans)[0])
        # Update the lists of unique entries
        unique_words = add_uniques(unique_words, processed_text[0])
        unique_POSs = add_uniques(unique_POSs, processed_text[1])
        unique_tags = add_uniques(unique_tags, processed_text[2])
        unique_deps = add_uniques(unique_deps, processed_text[3])
    return list(zip(*input_sets)), answer_sets, [unique_words, unique_POSs, unique_tags, unique_deps]
