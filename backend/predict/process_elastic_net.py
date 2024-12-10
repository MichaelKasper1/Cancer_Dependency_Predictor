from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import localconverter
import pandas as pd
import os
import time
import numpy as np

def process_elastic_net(df, log_transformed, selected_gene_set, expression_unit, medians_CCLE21Q1):
    print("Preprocessing data for elastic net...")
    start = time.time()

    # Ensure 'Gene' column is the index for medians_CCLE21Q1
    medians_CCLE21Q1.set_index('Gene', inplace=True)

    # Filter df to contain only genes present in medians_CCLE21Q1
    df = df[df['Gene'].isin(medians_CCLE21Q1.index)]

    # Add rows for genes that exist in medians_CCLE21Q1 but not in df
    missing_genes = medians_CCLE21Q1.index.difference(df['Gene'])
    missing_rows = pd.DataFrame(medians_CCLE21Q1.loc[missing_genes].reset_index())
    missing_rows = missing_rows.drop(columns=['Median'])  # Drop the 'Median' column
    df = pd.concat([df, missing_rows], ignore_index=True)

    # Fill NaN values in df with the Median value from medians_CCLE21Q1
    df = df.set_index('Gene')
    df = df.apply(lambda row: row.fillna(medians_CCLE21Q1.loc[row.name, 'Median']), axis=1)
    df.reset_index(inplace=True)

    print(df.head())
    print(medians_CCLE21Q1.head())
    print(df.shape)
    print(medians_CCLE21Q1.shape)

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
    print(f"Preprocessing data for elastic net took {end - start} seconds")

    pandas2ri.activate()
    with localconverter(pandas2ri.converter):
        r_df = pandas2ri.py2rpy(df)

    glmnet = importr('glmnet')
    base = importr('base')
    script_dir = os.path.dirname(__file__)
    models_dir = os.path.join(script_dir, 'models')

    model_files = base.list_files(models_dir, pattern="_model.rds", full_names=True)
    models = []
    for file in model_files:
        try:
            model = base.readRDS(file)
            models.append(model)
        except Exception as e:
            print(f"Error loading model {file}: {e}")
            continue

    with localconverter(pandas2ri.converter):
        r_matrix = r['as.matrix'](r_df.T)

    start_time = time.time()
    predictions = []
    for model in models:
        try:
            prediction = glmnet.predict(model, newx=r_matrix, s="lambda.min")
            predictions.append(pandas2ri.rpy2py(prediction))
        except Exception as e:
            print(f"Error predicting with model: {e}")
            continue

    end_time = time.time()
    print(f"Prediction took {end_time - start_time} seconds")

    predictions_df = pd.concat(predictions, axis=1)
    predictions_df.columns = [file.replace("_model.rds", "") for file in model_files]
    predictions_df.index = df.columns

    return predictions_df