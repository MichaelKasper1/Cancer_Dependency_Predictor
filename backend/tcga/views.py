# data manipulation libaries
import pandas as pd
import plotly.graph_objs as go # type: ignore

# django libraries
from django.shortcuts import render
from pymongo import MongoClient # type: ignore
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# load custom functions
from .sumTable import sumTable
from .chronosTable import chronosTable
from .geneEffect import geneEffect
from .survival import survival

# load the tcga data into the view from the mongoDB
def load_mongo_data(collection_name):
    collection = db[collection_name]
    data_records = collection.find({}, {'_id': 0, 'source_file': 0})
    return pd.DataFrame(list(data_records))

client = MongoClient('mongodb://localhost:27017/', username='michael_kasper', password='password', authSource='admin', authMechanism='SCRAM-SHA-1')
db = client['mongodb']

Cancer_types_tab3 = load_mongo_data('Cancer_types_tab3')
select_gene_tab3 = load_mongo_data('select_gene_tab3')
survival_data = load_mongo_data('survival_data')
tcga_clinicalData = load_mongo_data('tcga_clinicalData')
tcga_clinicalData_80 = load_mongo_data('tcga_clinicalData_80')
tcga_exp = load_mongo_data('tcga_exp')
tcga_mut = load_mongo_data('tcga_mut')
tcga_exp_sampleID = load_mongo_data('tcga_exp_sampleID')
tcga_mut_sampleID = load_mongo_data('tcga_mut_sampleID')
tcga_pred = load_mongo_data('tcga_pred')

@require_http_methods(["GET"])
def get_column_names_tcga(request):
    global Cancer_types_tab3, select_gene_tab3

    # Convert the data to dictionaries
    cancer_types_data = Cancer_types_tab3.to_dict(orient='records')
    select_gene_data = select_gene_tab3.to_dict(orient='records')

    # Return the data as a JSON response
    return JsonResponse({
        'Cancer_types_tab3': cancer_types_data,
        'select_gene_tab3': select_gene_data,
    })

# submit data happens automatically when TCGA Project and Gene Alteration 1 are selected.
@csrf_exempt
@require_http_methods(["POST"])
def submit_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_model = data.get('selectedModel')
            selected_option1 = data.get('selectedOption1')
            selected_option2 = data.get('selectedOption2')
            selected_option3 = data.get('selectedOption3')

            # Call the sumTable function
            dist_table = sumTable(
                cancer_types=selected_option1,
                select_gene1=selected_option2,
                select_gene2=selected_option3,
                tcga_clinicalData=tcga_clinicalData,
                tcga_exp=tcga_exp,
                tcga_mut=tcga_mut
            )

            # Convert the result to JSON
            dist_table_json = dist_table.to_json(orient='records')

            # Include the selected data and sample group in the response
            return JsonResponse({
                'status': 'success',
                'selectedModel': selected_model,
                'selectedOption1': selected_option1,
                'selectedOption2': selected_option2,
                'selectedOption3': selected_option3,
                'distTable': dist_table_json
            })
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

