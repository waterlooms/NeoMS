params.ms_instrument = "Lumos"
params.ms_energy = 0.34
params.prefix = "test"
params.mem = 80

instrument       = params.ms_instrument
energy           = params.ms_energy
threads          = params.cpu
memory           = params.mem
denovo_feature   = file(params.denovo_feature)
dbsearch_feature = file(params.dbsearch_feature)
model_dir        = file(params.model)
output_path      = file(params.out_dir)
sample           = params.prefix


process combine_features {
    tag "$sample"

    container "0731wsk/protemoics_base"
    containerOptions "--user root"

    publishDir "${output_path}", mode: "copy", overwrite: true

    input:
    file (dbsearch_feature) 
    file (denovo_feature)

    output:
    file ('feature.txt') into feature_file_ch

    script:
    """
    #!/bin/sh
    python3 ${baseDir}/bin/combine_feature.py  $denovo_feature $dbsearch_feature ./feature.txt
    """
}

process predict_score {
    tag "$sample"

    container "0731wsk/protemoics_base"
    containerOptions "--user root"
    publishDir "${output_path}", mode: "copy", overwrite: true

    input:
    file (feature_file) from feature_file_ch

    output:
    set file ('result_all.csv'),file('result.csv') into result_file_ch

    script:
    """
    #!/bin/sh
    python3 ${baseDir}/bin/predict_score.py  $feature_file $model_dir ./result_all.csv ./result.csv
    """
}