import pandas as pd
import plotly.graph_objs as go
from django.http import JsonResponse
import logging
import numpy as np

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_hline(y, x_width, color="blue"):
    return {
        "type": "line",
        "y0": y,
        "y1": y,
        "xref": "x",
        "yref": "y",
        "x0": 0,
        "x1": x_width,
        "line": {"color": color, "dash": "dot"}
    }

def create_annotation(x, y, msg):
    return {
        "x": x,
        "y": y,
        "xref": "x",
        "yref": "y",
        "text": msg,
        "showarrow": True,
        "arrowhead": 7,
        "ax": -20,
        "ay": -40,
        "font": {"color": "black", "size": 12}
    }

def normalize_gene_ids(df):
    df.columns = df.columns.str.replace(r'__\d+_', '', regex=True)
    return df

def create_bar_plot_logic(result_df, gene, column, data_source, GeneEffect_18Q2_278CCLs, ccl_predicted_data_model_10xCV_paper, cell_info, ccle_23q4_chronos_996, tcga_pred, tcga_clinicalData):

    # Normalize gene IDs
    ccle_23q4_chronos_996 = normalize_gene_ids(ccle_23q4_chronos_996)
    GeneEffect_18Q2_278CCLs = normalize_gene_ids(GeneEffect_18Q2_278CCLs)
    ccl_predicted_data_model_10xCV_paper = normalize_gene_ids(ccl_predicted_data_model_10xCV_paper)

    # Check if the column exists in the result_df
    if column not in result_df.columns:
        logger.error(f"Column '{column}' not found in result_df. Available columns: {result_df.columns}")
        return JsonResponse({"error": f"Column '{column}' not found in result_df."}, status=400)

    try:
        pre_dep = result_df.loc[result_df['gene'] == gene, column].values[0]
    except KeyError as e:
        raise KeyError(f"KeyError: {e}. Available columns: {result_df.columns}")

    # Initialize figure
    fig = go.Figure()

    if data_source == 'cell-line':
        
        if gene in GeneEffect_18Q2_278CCLs.columns:
            # Real CCLE data
            GeneEffect_18Q2_278CCLs = GeneEffect_18Q2_278CCLs.rename(columns={GeneEffect_18Q2_278CCLs.columns[0]: 'stripped_cell_line_name'})
            merged_real = pd.merge(GeneEffect_18Q2_278CCLs, cell_info, on='stripped_cell_line_name')
            data_temp = merged_real[gene].dropna().values
            data_ccle = pd.DataFrame({
                'PanCan': merged_real['primary_disease_fixed'],
                'Predicted_Dependency_Score': data_temp,
                'source': 'Real'
            })

            # Predicted CCLE data
            ccl_predicted_data_model_10xCV_paper = ccl_predicted_data_model_10xCV_paper.rename(columns={ccl_predicted_data_model_10xCV_paper.columns[0]: 'CCLE_Name'})
            merged_pred = pd.merge(ccl_predicted_data_model_10xCV_paper, cell_info, on='CCLE_Name')
            data_temp_pred = merged_pred[gene].dropna().values
            data_ccle_pred = pd.DataFrame({
                'PanCan': merged_pred['primary_disease_fixed'],
                'Predicted_Dependency_Score': data_temp_pred,
                'source': 'Predicted'
            })

            data_merge = pd.concat([data_ccle, data_ccle_pred])

            # ensure that the predicted_dependency_score column is float
            data_merge['Predicted_Dependency_Score'] = data_merge['Predicted_Dependency_Score'].astype(float)

            fig = go.Figure(data=[
                go.Box(y=data_merge[data_merge['source'] == 'Real']['Predicted_Dependency_Score'], x=data_merge[data_merge['source'] == 'Real']['PanCan'], name='Real', marker_color='skyblue'),
                go.Box(y=data_merge[data_merge['source'] == 'Predicted']['Predicted_Dependency_Score'], x=data_merge[data_merge['source'] == 'Predicted']['PanCan'], name='Predicted', marker_color='peachpuff')
            ])
            unique_tumors = merged_real['primary_disease_fixed'].unique()
            num_unique_tumor = len(unique_tumors)
        else:
            data_temp = ccle_23q4_chronos_996[gene].dropna().values
            cell_info_depmap = cell_info[cell_info['DepMap_ID'].isin(ccle_23q4_chronos_996['DepMapID'])]
            cell_info_depmap = cell_info_depmap.set_index('DepMap_ID').loc[ccle_23q4_chronos_996['DepMapID']]
            data_merge = pd.DataFrame({
                'PanCan': cell_info_depmap['primary_disease_fixed'],
                'Predicted_Dependency_Score': data_temp,
                'source': 'DepMap real Chronos score (n=996)'
            })
            logger.debug(f"Data Merge Head:\n{data_merge.head()}")
            fig = go.Figure(data=[
                go.Box(y=data_merge['Predicted_Dependency_Score'], x=data_merge['PanCan'], name='DepMap real Chronos score (n=996)', marker_color='skyblue')
            ])
            unique_tumors = cell_info_depmap['primary_disease_fixed'].unique()
            num_unique_tumor = len(unique_tumors)
    elif data_source == 'tumor':
        # TCGA logic
        tcga_CD = tcga_clinicalData[tcga_clinicalData['full_bcr_patient_barcode'].isin(tcga_pred.columns)]
        tcga_p = tcga_pred.loc[:, tcga_CD['full_bcr_patient_barcode']]
        tcga_p.index = tcga_pred['CRISPR_GENE']
        tcga_p = tcga_p.loc[gene, tcga_CD['full_bcr_patient_barcode']]
        data_temp = tcga_p.dropna().values

        data_tcga = pd.DataFrame({
            'PanCan': tcga_CD['type'],
            'Predicted_Dependency_Score': data_temp,
            'source': 'DeepDEP predicted CERES score (n=8238)'
        })

        unique_tumors = tcga_CD['type'].unique()
        num_unique_tumor = len(unique_tumors)

        cc = tcga_CD['type'].value_counts()
        x_text = [f"{tumor} ({count})" for tumor, count in cc.items()]

        fig = go.Figure(data=[
            go.Box(y=data_tcga['Predicted_Dependency_Score'], x=data_tcga['PanCan'], name='DeepDEP predicted CERES score (n=8238)', marker_color='rgba(190, 186, 218, 0.7)')
        ])

    else:
        logger.error(f"Invalid data source: {data_source}.")
        return JsonResponse({"error": f"Invalid data source: {data_source}."}, status=400)

    # X-axis label
    cc = pd.Series(unique_tumors).value_counts()
    x_text = [f"{tumor} ({count})" for tumor, count in cc.items()]

    fig.update_layout(
        barmode="group",
        boxmode="group",
        xaxis=dict(
            title="",
            categoryarray=unique_tumors,
            categoryorder="category ascending",
            showticklabels=True,
            tickmode='array',
            ticktext=x_text,
            tickvals=unique_tumors,
            showgrid=False  # Remove grid lines from x-axis
        ),
        yaxis=dict(
            title=f"Predicted Dependency Score ({gene})",
            titlefont=dict(size=15),
            zeroline=False,
            showgrid=False,  # Remove grid lines from y-axis
            tickformat=".2f"  # Round y-axis values to 2 decimal places
        ),
        shapes=[create_hline(pre_dep, num_unique_tumor + 1)],
        annotations=[create_annotation(num_unique_tumor + 1, pre_dep, "Query sample")],
        title={
            'text': f"<b>Predicted dependency scores of {gene} across different cancer subtypes</b>",
            'x': 0.5,
            'xanchor': 'center'
        },
        legend=dict(
            title="<b>DeepDEP CERES score (n=278)</b>",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        plot_bgcolor='white',  # Set plot background color to white
        paper_bgcolor='white'  # Set paper background color to white
    )

    return fig