import pandas as pd
import numpy as np
import time

def process_elastic_net(df, log_transformed, expression_unit, medians_CCLE21Q1, EN_gene_alias):
    print("Preprocessing data for elastic net...")
    start = time.time()
    gene_alias_table = EN_gene_alias

    # Ensure 'Gene' column is the index for medians_CCLE21Q1 if it exists
    if 'Gene' in medians_CCLE21Q1.columns:
        medians_CCLE21Q1.set_index('Gene', inplace=True)

    # Remove duplicates from medians_CCLE21Q1
    medians_CCLE21Q1 = medians_CCLE21Q1[~medians_CCLE21Q1.index.duplicated(keep='first')]

    # Rename first column
    df = df.rename(columns={df.columns[0]: "Gene"})
    # Remove duplicates
    df = df.drop_duplicates(subset='Gene')
    df['Gene'] = df['Gene'].str.upper()
    gene_lists = df['Gene']

    # Identify and standardize gene ID format from enembl to hgnc
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

    # Filter df to contain only genes present in medians_CCLE21Q1
    df = df[df['Gene'].isin(medians_CCLE21Q1.index)]
    # get rid of duplicates
    df = df.drop_duplicates(subset='Gene')

    # Add rows for genes that exist in medians_CCLE21Q1 but not in df
    missing_genes = medians_CCLE21Q1.index.difference(df['Gene'])
    missing_rows = pd.DataFrame(medians_CCLE21Q1.loc[missing_genes].reset_index())
    missing_rows = missing_rows.drop(columns=['Median'])  # Drop the 'Median' column
    df = pd.concat([df, missing_rows], ignore_index=True)

    # Fill NaN values in df with the Median value from medians_CCLE21Q1
    df = df.set_index('Gene')
    df = df.apply(lambda row: row.fillna(medians_CCLE21Q1.loc[row.name, 'Median']), axis=1)
    df.reset_index(inplace=True)
    # Ensure the final shape of df matches medians_CCLE21Q1
    df = df.set_index('Gene').reindex(medians_CCLE21Q1.index).reset_index()

    if log_transformed == 'not-log':
        df.set_index('Gene', inplace=True)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = np.log2(df + 1)
        df.reset_index(inplace=True)
    
    if expression_unit == "FPKM":
        df = df.set_index('Gene')
        total_rpkm = df.sum(axis=0)
        df = df.apply(lambda x: x * 10**6 / total_rpkm, axis=0)
    
    end = time.time()
    print(f"Processing time: {end - start} seconds")
        
    return df