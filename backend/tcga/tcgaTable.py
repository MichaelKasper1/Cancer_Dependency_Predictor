import pandas as pd

def tcgaTable(tcga_table_start, dist_table, gene_annotations):
    print("starting tcgaTable function.")
    
    # delete 'index' column of tcga_table_start
    if 'index' in tcga_table_start.columns:
        tcga_table_start.drop(columns=['index'], inplace=True)

    # Create a dictionary to map group# to groupNames
    group_names = dist_table.set_index('group')['groupNames'].to_dict()

    # Rename group# columns to corresponding groupNames
    rename_dict = {f'group{group}': name for group, name in group_names.items()}
    tcga_table_start.rename(columns=rename_dict, inplace=True)

    # Remove index column
    tcga_table_start.reset_index(drop=True, inplace=True)

    # Sort by p-value
    tcga_table_start.sort_values(by='pval', inplace=True)

    # subset gene annotations to include 'chromosome_name', 'start_position', 'end_position', 'ensembl_gene_id', 'entrezgene_id', 'external_synonym', 'Name', 'Chr_Band', 'Somatic', 'Germline', 'Tumour_Types_Somatic', 'Tumour_Types_Germline', 'Cancer_Syndrome', 'Tissue_Type', 'Molecular_Genetics', 'Role_in_Cancer', 'Mutation_Types', 'Translocation_Partner', 'Other_Germline_Mut', 'Other_Syndrome'
    gene_annotations_subset = gene_annotations[['Gene_Symbol','chromosome_name', 'start_position', 'end_position', 'ensembl_gene_id', 'entrezgene_id', 'external_synonym', 'Name', 'Chr_Band', 'Somatic', 'Germline', 'Tumour_Types_Somatic', 'Tumour_Types_Germline', 'Cancer_Syndrome', 'Tissue_Type', 'Molecular_Genetics', 'Role_in_Cancer', 'Mutation_Types', 'Translocation_Partner', 'Other_Germline_Mut', 'Other_Syndrome']]

    # rename both gene_id as well as CRISPR_GENE to "Gene"
    tcga_table_start.rename(columns={'CRISPR_GENE': 'Gene'}, inplace=True)
    gene_annotations_subset.rename(columns={'Gene_Symbol': 'Gene'}, inplace=True)
    
    tcga_table = pd.merge(tcga_table_start, gene_annotations_subset, on='Gene', how='left')

    # add 'Average Predicted CERES Score' to the names of column 2 and 3
    tcga_table.rename(columns={tcga_table.columns[1]: f"{tcga_table.columns[1]} (average predicted CERES score)",
                               tcga_table.columns[2]: f"{tcga_table.columns[2]} (average predicted CERES score)"}, inplace=True)

    # round the first 3 columns to 3 decimal points
    tcga_table.iloc[:, :4] = tcga_table.iloc[:, :4].round(3)

    # rename chromosome_name to chromosome, ensembl_gene_id to ensembl id, external_synonym to synonym
    tcga_table.rename(columns={'chromosome_name': 'chromosome', 'ensembl_gene_id': 'ensembl id', 'external_synonym': 'synonym'}, inplace=True)

    # The pval column gets renamed depending on the number of groups in dist_table. if it is 2 then it is a 'One tailed t-test p-value' and if it is more then it is a 'ANOVA p-value'
    if len(group_names) == 2:
        tcga_table.rename(columns={'pval': 'One tailed t-test p-value'}, inplace=True)
    else:
        tcga_table.rename(columns={'pval': 'ANOVA p-value'}, inplace=True)
    

    # replace remaining underscores in column names to spaces
    tcga_table.columns = tcga_table.columns.str.replace('_', ' ')

    return tcga_table