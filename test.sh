file="20120321_EXQ1_MiBa_SA_HCC1143_1"

mkdir result/${file}

~/project/Rescore/nextflow run preprocess.nf \
	--input data/${file}.raw \
	--out_dir result/${file}/

~/project/Rescore/nextflow run denovo.nf \
	--ms_file result/${file}/mgf_file/${file}.mgf \
	--out_dir result/${file}/denovo  \
	--mem 32 --cpu 80

~/project/Rescore/nextflow run dbsearch.nf \
	--ms_file result/${file}/mgf_file/${file}.mgf \
	--out_dir result/${file}/dbsearch  \
	--mem 32 --cpu 80

~/project/Rescore/nextflow run combine.nf \
	--dbsearch_feature result/${file}/dbsearch/features/dbsearch_feature.txt \
	--denovo_feature result/${file}/denovo/features/denovo_feature.txt \
	--model model/0
	--out_dir result/${file}/ --mem 32 --cpu 80