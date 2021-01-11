from keras.backend import clear_session
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Bidirectional
from typing import List, Any, Dict, Union, Tuple
from basic_AI import BasicAI, BasicAIPadding


class AI_LSTM_Padding(BasicAIPadding):
    ''' AI using LSTM and padding its' in- and output arrays.
    '''
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int) -> None:
        #TODO: Could add the option to customise the amount of LSTM layers or whether or not to make use of dropout layers
        ''' Inits the AI

        datasets: A tuple containing the dataset inputs, dataset desired outputs and all unique attributes in the dataset.
            sidenote: For a more specific denotion of what this tuple looks like, it's exactly the same as the output from the load_datasets() function in preprocessing.py.
        filler: An integer denoting the total length of both the in- and output arrays, said arrays will be padded up to the given size.
        '''
        # Create model
        model = Sequential()
        model.add(LSTM(256, input_shape=(None, 4), return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(256, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(128))
        model.add(Dropout(0.2))
        model.add(Dense(filler))

        # Define how the AI needs to be filled: [correct answer, incorrect answer, what to use as filler]
        what_to_fill_with = [1, 0, 1]
        # Create AI
        BasicAIPadding.__init__(self, datasets, filler, what_to_fill_with, model)


class AI_LSTM_Padding_bidirectional(BasicAIPadding):
    ''' AI using LSTM and padding its's in- and output arrays. Additionally, uses bidirectional LSTM layers instead of regular ones.
    '''
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int) -> None:
        #TODO: Could add the option to customise the amount of LSTM layers or whether or not to make use of dropout layers
        ''' Inits the AI

        datasets: A tuple containing the dataset inputs, dataset desired outputs and all unique attributes in the dataset.
            sidenote: For a more specific denotion of what this tuple looks like, it's exactly the same as the output from the load_datasets() function in preprocessing.py.
        filler: An integer denoting the total length of both the in- and output arrays, said arrays will be padded up to the given size.
        '''
        # Create model
        model = Sequential()
        model.add(Bidirectional(LSTM(256, return_sequences=True), input_shape=(None, 4)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(256, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(128)))
        model.add(Dropout(0.2))
        model.add(Dense(filler))

        # Define how the AI needs to be filled: [correct answer, incorrect answer, what to use as filler]
        what_to_fill_with = [1, 0, 1]
        # Create AI
        BasicAIPadding.__init__(self, datasets, filler, what_to_fill_with, model)
