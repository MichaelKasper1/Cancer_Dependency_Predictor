from django.apps import AppConfig
import os
import rpy2.robjects as ro

class PredictConfig(AppConfig):
    name = 'predict'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Load RDS files
        self.load_rds_files()

    def load_rds_files(self):
        global models
        models = {}
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        for filename in os.listdir(models_dir):
            if filename.endswith('_model.rds'):
                model_path = os.path.join(models_dir, filename)
                model_name = filename.replace('_model.rds', '')
                models[model_name] = ro.r['readRDS'](model_path)