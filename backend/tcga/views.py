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
import logging
logger = logging.getLogger(__name__)

# load custom functions
from .sumTable import sumTable
from .chronosTable import chronosTable
from .tcgaTable import tcgaTable
from .selected_gene_plots import tcga_boxplot
from .selected_gene_plots import survival

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
# LOAD ELASTIC NET MODELS HERE AND USE THEM IN THE FUNCTION TODO
gene_annotations = load_mongo_data('gene_annotations')

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
            dist_table, sample_group = sumTable(
                cancer_types=selected_option1,
                select_gene1=selected_option2,
                select_gene2=selected_option3,
                tcga_clinicalData=tcga_clinicalData,
                tcga_exp=tcga_exp,
                tcga_mut=tcga_mut
            )

            # call the chronosTable python function to perform statistical tests
            tcga_table_start, any_invalid_cases = chronosTable(
                sample_group=sample_group,
                tcga_pred=tcga_pred,
                selected_model=selected_model,
                tcga_pred_EN=tcga_pred
            )

            # call function to finish processing for tcga table by adding gene annotations and sorting
            tcga_table = tcgaTable(
                tcga_table_start=tcga_table_start,
                dist_table=dist_table,
                gene_annotations=gene_annotations
            )

            # TODO print a message to users if there are any invalid cases in red below the sample group table.
            print(any_invalid_cases)

            # Convert the result to JSON
            dist_table_json = dist_table.to_json(orient='records')
            tcga_table_json = tcga_table.to_json(orient='records')

            # Include the selected data and sample group in the response
            return JsonResponse({
                'status': 'success',
                'selectedModel': selected_model,
                'selectedOption1': selected_option1,
                'selectedOption2': selected_option2,
                'selectedOption3': selected_option3,
                'distTable': dist_table_json,
                'tcga_table': tcga_table_json
            })
        
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def get_visualization_data(request):
    if request.method == 'POST':
        try:
            print('starting the visualization function')
            data = json.loads(request.body)
            selected_gene = data.get('selectedGene')

            # Perform data processing and create visualizations based on the selected gene
            # Example: Generate a plotly graph

            # function for bar
            tcga_boxplot = tcga_boxplot(
                
            )

            # function for survival
            survival = survival(

            )

            return JsonResponse({
                'status': 'success',
                'selectedGene': selected_gene,
                'tcga_boxplot': tcga_boxplot,
                'survival': survival
                # plotly 2
            })
        
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)