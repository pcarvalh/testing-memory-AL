import fit_model
import random
import numpy as np
import pandas as pd
def run(df, b0, b1, c, alpha, tau, s):
    full_df = pd.DataFrame()
    activations = {}
    retrieval_probs = {}
    exp_inds = {}
    for pid in df:
        activations[pid] = {}
        exp_inds[pid] = {}
        retrieval_probs[pid] = np.zeros(16)
        # correctness_copy = df[pid]["correctness"][-16:]
        for i in range(24+16): # 24 questions
            activated_skill = df[pid]["answer_seq"][i]
            correct_skill = df[pid]["correct_ans"][i]
            question_type = df[pid]["question_type_seq"][i]
            if i > 23: #post-test
                # get all previously answered skills
                other_skills = set(df[pid]["answer_seq"][:i])
                other_skills.discard(correct_skill)
                other_skills = list(other_skills)
                # get skill to compare to
                compr_skill = random.choice(other_skills)
                if correct_skill in activations[pid] and activations[pid][correct_skill][-1] < activations[pid][compr_skill][-1]:
                    # change activated skill to other incorrect skill if random skill is higher
                    activated_skill = compr_skill
                    df[pid]["answer_seq"][i] = correct_skill
                    df[pid]["correctness"][i] = 0
                elif correct_skill in activations[pid]:
                    activated_skill = correct_skill
                    df[pid]["answer_seq"][i] = correct_skill
                    df[pid]["correctness"][i] = 1
                # otherwise don't modify anything if we haven't yet used the correct skill
            if activated_skill not in activations[pid]:
                exp_inds[pid][activated_skill] = np.array([i])
                activations[pid][activated_skill] = np.array([-np.inf])
            else:
                exp_inds[pid][activated_skill] = np.append(exp_inds[pid][activated_skill], i)
            fit_model.update_activation_itr(activated_skill, question_type, activations[pid], exp_inds[pid], b0, b1, c, alpha, t=i)
        sub_df = pd.DataFrame.from_dict(df[pid])
        sub_df['pid'] = [pid] * sub_df.shape[0]
        full_df = full_df.append(sub_df)

    full_df.to_csv('sim_results.csv')

def main():
    np.random.seed(1)
    df = fit_model.read_data("immediate_test_clean.csv")

    fitted_params = np.loadtxt("fitted_params.txt")
    b0, b1, c, alpha, tau, s = fitted_params
    run(df, b0, b1, c, alpha, tau, s)
if __name__ == "__main__":
    main()
