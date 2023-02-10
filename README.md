# NeoMS
## Overview
**NeoMS** is an end-to-end immunopeptidomics data analysis tool. NeoMS takes raw data as input and return the search result with high quality. The main steps of NeoMS is compiled in Nextflow(https://www.nextflow.io/docs/latest/getstarted.html)

## Installation
0. GPU is required to run NeoMS.

1. Install [Nextflow 20.10](https://github.com/nextflow-io/nextflow/releases/tag/v20.10.0) and add to environment variables.

2. Install [docker](https://docs.docker.com/engine/install/). Tools used by NeoMS have been dockerized and will be automatically installed when NeoMS is run in the first time on a computer. NeoMS has been tested on Linux.

3. Download NeoMS from Github
```
git clone https://github.com/waterlooms/NeoMS.git
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


index|charge|mass|peptide|mods|protein|myscore
-|-|-|-|-|-|-
20120321_EXQ1_MiBa_SA_HCC1143_1.10327.10327.2|2|1122.541603|SRSQNQQYL|0|sp&#124;O14782&#124;KIF3C_HUMAN,sp&#124;O15066&#124;KIF3B_HUMAN|1.090571005
20120321_EXQ1_MiBa_SA_HCC1143_1.14812.14812.2|2|1073.514985|QRYSGSTYL|0|sp&#124;P54277&#124;PMS1_HUMAN|1.086924661
20120321_EXQ1_MiBa_SA_HCC1143_1.5907.5907.3|3|1096.653946|RRAAQVQRL|0|sp&#124;Q969G5&#124;CAVN3_HUMAN|1.071481355
20120321_EXQ1_MiBa_SA_HCC1143_1.2026.2026.3|3|1129.518549|HRSPHTHQM|0|sp&#124;P11230&#124;ACHB_HUMAN|1.064637078
20120321_EXQ1_MiBa_SA_HCC1143_1.23613.23613.2|2|1013.586828|SRAELVQLV|0|sp&#124;Q96ST3&#124;SIN3A_HUMAN|1.057023507
