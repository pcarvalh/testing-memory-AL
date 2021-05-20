import pandas as pd
import numpy as np

# Notes: it looks like about 1/3 of the un-categorized rows have just numbers as answers

def analyze_data():
    df = pd.read_csv("immediate_test_clean_race.csv")
    categories = ['tria_S', 'rect_S', 'trap_S', 'circ_S', 'tria_F', 'rect_F', 'trap_F', 'circ_F']
    df_not_categorized = df.loc[~df['activated_skill'].isin(categories)]
    df_not_numbers = df_not_categorized.loc[~df_not_categorized['activated_skill'].str.fullmatch(r"[-+]?\d*\.\d+|\d+")]\
        .sort_values(by=['activated_skill'])

    # processing: turn everything to lowercase and strip spaces
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.lower().str.replace(' ', '')

    # fix vocabulary mismatches
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.replace('length', 'l')
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.replace('height', 'h')
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.replace('width', 'w')
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.replace('base', 'b')
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.replace('area', 'a')
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.replace('a=', '')

    # adhere to common math notation for multiplication
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.replace('*', '')
    df_not_numbers['activated_skill'] = df_not_numbers['activated_skill'].str.replace('x', '')

    # print the most common un-categorized values
    print(df_not_numbers.groupby(['activated_skill']).size().nlargest(n=30))

    # df_not_numbers.to_csv("miscategorized.csv", index=False)


if __name__ == "__main__":
    analyze_data()
