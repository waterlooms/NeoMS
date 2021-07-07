import math
import pandas as pd
import sys
def convert_mod(peptide):
    mods = []
    for i in range(len(peptide)):
        if peptide[i] == 'C':
            mods.append('%d_S_57.021464' % (i+1))
    if len(mods) == 0:
        return '-'
    else:
        return ','.join(mods)
    
template = """\
novor
{}"""
    
def novor_convert(f, f_out):
    df = pd.read_csv(f, skiprows = 20, sep = ', ', engine = 'python')
    df2 = pd.DataFrame(columns=["scan","num","charge","exp_neutral_mass","calc_neutral_mass","e-value","xcorr","delta_cn","sp_score","ions_matched","ions_total","plain_peptide","modified_peptide","prev_aa","next_aa","protein","protein_count","modifications","retention_time_sec","sp_rank"])
    df2['scan'] = df['scanNum']
    df2['num'] = 1
    df2['charge'] = df['z']
    df2['exp_neutral_mass'] = df.apply(lambda x: (x['mz(data)'] - 1.0073) * x['z'], axis=1)
    df2['calc_neutral_mass'] = df['pepMass(denovo)']
    df2['e-value'] = df['score'].apply(lambda x: math.exp(-x))
    df2['plain_peptide'] = df['peptide'].apply(lambda x: x.replace('(Cam)', ''))
    df2['modifications'] = df2['plain_peptide'].apply(lambda x: convert_mod(x))
    df2['protein'] = df['score'].apply(lambda x: 'sp' if x > 90 else 'XXX|sp')
    df2["retention_time_sec"] = df['RT']
    with open(f_out, 'w') as fp:
        fp.write(template.format(df2.to_csv(index=False, sep = '\t')))

args = sys.argv
novor_result, converted_file = args[1:]
novor_convert(novor_result, converted_file)
