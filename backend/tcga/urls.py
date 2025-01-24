# filepath: /Users/michaelkasper/Documents/Cancer_Dependency_Predictor/backend/tcga/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('get-column-names-tcga', views.get_column_names_tcga, name='get_column_names_tcga'),
    path('submit-data', views.submit_data, name='submit_data'),
    # other paths...
]