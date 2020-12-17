from AI_LSTM import AI_LSTM_Padding, AI_LSTM_Padding_bidirectional
from AI_seq2seq import AI_Seq2SeqNoPadding, AI_Seq2SeqPadding
from AI_LSTM import load_datasets
import numpy as np
from keras.backend import clear_session


def train_AI(AI, out_file, in_file=None):
    AI.train_AI(1, out_file, weights_input=in_file)


def run_AI(AI, file):
    x = np.asarray([AI.get_x_data()[0]])
    AI.run_AI(x, file, 10)


def main():
    # Load datasets
    datasets = load_datasets(["vac_1", "vac_2", "vac_3"])

    # Create AI
    AI_L_P = AI_LSTM_Padding(datasets, 1000)
    AI_L_P_b = AI_LSTM_Padding_bidirectional(datasets, 1000)

    AI_S_P = AI_Seq2SeqPadding(datasets, 1000, 4)
    AI_S_NP = AI_Seq2SeqNoPadding(datasets, 4)

    # Train AI
    print("AI_LSTM_Padding_1")
    AI_L_P.train_AI(1, "AI\obj\AI_LSTM_Padding_1", "AI\obj\AI_LSTM_Padding_1")
    print("AI_LSTM_Padding_bidirectional_1")
    train_AI(AI_L_P_b, "AI\obj\AI_LSTM_Padding_bidirectional_1", "AI\obj\AI_LSTM_Padding_bidirectional_1")

    #TODO: Cant run the following 2 in the same function?!?!?!??! (The Seq2Seq's that is)
    print("AI_Seq2SeqPadding_1")
    train_AI(AI_S_P, "AI\obj\AI_Seq2SeqPadding_1", "AI\obj\AI_Seq2SeqPadding_1")
    print("AI_Seq2SeqNoPadding_1")
    train_AI(AI_S_NP, "AI\obj\AI_Seq2SeqNoPadding_1", "AI\obj\AI_Seq2SeqNoPadding_1")

    # Run AI
    # print("AI_LSTM_Padding_1")
    # run_AI(AI_L_P, "AI\obj\AI_LSTM_Padding_1")
    # print("AI_LSTM_Padding_bidirectional_1")
    # run_AI(AI_L_P_b, "AI\obj\AI_LSTM_Padding_bidirectional_1")
    
    # Create exactly the same AI anew in the function call, if i just reference to the existing AI it starts fucking up and giving weirdass errors
    # print("AI_Seq2SeqPadding_1")
    # run_AI(AI_Seq2SeqNoPadding(datasets, 4), "AI\obj\AI_Seq2SeqPadding_1")
    # print("AI_Seq2SeqNoPadding_1")
    # run_AI(AI_Seq2SeqPadding(datasets, 1000, 4), "AI\obj\AI_Seq2SeqNoPadding_1")


main()