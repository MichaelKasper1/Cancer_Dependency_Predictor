import json
import pandas as pd
import gseapy as gp
from gseapy import gseaplot2
import plotly.graph_objects as go
import base64
from io import BytesIO
import logging
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def create_gsea_plot_logic(pathway_name, column_json, gene_column):
    if pathway_name is None:
        logger.error("Pathway name not provided")
        raise ValueError("Pathway name not provided")

    # Retrieve the JSON string for 'column' and convert it back to a pandas DataFrame or Series
    if column_json is not None:
        column = pd.read_json(column_json)
    else:
        column = None

    # Ensure the gene column is set as the index
    if gene_column not in column.columns:
        raise ValueError(f"Gene column '{gene_column}' not found in DataFrame")

    column.set_index(gene_column, inplace=True)

    first_column_name = column.columns[0]
    df_sorted = column.sort_values(by=first_column_name)

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

    # Check if the pathway name exists in the GSEA results
    if pathway_name not in pre_res.res2d['Term'].values:
        logger.error(f"Pathway '{pathway_name}' not found in GSEA results")
        raise ValueError(f"Pathway '{pathway_name}' not found in GSEA results")

    # Set up terms, hits, and RESs for gseaplot2 with only one term
    terms = [pathway_name]
    hits = [pre_res.results[pathway_name]['hits']]
    RESs = [pre_res.results[pathway_name]['RES']]
    rank_metric = pre_res.ranking  # Use the rank metric from pre_res

    # Generate the GSEA plot for a single term
    fig, ax = plt.subplots(figsize=(8, 6))
    gseaplot2(
        terms=terms,
        RESs=RESs,
        hits=hits,
        rank_metric=rank_metric,
        ax=ax  # Pass single axis to avoid list output
    )
    
    ax.axis('off')

    # Convert the figure to a PNG image in the buffer
    img_buf = BytesIO()
    fig.savefig(img_buf, format='png')
    img_buf.seek(0)

    # Base64 encode the PNG image buffer
    encoded_image = base64.b64encode(img_buf.read()).decode('utf-8')

    # Create a plotly figure with the image embedded
    plotly_fig = go.Figure()
    plotly_fig.add_layout_image(
        dict(
            source=f"data:image/png;base64,{encoded_image}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            sizex=1.7, sizey=1.27,
            xanchor="center", yanchor="middle",
            sizing="contain",
            layer="below"
        )
    )

    plotly_fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=50, r=50, t=50, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    # Convert the Plotly figure to JSON
    plot_json = plotly_fig.to_json()
    return plot_json