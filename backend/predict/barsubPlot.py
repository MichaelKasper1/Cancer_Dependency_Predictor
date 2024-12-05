import pandas as pd
import plotly.graph_objs as go
from django.http import JsonResponse

def create_hline(y, x_start, x_width, color="blue"):
    return {
        "type": "line",
        "y0": y,
        "y1": y,
        "xref": "x",
        "yref": "y",
        "x0": x_start,
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

def create_bar_sub_plot_logic(result_df, gene, column, data_source, GeneEffect_18Q2_278CCLs, ccl_predicted_data_model_10xCV_paper, cell_info, ccle_23q4_chronos_996, pancan_type):
    # Normalize gene IDs
    ccle_23q4_chronos_996 = normalize_gene_ids(ccle_23q4_chronos_996)
    GeneEffect_18Q2_278CCLs = normalize_gene_ids(GeneEffect_18Q2_278CCLs)
    ccl_predicted_data_model_10xCV_paper = normalize_gene_ids(ccl_predicted_data_model_10xCV_paper)

    # Check if the column exists in the result_df
    if column not in result_df.columns:
        return JsonResponse({"error": f"Column '{column}' not found in result_df."}, status=400)

    try:
        pre_dep = result_df.loc[result_df['gene'] == gene, column].values[0]
    except KeyError as e:
        raise KeyError(f"KeyError: {e}. Available columns: {result_df.columns}")

    tb = result_df[result_df['gene'] == gene]

    # Initialize figure
    fig = go.Figure()

    if data_source == 'cell-line':
        if gene in GeneEffect_18Q2_278CCLs.columns:
            # Real CCLE data
            GeneEffect_18Q2_278CCLs = GeneEffect_18Q2_278CCLs.rename(columns={GeneEffect_18Q2_278CCLs.columns[0]: 'stripped_cell_line_name'})
            cell_info_depmap = cell_info[cell_info['stripped_cell_line_name'].isin(GeneEffect_18Q2_278CCLs['stripped_cell_line_name'])]
            pancan_idx = cell_info_depmap[cell_info_depmap['primary_disease_fixed'] == pancan_type].index

            data_temp = GeneEffect_18Q2_278CCLs.loc[GeneEffect_18Q2_278CCLs['stripped_cell_line_name'].isin(cell_info_depmap.loc[pancan_idx, 'stripped_cell_line_name']), gene].dropna().values
            data_ccle = pd.DataFrame({
                'PanCan': cell_info_depmap.loc[pancan_idx, 'primary_disease_fixed'],
                'Subtype': cell_info_depmap.loc[pancan_idx, 'Subtype'],
                'Prediction': data_temp,
                'source': 'Real'
            })

            # Predicted CCLE data
            ccl_predicted_data_model_10xCV_paper = ccl_predicted_data_model_10xCV_paper.rename(columns={ccl_predicted_data_model_10xCV_paper.columns[0]: 'CCLE_Name'})
            cell_info_depmap = cell_info[cell_info['CCLE_Name'].isin(ccl_predicted_data_model_10xCV_paper['CCLE_Name'])]
            pancan_idx = cell_info_depmap[cell_info_depmap['primary_disease_fixed'] == pancan_type].index

            data_temp_pred = ccl_predicted_data_model_10xCV_paper.loc[ccl_predicted_data_model_10xCV_paper['CCLE_Name'].isin(cell_info_depmap.loc[pancan_idx, 'CCLE_Name']), gene].dropna().values
            data_ccle_pred = pd.DataFrame({
                'PanCan': cell_info_depmap.loc[pancan_idx, 'primary_disease_fixed'],
                'Subtype': cell_info_depmap.loc[pancan_idx, 'Subtype'],
                'Prediction': data_temp_pred,
                'source': 'Predicted'
            })

            data_merge = pd.concat([data_ccle, data_ccle_pred])

            # ensure that the predicted dependency score column is float
            data_merge['Prediction'] = data_merge['Prediction'].astype(float)

            fig = go.Figure(data=[
                go.Box(y=data_merge[data_merge['source'] == 'Real']['Prediction'], x=data_merge[data_merge['source'] == 'Real']['Subtype'], name='Real', marker_color='skyblue'),
                go.Box(y=data_merge[data_merge['source'] == 'Predicted']['Prediction'], x=data_merge[data_merge['source'] == 'Predicted']['Subtype'], name='Predicted', marker_color='peachpuff')
            ])

            unique_subtypes = data_merge['Subtype'].unique()
            num_unique_subtype = len(unique_subtypes)

            # X-axis label
            cc = data_merge['Subtype'].value_counts()
            x_text = [f"{subtype} ({count})" for subtype, count in cc.items()]

            fig.update_layout(
                boxmode="group",
                xaxis=dict(
                    title="",
                    categoryarray=unique_subtypes,
                    categoryorder="category ascending",
                    showticklabels=True,
                    tickmode='array',
                    ticktext=x_text,
                    tickvals=unique_subtypes,
                    showgrid=False  # Remove grid lines from x-axis
                ),
                yaxis=dict(
                    title=f"Predicted Dependency Score ({gene})",
                    titlefont=dict(size=15),
                    zeroline=False,
                    showgrid=False,  # Remove grid lines from y-axis
                    tickformat=".2f"  # Round y-axis values to 2 decimal places
                ),
                shapes=[create_hline(pre_dep, -0.5, num_unique_subtype + 0.5)],
                annotations=[create_annotation(num_unique_subtype + 0.5, pre_dep, "Query sample")],
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
        else:
            # Use ccle_23q4_chronos_996 if gene does not exist in GeneEffect_18Q2_278CCLs
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

            fig.update_layout(
                boxmode="group",
                xaxis=dict(
                    title="",
                    categoryarray=unique_tumors,
                    categoryorder="category ascending",
                    showticklabels=True,
                    tickmode='array',
                    ticktext=[f"{tumor} ({count})" for tumor, count in data_merge['PanCan'].value_counts().items()],
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
                shapes=[create_hline(pre_dep, -0.5, num_unique_tumor + 0.5)],
                annotations=[create_annotation(num_unique_tumor + 0.5, pre_dep, "Query sample")],
                title={
                    'text': f"<b>Predicted dependency scores of {gene} across different cancer subtypes</b>",
                    'x': 0.5,
                    'xanchor': 'center'
                },
                legend=dict(
                    title="<b>DeepDEP CERES score (n=996)</b>",
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
    else:
        return {"message": "Plot of predicted dependency scores of the selected gene across different cancer subtypes by choice available for cell line data only."}