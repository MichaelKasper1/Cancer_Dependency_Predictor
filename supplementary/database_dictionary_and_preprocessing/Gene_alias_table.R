# Generate gene alias table
# Date original: 20240206
# edited by mjk October 15, 2024

# This script updates the gene alias table for use in the DeepDep web server
# by querying the Ensembl database for gene information.

# Requirements located within your data_dir directory:
# - "ccle_exp_for_missing_value_6016.RData" available at code ocean for DeepDEP
# - "ccle_exp_and_mut_with_gene_alias_shinyDeepDep.RData" available at mongoDB

# Output placed in your dest_dir:
# - "ccle_exp_and_mut_with_gene_alias_DeepDep.RData"

######### SET THESE VARIABLES BASED ON OUTPUT AND REQUIREMENT LOCATIONS #######
data_dir <- "/Users/michaelkasper/Documents/DeepDep_learning/shinyDeepDEP_20240301/shinyDeepDep_20240301/data" #nolint
dest_dir <- "/Users/michaelkasper/Documents/Deepdep_data_processing_and_model_training/data processing/data_processing_mjk" #nolint
###############################################################################

# Load the biomaRt library for accessing the Ensembl database
library(biomaRt)

# Change the working directory to the local location of shinydeepdep directory
setwd(data_dir)

# Load required data files
load("Prep4DeepDep_data/ccle_exp_for_missing_value_6016.RData")
load("ccle_exp_and_mut_with_gene_alias_shinyDeepDep.RData")

# Convert all gene names to uppercase
check_table <- as.data.frame(apply(ccle_exp_ensembl_gene_alias, MARGIN = 2,
                                   FUN = function(x) return(toupper(x))))

# Filter the table to include only genes present in exp_index
exp_alias_table <- check_table[which(check_table$Gene %in% exp_index$Gene), ]

# Remove duplicate gene entries
exp_alias_table <- exp_alias_table[!duplicated(exp_alias_table$Gene), ]

# Identify genes that are in exp_index but not in exp_alias_table
loss_genes <- exp_index$Gene[-which(exp_index$Gene %in% exp_alias_table$Gene)]

# Connect to the Ensembl database
ensembl <- useEnsembl(biomart = "genes")

# Use the human gene dataset from Ensembl
ensembl <- useDataset(dataset = "hsapiens_gene_ensembl", mart = ensembl)

# Retrieve gene information for the loss_genes from Ensembl
gene_info <- getBM(attributes = c("hgnc_symbol", "external_synonym",
                                  "ensembl_gene_id", "entrezgene_id"),
                   filters = "hgnc_symbol",
                   values = loss_genes,
                   mart = ensembl)

# Create a temporary alias table with the same structure as exp_alias_table
temp_alias <- data.frame(matrix(data = NA, nrow = length(loss_genes),
                                ncol = ncol(exp_alias_table)),
                         stringsAsFactors = FALSE)
colnames(temp_alias) <- colnames(exp_alias_table)
temp_alias$Gene <- loss_genes

# Populate the temporary alias table with gene information from Ensembl
for (i in seq_along(loss_genes)) {
  tb1 <- gene_info[which(gene_info$hgnc_symbol == temp_alias$Gene[i]), ]

  if (nrow(tb1) != 0) {
    temp_alias$ensembl_id[i] <- unique(tb1$ensembl_gene_id)[1]

    if (length(unique(tb1$external_synonym)) > 1) {
      temp_alias[i, 3:(length(unique(tb1$external_synonym)) + 2)] <- unique(tb1$external_synonym) #nolint
    }

    if (all(length(unique(tb1$external_synonym)) == 1 & unique(tb1$external_synonym) != "")) { #nolint
      temp_alias[i, 3] <- unique(tb1$external_synonym)
    }
  }
}

# Update the exp_alias_table with the new gene information
exp_alias_table_update <- rbind(exp_alias_table, temp_alias)
exp_alias_table_update <- exp_alias_table_update[match(exp_index$Gene,
                                                       exp_alias_table_update$Gene), ] #nolint
identical(exp_alias_table_update$Gene, exp_index$Gene)

# Set working directory to destination directory
setwd(dest_dir)

# Save the updated alias table
write.csv(exp_alias_table_update, file = "ccle_exp_with_gene_alias_DeepDep.csv",
          row.names = FALSE)

print("Gene alias table updated successfully.")