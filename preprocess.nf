params.prefix = "test"

raw_data         = file(params.input)
output_path      = file(params.out_dir)
sample           = params.prefix


process convert_to_mgf {
    tag "$sample"

    container "chambm/pwiz-skyline-i-agree-to-the-vendor-licenses"
    containerOptions "--user root"

    publishDir "${output_path}", mode: "copy", overwrite: true

    input:
    file (raw_data) 

    output:
    file ('mgf_file') into result_file_ch

    script:
    """
    #!/bin/sh
    wine msconvert $raw_data -c ${baseDir}/config/MSconvert_config.txt -o ./mgf_file
    """
}
