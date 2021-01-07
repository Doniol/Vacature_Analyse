# This Seq2Seq library requires an older version of Python: v3.7.8; because with this version of python, older versions of keras and tensorflow can be installed; 
#  v2.2.4 and v1.13.1 respectively. And those versions are necessary for running Seq2Seq
import seq2seq.seq2seq
from seq2seq.seq2seq.models import SimpleSeq2Seq
from keras.backend import clear_session
from typing import List, Any, Dict, Union, Tuple
from basic_AI import BasicAI, BasicAIPadding, BasicAINoPadding
from preprocessing import load_datasets


class AI_Seq2SeqPadding(BasicAIPadding):
    ''' AI using Seq2Seq and padding its' in- and output arrays.
    '''
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], filler: int, 
                 depth: Union[int, List[int]]) -> None:
        ''' Init AI

        datasets: A tuple containing the dataset inputs, dataset desired outputs and all unique attributes in the dataset
        filler: An integer denoting the total length of both the in- and output arrays
        depth: Defines amount of LSTMs in the de- and encoders; 3 means 3 in both, while (3, 1) means 3 in the encoder
         and 1 in the decoder
        '''
        # Create model
        model = SimpleSeq2Seq(input_dim=4, output_length=filler, output_dim=1, depth=depth)
    
        # Define how the AI needs to be filled: [correct answer, incorrect answer, what to use as filler]
        what_to_fill_with =[[1], [0], [1]]
        # Create AI
        BasicAIPadding.__init__(self, datasets, filler, what_to_fill_with, model)


class AI_Seq2SeqNoPadding(BasicAINoPadding):
    ''' AI using Seq2Seq witout padding the in- and output arrays.
    '''
    def __init__(self, datasets: Tuple[List[List[List[str]]], List[List[str]], List[List[str]]], depth: Union[int, List[int]]) -> None:
        ''' Init AI

        datasets: A tuple containing the dataset inputs, dataset desired outputs and all unique attributes in the dataset
        depth: Defines amount of LSTMs in the de- and encoders; 3 means 3 in both, while (3, 1) means 3 in the encoder
         and 1 in the decoder
        '''
        self.depth = depth
        # Create temporary model
        model = SimpleSeq2Seq(input_dim=4, output_length=1, output_dim=1, depth=self.depth)
        # Define how the AI needs to be filled: [correct answer, incorrect answer]
        what_to_fill_with =[[1], [0]]
        # Create AI
        BasicAINoPadding.__init__(self, datasets, what_to_fill_with, model)

    def update_model(self, output_length):
        ''' Create a new model to fit the selected outpu_length

        output_length: The length of the output array for the new model
        '''
        # Clear session to reset naming; layers are named using a number that keeps track of the amount of layers.
        #  If this number isn't reset, it will rise into the hundreds, while in reality, there's not that many layers because
        #  the old models were erased and their layers thus lost.
        clear_session()
        # Create and store new model
        self.model = SimpleSeq2Seq(input_dim=4, output_length=output_length, output_dim=1, depth=self.depth)
