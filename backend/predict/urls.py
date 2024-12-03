from django.urls import path
from . import views

urlpatterns = [
    path('get-column-names', views.get_column_names, name='get_column_names'),
    path('reset-backend-data', views.reset_backend_data, name='reset_backend_data'),
]