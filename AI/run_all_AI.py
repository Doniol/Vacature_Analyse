from preprocessing import load_datasets
from basic_AI import BasicAI
from AI_LSTM import AI_LSTM_Padding, AI_LSTM_Padding_bidirectional
from AI_seq2seq import AI_Seq2SeqNoPadding, AI_Seq2SeqPadding
import numpy as np
from keras.backend import clear_session
from basic_test import test


def train_AI(AI: BasicAI, out_file: str, in_file: str=None):
    ''' Function for training a selected AI

    AI: The selected AI
    out_file: File in which to save the trained weights
    in_file: File from which to load existing weights
    '''
    AI.train_AI(1, out_file, weights_input=in_file)


def run_AI(AI, file: str):
    ''' Function for running a selected AI

    AI: The selected AI
    file: File from which the weights need to be loaded
    '''
    #TODO: Make the answers dynamically retrievable via a file or the dataset pipeline
    x = np.asarray([AI.get_x_data()[0]])
    # Answers for vac_1
    ans = ["besturing", "beveiliging", "optimalisatie", "hbo", "it-opleiding", "php", "laravel", "vue", "scrum", "git", "htmlvijf", "javascript", "bitbucket", "jira", "nodejs", "mysql", "bootstrap", "oplossingsgericht", "analytisch", "nederlands", "engelse", "duitse", "software", "engineer", "it", "developer", "softwaresysteem", "besturing", "beveiliging", "optimalisatie", "interne", "systemen", "gemotiveerde", "optimaliseren", "nederlandse", "embedded", "microcontroller", "c++"]
    AI_test = test(None, x, ans, AI.run_AI(x, file, 10))
    AI_test.get_test_results(0.5, 1, True)


def main():
    ''' Main function
    In this case used to run and/or train different AI's.
    Note that not all AI's can be ran/trained at the same time. Why this is, I can't figure out, so just don't be surprised when you
     try to run/train multiple AI's, and you get errors.
    To run/train an AI, simply uncomment the desired part.
    '''
    # Load datasets
    datasets = load_datasets(["vac_1", "vac_2", "vac_3"])

    # Create AI
    AI_L_P = AI_LSTM_Padding(datasets, 1000)
    AI_L_P_b = AI_LSTM_Padding_bidirectional(datasets, 1000)

    AI_S_P = AI_Seq2SeqPadding(datasets, 1000, 4)
    AI_S_NP = AI_Seq2SeqNoPadding(datasets, 4)

    # Train AI
    # print("AI_LSTM_Padding_1")
    # train_AI(AI_L_P, "AI\obj\AI_LSTM_Padding_1")
    # print("AI_LSTM_Padding_bidirectional_1")
    # train_AI(AI_L_P_b, "AI\obj\AI_LSTM_Padding_bidirectional_1")

    # print("AI_Seq2SeqPadding_1")
    # train_AI(AI_S_P, "AI\obj\AI_Seq2SeqPadding_1")
    # print("AI_Seq2SeqNoPadding_1")
    # train_AI(AI_S_NP, "AI\obj\AI_Seq2SeqNoPadding_1")

    # Run AI
    # print("AI_LSTM_Padding_1")
    # run_AI(AI_L_P, "AI\obj\AI_LSTM_Padding_1")
    # print("AI_LSTM_Padding_bidirectional_1")
    # run_AI(AI_L_P_b, "AI\obj\AI_LSTM_Padding_bidirectional_1")

    # Create exactly the same AI anew in the function call, if i just reference to the existing AI it starts fucking up and giving weirdass errors
    # print("AI_Seq2SeqPadding_1")
    # run_AI(AI_S_P, "AI\obj\AI_Seq2SeqPadding_1")
    # print("AI_Seq2SeqNoPadding_1")
    # run_AI(AI_S_NP, "AI\obj\AI_Seq2SeqNoPadding_1")


main()
