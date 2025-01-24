import pandas as pd
import time

def annotate_EN_table(predictions_df, gene_annotations, model_performances_EN, ccle_21q1_expression, GeneEffect_21q1, ccle_predictions_EN):
    start = time.time()

    print("Model Performances EN:")
    print(model_performances_EN.head())
    print("CCLE 21Q1 Expression:")
    print(ccle_21q1_expression.head())
    print("Gene Annotations:")
    print(gene_annotations.head())
    print("Gene Effect 21Q1:")
    print(GeneEffect_21q1.head())
    print("Predictions DataFrame:")
    print(ccle_predictions_EN.head())

    # print shapes of all these
    print("Model Performances EN shape:", model_performances_EN.shape)
    print("CCLE 21Q1 Expression shape:", ccle_21q1_expression.shape)
    print("Gene Annotations shape:", gene_annotations.shape)
    print("Gene Effect 21Q1 shape:", GeneEffect_21q1.shape)
    print("Predictions DataFrame shape:", ccle_predictions_EN.shape)

    # Clean the ccle_21q1_expression DataFrame
    ccle_21q1_expression.columns = [col.split(' ')[0] for col in ccle_21q1_expression.columns]
    result_df = predictions_df.copy()

    # Add row names (genes) as a new column at the beginning
    result_df.insert(0, 'gene', result_df.index)

    # Round all numerical entries to two decimals
    ccle_21q1_expression = ccle_21q1_expression.round(2)
    result_df = result_df.round(2)

    # Calculate the average of the columns (excluding the 'gene' column)
    result_df['Average_Score'] = result_df.iloc[:, 1:].mean(axis=1)

    # Sort by the average score
    result_df = result_df.sort_values(by='Average_Score', ascending=True)

    # Extract dynamic column names (excluding the 'gene' column)
    dynamic_columns = result_df.columns[1:-1].tolist()  # Exclude 'gene' and 'Average_Score'

    # Columns to merge from gene_annotations
    common_columns = [
        "ensembl_gene_id", "entrezgene_id", "external_synonym", "Cancer_Syndrome",
        "Tissue_Type", "Molecular_Genetics", "Role_in_Cancer", "Mutation_Types",
        "Translocation_Partner", "Other_Syndrome"
    ]

    # Ensure the missing columns are created in gene_annotations
    for col in ["CCLE_pred_1376CCLs", "CCLE_real_1376CCLs"]:
        if col not in gene_annotations.columns:
            gene_annotations[col] = None

    additional_columns = ["CCLE_pred_1376CCLs", "CCLE_real_1376CCLs"]
    final_columns = dynamic_columns + [
        "Prediction performance (Corr)", "Prediction DepMap percentile (CERES; n=1376)", "Predicted DepMap range (CERES; n=1376)",
        "Real DepMap percentile (CCLE; n=1376)", "Real DepMap range (CCLE; n=1376)", "Ensembl gene ID", 
        "Entrez gene ID", "Synonym", "Cancer syndrome", "Tissue type", "Molecular genetics", 
        "Role in cancer", "Mutation types", "Translocation partner", "Other syndrome"
    ]

    # Add new columns for percentiles
    result_df["Prediction_Percentile_1376_cell_lines"] = None
    result_df["Real_Percentile_1376_cell_lines"] = None
    result_df["Prediction_Range_1376_cell_lines"] = None

    # Calculate percentiles and ranges
    for i, row in result_df.iterrows():
        gene_symbol = row['gene']
        if gene_symbol in ccle_21q1_expression.columns:
            # Prediction values
            pred_value = ccle_21q1_expression[gene_symbol]
            try:
                pred_value = pred_value.astype(float)
                average_score = float(row['Average_Score'])
            except ValueError as e:
                print(f"ValueError: {e} for gene_symbol: {gene_symbol}")
                continue

            percentile = sum(pred_value <= average_score) / len(pred_value)
            result_df.at[i, "Prediction_Percentile_1376_cell_lines"] = round((1 - percentile) * 100, 2)

            # Calculate range
            min_val = round(pred_value.min(), 2)
            max_val = round(pred_value.max(), 2)
            result_df.at[i, "Prediction_Range_1376_cell_lines"] = f"[{min_val}, {max_val}]"

            # Real (1376 cell lines)
            if gene_symbol in GeneEffect_21q1.columns:
                real_value = GeneEffect_21q1[gene_symbol]
                try:
                    real_value = real_value.astype(float)
                except ValueError as e:
                    print(f"ValueError: {e} for gene_symbol: {gene_symbol}")
                    continue

                percentile = sum(real_value <= average_score) / len(real_value)
                result_df.at[i, "Real_Percentile_1376_cell_lines"] = round((1 - percentile) * 100, 2)
            else:
                result_df.at[i, "Real_Percentile_1376_cell_lines"] = ""
        else:
            result_df.at[i, "Prediction_Percentile_1376_cell_lines"] = ""
            result_df.at[i, "Real_Percentile_1376_cell_lines"] = ""
            result_df.at[i, "Prediction_Range_1376_cell_lines"] = ""

    # debug print the head of result_df
    print(result_df.head())

    # Ensure 'Gene_Symbol' column exists in gene_annotations
    if 'Gene_Symbol' not in gene_annotations.columns:
        raise KeyError("The 'Gene_Symbol' column is missing from gene_annotations DataFrame")

    # Merge result_df with gene_annotations based on the gene symbols
    columns_to_merge = ["Gene_Symbol"] + additional_columns + common_columns
    result_df = result_df.merge(gene_annotations[columns_to_merge], left_on='gene', right_on='Gene_Symbol', how='left')

    # Merge result_df with model_performances_EN to include the 'x' values
    result_df = result_df.merge(model_performances_EN[['Gene_Symbol', 'x']], left_on='gene', right_on='Gene_Symbol', how='left')

    # Round the 'x' column to two decimal points
    result_df['x'] = result_df['x'].round(2)

    # Rename columns to match the final desired column names
    column_rename_map = {
        "x": "Prediction performance (Corr)",
        # "Prediction_Percentile_TCGA": "Prediction Percentile TCGA",
        "Prediction_Percentile_1376_cell_lines":  "Prediction DepMap percentile (CERES; n=1376)",
        "Prediction_Range_1376_cell_lines": "Predicted DepMap range (CERES; n=1376)",
        "Real_Percentile_1376_cell_lines": "Real DepMap percentile (CCLE; n=1376)",
        "CCLE_real_1376CCLs": "Real DepMap range (CCLE; n=1376)",
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

    return result_df