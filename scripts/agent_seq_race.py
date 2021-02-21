import random
import argparse
import re
import json

def generate_training_seq(condition, concept, shapes, seed):
    random.seed(seed)
    train_qs, retrieval_practice, worked_examples = [], [], []
    if concept == "Facts":
        for shape in shapes:
            if condition == "Retrieval Practice": # this loop needs to change if we duplicate brds for retrieval practice
                retrieval_practice = retrieval_practice + [shape + "_" + "1" + l for l in ["a", "b", "c"]]
                worked_examples = worked_examples + [shape + "_" + "1" + "_we"]
            else:
                retrieval_practice = retrieval_practice + [shape + "_" + "1" + l for l in ["a", "b"]]
                worked_examples = worked_examples + [shape + "_" + "1" + "_we" for n in range(2)]
    else:
        for shape in shapes:
            order = random.sample(range(2,6), 4) # shuffle q order
            if condition == "Retrieval Practice":
                we_n = [order[0]] # one WE, three RP
                rp_n = order[1:]
            else:
                we_n = order[:2] # two WE, two RP
                rp_n = order[2:]
            retrieval_practice = retrieval_practice + [shape + "_" + str(n) for n in rp_n]
            worked_examples = worked_examples + [shape + "_" + str(n) + "_we" for n in we_n]
    if condition == "Retrieval Practice":
        # randomize RP order (since we're using all the questions)
        random.shuffle(retrieval_practice)
        if concept == "Facts":
            prefixes = [item[:-3] for item in retrieval_practice]
        else:
            prefixes = [item[:-2] for item in retrieval_practice]
        for i in range(len(shapes)):
            idx = prefixes.index(shapes[i]) # find first instance of shape
            we_q = worked_examples[i]
            # insert the chosen WE before the first RP
            retrieval_practice.insert(idx, we_q)
            prefixes.insert(idx, shapes[i])
        train_qs = retrieval_practice
    else:
        for (we_q, rp_q) in zip(worked_examples, retrieval_practice):
            train_qs = train_qs + [[we_q, rp_q]]
        random.shuffle(train_qs)
        flat_list = [item for sublist in train_qs for item in sublist]
        train_qs = flat_list

    return train_qs

def to_json(df, train_seqs, post_seq, fname, use_memory):
    data = {"training_set1": []}
    for i in range(len(df)):
        agent_id = df[i][0]
        if df[i][2] == "Skills":
            ops = ["Diamond", "Sun", "Command", "Bullseye"]
        else:
            ops = []
        training_qs = []
        for q in train_seqs[i]:
            if re.search("_we", q):
                training_qs.append({"set_params": {"examples_only": True,
                                                    "test_mode": False}})
            else:
                training_qs.append({"set_params": {"examples_only": False,
                "test_mode": False}})
            training_qs.append({"question_file": str("../NewExperiment/" + q + ".brd")}) # question path
        seq = {"agent_name": agent_id,
        "agent_type": "MemoryAgent",
        "stay_active": True,
        "dont_save": True,
        "args": {
            "search_depth": 2,
            "when_learner": "decisiontree",
            "where_learner": "MostSpecific",
                        "use_memory": use_memory,
            # "heuristic_learner": "proportioncorrect",
            # "how_cull_rule": "mostparsimonious",
            "planner": "numba",
            # "numerical_epsilon": 0.0,
            "c": 0.277,
            "alpha": 0.177,
            "tau": -0.7,
            "exp_beta": 4,
            "noise_mu": 0,
            "noise_sigma": 1,
            "decay_acc": 0,
            "default_gamma": 0.1,
            "exp_gamma": 0.01,
            "operators": {
                'Sun': ['spiky', 'roundish', 'unfilled', 'multi'],
                'Diamond': ['spiky', 'filled', 'squarish', 'single'],
                'Command': ['roundish', 'squarish', 'unfilled', 'single'],
                'Bullseye': ['roundish', 'unfilled', 'multi']
            },
            "agent_id": agent_id,
            "feature_set" : ["Equals"],
            "function_set": ["RipFloatValue", "Add", "Subtract", "Multiply", "Divide"] + ops,
            "activation_path": fname + ".txt"
            },
        "problem_set": [{"set_params":
                        {"HTML": "model/HTML/new_experiment.html", #html path
                        # "examples_only": True,
                        "repetitions": 1}
                        }] +
                        training_qs +
                        [{"set_params" :
                            {"examples_only" : False,
                            "test_mode": True,
                            "repetitions": 1}}] +
                        [{"question_file": str("../NewExperiment/" + q + ".brd")} for q in post_seq] #question_path
        }
        data["training_set1"].append(seq)
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='CSV filename', type=str, required=True)
    parser.add_argument('-n', help='Number of agents per condition', type=int, required=True)
    parser.add_argument('-m', '--memory', help='Use memory? (boolean)', type=bool, required=True)
    parser.add_argument('-s','--seed', help='Random seed (for reproducibility)', type=float, required=False)
    args = vars(parser.parse_args())
    fname = args["f"]
    n = args["n"]
    seed = args.get("seed")
    use_memory = args.get("memory")
    random.seed(seed)

    shapes = ["diamond", "sun", "command", "bullseye"]
    n_shapes = len(shapes)
    if seed:
        seeds = [random.random() for i in range(n*n_shapes)]

    conditions = ["RP_S", "WE_S", "RP_F", "WE_F"]
    training_type = ["Retrieval Practice", "Worked Examples", "Retrieval Practice", "Worked Examples"]
    training_concept = ["Skills", "Skills", "Facts", "Facts"]
    df = [[]] * (n*n_shapes) # write to csv
    train_seqs = [[]] * (n*n_shapes) # store training sequence for json
    post_seq = ["prepost2_" + str(n) for n in random.sample([2,4,6,8,10,12,14,16], 8)] # this needs to be generalized in case we add more shapes

    for i in range(len(conditions)):
        for j in range(n):
            s = seeds[j + n*i] if seed else None
            agent_id = conditions[i] + "_" + str(j+1)
            train_seq = generate_training_seq(training_type[i], training_concept[i], shapes, s)
            train_seqs[j + n*i] = train_seq
            df[j + n*i] = [agent_id] + [training_type[i]] + [training_concept[i]] + train_seq + post_seq
    js = to_json(df, train_seqs, post_seq, fname, use_memory)
    with open(fname + ".json", 'w') as f:
        json.dump(js, f)

    header = "agent_id," + "training_type," + "training_concept," + ",".join(["q" + str(i) for i in range(1, n_shapes*4+1)]) +  "," + ",".join(["post_q" + str(i) for i in range(1, 9)]) + "\n"
    with open(fname + ".csv", 'w') as f:
        f.write(header)
        for i in range(n*4):
            f.write(",".join(df[i]) + "\n")
    

if __name__ == "__main__":
    main()
