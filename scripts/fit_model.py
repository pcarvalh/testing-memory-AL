import pandas as pd
import numpy as np

def read_data(fname):
    df = pd.read_csv(fname)
    df = df.groupby(by=["prolific_id"])
    df = df.apply(lambda x : {"participant_concepts": x["participant_concepts"].unique()[0],
    "participant_training": x["participant_training"].unique()[0],
    "answer_seq": x["activated_skill"].to_numpy(),
    "correctness": x["correctness"].to_numpy(),
    "question_type_seq": x["question_type"].to_numpy()})
    df_idx = df.apply(lambda x : dict.fromkeys(x["answer_seq"]))
    df = df.to_dict()
    df_idx = df_idx.to_dict()
    for pid in df_idx:
        for ans in df_idx[pid]:
            df_idx[pid][ans] = np.where(df[pid]["answer_seq"] == ans)[0]
    return df, df_idx

def main():
    df, df_idx = read_data("immediate_test_clean.csv")

if __name__ == "__main__":
    main()