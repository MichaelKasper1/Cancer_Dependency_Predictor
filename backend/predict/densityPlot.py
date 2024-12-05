import json
import pandas as pd
import plotly.graph_objs as go
from scipy.stats import gaussian_kde
import numpy as np

def compute_density(data):
    kde = gaussian_kde(data)
    x = np.linspace(min(data), max(data), 1000)
    y = kde(x)
    return x, y

def create_density_trace(data, color, fillcolor, name):
    x, y = compute_density(data)
    return go.Scatter(
        x=x,
        y=y,
        mode='lines',
        fill='tozeroy',
        line=dict(color=color),
        fillcolor=fillcolor,
        name=name
    )

def create_density_plot_logic(result_df, gene, column, data_source, ccl_predicted_data_model_10xCV_paper, GeneEffect_18Q2_278CCLs, ccle_23q4_chronos_996, tcga_pred):

    fig = go.Figure()

    if data_source == 'cell-line':
        if gene in GeneEffect_18Q2_278CCLs.columns:
            # CCLE prediction
            dataC = pd.to_numeric(ccl_predicted_data_model_10xCV_paper[gene].dropna(), errors='coerce')
            fig.add_trace(create_density_trace(dataC, '#99ccff', 'rgba(153, 206, 235, 0.5)', 'Predicted'))
            # CCLE real
            data_og = pd.to_numeric(GeneEffect_18Q2_278CCLs[gene].dropna(), errors='coerce')
            fig.add_trace(create_density_trace(data_og, '#ff9999', 'rgba(255, 204, 153, 0.5)', 'Real'))
            y_max = max(compute_density(dataC)[1].max(), compute_density(data_og)[1].max())
        else:
            # CCLE23q4 real
            data = pd.to_numeric(ccle_23q4_chronos_996[column].dropna(), errors='coerce')
            fig.add_trace(create_density_trace(data, '#99ccff', 'rgba(153, 206, 235, 0.5)', 'DepMap real Chronos score (n=996)'))
            y_max = compute_density(data)[1].max()

        pre_dep = pd.to_numeric(result_df[result_df['gene'] == gene].iloc[0][column], errors='coerce')
        fig.update_layout(
            title={
                'text': f"<b>Dependencies across all cell lines or tumors with {gene} from sample {column}</b>",  # Bold the title using HTML tags
                'x': 0.5,  # Center the title
                'xanchor': 'center'
            },
            shapes=[
                dict(
                    type='line',
                    y0=0,
                    y1=y_max,
                    yref='y',
                    x0=-1,
                    x1=-1,
                    line=dict(color='#000000')
                ),
                dict(
                    type='line',
                    y0=0,
                    y1=y_max,
                    yref='y',
                    x0=pre_dep,
                    x1=pre_dep,
                    line=dict(color='#000000')
                )
            ],
            annotations=[
                dict(
                    x=-1,
                    y=y_max * 0.75,
                    text="Threshold for essentiality",
                    xref="x",
                    yref="y",
                    showarrow=True,
                    arrowhead=7,
                    ax=-20,
                    ay=-40,
                    font=dict(color="black", size=12)
                ),
                dict(
                    x=pre_dep,
                    y=y_max * 0.85,
                    text="Query sample",
                    xref="x",
                    yref="y",
                    showarrow=True,
                    arrowhead=7,
                    ax=-20,
                    ay=-40,
                    font=dict(color="black", size=12)
                )
            ],
            xaxis=dict(
                title=f"Predicted/real Dependency on {gene}",
                titlefont=dict(size=15),
                zeroline=False,
                showgrid=False
            ),
            yaxis=dict(
                title="Density of Samples",
                titlefont=dict(size=15),
                showgrid=False
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        if gene in GeneEffect_18Q2_278CCLs.columns:
            fig.update_layout(legend=dict(title=dict(text='<b> DeepDEP CERES score (n=278)</b>')))
        else:
            fig.update_layout(legend=dict(title=dict(text='<b> DeepDEP CERES score (n=996)</b>')))
    else:
        # TCGA
        data = tcga_pred[tcga_pred['CRISPR_GENE'] == gene].iloc[:, 1:].values.flatten()
        data = pd.Series(data)
        data = pd.to_numeric(data, errors='coerce').dropna()
        pre_dep = pd.to_numeric(result_df[result_df['gene'] == gene].iloc[0][column], errors='coerce')
        fig.add_trace(create_density_trace(data, '#BEBADA', 'rgba(190, 186, 218, 0.5)', 'DeepDep predicted CERES score in TCGA (n=8238)'))
        y_max = compute_density(data)[1].max()

        fig.update_layout(
            title={
                'text': f"<b>Dependencies across all cell lines or tumors with {gene} from sample {column}</b>",  # Bold the title using HTML tags
                'x': 0.5,  # Center the title
                'xanchor': 'center'
            },
            shapes=[
                dict(
                    type='line',
                    y0=0,
                    y1=y_max,
                    yref='y',
                    x0=-1,
                    x1=-1,
                    line=dict(color='#000000')
                ),
                dict(
                    type='line',
                    y0=0,
                    y1=y_max,
                    yref='y',
                    x0=pre_dep,
                    x1=pre_dep,
                    line=dict(color='#000000')
                )
            ],
            annotations=[
                dict(
                    x=-1,
                    y=y_max * 0.75,
                    text="Threshold for essentiality",
                    xref="x",
                    yref="y",
                    showarrow=True,
                    arrowhead=7,
                    ax=-20,
                    ay=-40,
                    font=dict(color="black", size=12)
                ),
                dict(
                    x=pre_dep,
                    y=y_max * 0.85,
                    text="Query sample",
                    xref="x",
                    yref="y",
                    showarrow=True,
                    arrowhead=7,
                    ax=-20,
                    ay=-40,
                    font=dict(color="black", size=12)
                )
            ],
            xaxis=dict(
                title=f"DeepDEP Predicted Dependency on {gene}",
                titlefont=dict(size=15),
                zeroline=False,
                showgrid=False
            ),
            yaxis=dict(
                title="Density of Samples",
                titlefont=dict(size=15),
                showgrid=False
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
    return fig