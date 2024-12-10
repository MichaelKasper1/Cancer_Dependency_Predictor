import numpy as np
import pandas as pd
import time

def preprocess(df, is_log_transformed, gene_dependencies, expressionUnit, ccle_exp_for_missing_value_6016, crispr_gene_fingerprint_cgp, c2cp_table, hallmark_table, fingerprint, ccle_exp_with_gene_alias_DeepDep):
    print("preprocessing started...")

    start = time.time()
    # Rename first column
    df = df.rename(columns={df.columns[0]: "Gene"})

    # Remove duplicates
    df = df.drop_duplicates(subset='Gene')

    df['Gene'] = df['Gene'].str.upper()
    gene_lists = df['Gene']

    # Convert alias table gene names to uppercase
    gene_alias_table = ccle_exp_with_gene_alias_DeepDep.applymap(lambda x: x.upper() if isinstance(x, str) else x)

    # Identify gene ID format
    if not any(gene_lists.str.startswith("ENSG")): # Gene symbol only
        direct_matches = df['Gene'].isin(gene_alias_table['Gene'])

        # Melt alias table for an alias-to-primary gene lookup
        alias_mapping = gene_alias_table.melt(id_vars='Gene', value_vars=gene_alias_table.columns[3:], 
                                            value_name='Alias').dropna()
        alias_dict = alias_mapping.set_index('Alias')['Gene'].to_dict()

        # Replace unmatched genes using alias dictionary
        df['Gene'] = df.apply(
            lambda row: alias_dict.get(row['Gene'], row['Gene']) if not direct_matches[row.name] else row['Gene'],
            axis=1
        )

    elif all(gene_lists.str.startswith("ENSG")): # Ensembl IDs only
        ensembl = gene_lists[gene_lists.str.startswith("ENSG")]
        out_table = pd.DataFrame({'ensembl': ensembl, 'ensembl.update': [None] * len(ensembl)})

        idx = out_table['ensembl'].isin(gene_alias_table['Gene'])
        out_table.loc[idx, 'ensembl.update'] = out_table.loc[idx, 'ensembl']

        for i in out_table.index[out_table['ensembl.update'].isna()]:
            tb1 = gene_alias_table[gene_alias_table.isin([out_table.at[i, 'ensembl']]).any(axis=1)]
            if len(tb1) == 1:
                out_table.at[i, 'ensembl.update'] = tb1['Gene'].values[0]

        df = out_table.rename(columns={'ensembl': 'Gene', 'ensembl.update': 'Gene'})

    else: # Mixed gene symbols and Ensembl IDs
        gene_symbol = gene_lists[~gene_lists.str.startswith("ENSG")]
        ensembl = gene_lists[gene_lists.str.startswith("ENSG")]

        gene_symbol_out = pd.DataFrame({'gene.symbol': gene_symbol, 'gene.symbol.update': [None] * len(gene_symbol)})
        ensembl_out = pd.DataFrame({'ensembl': ensembl, 'ensembl.update': [None] * len(ensembl)})

        idx = gene_symbol_out['gene.symbol'].isin(gene_alias_table['Gene'])
        gene_symbol_out.loc[idx, 'gene.symbol.update'] = gene_symbol_out.loc[idx, 'gene.symbol']

        for i in gene_symbol_out.index[gene_symbol_out['gene.symbol.update'].isna()]:
            tb1 = gene_alias_table[gene_alias_table.isin([gene_symbol_out.at[i, 'gene.symbol']]).any(axis=1)]
            if len(tb1) == 1:
                gene_symbol_out.at[i, 'gene.symbol.update'] = tb1['Gene'].values[0]

        idx = ensembl_out['ensembl'].isin(gene_alias_table['Gene'])
        ensembl_out.loc[idx, 'ensembl.update'] = ensembl_out.loc[idx, 'ensembl']

        for i in ensembl_out.index[ensembl_out['ensembl.update'].isna()]:
            tb1 = gene_alias_table[gene_alias_table.isin([ensembl_out.at[i, 'ensembl']]).any(axis=1)]
            if len(tb1) == 1:
                ensembl_out.at[i, 'ensembl.update'] = tb1['Gene'].values[0]

        out_table = pd.concat([gene_symbol_out.rename(columns={'gene.symbol': 'Gene', 'gene.symbol.update': 'Gene'}),
                               ensembl_out.rename(columns={'ensembl': 'Gene', 'ensembl.update': 'Gene'})], ignore_index=True)
        df = out_table

    exp_index = ccle_exp_for_missing_value_6016
    exp_index['Gene'] = exp_index['Gene'].str.upper().str.strip()
    exp_index = exp_index.drop(columns='index')
    output_data = pd.merge(exp_index, df, on="Gene", how='left')
    missing_cols = output_data.columns.difference(['Gene', 'Mean'])
    for col in missing_cols:
        output_data[col] = output_data[col].fillna(output_data['Mean'])
    # remove 'mean' column
    output_data = output_data.drop(columns='Mean')
    output_data = output_data[output_data['Gene'].isin(exp_index['Gene'])]
    # drop duplicates
    gene_1_mar = output_data[output_data['Gene'] == '1-MAR']
    output_data = output_data[output_data['Gene'] != '1-MAR'].drop_duplicates(subset='Gene')
    df = pd.concat([output_data, gene_1_mar])

    # Convert FPKM/rpkm to TPM if needed
    if expressionUnit == "FPKM":
        df = df.set_index('Gene')
        total_rpkm = df.sum(axis=0)
        for column in df.columns:
            df[column] = df[column] * 10**6 / total_rpkm

    # handle log transformation, the is_log_transformed will be either log or not-log
    if is_log_transformed == "not-log":
        df = df.set_index('Gene')
        df = df.apply(pd.to_numeric, errors='coerce')
        df = np.log2(df + 1)
        df = df.reset_index()
        
    # Create fingerprint_df based on gene set selection
    if gene_dependencies == "default-gene-set":
        crispr_gene_fingerprint_cgp = crispr_gene_fingerprint_cgp.drop(columns='index')
        fingerprint_df = crispr_gene_fingerprint_cgp
    else:
        # Check if gene_dependencies is in hallmark_table or c2cp_table
        if gene_dependencies in hallmark_table.columns:
            gene_set = hallmark_table[gene_dependencies].dropna()
        elif gene_dependencies in c2cp_table.columns:
            gene_set = c2cp_table[gene_dependencies].dropna()
        else:
            raise ValueError(f"Column '{gene_dependencies}' not found in hallmark_table or c2cp_table")

        # Filter out any values in gene_set that are not in fingerprint columns
        valid_genes = [gene for gene in gene_set if gene in fingerprint.columns]
        if not valid_genes:
            raise ValueError("No valid genes found in fingerprint data for the given gene_dependencies")
        
        # Get fingerprint_df using the valid_genes and the fingerprint data
        fingerprint_df = fingerprint[['GeneSet'] + valid_genes]
    
    #get time
    end = time.time()

    print("Preprocessing completed in %s seconds." % (end - start))

    print('Finished preprocessing.')

    return df, fingerprint_df
