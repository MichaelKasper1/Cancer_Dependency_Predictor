import logging
import numpy as np
import pandas as pd
from scipy import stats
from joblib import Parallel, delayed
import time

def perform_anova(tcga_pred_select_t):
    """Perform one-way ANOVA across groups."""
    start_time = time.time()
    def anova_for_column(col):
        groups = [group[col].values for _, group in tcga_pred_select_t.groupby("group")]
        _, p_value = stats.f_oneway(*groups)
        return p_value
    
    columns = tcga_pred_select_t.columns[:-3]  # Exclude 'gene1', 'group1', 'group'
    pvals = Parallel(n_jobs=-1)(delayed(anova_for_column)(col) for col in columns)

    end_time = time.time()
    print(f"ANOVA took {end_time - start_time:.2f} seconds")

    return np.array(pvals)

def perform_ttest(tcga_pred_select_t):
    """Perform pairwise t-test between two groups."""
    start_time = time.time()
    def ttest_for_column(col):
        group0 = tcga_pred_select_t[tcga_pred_select_t["group"] == 0][col]
        group1 = tcga_pred_select_t[tcga_pred_select_t["group"] == 1][col]
        _, p_value = stats.ttest_ind(group1, group0, alternative='greater', equal_var=False)
        return p_value
    
    columns = tcga_pred_select_t.columns[:-3]  # Exclude 'gene1', 'group1', 'group'
    pvals = Parallel(n_jobs=-1)(delayed(ttest_for_column)(col) for col in columns)
    
    end_time = time.time()
    print(f"T-test took {end_time - start_time:.2f} seconds")
    
    return np.array(pvals)

def chronosTable(sample_group=None, tcga_pred=None, selected_model=None, tcga_pred_EN=None):
    """Generate prediction table with ANOVA/t-test p-values based on group differences."""
    
    # Select appropriate prediction matrix
    tcga_pred_matrix = tcga_pred if selected_model == "deepDEP" else tcga_pred_EN
    
    # Ensure sample_group has at least 3 samples per group
    dist_table = sample_group.groupby("group").size().reset_index(name="n")
    valid_groups = dist_table[dist_table["n"] >= 3]["group"]
    sample_group = sample_group[sample_group["group"].isin(valid_groups)]
    
    # Check if there were any cases that did not pass the check
    any_invalid_cases = len(valid_groups) < len(dist_table["group"].unique())
    
    # Subset tcga_pred based on sample group
    sample_ids = sample_group.index.intersection(tcga_pred_matrix.columns[1:])
    tcga_pred_select = tcga_pred_matrix[["CRISPR_GENE"] + list(sample_ids)]
    
    # Compute mean values per group
    group_means = sample_group.groupby("group").apply(
        lambda x: tcga_pred_select.loc[:, x.index].mean(axis=1)
    ).T
    group_means.columns = [f"group{g}" for g in group_means.columns]
    
    # Transpose for statistical tests
    tcga_pred_select_t = tcga_pred_select.set_index("CRISPR_GENE").T
    tcga_pred_select_t = tcga_pred_select_t.merge(sample_group, left_index=True, right_index=True)
    tcga_pred_select_t = tcga_pred_select_t.reset_index(drop=True)

    # Perform statistical tests
    if len(valid_groups) >= 3:
        pvals = perform_anova(tcga_pred_select_t)
    elif len(valid_groups) == 2:
        pvals = perform_ttest(tcga_pred_select_t)
    else:
        pvals = np.nan

    # Construct output table
    tcga_pred_select = pd.concat([tcga_pred_select, group_means], axis=1)
    tcga_pred_select["pval"] = pvals
    tcga_pred_select["index"] = tcga_pred_select["CRISPR_GENE"] + "_" + (tcga_pred_select.index + 1).astype(str)

    # Reorder columns
    final_cols = ["index", "CRISPR_GENE"] + list(group_means.columns) + ["pval"]
    return tcga_pred_select[final_cols], any_invalid_cases