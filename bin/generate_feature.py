from mhctools import MHCflurry
import pandas as pd
import sys

def generate_feature(psm_file, pdeep_result, autoRT_result, predfull_result, out_file, denovo):
    df_psm = pd.read_csv(psm_file, sep='\t')
    df_pdeep = pd.read_csv(pdeep_result, sep = '\t')
    df_pdeep['peptide'] = df_pdeep['pdeep_title'].apply(lambda x: x.split('|')[0])
    df_autoRT = pd.read_csv(autoRT_result, sep = '\t')
    df_autoRT['delta_rt'] = df_autoRT.apply(lambda row: abs(row['y'] - row['y_pred']), axis = 1)
    df_predfull = pd.read_csv(predfull_result, sep = '\t')

    df = pd.merge(df_pdeep, df_autoRT, left_on=['index', 'peptide'], right_on=['index', 'x'])
    df = pd.merge(df, df_predfull, how = 'left', left_on=['index', 'peptide'], right_on=['title', 'peptide'])
    df_feature = df[['index', 'peptide', 'similarity', 'delta_rt', 'full_similarity']]
    df_feature = pd.merge(df_psm, df_feature, on=['index', 'peptide'])

    if denovo != 'denovo':
        df_feature = df_feature[df_feature['peptide'].apply(lambda x: len(x) <= 15)]
        alleles = ["HLA-B*08:01","HLA-A*26:01","HLA-A*01:01","HLA-A*02:01","HLA-A*03:01","HLA-A*24:02","HLA-B*07:02","HLA-B*27:05","HLA-B*39:01","HLA-B*40:01","HLA-B*58:01","HLA-B*15:01"]
        predictor = MHCflurry(alleles=alleles)
        peptide_list = df_feature['peptide']
        n_peptides = len(peptide_list)
        affinity_all = predictor.predict_peptides_dataframe(peptide_list)
        for name in alleles:
            affinity = affinity_all[affinity_all['allele'] == name]['percentile_rank'].tolist()
    #        affinity = affinity_all.iloc[n_peptides * i: n_peptides * (i + 1)]['percentile_rank'].tolist()
            df_feature[name] = affinity
  
    df_feature.to_csv(out_file, index = False, sep = '\t')
"""
psm_file = 'generate_feature/test_rawPSMs.txt'
pdeep_result = 'generate_feature/test_similarity_SA.txt'
autoRT_result = 'generate_feature/test_results.txt'
predfull_result = 'generate_feature/full_similarity.txt'
out_file = 'generate_feature/feature.txt'
"""
args = sys.argv
psm_file, pdeep_result, autoRT_result, predfull_result, out_file, denovo = args[1:]
generate_feature(psm_file, pdeep_result, autoRT_result, predfull_result, out_file, denovo)
