import pandas as pd
import gseapy as gp
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def perform_gsea_django(request, column, gene_column='gene'):
    try:
        if not isinstance(column, pd.DataFrame):
            raise ValueError("Input is not a DataFrame")
        
        # Save the column and gene in cache
        cache.set('column_gsea', column.to_json(), timeout=None)
        cache.set('gene_column', gene_column, timeout=None)
        
        # Ensure the gene column is set as the index
        if gene_column not in column.columns:
            raise ValueError(f"Gene column '{gene_column}' not found in DataFrame")
        
        column.set_index(gene_column, inplace=True)
        
        first_column_name = column.columns[0]
        df_sorted = column.sort_values(by=first_column_name)
        
        # # Add small jitter to avoid duplicated values
        # df_sorted[first_column_name] += pd.Series([1e-9 * i for i in range(len(df_sorted))], index=df_sorted.index)

        rnk = pd.Series(df_sorted[first_column_name].values, index=df_sorted.index)

        # Run prerank GSEA using gseapy with predefined gene sets (e.g., KEGG)
        try:
            pre_res = gp.prerank(
                rnk=rnk, 
                gene_sets='MSigDB_Oncogenic_Signatures',  # Use a specific gene set
                min_size=15, 
                max_size=500, 
                permutation_num=1000, 
                outdir=None
            )
        except Exception as e:
            logger.error(f"Error during GSEA analysis: {e}")
            raise

        # Process GSEA results
        fgsea_res = pd.DataFrame(pre_res.res2d)
        
        # Rename the "Term" column to "Pathway"
        fgsea_res.rename(columns={'Term': 'Pathway'}, inplace=True)
        fgsea_res_sorted = fgsea_res.sort_values(by='ES', ascending=True)

        # Sort by "NOM p-val" column
        fgsea_res_sorted = fgsea_res.sort_values(by='NOM p-val', ascending=True)

        # Explicitly convert columns to numeric, if possible
        fgsea_res_sorted = fgsea_res_sorted.apply(pd.to_numeric, errors='ignore')

        # Round numeric columns to 3 decimals
        fgsea_res_sorted = fgsea_res_sorted.round(3)

        # Drop the first column "Name"
        fgsea_res_sorted = fgsea_res_sorted.drop(columns="Name")
        
        # Make fgsea_res_sorted into a dict to return as before
        fgsea_res_sorted = fgsea_res_sorted.to_dict(orient='records')

        logger.info("Done with GSEA analysis")
        return fgsea_res_sorted  # Return as a plain list of dictionaries
    except ValueError as ve:
        logger.error(f"Input error: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during GSEA analysis: {e}")
        raise