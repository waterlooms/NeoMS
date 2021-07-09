params.ms_instrument = "Lumos"
params.ms_energy = 0.34
params.prefix = "test"
params.mem = 80

instrument      = params.ms_instrument
energy          = params.ms_energy
threads         = params.cpu
memory          = params.mem
spectrum_file   = file(params.ms_file)
output_path     = file(params.out_dir)
sample          = params.prefix

process run_novor {
    tag "$sample"

    container "0731wsk/novor"
    containerOptions "--user root"

    publishDir "${output_path}/psm", mode: "copy", overwrite: true

    input:
    file (spectrum_file)

    output:
    file ('./denovo.csv') into result_file_ch1

    script:
    """
    #!/bin/sh
    mkdir psm
    python ${baseDir}/bin/add_scan.py $spectrum_file ./temp.mgf
    novor.sh -p ${baseDir}/config/novor_params.txt -f ./temp.mgf -o ./denovo.csv

    """
}

process convert_novor {
    tag "$sample"

    container "0731wsk/proteomics"
    containerOptions "--user root"

    publishDir "${output_path}/psm", mode: "copy", overwrite: true


    input:
    file (result_file) from result_file_ch1

    output:
    file ('./result.txt') into result_file_ch2

    script:
    """
    #!/bin/sh
    python3 ${baseDir}/bin/novor_convert.py $result_file ./result.txt

    """
}


process generate_input {
    tag "$sample"

    container "0731wsk/proteomics"
    containerOptions "--gpus all"
    containerOptions "--user root"

    publishDir "${output_path}", mode: "copy", overwrite: true

    input:
    file (spectrum_file)
    file (result_file) from result_file_ch2

    output:
    file("${sample}-rawPSMs.txt") into pga_results_ch1
    file("${sample}-rawPSMs.txt") into pga_results_ch2
    file("./pDeep2_prediction/") into pDeep2_prediction_ch
    file("./autoRT_train/") into autoRT_train_ch
    file("./autoRT_prediction/") into autoRT_prediction_ch
    file('./predfull') into predfull_ch


    script:
    """
    #!/bin/sh
    mkdir autoRT_train autoRT_prediction pDeep2_prediction predfull
    python3 ${baseDir}/bin/generate_input.py $result_file $spectrum_file \
        ./${sample}-rawPSMs.txt \
        ./autoRT_train/autort.txt ./autoRT_prediction/autort.txt\
        ./pDeep2_prediction/${sample}_pdeep2_prediction.txt ./pDeep2_prediction/${sample}_pdeep2_prediction_unique.txt\
        denovo
    
    """
}

process run_predfull {
    tag "$sample"
    container "0731wsk/predfull"
    containerOptions "--gpus all"

    publishDir "${output_path}/predfull/", mode: "copy", overwrite: true

    input:
    file (result_file) from result_file_ch2
    file (predfull) from predfull_ch

    output:
    file ("./predict.mgf") into pred_spectrum

    script:
    """
    #!/bin/sh
    python3 /home/Predfull/predfull.py \
        --input $result_file \
        --model /home/Predfull/pm.h5 \
        --output predict.mgf
    """

}


process process_predfull_result{
    tag "$sample"

    accelerator 1

    container "0731wsk/proteomics"
    containerOptions "--gpus all"

    publishDir "${output_path}/predfull/", mode: "copy", overwrite: true

    input:
    file (spectrum_file)
    file (predfull_result) from pred_spectrum

    output:
    file("./full_similarity.txt") into predfull_similarity

    script:
    """
    #!/bin/sh
    python3 ${baseDir}/bin/spectrum_compare.py --real $spectrum_file --pred $predfull_result \
        --output ./full_similarity.txt
    
    """
}

process run_pdeep2 {

    tag "$sample"

    container "proteomics/pdeep2:latest"
    containerOptions "--gpus all"

    publishDir "${output_path}/pDeep2_prediction/", mode: "copy", overwrite: true

    input:
    file(pdeep2_folder) from pDeep2_prediction_ch
    file(predfull_result) from predfull_similarity

    output:
    set file("${sample}_pdeep2_prediction_results.txt"), file{"${pdeep2_folder}/${sample}_pdeep2_prediction.txt"} into pDeep2_results_ch

    script:
    """
    #export CUDA_VISIBLE_DEVICES=0
    python /opt/pDeep2/predict.py -e $energy -i $instrument -in ${pdeep2_folder}/${sample}_pdeep2_prediction_unique.txt -out ./${sample}_pdeep2_prediction_results.txt
    """
}

process process_pDeep2_results {

    tag "$sample"

    container "0731wsk/proteomics"
    containerOptions "--gpus all"

    publishDir "${output_path}/pDeep2_prediction/", mode: "copy", overwrite: true

    input:
    file (rawPSMs_file) from pga_results_ch1
    file (spectrum_file)
    set file(pDeep2_results), file(pDeep2_prediction) from pDeep2_results_ch

    output:
    set file("./${sample}_format_titles.txt"), file("./${sample}_spectrum_pairs.txt"), file("./${sample}_similarity_SA.txt") into similarity_ch
    file ("./${sample}_similarity_SA.txt") into pDee2_next_ch

    script:
    """
    #!/bin/sh
    mv $pDeep2_results ${pDeep2_results}.mgf
    Rscript ${baseDir}/bin/format_pDeep2_titile.R $pDeep2_prediction $rawPSMs_file ./${sample}_format_titles.txt

    python3 ${baseDir}/bin/calculate_sa.py ./${sample}_format_titles.txt $spectrum_file ${pDeep2_results}.mgf ./${sample}_spectrum_pairs.txt
    mkdir sections sections_results
    Rscript ${baseDir}/bin/similarity/devide_file.R ./${sample}_spectrum_pairs.txt $threads ./sections/
    for file in ./sections/*
    do
        name=`basename \$file`
        Rscript ${baseDir}/bin/similarity/calculate_similarity_SA.R \$file ./sections_results/\${name}_results.txt &
    done
    wait
    awk 'NR==1 {header=\$_} FNR==1 && NR!=1 { \$_ ~ \$header getline; } {print}' ./sections_results/*_results.txt > ./${sample}_similarity_SA.txt
    
    """
}


process train_autoRT {

    tag "$sample"

    accelerator 1

    container "proteomics/autort:latest"
    containerOptions "--gpus all"

    publishDir "${output_path}/autoRT_train/", mode: "copy", overwrite: true

    input:
    file(autoRT_train_folder) from autoRT_train_ch
    file(sa_file) from pDee2_next_ch

    output:
    file ("./autoRT_models/") into model_prediction_ch

    script:
    """
    #!/bin/sh
    set -e
    mkdir -p ./autoRT_models
    for file in ${autoRT_train_folder}/*.txt
    do
        fraction=`basename \${file} .txt`
        mkdir -p ./autoRT_models/\${fraction}
        python /opt/AutoRT/autort.py train \
        -i \$file \
        -o ./autoRT_models/\${fraction} \
        -e 40 \
        -b 64 \
        -u m \
        -m /opt/AutoRT/models/base_models_PXD006109/model.json \
        -rlr \
        -n 10 
    done
    wait
    """
}

process predict_autoRT {

    tag "$sample"

    container "proteomics/autort:latest"
    containerOptions "--gpus all"

    publishDir "${output_path}/autoRT_prediction/", mode: "copy", overwrite: true

    input:
    file autoRT_prediction_folder from autoRT_prediction_ch
    file (autoRT_models_folder) from model_prediction_ch

    output:

    file("./results") into autoRT_results_ch

    script:
    """
    #!/bin/sh
    set -e
    mkdir -p ./results
    for file in ${autoRT_prediction_folder}/*.txt
    do
        fraction=`basename \${file} .txt`
        mkdir -p ./\${fraction}
        python /opt/AutoRT/autort.py predict \
        -t \$file \
        -s ${autoRT_models_folder}/\${fraction}/model.json \
        -o ./\${fraction} \
        -p \${fraction}
    done

    for file in ${autoRT_prediction_folder}/*.txt
    do
        fraction=`basename \${file} .txt`
        cp ./\${fraction}/\${fraction}.csv ./results/
    done

    wait
    awk 'NR==1 {header=\$_} FNR==1 && NR!=1 { \$_ ~ \$header getline; } {print}' ./results/*.csv \
    > ./results/${sample}_results.txt
    """
}


process generate_feature{
    tag "$sample"
    container "0731wsk/proteomics"
    containerOptions "--gpus all"
    containerOptions "--user root"

    publishDir "${output_path}", mode: "copy", overwrite: true

    input:
    file(rawPSMs_file) from pga_results_ch2
    set file(similarity_title_file), file(similarity_pair_file), file(similarity_SA_file) from similarity_ch
    file(autoRT_result_folder) from autoRT_results_ch
    file(predfull_result) from predfull_similarity

    output:
    file("./features") into features

    script:
    """
    #!/bin/sh
    mkdir features
    python3 ${baseDir}/bin/generate_feature.py $rawPSMs_file $similarity_SA_file \
        $autoRT_result_folder/${sample}_results.txt $predfull_result\
        features/denovo_feature.txt\
        denovo
    """

}