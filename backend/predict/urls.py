from django.urls import path, include
from . import views

urlpatterns = [
    path('get-csrf-token', views.get_csrf_token, name='get_csrf_token'),
    path('get-column-names', views.get_column_names, name='get_column_names'),
    path('reset-backend-data', views.reset_backend_data, name='reset_backend_data'),
    path('get-example-file', views.get_example_file, name='get_example_file'),
    path('process-data', views.process_data, name='process_data'),
    path('selected-data', views.selected_data, name='selected_data'),
    path('gsea-data', views.gsea_data, name='gsea_data'),
    path('create-gsea-plot', views.create_gsea_plot, name='create_gsea_plot'),
    path('create-density-plot', views.create_density_plot, name='create_density_plot'),
    path('create-bar-plot', views.create_bar_plot, name='create_bar_plot'),
    path('create-bar-sub-plot', views.create_bar_sub_plot, name='create_bar_sub_plot'),
    path('create-network-plot', views.create_network_plot, name='create_network_plot'),
    path('download-network/', views.download_network, name='download_network'),
]