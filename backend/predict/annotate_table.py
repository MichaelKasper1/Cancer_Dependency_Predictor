import pandas as pd
import time

def annotate_table(result_df, gene_annotations, data_source, ccl_predicted_data_model_10xCV_paper, GeneEffect_18Q2_278CCLs, tcga_pred):
    # track time for this function
    start = time.time()

    # Add row names (genes) as a new column at the beginning
    result_df.insert(0, 'gene', result_df.index)

    # Round all numerical entries to two decimals
    result_df = result_df.round(2)

    # Calculate the average of the columns (excluding the 'gene' column)
    result_df['Average_Score'] = result_df.iloc[:, 1:].mean(axis=1)

    # Sort by the average score
    result_df = result_df.sort_values(by='Average_Score', ascending=True)

    # Extract dynamic column names (excluding the 'gene' column)
    dynamic_columns = result_df.columns[1:-1].tolist()  # Exclude 'gene' and 'Average_Score'

    # Columns to merge from gene_annotations
    common_columns = [
        "Model_Exp", "ensembl_gene_id", "entrezgene_id", "external_synonym", "Cancer_Syndrome",
        "Tissue_Type", "Molecular_Genetics", "Role_in_Cancer", "Mutation_Types",
        "Translocation_Partner", "Other_Syndrome"
    ]

    if data_source == "tumor":
        additional_columns = ["TCGA_pred_8238"]
        final_columns = dynamic_columns + [
            "Prediction performance (Corr)", "Prediction Percentile TCGA", "Prediction range (TCGA; n=8238)", "Ensembl gene ID", 
            "Entrez gene ID", "Synonym", "Cancer syndrome", "Tissue type", "Molecular genetics", 
            "Role in cancer", "Mutation types", "Translocation partner", "Other syndrome"
        ]

        # Add new columns for TCGA percentiles
        result_df["Prediction_Percentile_TCGA"] = None

        # Calculate TCGA percentiles
        for i, row in result_df.iterrows():
            gene_symbol = row['gene']

            # Find the row in tcga_pred that matches the gene symbol
            tcga_row = tcga_pred[tcga_pred['CRISPR_GENE'] == gene_symbol]
            if not tcga_row.empty:
                pred_values = tcga_row.iloc[0, 1:]  # Exclude the gene symbol column
                # Ensure the values are floats
                try:
                    pred_values = pred_values.astype(float)
                    average_score = float(row['Average_Score'])
                except ValueError as e:
                    print(f"ValueError: {e} for gene_symbol: {gene_symbol}")
                    continue

                percentile = sum(pred_values <= average_score) / len(pred_values)
                result_df.at[i, "Prediction_Percentile_TCGA"] = round((1 - percentile) * 100, 2)
            else:
                result_df.at[i, "Prediction_Percentile_TCGA"] = ""

    elif data_source == "cell-line":
        additional_columns = ["CCLE_pred_278CCLs", "CCLE_real_278CCLs", "CCLE_real_996CCLs"]
        final_columns = dynamic_columns + [
            "Prediction performance (Corr)", "Prediction DepMap percentile (CERES; n=278)", "Predicted DepMap range (CERES; n=278)",
            "Real DepMap percentile (CCLE; n=278)", "Real DepMap range (CCLE; n=278)", "Real DepMap range (Chronos; n=996)", "Ensembl gene ID", 
            "Entrez gene ID", "Synonym", "Cancer syndrome", "Tissue type", "Molecular genetics", 
            "Role in cancer", "Mutation types", "Translocation partner", "Other syndrome"
        ]

        # Add new columns for percentiles
        result_df["Prediction_Percentile_278_cell_lines"] = None
        result_df["Real_Percentile_278_cell_lines"] = None

        # Calculate percentiles
        for i, row in result_df.iterrows():
            gene_symbol = row['gene']
            if gene_symbol in ccl_predicted_data_model_10xCV_paper.columns:
                # Prediction (278 cell lines)
                pred_value = ccl_predicted_data_model_10xCV_paper[gene_symbol]
                # Ensure the values are floats
                try:
                    pred_value = pred_value.astype(float)
                    average_score = float(row['Average_Score'])
                except ValueError as e:
                    print(f"ValueError: {e} for gene_symbol: {gene_symbol}")
                    continue

                percentile = sum(pred_value <= average_score) / len(pred_value)
                result_df.at[i, "Prediction_Percentile_278_cell_lines"] = round((1 - percentile) * 100, 2)

                # Real (278 cell lines)
                real_value = GeneEffect_18Q2_278CCLs[gene_symbol]
                # Ensure the values are floats
                try:
                    real_value = real_value.astype(float)
                except ValueError as e:
                    print(f"ValueError: {e} for gene_symbol: {gene_symbol}")
                    continue

                percentile = sum(real_value <= average_score) / len(real_value)
                result_df.at[i, "Real_Percentile_278_cell_lines"] = round((1 - percentile) * 100, 2)
            else:
                result_df.at[i, "Prediction_Percentile_278_cell_lines"] = ""
                result_df.at[i, "Real_Percentile_278_cell_lines"] = ""
    else:
        raise ValueError(f"Invalid data source: {data_source}")

    # Merge result_df with gene_annotations based on the gene symbols
    columns_to_merge = ["Gene_Symbol"] + additional_columns + common_columns
    result_df = result_df.merge(gene_annotations[columns_to_merge], left_on='gene', right_on='Gene_Symbol', how='left')

    # Rename columns to match the final desired column names
    column_rename_map = {
        "Model_Exp": "Prediction performance (Corr)",
        "Prediction_Percentile_TCGA": "Prediction Percentile TCGA",
        "Prediction_Percentile_278_cell_lines":  "Prediction DepMap percentile (CERES; n=278)",
        "CCLE_pred_278CCLs": "Predicted DepMap range (CERES; n=278)",
        "Real_Percentile_278_cell_lines": "Real DepMap percentile (CCLE; n=278)",
        "CCLE_real_278CCLs": "Real DepMap range (CCLE; n=278)",
        "TCGA_pred_8238": "Prediction range (TCGA; n=8238)",
        "CCLE_real_996CCLs": "Real DepMap range (Chronos; n=996)",
        "ensembl_gene_id": "Ensembl gene ID",
        "entrezgene_id": "Entrez gene ID",
        "external_synonym": "Synonym",
        "Cancer_Syndrome": "Cancer syndrome",
        "Tissue_Type": "Tissue type",
        "Molecular_Genetics": "Molecular genetics",
        "Role_in_Cancer": "Role in cancer",
        "Mutation_Types": "Mutation types",
        "Translocation_Partner": "Translocation partner",
        "Other_Syndrome": "Other syndrome"
    }
    result_df = result_df.rename(columns=column_rename_map)

    # Replace NaN values with None
    result_df = result_df.where(pd.notnull(result_df), None)

    # Check if all final columns are present in the DataFrame
    missing_columns = [col for col in final_columns if col not in result_df.columns]
    if missing_columns:
        raise KeyError(f"Missing columns in the DataFrame: {missing_columns}")

    # Select only the final columns
    result_df = result_df[["gene"] + final_columns]

    # Print the time taken for this function
    print(f"Time taken for annotate_table function: {time.time() - start:.2f} seconds")

    # make the 
    return result_df