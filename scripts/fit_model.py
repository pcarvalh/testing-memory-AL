import pandas as pd
import numpy as np
import math
from pprint import pprint
from random import random
from scipy.optimize import minimize
def read_data(fname):
    df = pd.read_csv(fname)
    df = df.groupby(by=["prolific_id"])
    df = df.apply(lambda x : {"participant_concepts": x["participant_concepts"].unique()[0],
    "participant_training": x["participant_training"].unique()[0],
    "answer_seq": x["activated_skill"].to_numpy(),
    "correct_ans": x["correct_skill"].to_numpy(),
    "correctness": x["correctness"].to_numpy(),
    "question_type_seq": x["question_type"].to_numpy()})
    # df_idx = df.apply(lambda x : dict.fromkeys(x["answer_seq"]))
    df = df.to_dict()
    # df_idx = df_idx.to_dict()
    # for pid in df_idx:
    #     for ans in df_idx[pid]:
    #         df_idx[pid][ans] = np.zeros(40)
    #         df_idx[pid][ans][np.where(df[pid]["answer_seq"] == ans)[0]] = 1
    return df

def compute_activation_recursive(times, decay, beta):
    times = times + 1
    return beta + math.log(np.sum(np.power(times, -decay)))

def compute_decay(activations, exp_i, c, alpha):
    relevant_activations = activations[exp_i]
    decay = c*np.exp(relevant_activations)+alpha
    return decay

def compute_retrieval(activation, tau, s):
    # print("probability of retrieval:", (1/(1+math.exp((tau - activation[-1]) / s))))
    # return random() < (1/(1+math.exp((tau - activation) / s)))
    return (1/(1+math.exp((tau - activation[-1]) / s)))

def update_activation_itr(activated_skill, question_type, activations, exp_inds, b0, b1, c, alpha, t):
    for skill in activations:
        if question_type == "WE" and skill == activated_skill:
            beta = b0
        else:
            beta = b1
        decay = compute_decay(activations=activations[skill],
        exp_i = exp_inds[skill] - exp_inds[skill][0],
        c=c,
        alpha=alpha)
        activations[skill] = np.append(activations[skill], compute_activation_recursive(t - exp_inds[skill], decay, beta))

def calculate_training_activation(df, b0, b1, c, alpha, tau, s):
    activations = {}
    retrieval_probs = {}
    exp_inds = {}
    for pid in df:
        activations[pid] = {}
        exp_inds[pid] = {}
        retrieval_probs[pid] = np.zeros(16)
        for i in range(24+16): # 24 questions
            activated_skill = df[pid]["answer_seq"][i]
            correct_skill = df[pid]["correct_ans"][i]
            question_type = df[pid]["question_type_seq"][i]
            if i > 23:
                if activated_skill in activations[pid] and correct_skill in activations[pid]:
                    retrieval_probs[pid][i-24] = compute_retrieval(activations[pid][correct_skill], tau, s)
            if activated_skill not in activations[pid]:
                exp_inds[pid][activated_skill] = np.array([i])
                activations[pid][activated_skill] = np.array([-np.inf])
            else:
                exp_inds[pid][activated_skill] = np.append(exp_inds[pid][activated_skill], i)
            update_activation_itr(activated_skill, question_type, activations[pid], exp_inds[pid], b0, b1, c, alpha, t=i)
    return retrieval_probs

def sse(args):
    total = 0
    b0, b1, c, alpha, tau, s = args
    retrieval_probs = calculate_training_activation(df, b0, b1, c, alpha, tau, s)
    for pid in retrieval_probs:
        total += np.sum((df[pid]["correctness"][-16:] - retrieval_probs[pid])**2)
    return total

def main():
    # put these in the fitting function
    # "c": 0.277, "alpha": 0.177, "tau": -0.7, "exp_beta": 4
    initial_guess = [4, 0, 0.277, 0.177, -0.7, 1]
    global df
    df = read_data("immediate_test_clean.csv")
    fitted_params = minimize(sse, initial_guess, tol=1e-3, method="Powell")
    print(fitted_params)
    np.savetxt("fitted_params.txt", fitted_params["x"], fmt="%s")


if __name__ == "__main__":
    main()