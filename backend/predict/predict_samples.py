# The code in this file uses the DeepDEP algorithm with the data loaded from the user.
# code in this file is modified for the app. Original code is here: https://codeocean.com/capsule/7914207/tree/v1

from keras import models
import numpy as np
import pandas as pd
import time

def load_data(df):
    data = []
    gene_names = []
    sample_names = df.columns[1:]
    data_labels = []

    for i in range(len(df)):
        gene = str.upper(df.iloc[i, 0])
        gene_names.append(gene)
        data.append(df.iloc[i, 1:].to_numpy(dtype='float32'))

    data = np.array(data, dtype='float32')
    data = np.transpose(data)

    return data, data_labels, sample_names, gene_names

def predict_samples(df, dep_data):
    print("predicting samples started...")
    start = time.time()
    data_exp_tcga, data_labels_exp_tcga, sample_names_exp_tcga, gene_names = load_data(df)

    data_fprint_1298DepOIs, data_labels_fprint, gene_names_fprint, function_names_fprint = load_data(dep_data)
    
    model = models.load_model('./predict/models/model_final_exp.h5')

    batch_size = 500
    num_samples = data_exp_tcga.shape[0]  # number of samples
    
    data_pred = np.zeros((num_samples, data_fprint_1298DepOIs.shape[0]))
    for z in np.arange(0, num_samples):
        data_pred_tmp = model.predict([data_exp_tcga[np.repeat(z, data_fprint_1298DepOIs.shape[0])],data_fprint_1298DepOIs], batch_size=batch_size, verbose=0)
        data_pred[z] = np.transpose(data_pred_tmp)
        # print("Sample %d predicted..." % z)

    # return prediction results as a dataframe
    data_pred_df = pd.DataFrame(data=np.transpose(data_pred), index=gene_names_fprint, columns=sample_names_exp_tcga[0:num_samples])

    print('successfully done with deep learning')
    print("Time taken: %f seconds" % (time.time() - start))
    return data_pred_df