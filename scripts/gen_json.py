import pandas as pd
import json
import argparse

def create_json(order, use_memory):
    data = {"training_set1": []}
    for id in order.index[0:]:
        test_qs = order.loc[id, 'V1':'V16'].values.tolist()
        post_qs = order.loc[id, 'q01':'q16'].values.tolist()

        seq = {"agent_name": id,
                "agent_type": "ModularAgent",
                "stay_active": True,
                "dont_save": True,
                "args": {
    		    "when_learner": "trestle",
    		    "where_learner": "mostspecific",
    				"heuristic_learner": "proportioncorrect",
    				"how_cull_rule": "mostparsimonious",
    				"planner": "fo_planner",
    				"search_depth": 1,
    				"numerical_epsilon": 0.0,
                    "use_memory": use_memory
    			  },
                 "feature_set" : ["equals"],
                 "function_set": ["add", "subtract", "multiply", "divide", "circ_rule", "trap_rule", "tria_rule"],
                 "problem_set": [{"set_params":
     				               {"HTML": "model/HTML/worked_example.html",
                     				"examples_only": True,
                     				"repetitions": 1}
     			                 }] +
                                 [{"question_file": str("../Final/" + q + ".brd")} for q in test_qs] +
                                 [{"set_params" :
                                     {"examples_only" : False,
                                     "repetitions": 1}}] +
                                 [{"question_file": str("../Final/" + q + ".brd")} for q in post_qs]

              }
        data["training_set1"].append(seq)
    return(data)

def main():
    parser = argparse.ArgumentParser(description="get paths for data files")
    parser.add_argument("--data", "-d")
    parser.add_argument("--memory", "-m")
    parser.add_argument("--file", "-f")

    args = parser.parse_args()
    order = pd.read_csv(args.data, index_col = 0)
    data = create_json(order, use_memory=args.memory)
    with open(args.file, 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    main()
