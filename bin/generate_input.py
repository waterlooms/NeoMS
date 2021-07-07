import pandas as pd
import numpy as np
from pyteomics import mgf
from math import log
import sys

def parse_mod(x):
    if x == '-':
        return ''
    mod_list = x.split(',')
    mod_pos = [x.split('_')[0] + ',Carbamidomethyl[C];' for x in mod_list]
    mod_str = ''
    for x in mod_pos:
        mod_str += x
    return mod_str


def generate_file(search_file_name, mgf_file_name, out_PSM, rt_train, rt_all, pdeep_input, pdeep_unique, denovo):
    df2 = pd.read_csv(search_file_name, sep='\t', skiprows=1,)
    spectra = mgf.read(mgf_file_name)
    ls = []
    for sp in spectra:
        ls.append([sp['params']['title'], sp['params']['rtinseconds']])

    df1 = pd.DataFrame(ls, columns=['title', 'rt'])
    df1['scan'] = df1['title'].apply(lambda x: int(x.split('.')[-2]))
    df = pd.merge(df1, df2, how = 'right', on = 'scan')
    if denovo != "denovo":
        df = df[df['plain_peptide'].apply(lambda x: len(x)) >= 8]
        df = df[df['plain_peptide'].apply(lambda x: len(x)) <= 15]
    else:
        df = df[df['plain_peptide'].apply(lambda x: len(x)) >= 6]
        df = df[df['plain_peptide'].apply(lambda x: len(x)) <= 30]
    df['mods'] = df['modifications'].apply(lambda x: parse_mod(x))
    df['score'] = df['e-value'].apply(lambda x: -log(x))

    df1 = df.groupby(['title']).head(1)

    df_PSMs = df[['title', 'charge', 'exp_neutral_mass', 'plain_peptide', 'mods', 'protein', 'score', 'xcorr', 'delta_cn', 'sp_score']]
    df_PSMs.columns = ['index', 'charge', 'mass', 'peptide', 'mods', 'protein', 'score', 'xcorr', 'delta_cn', 'sp_score']
    df_PSMs.to_csv(out_PSM, index = False, sep = '\t')

    df_rt_train = df1.sort_values(by = 'score', ascending = False)
    is_decoy = ['XXX' in x for x in df_rt_train['protein']]
    df_rt_train['is_decoy'] = is_decoy
    num_decoy = np.cumsum(is_decoy)
    df_rt_train['fdr'] = [num_decoy[i] / (i + 1) for i in range(len(num_decoy))]
    df_rt_train = df_rt_train[df_rt_train['fdr'] < 0.01]
    df_rt_train = df_rt_train[df_rt_train['is_decoy'] == False]
    df_rt_train = df_rt_train[['plain_peptide', 'rt', 'score']].copy()
    df_rt_train.columns = ['x', 'y', 'evalue']
    df_rt_train = df_rt_train.sort_values(by = 'evalue', ascending = False)
    df_rt_train = df_rt_train.groupby(['x']).head(1)
    df_rt_train['y'] /= 60
    df_rt_train = df_rt_train.sort_values(by = 'x')
    df_rt_train.to_csv(rt_train, index = False, sep = '\t')

    df_rt = df[['plain_peptide', 'rt', 'title']].copy()
    df_rt.columns = ['x', 'y', 'index']
    df_rt['y'] /= 60
    df_rt.to_csv(rt_all, index = False, sep = '\t')

    df_pdeep = df[['plain_peptide', 'modifications', 'charge']].copy()
    df_pdeep.columns = ['peptide', 'modifications', 'charge']
    df_pdeep['modifications'] = df_pdeep['modifications'].apply(lambda x: parse_mod(x))
    df_pdeep.to_csv(pdeep_input, index = False, sep = '\t')

    df_pdeep_unique = df_pdeep.groupby(['peptide', 'charge']).head(1)
    df_pdeep_unique.to_csv(pdeep_unique, index = False, sep = '\t')
    
args = sys.argv
search_file_name, mgf_file_name, out_PSM, rt_train, rt_all, pdeep_input, pdeep_unique, denovo = args[1:]
generate_file(search_file_name, mgf_file_name, out_PSM, rt_train, rt_all, pdeep_input, pdeep_unique, denovo)
