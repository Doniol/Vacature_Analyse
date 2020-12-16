from AI_LSTM import AI_LSTM_Padding, AI_LSTM_Padding_bidirectional
from AI_seq2seq import AI_Seq2SeqNoPadding, AI_Seq2SeqPadding
from AI_LSTM import load_datasets
import numpy as np

def main():
    # Load datasets
    datasets = load_datasets(["vac_1", "vac_2", "vac_3"])

    # Create AI
    AI_L_P = AI_LSTM_Padding(datasets, 1000)
    AI_L_P_b = AI_LSTM_Padding_bidirectional(datasets, 1000)

    AI_S_NP = AI_Seq2SeqNoPadding(datasets, 4)
    AI_S_P = AI_Seq2SeqPadding(datasets, 1000, 4)

    # Train AI
    AI_L_P.train_AI(200, "AI_LSTM_Padding_1")
    AI_L_P_b.train_AI(200, "AI_LSTM_Padding_bidirectional_1")

    AI_S_NP.train_AI(200, "AI_Seq2SeqNoPadding_1")
    AI_S_P.train_AI(200, "AI_Seq2SeqPadding_1")

    # Run AI
    # x = np.asarray(AI_L_P.get_x_data()[0])
    # AI_L_P.run_AI(x, "AI_LSTM_Padding_1", 10)
    # AI_L_P_b.run_AI(x, "AI_LSTM_Padding_bidirectional_1", 10)
    
    # AI_S_NP.run_AI(x, "AI_Seq2SeqNoPadding_1", 10)
    # AI_S_P.run_AI(x, "AI_Seq2SeqPadding_1", 10)


main()