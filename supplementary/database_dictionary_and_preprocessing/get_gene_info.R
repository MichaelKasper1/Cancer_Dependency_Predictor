# Generate Gene Annotation Table
# edited on October 15, 2024 by mjk

# This script is used to create the final gene annotation table that is used in the database of the web server. In addition to the get_gene_info.R script written by LJW, this script also includes the creation of performance and range scores for expression. Please be sure to set your data directories before executing. The script takes a few minutes to run.

# The script is quite long in my opinion for a single file of code. When referencing this code, I suggest using an IDE that can collapse sections of code to make it easier to read. Sections of code are as follows:
# Load libraries and data and prepare ensembl connection
# Get info from crispr_gene_23q4 genes
# Get info from the 1298 genes used in original science advances paper
# Get info from Cosmic genes
# Include ranges and performances for predicted dependency scores
# Limit rows ones used in app based on fingerprints
# Remap names of tissue type column
# Standardize NA, rename to match app, select needed columns
# Save final gene annotation table
# ensure similarity between this and previous gene annotation file.


# Requirements (read details on Readme.md):
# - gene_fingerprints_CGP.RData
# - CRISPRGeneEffect.csv
# - Cosmic_v99_grch38.txt
# - gene_symbols_IDs.txt
# - ccl_predicted_data_model_10xCV_paper.txt
# - performance_per-gene_1288gene_272CLs_20240213.txt

# Output:
# - gene_annotations.csv

####### SET DIRECTORIES ACCORDING TO LOCATION OF YOUR DATA #######
# Some of these were included in the data directory of the Rshiny deep dep app. If you have the old version of the shiny app, set data_dir to the location of the shinydeepdep data directory, it should work to load most of the required data. Set separate paths for cosmic data, data of model performances, and where you'd like to output the final gene annotation table.

data_dir <- "/Users/michaelkasper/Documents/DeepDep_learning/shinyDeepDEP_20240301/shinyDeepDep_20240301/data"
cosmic_dir <- "/Users/michaelkasper/Downloads/Cosmic_CancerGeneCensus_Tsv_v99_GRCh38"
performance_dir <- "/Users/michaelkasper/Downloads"
dest_dir <- "/Users/michaelkasper/Documents/Deepdep_data_processing_and_model_training/data_processing/data_processing_mjk"
#################################################################


##### Load libraries, load data, prepare ensembl data for all genes #####
# Load required libraries
library(biomaRt)
library(stringr)
library(tibble)
library(dplyr)

# Load data
setwd(data_dir)
load("Prep4DeepDEP_data/gene_fingerprints_CGP.RData")
ccle_23q4_chronos <- read.delim("CCLE_23Q4/CRISPRGeneEffect.csv", sep = ",") # for ccle real range
target_gene <- read.delim("gene_symbols_IDs_1298.txt", sep = "\t") # for mapping gene symbols
load("TCGA/tcga_predicted_data_model_paper.RData") # TCGA prediction range
GeneEffect_18Q2_278CCLs <- readRDS("DeepDep_data/GeneEffect_18Q2_278CCLs.rds") # real ccle range for 278 cell lines
ccle_pred_278CCLs <- readRDS("DeepDep_data/ccl_predicted_data_model_10xCV_paper.rds") # predicted ccle range for 278 cell lines
hallmark= readRDS("MSigDB/Hallmark_gene_list.RDS")
C2_cp = readRDS("MSigDB/C2_CP_gene_list.RDS")
C2_cp_cat <- unique(str_split_fixed(colnames(C2_cp),pattern = "_",n = 2)[,1])
C2_cp = C2_cp[,which(str_split_fixed(colnames(C2_cp),pattern = "_",n = 2)[,1] %in% c("BIOCARTA", "KEGG" ))] #1097 terms in KEGG & BIOCARTA

setwd(cosmic_dir)
cosmic <- read.delim("Cosmic_CancerGeneCensus_v99_GRCh38.tsv", header = T,sep = "\t")

setwd(performance_dir)
performance <- read.delim("performance_per-gene_1288gene_272CLs_20240213.txt", sep = "\t")

# Initialize Ensembl connection
ensembl <- useEnsembl(biomart = "genes")
datasets <- listDatasets(ensembl)
# List Ensembl versions
ensembl_versions <- listEnsembl()
# Print the Ensembl version
print("Ensembl version:")
print(ensembl_versions$version)
searchDatasets(mart = ensembl, pattern = "hsapiens")
ensembl <- useDataset(dataset = "hsapiens_gene_ensembl", mart = ensembl)
ensembl <- useEnsembl(biomart = "genes", dataset = "hsapiens_gene_ensembl")
filters <- listFilters(ensembl)
attr <- listAttributes(ensembl)
searchAttributes(mart = ensembl, pattern = "hgnc")

# Retrieve gene information from Ensembl
# Transpose the fingerprint matrix and extract gene symbols
crispr_gene <- as.character(t(fingerprint[1, -1]))

# Define the attributes to retrieve from Ensembl
attributes <- c('hgnc_symbol', 'chromosome_name', 'start_position', 'end_position', 
                'gene_biotype', 'ensembl_gene_id', 'entrezgene_id', 'external_synonym')

# Retrieve gene information using the specified attributes and filters
gene.info <- getBM(attributes = attributes,
                   filters = 'hgnc_symbol', 
                   values = crispr_gene, 
                   mart = ensembl)

# Create a data frame to store gene information
gene.all <- data.frame(matrix(data = NA, ncol = ncol(gene.info), nrow = length(unique(crispr_gene))), stringsAsFactors = F)
colnames(gene.all) <- c("Gene_Symbol", colnames(gene.info)[-1])
gene.all$Gene_Symbol <- crispr_gene

# Populate the data frame with gene information
for (i in 1:nrow(gene.all)) {
  tb <- gene.info[which(gene.info$hgnc_symbol == gene.all$Gene_Symbol[i]),]
  
  if (nrow(tb) == 1) {
    gene.all[i, 2:ncol(tb)] <- tb[,-1]
  }
  
  if (nrow(tb) > 1) {
    gene.all$chromosome_name[i] <- unique(tb$chromosome_name)[1]
    gene.all$start_position[i] <- unique(tb$start_position)[1]
    gene.all$end_position[i] <- unique(tb$end_position)[1]
    gene.all$gene_biotype[i] <- unique(tb$gene_biotype)[1]
    gene.all$ensembl_gene_id[i] <- unique(tb$ensembl_gene_id)[1]
    gene.all$entrezgene_id[i] <- unique(tb$entrezgene_id)[1]
    gene.all$external_synonym[i] <- paste(unique(tb$external_synonym), collapse = ",")
  }
  
  tb1 <- gene.info[which(gene.info$external_synonym == gene.all$Gene_Symbol[i]),]
  
  if (nrow(tb1) == 1) {
    gene.all$chromosome_name[i] <- tb1$chromosome_name
    gene.all$start_position[i] <- tb1$start_position
    gene.all$end_position[i] <- tb1$end_position
    gene.all$gene_biotype[i] <- tb1$gene_biotype
    gene.all$ensembl_gene_id[i] <- tb1$ensembl_gene_id
    gene.all$entrezgene_id[i] <- tb1$entrezgene_id
    gene.all$external_synonym[i] <- tb1$hgnc_symbol
  }
  
  if (nrow(tb1) > 1) {
    gene.all$chromosome_name[i] <- unique(tb1$chromosome_name)[1]
    gene.all$start_position[i] <- unique(tb1$start_position)[1]
    gene.all$end_position[i] <- unique(tb1$end_position)[1]
    gene.all$gene_biotype[i] <- unique(tb1$gene_biotype)[1]
    gene.all$ensembl_gene_id[i] <- unique(tb1$ensembl_gene_id)[1]
    gene.all$entrezgene_id[i] <- unique(tb1$entrezgene_id)[1]
    gene.all$external_synonym[i] <- paste(unique(tb1$hgnc_symbol), collapse = ",")
  }
}
#################################################################


##### Get info from crispr_gene_23q4 genes #####
# Using crispr gene data from 23Q4 from depmaps CCLE
# Extract and transpose column names from ccle_23q4_chronos, excluding the first column
crispr_gene_23q4 <- as.character(t(colnames(ccle_23q4_chronos)[-1]))

# Split the transposed column names into two parts using the pattern ".."
crispr_gene_23q4 <- as.data.frame(stringi::stri_split_fixed(crispr_gene_23q4, pattern = "..", n = 2, simplify = T))

# Further split the second part of the split result using the pattern "." and keep only the first part
crispr_gene_23q4$V2 <- str_split_fixed(crispr_gene_23q4$V2, pattern = "\\.", n = 2)[,1]

# Rename the columns to 'hgnc_symbol' and 'entrezgene_id'
colnames(crispr_gene_23q4) <- c('hgnc_symbol', "entrezgene_id")

# Add a new column with the original column names from ccle_23q4_chronos, placing it before 'hgnc_symbol'
crispr_gene_23q4 <- crispr_gene_23q4 %>% add_column(colname = colnames(ccle_23q4_chronos)[-1], .before = 'hgnc_symbol')

# Create a new data frame ccle_23q4_gene_index that is a copy of crispr_gene_23q4
ccle_23q4_gene_index <- crispr_gene_23q4

# Rename the first column of ccle_23q4_chronos to 'DepMapID'
colnames(ccle_23q4_chronos)[1] <- "DepMapID"

# Retrieve gene information for CCLE 23Q4: 18443 genes
gene.info <- getBM(
  attributes = c(
    "hgnc_symbol",
    "chromosome_name",
    "start_position",
    "end_position",
    "gene_biotype",
    "ensembl_gene_id",
    "entrezgene_id",
    "external_synonym"
  ),
  filters = "hgnc_symbol",
  values = crispr_gene,
  mart = ensembl
)

# Initialize an empty data frame to store the gene information
gene.info.out <- data.frame(matrix(data = NA, ncol = ncol(gene.info), nrow = length(crispr_gene)), stringsAsFactors = FALSE)
colnames(gene.info.out) <- c("Gene_Symbol", colnames(gene.info)[-1])

# Since crispr_gene is a vector, you can directly assign it to the Gene_Symbol column
gene.info.out$Gene_Symbol <- crispr_gene

# Populate the data frame with the retrieved gene information from ensembl
for (i in 1:nrow(gene.info.out)) {
  # Filter the gene information for the current gene symbol
  tb <- gene.info[which(gene.info$hgnc_symbol == gene.info.out$Gene_Symbol[i]),]

  # If there is exactly one match, populate the row with the gene information
  if (nrow(tb) == 1) {
    gene.info.out[i, 2:ncol(tb)] <- tb[,-1]
  }

  # If there are multiple matches, populate the row with unique values
  if (nrow(tb) > 1) {
    gene.info.out$chromosome_name[i] <- unique(tb$chromosome_name)[1]
    gene.info.out$start_position[i] <- unique(tb$start_position)[1]
    gene.info.out$end_position[i] <- unique(tb$end_position)[1]
    gene.info.out$gene_biotype[i] <- unique(tb$gene_biotype)[1]
    gene.info.out$ensembl_gene_id[i] <- unique(tb$ensembl_gene_id)[1]
    gene.info.out$entrezgene_id[i] <- unique(tb$entrezgene_id)[1]
    gene.info.out$external_synonym[i] <- paste(unique(tb$external_synonym), collapse = ",")
  }

  # Check for matches in the external_synonym field
  tb1 <- gene.info[which(gene.info$external_synonym == gene.info.out$Gene_Symbol[i]),]

  # If there is exactly one match, populate the row with the gene information
  if (nrow(tb1) == 1) {
    gene.info.out$chromosome_name[i] <- tb1$chromosome_name
    gene.info.out$start_position[i] <- tb1$start_position
    gene.info.out$end_position[i] <- tb1$end_position
    gene.info.out$gene_biotype[i] <- tb1$gene_biotype
    gene.info.out$ensembl_gene_id[i] <- tb1$ensembl_gene_id
    gene.info.out$entrezgene_id[i] <- tb1$entrezgene_id
    gene.info.out$external_synonym[i] <- tb1$hgnc_symbol
  }

  # If there are multiple matches, populate the row with unique values
  if (nrow(tb1) > 1) {
    gene.info.out$chromosome_name[i] <- unique(tb1$chromosome_name)[1]
    gene.info.out$start_position[i] <- unique(tb1$start_position)[1]
    gene.info.out$end_position[i] <- unique(tb1$end_position)[1]
    gene.info.out$gene_biotype[i] <- unique(tb1$gene_biotype)[1]
    gene.info.out$ensembl_gene_id[i] <- unique(tb1$ensembl_gene_id)[1]
    gene.info.out$entrezgene_id[i] <- unique(tb1$entrezgene_id)[1]
    gene.info.out$external_synonym[i] <- paste(unique(tb1$hgnc_symbol), collapse = ",")
  }
}
#################################################################


##### Get info from the 1298 genes used in original science advances paper #####
# Retrieve gene information for 1298 genes
gene.info1 <- getBM(
  attributes = c(
    "hgnc_symbol",
    "chromosome_name",
    "start_position",
    "end_position",
    "gene_biotype",
    "ensembl_gene_id",
    "entrezgene_id",
    "external_synonym"
  ),
  filters = "entrezgene_id",
  values = target_gene$Entrez_ID,
  mart = ensembl
)

# Initialize an empty data frame to store the gene information
gene.info.out1 <- data.frame(matrix(data = NA, ncol = ncol(gene.info1), nrow = nrow(target_gene)), stringsAsFactors = F)
colnames(gene.info.out1) <- c("Gene_Symbol", colnames(gene.info1)[-1])
gene.info.out1$Gene_Symbol <- target_gene$Symbol

# Populate the data frame with the retrieved gene information
for (i in 1:nrow(gene.info.out1)) {
  # Filter the gene information for the current gene symbol
  tb <- gene.info1[which(gene.info1$hgnc_symbol == gene.info.out1$Gene_Symbol[i]),]

  # If there is exactly one match, populate the row with the gene information
  if (nrow(tb) == 1) {
    gene.info.out1[i, 2:ncol(tb)] <- tb[,-1]
  }

  # If there are multiple matches, populate the row with unique values
  if (nrow(tb) > 1) {
    gene.info.out1$chromosome_name[i] <- unique(tb$chromosome_name)[1]
    gene.info.out1$start_position[i] <- unique(tb$start_position)[1]
    gene.info.out1$end_position[i] <- unique(tb$end_position)[1]
    gene.info.out1$gene_biotype[i] <- unique(tb$gene_biotype)[1]
    gene.info.out1$ensembl_gene_id[i] <- unique(tb$ensembl_gene_id)[1]
    gene.info.out1$entrezgene_id[i] <- unique(tb$entrezgene_id)[1]
    gene.info.out1$external_synonym[i] <- paste(unique(tb$external_synonym), collapse = ",")
  }

  # Check for matches in the external_synonym field
  tb1 <- gene.info1[which(gene.info1$external_synonym == gene.info.out1$Gene_Symbol[i]),]

  # If there is exactly one match, populate the row with the gene information
  if (nrow(tb1) == 1) {
    gene.info.out1$chromosome_name[i] <- tb1$chromosome_name
    gene.info.out1$start_position[i] <- tb1$start_position
    gene.info.out1$end_position[i] <- tb1$end_position
    gene.info.out1$gene_biotype[i] <- tb1$gene_biotype
    gene.info.out1$ensembl_gene_id[i] <- tb1$ensembl_gene_id
    gene.info.out1$entrezgene_id[i] <- tb1$entrezgene_id
    gene.info.out1$external_synonym[i] <- tb1$hgnc_symbol
  }

  # If there are multiple matches, populate the row with unique values
  if (nrow(tb1) > 1) {
    gene.info.out1$chromosome_name[i] <- unique(tb1$chromosome_name)[1]
    gene.info.out1$start_position[i] <- unique(tb1$start_position)[1]
    gene.info.out1$end_position[i] <- unique(tb1$end_position)[1]
    gene.info.out1$gene_biotype[i] <- unique(tb1$gene_biotype)[1]
    gene.info.out1$ensembl_gene_id[i] <- unique(tb1$ensembl_gene_id)[1]
    gene.info.out1$entrezgene_id[i] <- unique(tb1$entrezgene_id)[1]
    gene.info.out1$external_synonym[i] <- paste(unique(tb1$hgnc_symbol), collapse = ",")
  }

}

#1298 genes
# Retrieve gene information for the target genes
gene.info1 <- getBM(
  attributes = c(
    "hgnc_symbol",
    "chromosome_name",
    "start_position",
    "end_position",
    "gene_biotype",
    "ensembl_gene_id",
    "entrezgene_id",
    "external_synonym"
  ),
  filters = "entrezgene_id",
  values = target_gene$Entrez_ID,
  mart = ensembl
)

# Initialize an empty data frame to store the gene information
gene.info.out1 <- data.frame(matrix(data = NA, ncol = ncol(gene.info1), nrow = nrow(target_gene)), stringsAsFactors = F)
colnames(gene.info.out1) <- c("Gene_Symbol", colnames(gene.info1)[-1])
gene.info.out1$Gene_Symbol <- target_gene$Symbol

# Populate the data frame with the retrieved gene information
for (i in 1:nrow(gene.info.out1)) {
  # Filter the gene information for the current gene symbol
  tb <- gene.info1[which(gene.info1$hgnc_symbol == gene.info.out1$Gene_Symbol[i]),]

  # If there is exactly one match, populate the row with the gene information
  if (nrow(tb) == 1) {
    gene.info.out1[i, 2:ncol(tb)] <- tb[,-1]
  }

  # If there are multiple matches, populate the row with unique values
  if (nrow(tb) > 1) {
    gene.info.out1$chromosome_name[i] <- unique(tb$chromosome_name)[1]
    gene.info.out1$start_position[i] <- unique(tb$start_position)[1]
    gene.info.out1$end_position[i] <- unique(tb$end_position)[1]
    gene.info.out1$gene_biotype[i] <- unique(tb$gene_biotype)[1]
    gene.info.out1$ensembl_gene_id[i] <- unique(tb$ensembl_gene_id)[1]
    gene.info.out1$entrezgene_id[i] <- unique(tb$entrezgene_id)[1]
    gene.info.out1$external_synonym[i] <- paste(unique(tb$external_synonym), collapse = ",")
  }

  # Check for matches in the external_synonym field
  tb1 <- gene.info1[which(gene.info1$external_synonym == gene.info.out1$Gene_Symbol[i]),]

  # If there is exactly one match, populate the row with the gene information
  if (nrow(tb1) == 1) {
    gene.info.out1$chromosome_name[i] <- tb1$chromosome_name
    gene.info.out1$start_position[i] <- tb1$start_position
    gene.info.out1$end_position[i] <- tb1$end_position
    gene.info.out1$gene_biotype[i] <- tb1$gene_biotype
    gene.info.out1$ensembl_gene_id[i] <- tb1$ensembl_gene_id
    gene.info.out1$entrezgene_id[i] <- tb1$entrezgene_id
    gene.info.out1$external_synonym[i] <- tb1$hgnc_symbol
  }

  # If there are multiple matches, populate the row with unique values
  if (nrow(tb1) > 1) {
    gene.info.out1$chromosome_name[i] <- unique(tb1$chromosome_name)[1]
    gene.info.out1$start_position[i] <- unique(tb1$start_position)[1]
    gene.info.out1$end_position[i] <- unique(tb1$end_position)[1]
    gene.info.out1$gene_biotype[i] <- unique(tb1$gene_biotype)[1]
    gene.info.out1$ensembl_gene_id[i] <- unique(tb1$ensembl_gene_id)[1]
    gene.info.out1$entrezgene_id[i] <- unique(tb1$entrezgene_id)[1]
    gene.info.out1$external_synonym[i] <- paste(unique(tb1$hgnc_symbol), collapse = ",")
  }
}
#################################################################


##### Get info from cosmic data #####
# Cosmic 738 genes
# Identify loss genes that are not in gene.all
loss_genes <- cosmic$GENE_SYMBOL[!cosmic$GENE_SYMBOL %in% gene.all$Gene_Symbol]

# Retrieve gene information for the loss genes
gene.info2 <- getBM(
  attributes = c(
    "hgnc_symbol",
    "chromosome_name",
    "start_position",
    "end_position",
    "gene_biotype",
    "ensembl_gene_id",
    "entrezgene_id",
    "external_synonym"
  ),
  filters = "hgnc_symbol",
  values = loss_genes,
  mart = ensembl
)

# Initialize an empty data frame to store the gene information
gene.info.out2 <- data.frame(matrix(data = NA, ncol = ncol(gene.info2), nrow = length(loss_genes)), stringsAsFactors = FALSE)
colnames(gene.info.out2) <- c("Gene_Symbol", colnames(gene.info2)[-1])
gene.info.out2$Gene_Symbol <- loss_genes

# sum(toupper(gene.all$external_synonym) %in% toupper(gene.info2$external_synonym))

# Populate the data frame with the retrieved gene information
for (i in 1:nrow(gene.info.out2)) {
  # Filter the gene information for the current gene symbol
  tb <- gene.info2[which(gene.info2$hgnc_symbol == gene.info.out2$Gene_Symbol[i]),]

  # If there is exactly one match, populate the row with the gene information
  if (nrow(tb) == 1) {
    gene.info.out2[i, 2:ncol(tb)] <- tb[,-1]
  }

  # If there are multiple matches, populate the row with unique values
  if (nrow(tb) > 1) {
    gene.info.out2$chromosome_name[i] <- unique(tb$chromosome_name)[1]
    gene.info.out2$start_position[i] <- unique(tb$start_position)[1]
    gene.info.out2$end_position[i] <- unique(tb$end_position)[1]
    gene.info.out2$gene_biotype[i] <- unique(tb$gene_biotype)[1]
    gene.info.out2$ensembl_gene_id[i] <- unique(tb$ensembl_gene_id)[1]
    gene.info.out2$entrezgene_id[i] <- unique(tb$entrezgene_id)[1]
    gene.info.out2$external_synonym[i] <- paste(unique(tb$external_synonym), collapse = ",")
  }

  # Check for matches in the external_synonym field
  tb1 <- gene.info2[which(gene.info2$external_synonym == gene.info.out2$Gene_Symbol[i]),]

  # If there is exactly one match, populate the row with the gene information
  if (nrow(tb1) == 1) {
    gene.info.out2$chromosome_name[i] <- tb1$chromosome_name
    gene.info.out2$start_position[i] <- tb1$start_position
    gene.info.out2$end_position[i] <- tb1$end_position
    gene.info.out2$gene_biotype[i] <- tb1$gene_biotype
    gene.info.out2$ensembl_gene_id[i] <- tb1$ensembl_gene_id
    gene.info.out2$entrezgene_id[i] <- tb1$entrezgene_id
    gene.info.out2$external_synonym[i] <- tb1$hgnc_symbol
  }

  # If there are multiple matches, populate the row with unique values
  if (nrow(tb1) > 1) {
    gene.info.out2$chromosome_name[i] <- unique(tb1$chromosome_name)[1]
    gene.info.out2$start_position[i] <- unique(tb1$start_position)[1]
    gene.info.out2$end_position[i] <- unique(tb1$end_position)[1]
    gene.info.out2$gene_biotype[i] <- unique(tb1$gene_biotype)[1]
    gene.info.out2$ensembl_gene_id[i] <- unique(tb1$ensembl_gene_id)[1]
    gene.info.out2$entrezgene_id[i] <- unique(tb1$entrezgene_id)[1]
    gene.info.out2$external_synonym[i] <- paste(unique(tb1$hgnc_symbol), collapse = ",")
  }

}
####################################################

###### Combine gene information from cosmic, 1298 genes, and 23Q4 genes
# Combine all gene information into a single data frame
gene.info.all <- rbind(gene.all, gene.info.out, gene.info.out1, gene.info.out2)
gene.info.all$check <- paste(gene.info.all$Gene_Symbol, gene.info.all$entrezgene_id, sep = "_")

# Remove duplicate entries based on the check column
gene.info.all <- gene.info.all[!duplicated(gene.info.all$check),]

#rename cosmic$GENE_SYMBOL to Gene_Symbol
colnames(cosmic)[1] <- "Gene_Symbol"

# Merge the combined gene information with COSMIC data
gene.info.all.cosmic <- merge(x = gene.info.all, y = cosmic[, c(1:2, 7:19)], by = "Gene_Symbol", all.x = TRUE)

# Remove duplicate entries based on the Gene_Symbol column
gene.info.all.cosmic <- gene.info.all.cosmic[!duplicated(gene.info.all.cosmic$Gene_Symbol),]

#gene fingerprtint: 20597 + cosmic data
gene.info.all.cosmic <- merge(x = gene.all,y = cosmic[,c(1:2,7:19)], by = "Gene_Symbol", all.x= T, sort = F)

#################################################################


##### Get Ranges for predicted dependency scores in different datasets #####
# Calculate the range for each gene in GeneEffect_18Q2_278CCLs
range_gene_effect_278 <- apply(GeneEffect_18Q2_278CCLs, 2, function(x) {
  range_values <- as.numeric(range(x, na.rm = TRUE))
  paste0("[", sprintf("%.2f", range_values[1]), ", ", sprintf("%.2f", range_values[2]), "]")
})

# Calculate the range for each gene in ccle_pred_278CCLs
range_ccle_pred_278 <- apply(ccle_pred_278CCLs, 2, function(x) {
  range_values <- as.numeric(range(x, na.rm = TRUE))
  paste0("[", sprintf("%.2f", range_values[1]), ", ", sprintf("%.2f", range_values[2]), "]")
})

# Calculate the range for each gene in ccle_23q4_chronos for real 996
gene_symbols <- gsub("\\..*", "", colnames(ccle_23q4_chronos)) # clean column names which are gene symbols
colnames(ccle_23q4_chronos) <- gene_symbols
rownames(ccle_23q4_chronos) <- ccle_23q4_chronos[,1] # make the first column into the rownames and delete the first column
ccle_23q4_chronos <- ccle_23q4_chronos[,-1]
range_ccle_23q4 <- apply(ccle_23q4_chronos, 2, function(x) {
  range_values <- as.numeric(range(x, na.rm = TRUE))
  paste0("[", sprintf("%.2f", range_values[1]), ", ", sprintf("%.2f", range_values[2]), "]")
})

# Calculate the range for each gene in tcga.pred
# since the first column of tcga.pred is CRISPR_GENE, we need to transpose and then make the first row into the column names
tcga_pred <- as.data.frame(t(tcga.pred))
colnames(tcga_pred) <- tcga_pred[1,]
tcga_pred <- tcga_pred[-1,]
tcga_pred <- as.data.frame(apply(tcga_pred, 2, as.numeric))

# now we can create range scores for tcga.pred where I am looking for the range of each gene (column)
range_tcga_pred <- apply(tcga_pred, 2, function(x) {
  range_values <- as.numeric(range(x, na.rm = TRUE))
  paste0("[", sprintf("%.2f", range_values[1]), ", ", sprintf("%.2f", range_values[2]), "]")
})

# Create a data frame for range scores with NA for missing values
range_scores <- data.frame(
  Gene_Symbol = gene.all$Gene_Symbol,
  Range_GeneEffect = rep(NA, nrow(gene.all)),
  Range_CclePred = rep(NA, nrow(gene.all)),
  Range_TcgaPred = rep(NA, nrow(gene.all)),
  Range_Ccle23q4 = rep(NA, nrow(gene.all)),
  stringsAsFactors = FALSE
)

# Create data frames for each range score
range_gene_effect_df <- data.frame(Gene_Symbol = names(range_gene_effect_278), Range_GeneEffect = range_gene_effect_278, stringsAsFactors = FALSE)
range_ccle_pred_df <- data.frame(Gene_Symbol = names(range_ccle_pred_278), Range_CclePred = range_ccle_pred_278, stringsAsFactors = FALSE)
range_tcga_pred_df <- data.frame(Gene_Symbol = names(range_tcga_pred), Range_TcgaPred = range_tcga_pred, stringsAsFactors = FALSE)
range_ccle_23q4_df <- data.frame(Gene_Symbol = names(range_ccle_23q4), Range_Ccle23q4 = range_ccle_23q4, stringsAsFactors = FALSE)

# Merge the range scores with the range_scores data frame
range_scores <- merge(range_scores, range_gene_effect_df, by = "Gene_Symbol", all.x = TRUE)
range_scores <- merge(range_scores, range_ccle_pred_df, by = "Gene_Symbol", all.x = TRUE)
range_scores <- merge(range_scores, range_tcga_pred_df, by = "Gene_Symbol", all.x = TRUE)
range_scores <- merge(range_scores, range_ccle_23q4_df, by = "Gene_Symbol", all.x = TRUE)

# Ensure the final data frame has the correct column order
range_scores <- range_scores[, c("Gene_Symbol", "Range_GeneEffect.y", "Range_CclePred.y", "Range_TcgaPred.y", "Range_Ccle23q4.y")]

# Rename columns to remove the .y suffix
colnames(range_scores) <- c("Gene_Symbol", "Range_GeneEffect", "Range_CclePred", "Range_TcgaPred", "Range_Ccle23q4")

# Add range scores to gene.info.all.cosmic
gene.info.all.cosmic <- merge(x = gene.info.all.cosmic, y = range_scores, by = "Gene_Symbol", all.x = TRUE)

# Add performance based on Gene Symbol column, only including the "Exp" column
gene.info.all.cosmic <- merge(x = gene.info.all.cosmic, y = performance[, c("Gene_Symbol", "Exp")], by = "Gene_Symbol", all.x = TRUE)
#################################################################


##### Limit rows to genes within gene sets from fingerprint with columns that are needed by app #####
# # Extract gene symbols from hallmark dataframe
# hallmark_genes <- as.vector(unlist(hallmark))
# # Extract gene symbols from C2_cp dataframe
# C2_cp_genes <- as.vector(unlist(C2_cp))
# # Combine the gene symbols into a single vector
# all_genes <- c(hallmark_genes, C2_cp_genes)
# # Remove duplicates to get unique gene symbols
# unique_genes <- unique(all_genes)
# # remove NA in unique genes
# unique_genes <- unique_genes[is.na(unique_genes) == FALSE]

# #print length of desired unique genes from hallmark and c2cp
# print("printing length of desired unique genes from hallmark and c2cp")
# print(length(unique_genes))

# # Create a new dataframe from gene_annotations with only the unique genes
# gene.info.all.cosmic <- gene.info.all.cosmic[gene.info.all.cosmic$Gene_Symbol %in% unique_genes,]
################################################


##### change tissue type abbreviations to terms for the tissue type column #####
abbreviation_to_term <- list(
  A = "amplification",
  aCML = "atypical chronic myeloid leukaemia",
  AEL = "acute eosinophilic leukaemia",
  AITL = "angioimmunoblastic T cell lymphoma",
  AL = "acute leukaemia",
  ALCL = "anaplastic large-cell lymphoma",
  ALL = "acute lymphocytic leukaemia",
  AML = "acute myeloid leukaemia",
  `AML*` = "acute myeloid leukaemia (primarily treatment associated)",
  APL = "acute promyelocytic leukaemia",
  `B-ALL` = "B-cell acute lymphocytic leukaemia",
  `B-CLL` = "B-cell lymphocytic leukaemia",
  `B-NHL` = "B-cell non-Hodgkin lymphoma",
  CLL = "chronic lymphocytic leukaemia",
  CML = "chronic myeloid leukaemia",
  CMML = "chronic myelomonocytic leukaemia",
  CNL = "chronic neutrophilic leukaemia",
  CNS = "central nervous system",
  D = "large deletion",
  DFSP = "dermatofibrosarcoma protuberans",
  DGC = "diffuse-type gastric carcinoma",
  DIPG = "diffuse intrinsic pontine glioma",
  DLBCL = "diffuse large B-cell lymphoma",
  DLCL = "diffuse large-cell lymphoma",
  Dom = "dominant",
  E = "epithelial",
  `ETP-ALL` = "early T-cell precursor acute lymphoblastic leukaemia",
  F = "frameshift",
  GBM = "glioblastoma multiforme",
  GIST = "gastrointestinal stromal tumour",
  HES = "hypereosinophilic syndrome",
  HNSCC = "head and neck squamous cell carcinoma",
  JMML = "juvenile myelomonocytic leukaemia",
  L = "leukaemia/lymphoma",
  M = "mesenchymal",
  MALT = "mucosa-associated lymphoid tissue lymphoma",
  MCL = "mantle cell lymphoma",
  MDS = "myelodysplastic syndrome",
  Mis = "missense",
  MLCLS = "mediastinal large cell lymphoma with sclerosis",
  MM = "multiple myeloma",
  MPN = "myeloproliferative neoplasm",
  N = "nonsense",
  NHL = "non-Hodgkin lymphoma",
  `NK/T` = "natural killer T cell",
  NSCLC = "non small cell lung cancer",
  O = "other",
  PMBL = "primary mediastinal B-cell lymphoma",
  `pre-B ALL` = "pre-B-cell acute lymphoblastic leukaemia",
  RCC = "renal cell carcinoma",
  Rec = "recessive",
  S = "splice site",
  sAML = "secondary acute myeloid leukaemia",
  SCC = "squamous cell carcinoma",
  SCCOHT = "small cell carcinoma of the ovary, hypercalcaemic type",
  `SM-AHD` = "systemic mastocytosis associated with other haematological disorder",
  SMZL = "splenic marginal zone lymphoma",
  T = "translocation",
  `T-ALL` = "T-cell acute lymphoblastic leukaemia",
  `T-CLL` = "T-cell chronic lymphocytic leukaemia",
  `T-PLL` = "T-cell prolymphocytic leukaemia",
  TGCT = "testicular germ cell tumour",
  TSG = "Tumour Suppressor Gene",
  WM = "Waldenstrom's macroglobulinaemia"
)

gene.info.all.cosmic <- gene.info.all.cosmic %>%
  mutate(TISSUE_TYPE = recode(TISSUE_TYPE, !!!abbreviation_to_term))


##### clean final data ####
# rename gene.info.all.cosmic to gene_annotations
gene_annotations <- gene.info.all.cosmic
# Standardize NA values to empty strings.
gene_annotations[is.na(gene_annotations)] <- ""
# also standardize if it is a string NA
gene_annotations[gene_annotations == "NA"] <- ""

# Rename the gene_annotations columns based on matching names in gene_info_shiny
colnames(gene_annotations)[which(colnames(gene_annotations) == "NAME")] <- "Name"
colnames(gene_annotations)[which(colnames(gene_annotations) == "CHR_BAND")] <- "Chr.Band"
colnames(gene_annotations)[which(colnames(gene_annotations) == "SOMATIC")] <- "Somatic"
colnames(gene_annotations)[which(colnames(gene_annotations) == "GERMLINE")] <- "Germline"
colnames(gene_annotations)[which(colnames(gene_annotations) == "TUMOUR_TYPES_SOMATIC")] <- "Tumour.Types.Somatic."
colnames(gene_annotations)[which(colnames(gene_annotations) == "TUMOUR_TYPES_GERMLINE")] <- "Tumour.Types.Germline."
colnames(gene_annotations)[which(colnames(gene_annotations) == "CANCER_SYNDROME")] <- "Cancer.Syndrome"
colnames(gene_annotations)[which(colnames(gene_annotations) == "TISSUE_TYPE")] <- "Tissue.Type"
colnames(gene_annotations)[which(colnames(gene_annotations) == "MOLECULAR_GENETICS")] <- "Molecular.Genetics"
colnames(gene_annotations)[which(colnames(gene_annotations) == "ROLE_IN_CANCER")] <- "Role.in.Cancer"
colnames(gene_annotations)[which(colnames(gene_annotations) == "MUTATION_TYPES")] <- "Mutation.Types"
colnames(gene_annotations)[which(colnames(gene_annotations) == "TRANSLOCATION_PARTNER")] <- "Translocation.Partner"
colnames(gene_annotations)[which(colnames(gene_annotations) == "OTHER_GERMLINE_MUT")] <- "Other.Germline.Mut"
colnames(gene_annotations)[which(colnames(gene_annotations) == "OTHER_SYNDROME")] <- "Other.Syndrome"
colnames(gene_annotations)[which(colnames(gene_annotations) == "Range_CclePred")] <- "CCLE_pred_278CCLs"
colnames(gene_annotations)[which(colnames(gene_annotations) == "Range_TcgaPred")] <- "TCGA_pred_8238"
colnames(gene_annotations)[which(colnames(gene_annotations) == "Range_Ccle23q4")] <- "CCLE_real_996CCLs"
colnames(gene_annotations)[which(colnames(gene_annotations) == "Range_GeneEffect")] <- "CCLE_real_278CCLs"
colnames(gene_annotations)[which(colnames(gene_annotations) == "Exp")] <- "Model_Exp"

# limit columnss to those needed in app
gene_annotations <- gene_annotations[, !(colnames(gene_annotations) %in% c("start_position", "end_position", "Germline", "Tumour.Types.Germline.", "Tumour.Types.Somatic.", "Name", "Somatic", "gene_biotype", "Other.Germline.Mut", "Other.Syndrome", "Chr.Band", "chromosome_name"))]

# Reorder columns to the specified order
gene_annotations <- gene_annotations[, c("Gene_Symbol", "ensembl_gene_id", "entrezgene_id", 
                                         "external_synonym", "Cancer.Syndrome", "Tissue.Type", 
                                         "Molecular.Genetics", "Role.in.Cancer", "Mutation.Types", 
                                         "Translocation.Partner", "CCLE_pred_278CCLs", "CCLE_real_278CCLs", 
                                         "CCLE_real_996CCLs", "TCGA_pred_8238", "Model_Exp")]


# Convert columns in gene_annotations to match the data types in gene_info_shiny
setwd(data_dir)
gene_info_shiny <- read.delim("gene_info_20597_fpsGs_with_cosmic_ranges_and_performance.txt", sep = "\t")
# Columns to convert
columns_to_convert <- colnames(gene_annotations)
for (col in columns_to_convert) {
  gene_annotations[[col]] <- as(gene_info_shiny[[col]], class(gene_info_shiny[[col]]))
}
gene_info_shiny$entrezgene_id <- as.numeric(gene_info_shiny$entrezgene_id)
gene_info_shiny$Model_Exp <- as.numeric(gene_info_shiny$Model_Exp)
###############################


##### Save the final gene annotation table #####
# set wd to the destination directory
setwd(dest_dir)

# save the gene information as gene_annotations.csv
write.csv(gene_annotations, file = "gene_annotations.csv", row.names = F)

# include gene index if needed
#save(ccle_23q4_chronos, ccle_23q4_gene_index, file = "ccle_23q4_gene_index")
#################################################


########### print validation that the gene_annotations.csv file is the same as the shiny gene annotations table ###########
# make a new subset named gene_info_shiny that does not have a few of the columns: Model_Meth, Model_CNA, Model_Mut, Model_MutExp, Model_Full, "start_position", "end_position", "Germline", "Tumour.Types.Germline.", "Tumour.Types.Somatic.", "Name", "Somatic", "gene_biotype", "Other.Germline.Mut", "Other.Syndrome", "Chr.Band", "chromosome_name" which are columns not included in the new app.
gene_info_shiny <- gene_info_shiny[, !(colnames(gene_info_shiny) %in% c("Model_Meth", "Model_CNA", "Model_Mut", "Model_MutExp", "Model_Full", "start_position", "end_position", "Germline", "Tumour.Types.Germline.", "Tumour.Types.Somatic.", "Name", "Somatic", "gene_biotype", "Other.Germline.Mut", "Other.Syndrome", "Chr.Band", "chromosome_name"))]

# print if the dataframes are equal
print('printing if the dataframes is the same as the previous data frame created for app development. If TRUE, they are the same, if FALSE, you will understand how your new data differs from the previous data')
print(all.equal(gene_info_shiny, gene_annotations))