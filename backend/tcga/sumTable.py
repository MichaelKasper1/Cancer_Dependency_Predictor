import pandas as pd
import numpy as np

def sumTable(cancer_types=None, select_gene1=None, select_gene2=None, tcga_clinicalData=None, tcga_exp=None, tcga_mut=None):
    print("Starting sumTable function")
    sample_group = None

    if cancer_types and select_gene1:
        print(f"Processing cancer_types: {cancer_types}, select_gene1: {select_gene1}")
        if cancer_types == "PanCan":
            selected_samples = tcga_clinicalData['full_bcr_patient_barcode']
        else:
            selected_samples = tcga_clinicalData['full_bcr_patient_barcode'][tcga_clinicalData['full_names'] == cancer_types]

        if 'Gene' in tcga_exp.columns:
            tcga_exp = tcga_exp.set_index(tcga_exp['Gene'] + '_exp').drop(columns=['Gene'])
        else:
            raise KeyError("Column 'Gene' not found in tcga_exp")

        if 'Gene' in tcga_mut.columns:
            tcga_mut = tcga_mut.set_index(tcga_mut['Gene'] + '_mut').drop(columns=['Gene'])
        else:
            raise KeyError("Column 'Gene' not found in tcga_mut")

        G1 = select_gene1.split('_')
        if G1[1] == "exp":
            gene_data = tcga_exp.loc[f"{G1[0]}_exp", selected_samples]

            sample_group = pd.DataFrame(gene_data.values, index=gene_data.index, columns=['gene1'])

            if G1[2] == "high":
                sample_group['group1'] = (sample_group['gene1'] >= sample_group['gene1'].quantile(0.75)).astype(int)
            else:
                sample_group['group1'] = (sample_group['gene1'] < sample_group['gene1'].quantile(0.25)).astype(int)
            sample_group['group'] = sample_group['group1']
        else:
            gene_data = tcga_mut.loc[f"{G1[0]}_mut", selected_samples]
            sample_group = pd.DataFrame(gene_data.T, columns=['gene1'])
            sample_group['group1'] = sample_group['gene1'].replace(1, 4)
            sample_group['group'] = sample_group['group1']
        print("Sample group created for select_gene1")

    if select_gene2 and sample_group is not None:
        print(f"Processing select_gene2: {select_gene2}")
        G2 = select_gene2.split('_')
        if G2[1] == "exp":
            gene2_data = tcga_exp.loc[f"{G2[0]}_exp", selected_samples]
            gene2_df = pd.DataFrame(gene2_data.values, index=gene2_data.index, columns=['gene2'])
            sample_group = sample_group.join(gene2_df)
            if G2[2] == "high":
                sample_group['group2'] = (sample_group['gene2'] >= sample_group['gene2'].quantile(0.75)).astype(int)
            else:
                sample_group['group2'] = (sample_group['gene2'] < sample_group['gene2'].quantile(0.25)).astype(int)
        else:
            gene2_data = tcga_mut.loc[f"{G2[0]}_mut", selected_samples]
            gene2_df = pd.DataFrame(gene2_data.values, index=gene2_data.index, columns=['gene2'])
            sample_group = sample_group.join(gene2_df)
            sample_group['group2'] = sample_group['gene2'].replace(1, 4)

        sample_group['group'] = sample_group[['group1', 'group2']].sum(axis=1)
        print("Sample group updated for select_gene2")

    if sample_group is None:
        raise ValueError("sample_group is not defined. Ensure that cancer_types and select_gene1 are provided.")

    # Create the distribution table
    dist_table = sample_group.groupby('group').size().reset_index(name='n')
    dist_table['groupNames'] = dist_table['group'].astype(str)
    dist_table['groupNames'] = dist_table['groupNames'].replace('0', 'zero')

    nameZero = None
    name1 = None
    name2 = None
    name4 = None
    name5 = None
    name8 = None

    if not select_gene2:
        gene_string1 = select_gene1.split('_')
        
        if gene_string1[1] == "exp":
            if gene_string1[2] == "high":
                name1 = f"{gene_string1[0]}-high"
                nameZero = f"{gene_string1[0]}-medium/low"
            else:
                name1 = f"{gene_string1[0]}-low"
                nameZero = f"{gene_string1[0]}-high/medium"
        else:
            name4 = f"{gene_string1[0]}-mutated"
            nameZero = f"{gene_string1[0]}-WT"
        
        dist_table['groupNames'] = dist_table['groupNames'].replace({
            'zero': nameZero, '1': name1, '4': name4
        })
    else:
        gene_string1 = select_gene1.split('_')
        gene_string2 = select_gene2.split('_')
        
        if gene_string1[1] == "exp":
            if gene_string1[2] == "high":
                name1_1 = f"{gene_string1[0]}-high"
                name2_1 = f"{gene_string1[0]}-medium/low"
            else:
                name1_1 = f"{gene_string1[0]}-low"
                name2_1 = f"{gene_string1[0]}-high/medium"
            
            if gene_string2[1] == "exp":
                if gene_string2[2] == "high":
                    name1_2 = f"{gene_string2[0]}-high"
                    name2_2 = f"{gene_string2[0]}-medium/low"
                else:
                    name1_2 = f"{gene_string2[0]}-low"
                    name2_2 = f"{gene_string2[0]}-high/medium"
                name2 = f"{name1_1} & {name1_2}"
            else:
                name1_2 = f"{gene_string2[0]}-mutated"
                name2_2 = f"{gene_string2[0]}-WT"
                name4 = f"{name2_1} & {name1_2}"
                name5 = f"{name1_1} & {name1_2}"
            
            name1 = f"{name1_1} & {name2_2}"
            nameZero = f"{name2_1} & {name2_2}"
        else:
            name1_1 = f"{gene_string1[0]}-mutated"
            name2_1 = f"{gene_string1[0]}-WT"
            
            if gene_string2[1] == "exp":
                if gene_string2[2] == "high":
                    name1_2 = f"{gene_string2[0]}-high"
                    name2_2 = f"{gene_string2[0]}-medium/low"
                else:
                    name1_2 = f"{gene_string2[0]}-low"
                    name2_2 = f"{gene_string2[0]}-high/medium"
                name1 = f"{name2_1} & {name1_2}"
                name5 = f"{name1_1} & {name1_2}"
            else:
                name1_2 = f"{gene_string2[0]}-mutated"
                name2_2 = f"{gene_string2[0]}-WT"
                name8 = f"{name1_1} & {name1_2}"
            
            nameZero = f"{name2_1} & {name2_2}"
            name4 = f"{name1_1} & {name2_2}"
        
        dist_table['groupNames'] = dist_table['groupNames'].replace({
            'zero': nameZero, '1': name1, '2': name2, '4': name4, '5': name5, '8': name8
        })

    # Check if any group has fewer than 3 samples
    if len(dist_table) < 4 and select_gene2:
        dist_table = dist_table.append({
            'group': 'Warning',
            'n': '',
            'groupNames': '*The tool only analyzes a gene(s) selection that yields at least two groups with n >= 3.'
        }, ignore_index=True)
    
    # Return both the distribution table and the sample group
    return dist_table, sample_group