import difflib
from pyteomics import mass
import numpy as np
import sys
import pandas as pd

def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def compute_uniqueness(df):
    df['pep_len'] = df['peptide'].apply(lambda x: int(len(x)))
    df['mass_error'] = df.apply(lambda x: 1e6 * (mass.fast_mass(x['peptide']) - x['mass']) / x['mass'], axis=1)
    df['avg_mass_err'] = np.mean(df['mass_error'])

    index_set = df['index'].tolist()
    diff_all = {}
    for f in ['score', 'similarity', 'delta_rt', 'full_similarity']:
        diff_all[f + '_mean'] = []
        diff_all[f + '_var'] = []
        diff_all[f + '_min'] = []
        diff_all[f + '_max'] = []
    boundary = []
    for num in range(len(index_set)):
        if index_set[num] != index_set[num - 1]:
            boundary.append(num)
    boundary.append(len(index_set) + 1)
    for idx in range(len(boundary) - 1):
        target = df.iloc[boundary[idx]: boundary[idx + 1]]
        peptides = target['peptide'].tolist()
        peptides = [p.replace('I', 'L') for p in peptides]
        n = len(peptides)
        for f in ['score', 'similarity', 'delta_rt', 'full_similarity']:
            f_list = target[f].to_numpy()
            for i in range(n):
                diff = f_list - f_list[i]
                diff = np.delete(diff, i)
                diff_all[f + '_mean'].append(np.mean(diff) if len(diff) > 0 else 0)
                diff_all[f + '_var'].append(np.var(diff) if len(diff) > 0 else 0)
                diff_all[f + '_min'].append(min(diff) if len(diff) > 0 else 0)
                diff_all[f + '_max'].append(max(diff) if len(diff) > 0 else 0)
    for f in ['score', 'similarity', 'delta_rt', 'full_similarity']:
        df[f + '_mean'] = diff_all[f + '_mean']
        df[f + '_var'] = diff_all[f + '_var']
        df[f + '_min'] = diff_all[f + '_min']
        df[f + '_max'] = diff_all[f + '_max']
    df['Label'] = df['protein'].apply(lambda x: 'XXX' not in x)
    return df

def combine_feature(f1, f2, f_out):
    df1 = pd.read_csv(f1, sep = '\t')
    df2 = pd.read_csv(f2, sep = '\t')
    denovo = df1[['index', 'peptide', 'score', 'similarity', 'delta_rt', 'full_similarity']]
    denovo.columns = ['index', 'peptide_denovo', 'score_denovo', 'similarity_denovo', 'delta_rt_denovo', 'full_similarity_denovo']
    new_df = pd.merge(df2, denovo, how = 'left', on = 'index')
    new_df['delta_rt_denovo'] = new_df['delta_rt_denovo'].fillna(120)
    new_df = new_df.fillna(0)
    new_df['similarity_denovo'] = new_df['similarity_denovo'] - new_df['similarity']
    new_df['delta_rt_denovo'] = new_df['delta_rt_denovo'] - new_df['delta_rt']
    new_df['full_similarity_denovo'] = new_df['full_similarity_denovo'] - new_df['full_similarity']
    new_df['peptide_similarity'] = new_df.apply(lambda x: string_similar(x['peptide_denovo'], x['peptide']) if x['peptide_denovo'] != 0 else 0, axis = 1)
    compute_uniqueness(new_df)
    new_df.to_csv(f_out, index = False)

args = sys.argv
denovo_feature, dbsearch_feature, result_out = args[1:]
combine_feature(denovo_feature, dbsearch_feature, result_out)
