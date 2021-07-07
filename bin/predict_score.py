import lightgbm as lgb
import pandas as pd
import sys

def extract_feature(df):
    x = df[['score', 'similarity', 'delta_rt', 'full_similarity', 'score_mean', 'score_var', 'score_max', 'similarity_mean', 'similarity_var', 'similarity_max', 'delta_rt_mean', 'delta_rt_var', 'delta_rt_max', 'full_similarity_mean', 'full_similarity_var', 'full_similarity_max', 'xcorr', 'delta_cn', 'sp_score', 'mass_error', "HLA-B*08:01","HLA-A*26:01","HLA-A*01:01","HLA-A*02:01","HLA-A*03:01","HLA-A*24:02","HLA-B*07:02","HLA-B*27:05","HLA-B*39:01","HLA-B*40:01","HLA-B*58:01","HLA-B*15:01"]]
    y = df['Label']
    x.columns = ['score', 'similarity','delta_rt', 'full_similarity', 'score_mean', 'score_var', 'score_max', 'similarity_mean', 'similarity_var', 'similarity_max', 'delta_rt_mean', 'delta_rt_var', 'delta_rt_max', 'full_similarity_mean', 'full_similarity_var', 'full_similarity_max', 'xcorr', 'delta_cn', 'sp_score', 'mass_error', "HLA1","HLA2","HLA3","HLA4","HLA5","HLA6","HLA7","HLA8","HLA9","HLA10","HLA11","HLA12"]
    return df, x, y

def predict_score(feature_file, model_dir, out_dir1, out_dir2):
    df = pd.read_csv(feature_file)
    _, x, y = extract_feature(df)
    model = lgb.Booster(model_file = model_dir)
    df['myscore'] = model.predict(x)
    df.to_csv(out_dir1, index = False)
    df = df.sort_values(by = 'myscore', ascending = False).groupby(['index']).head(1)
    df[['index', 'charge', 'mass', 'peptide', 'mods', 'protein', 'myscore']].to_csv(out_dir2, index = False)

args = sys.argv
feature_file, model_dir, out_dir1, out_dir2 = args[1:]
predict_score(feature_file, model_dir, out_dir1, out_dir2)