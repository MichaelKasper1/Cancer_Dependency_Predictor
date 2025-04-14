import plotly.graph_objs as go
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
import plotly.io as pio

def tcga_boxplot(selected_gene, dist_table, tcga_pred, sample_group, selected_option3=False):
    print('tcga_boxplot called')
    
    print(f"Selected gene: {selected_gene}")
    print(f"dist_table head:\n{dist_table.head()}")
    print(f"tcga_pred head:\n{tcga_pred.head()}")
    print(f"sample_group head:\n{sample_group.head()}")

    # Check inputs
    if selected_gene is None:
        raise ValueError("selected_gene cannot be None")
    if dist_table is None or tcga_pred is None or sample_group is None:
        raise ValueError("dist_table, tcga_pred, and sample_group cannot be None")
    
    # Ensure 'CRISPR_GENE' column exists
    if 'CRISPR_GENE' not in tcga_pred.columns:
        raise KeyError("CRISPR_GENE column missing in tcga_pred")
    
    if tcga_pred['CRISPR_GENE'].duplicated().any():
        raise ValueError("Duplicate values found in CRISPR_GENE column")
    
    # Set index
    tcga_pred = tcga_pred.set_index('CRISPR_GENE')
    
    # Check if selected_gene exists in the index
    if selected_gene not in tcga_pred.index:
        raise KeyError(f"Selected gene {selected_gene} not found in tcga_pred index")
    
    # Map sample IDs to groups
    sample_group_mapping = sample_group['group'].to_dict()
    tcga_pred = tcga_pred.rename(columns=sample_group_mapping)
    
    selected_groups = list(sample_group_mapping.values())
    tcga_pred_select = tcga_pred.loc[[selected_gene], selected_groups].T.reset_index()
    tcga_pred_select.columns = ['TCGA Sample ID', 'select_crispr_gene']
    
    # Process dist_table
    if selected_option3:
        dist_table[['gene1', 'gene2']] = dist_table['groupNames'].str.split(' & ', expand=True)
        dist_table['figName'] = dist_table.apply(lambda row: f"{row['gene1']}<br>{row['gene2']}<br>(n={row['n']})", axis=1)
    else:
        dist_table['figName'] = dist_table.apply(lambda row: f"{row['groupNames']}<br>(n={row['n']})", axis=1)
    
    # Merge data for plot
    input_dat = tcga_pred_select.merge(dist_table, left_on='TCGA Sample ID', right_on='group', how='left')
    input_dat['group.name'] = input_dat['group'].map(dist_table.set_index('group')['figName'])
    input_dat['group.name'] = pd.Categorical(input_dat['group.name'], categories=dist_table['figName'], ordered=True)
    
    # Create box plot
    fig = go.Figure()
    for group_name in input_dat['group.name'].unique():
        group_data = input_dat[input_dat['group.name'] == group_name]
        fig.add_trace(go.Box(
            y=group_data['select_crispr_gene'],
            name=group_name,
            boxpoints=False,  # Removes all individual points
            jitter=0.3,
            pointpos=-1.8
        ))
    
    # Update layout
    fig.update_layout(
        title=f"Predicted Gene Dependency (CERES Score) for {selected_gene}",
        yaxis_title="Predicted Gene Dependency (CERES Score)",
        showlegend=False,
        plot_bgcolor='white',  # Set the plot background to white
        paper_bgcolor='white',  # Set the paper (outer) background to white
        xaxis=dict(
            gridcolor='white'  # Remove grid lines for the x-axis
        ),
        yaxis=dict(
            gridcolor='white'  # Remove grid lines for the y-axis
        )
    )
    print('done with tcga_boxplot function')
    return pio.to_json(fig)

def survival(selected_gene, cancer_types, survival_data, tcga_clinicalData, tcga_pred):

    if selected_gene is None:
        raise ValueError("selected_gene cannot be None")
    
    selected_samples = (
        tcga_clinicalData['bcr_patient_barcode'] if cancer_types == "PanCan"
        else tcga_clinicalData.loc[tcga_clinicalData['full_names'].astype(str) == str(cancer_types), 'full_bcr_patient_barcode'].str[:12]
    )
    print(f"Selected samples for PanCan:\n{selected_samples}")
    
    if 'CRISPR_GENE' not in tcga_pred.columns:
        raise KeyError("CRISPR_GENE column missing in tcga_pred")
    
    select_crispr_gene = selected_gene.split('_')[0]
    if select_crispr_gene not in tcga_pred['CRISPR_GENE'].values:
        raise KeyError(f"Selected gene {select_crispr_gene} not found in tcga_pred")
    
    survival_predictions = tcga_pred.loc[tcga_pred['CRISPR_GENE'] == select_crispr_gene].set_index('CRISPR_GENE').T
    survival_predictions.columns = ['predicted_dependency']
    survival_predictions['bcr_patient_barcode'] = survival_predictions.index.str[:12]
    survival_predictions = survival_predictions[survival_predictions['bcr_patient_barcode'].isin(selected_samples)]

    survival_data = survival_data.merge(survival_predictions, on='bcr_patient_barcode', how='inner').dropna(subset=['OS.time'])
    survival_data['OS.time'] /= 30  # Convert to months
    
    cph = CoxPHFitter()
    cph.fit(survival_data, duration_col='OS.time', event_col='OS', formula='predicted_dependency')
    hazard_ratio = cph.hazard_ratios_['predicted_dependency']
    
    median_dependency = survival_data['predicted_dependency'].median()
    survival_high = survival_data[survival_data['predicted_dependency'] >= median_dependency]
    survival_low = survival_data[survival_data['predicted_dependency'] < median_dependency]
    
    kmf_high = KaplanMeierFitter()
    kmf_low = KaplanMeierFitter()
    kmf_high.fit(survival_high['OS.time'], survival_high['OS'], label='Weak Gene Dependency')
    kmf_low.fit(survival_low['OS.time'], survival_low['OS'], label='Strong Gene Dependency')
    
    log_rank_p = logrank_test(
        survival_high['OS.time'], survival_low['OS.time'],
        event_observed_A=survival_high['OS'], event_observed_B=survival_low['OS']
    ).p_value
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=kmf_high.survival_function_.index, y=kmf_high.survival_function_['Weak Gene Dependency'], mode='lines', name=f'Weak Gene Dependency (n={len(survival_high)})'))
    fig.add_trace(go.Scatter(x=kmf_low.survival_function_.index, y=kmf_low.survival_function_['Strong Gene Dependency'], mode='lines', name=f'Strong Gene Dependency (n={len(survival_low)})'))
    
    fig.update_layout(
        title=f"Kaplan-Meier Estimates for {cancer_types} and {select_crispr_gene}",
        xaxis_title="Survival Duration (months)",
        yaxis_title="Survival Probability",
        plot_bgcolor='white',  # Set the plot background to white
        paper_bgcolor='white',  # Set the paper (outer) background to white
        xaxis=dict(
            gridcolor='white'  # Remove grid lines for the x-axis
        ),
        yaxis=dict(
            gridcolor='white'  # Remove grid lines for the y-axis
        ),
        annotations=[dict(x=max(kmf_high.survival_function_.index.max(), kmf_low.survival_function_.index.max()), y=0.9, text=f"Log-rank p: {log_rank_p:.3f}<br>HR: {hazard_ratio:.3f}", showarrow=False)]
    )
    
    return pio.to_json(fig)