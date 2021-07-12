# HLA-search
## Overview
**HLA-search** is an end-to-end immunopeptidomics data analysis tool. HLA-search takes raw data as input and return the search result with high quality. The main steps of HLA-search is compiled in Nextflow(https://www.nextflow.io/docs/latest/getstarted.html)

## Installation
0. GPU is required to run HLA-search.

1. Install [Nextflow 20.10](https://github.com/nextflow-io/nextflow/releases/tag/v20.10.0) and add to environment variables.

2. Install [docker](https://docs.docker.com/engine/install/). Tools used by HLA-search have been dockerized and will be automatically installed when HLA-search is run in the first time on a computer. HLA-search has been tested on Linux.

3. Download HLA-search from Github
```
git clone https://github.com/waterlooms/HLA-search.git
```

4. Download test raw data in data folder
```
cd data/
chmod +x download_test.sh
bash download_test.sh
```

5. Run the whole pipeline. The whole pipeline include 4 steps in nextflow: 
    1. Preprocessing: Convert the raw file to mgf format.
    2. De novo: Run de novo software (Novor) on the mgf file and compute features on de novo PSMs(Peptide Spectrum Matching).
    3. Database search: Run database search tool (comet) on the mgf file and compute features on searched PSMs. Notice that the .fasta file will be copy to /tmp folder.
    4. Combine: Combine features from de novo and db search result. A machine learning model is applied to compute a score for each PSM. 
    
The 4 steps have been put into single bash file. You can run the whole pipeline simply by:
```
chmod +x test.sh
bash test.sh
```

6. It will automatically generate a folder in result/ with same name of raw file. It might take 30~40 mins for the whole pipeline. After finished, the result is at result/20120321_EXQ1_MiBa_SA_HCC1143_1/result.csv.

## Result
The result includes best peptide(can be target or decoy) for each spectrum. The result will be sorted by a score. The first few rows will be like this:


|index|charge|mass|peptide|mods|protein|myscore|
|-|-|-|-|-|-|-|
|A1.7522.7522.2|2|1218.671482|RLLEYTPTAR|0|sp&#124;P49841&#124;GSK3B_HUMAN|1.0652809430298136|
|A1.12663.12663.2|2|1093.592503|RASPFLLQY|0|sp&#124;O60256&#124;KPRB_HUMAN|sp&#124;Q14558&#124;KPRA_HUMAN||1.0544916867886331
|A1.4247.4247.2|2|1124.5947|TRLQHQTEL|0|sp&#124;Q9UL54&#124;TAOK2_HUMAN|1.0509270824169652|
|A1.5765.5765.2|2|921.467442|FANGRSTGL|0|sp&#124;O94805&#124;ACL6B_HUMAN|sp&#124;O96019&#124;ACL6A_HUMAN||1.0467162548857218
|A1.7431.7431.2|2|850.50272|ARGPPAAVL|0|sp&#124;Q05923&#124;DUS2_HUMAN|1.038806109652818|
|A1.7161.7161.3|3|945.565573|GLFGKTVPK|0|sp&#124;P23284&#124;PPIB_HUMAN|1.0383908589384576|