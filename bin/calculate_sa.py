from pyteomics import mgf
import pandas as pd
import numpy as np
from tqdm import tqdm
import sys

def mz_int(sp):
    mz_list, int_list = sp['m/z array'], sp['intensity array']
    ret = ''
    for mz, inte in zip(mz_list, int_list):
        ret += '%s %s ' %(mz, inte)
    return ret

def calculate_SA(title_file, exp_file, pdeep_file, output_pair):
    spectra1 = mgf.read(source = exp_file, read_charges = False)
    spectra2 = mgf.read(source = pdeep_file, read_ions = True, read_charges = False)

    df = pd.read_csv(title_file, sep = '\t')
    index1, index2 = df['index'], df['pdeep_title']

    mz_int1, mz_int2 = [], []
    for i in tqdm(range(len(df))):
        title1, title2 = index1[i], index2[i]
        mz_int1.append(mz_int(spectra1[title1]))
        mz_int2.append(mz_int(spectra2[title2]))
    df['ori_mz_int'] = mz_int1
    df['pdeep2_mz_int'] = mz_int2

    df[['index', 'pdeep_title', 'ori_mz_int','pdeep2_mz_int']].to_csv(output_pair, index = False, sep = '\t')

args = sys.argv
title_file, exp_file, pdeep_file, output_pair = args[1:]
calculate_SA(title_file, exp_file, pdeep_file, output_pair)
