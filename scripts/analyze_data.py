import pandas as pd

# Notes: it looks like about 1/3 of the un-categorized rows have just numbers as answers

def main():
    df = pd.read_csv("immediate_test_clean.csv")
    categories = ['tria_S', 'rect_S', 'trap_S', 'circ_S', 'tria_F', 'rect_F', 'trap_F', 'circ_F']
    df_not_categorized = df.loc[~df['activated_skill'].isin(categories)]
    df_not_numbers = df_not_categorized.loc[~df_not_categorized['activated_skill'].str.match(r"[-+]?\d*\.\d+|\d+")]\
        .sort_values(by=['activated_skill'])
    df_not_numbers.to_csv("miscategorized.csv", index=False)

if __name__ == "__main__":
    main()
