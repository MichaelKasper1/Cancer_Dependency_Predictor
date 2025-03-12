# **Data for Deep dep web servers**

## **Data Dictionary**

The django app uses a MongoDB database. These are the data (collections) within the database:

- **gene_annotations** Comes from running the code described below within the Gene Annotation Table section.
- **exp_file** Example data for example button. Right now, the data comes from the [code ocean]( https://codeocean.com/capsule/7914207/tree/v1).
- **ccl_predicted_data_model_10xCV_paper** This contains the predicted dependency scores from the Science Advances paper for 278 genes. It can be found at [code ocean](https://codeocean.com/capsule/7914207/tree/v1).
- **ccle_23q4_chronos_996** Contains the chronos predicted dependency score for 996 cell lines from the Cancer Cell Line Encyclopedia from [DepMap](https://depmap.org/portal/data_page/?tab=allData).
- **GeneEffect_18Q2_278CCLs** Contains predicted dependency score for the 278 cell lines that were used for model training in the Science Advances paper. Available at [DepMap](https://depmap.org/portal/data_page/?tab=allData).
- **ccle_exp_for_missing_value_6016** Helps handle missing expression data by substituting mean expression values from reference. This file originates from the Prep4DeepDEP [github](https://github.com/chenlabgccri/Prep4DeepDEP/blob/master/R/Prep4DeepDEP.r)
- **tcga_clinical_data** Used in network plot as well as bar plots. Accessible at [NIH TCGA data portal](https://portal.gdc.cancer.gov/).
- **tcga_pred** This file is named tcga_predicted_data_model_paper.txt on [code ocean](https://codeocean.com/capsule/7914207/tree/v1) under the path data/predictions/. It is predicted dependency scores of TCGA tumors.
- **cell_info_21Q3_PrimaryTypeFixed** This file contains cancer type which is used in bar plots. It initially comes from depmap, but has been edited to only include a reduced number of groups for visualization purposes.
- **hallmark** A predefined list of hallmark sets used in the user interface to generate the drop down menu and make fingerprint matricies.
- **C2_cp** A list of C2_cp gene sets used within the drop down menu enabling users to select a set of genes and make fingerprint matricies.
- **ccle_exp_with_gene_alias_DeepDep** This is a table with gene alias names for all genes used in the deep dep expression model (6016 genes). It is created using Gene_alias_table.R
- **fingerprint** This file comes from the original shiny app and is the fingerprint for all genes.
- **crispr_gene_fingerprint** The original fingerprint for 1298 default genes available on code ocean.
- **CCLE_expression_EN_21Q1_predictions** This data is from the model_training/output directory. It contains predictions of CCLE gene essentiality from models trained specifically for the app.
- **CCLE_expression_21Q1** This data is the 21Q1 depmap expression data that is used to train the EN models available at DEPMAP portal.
- **medians_CCLE21Q1** This data is the median scores that are used to impute values for missing genes in a given sample for the EN model. It is calculated in the ~/supplementary/build_depmap_EN.R
- **model_performances_EN** This data is the model performances of the newly trained EN models. It is also calculated in ~/supplementary/build_depmap_EN.R
- **gene_alias_EN.py** This data is made in the gene_alias_EN.py script and is used to try to mitigate lost genes (would be replaced with median expression values) during preprocessing due to different gene symbol types of mismatched hgnc symbols.


## **Gene Annotation Tables**

To create the gene annotation table, 2 scripts from within this directory are executed.

#### **Gene Alias Tables**

Gene_alias_table.R is a script that is used to update gene alias names from ensembl. The following data is required and used by this script

- **ccle_exp_for_missing_value_6016.RData** This file is used in the app for missing data, but it also is used in the data processing here to collect the IDs.
- **ccle_exp_and_mut_with_gene_alias_shinyDeepDep.RData** This file contains the gene alias names. It was created for the first app and can be updated with information from ensembl using this script.

Execute the following in an R terminal:

    Rscript Gene_alias_table.R

Your output will be an updated gene alias table within the desired directory with the name ccle_exp_gene_alias_DeepDep.RData

The other gene alias table script is gene_alias_EN.py. This script takes gives you alias for elastic net models.

#### **Gene Annotations Table 1**

get_gene_info.R gathers gene annotations from ensembl, depmap data, cosmic data.

The latest version of Ensembl used in the app is: 113
This version gets printed near the start of the execution of the get_gene_info.R.

The following data is used within this script:

- **ccle_exp_and_mut_with_gene_alias_shinyDeepDep.RData** This file contains the gene alias names. It is created in step 1.
- **CRISPRGeneEffect.csv** The current version of this file that we are using in the app is 23q4. It is available through this [depmap page](https://depmap.org/portal/data_page/?tab=allData)
- **COSMIC/Cosmic_v99_grch38.txt** COSMIC is a catalogue of somatic mutations in cancer. It is a large source with useful gene annotations. This data can be found at the [COSMIC site](https://cancer.sanger.ac.uk/cosmic/download/cosmic/v99/cancergenecensus), you can make a free account with an academic email.
- **tcga_predicted_data_model_paper.txt** Used to generate prediction ranges. Found at [code ocean](https://codeocean.com/capsule/7914207/tree/v1).
- **ccl_predicted_data_model_10xCV_paper.txt** Used to generate prediction ranges. Found at [code ocean](https://codeocean.com/capsule/7914207/tree/v1).
- **performance_per-gene_1288gene_272CLs_20240213.txt** Used to provide prediction performance. Passed from Chris on slack to shinydeepdep channel on February, 12, 2024. Under this path on OneDrive: data/DeepDEP_performance_publication/performance_per-gene_1288gene_272CLs_20240213.txt
- **GeneEffect_18Q2_278CCLs.rds** Used to generate real range of gene dependency from [depmap](https://depmap.org/portal/data_page/?tab=allData).

Execute the following:

    Rscript get_gene_info.R

Your output will be gene_annotations.csv which is a main annotation file for the django deepdep web server containing over 20,000 genes.
