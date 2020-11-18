from .spec_base import Spec
import os
import dtlpy as dl
import json
class OptModel(Spec):

    def __init__(self, models_config_location):
        self.models_config_location = models_config_location
        super().__init__()

    @property
    def model_space(self):
        for dic in self.spec_data.values():
            if 'model_space' in dic:
                return dic['model_space']

        return None

    @property
    def task(self):
        for dic in self.spec_data.values():
            if 'task' in dic:
                return dic['task']

        return None

    @property
    def home_path(self):
        for dic in self.spec_data.values():
            if 'home_path' in dic:
                return dic['home_path']

        return None

    @property
    def annotation_type(self):
        for dic in self.spec_data.values():
            if 'annotation_type' in dic:
                return dic['annotation_type']

        return None

    @property
    def max_trials(self):
        for dic in self.spec_data.values():
            if 'max_trials' in dic:
                return dic['max_trials']

        return None

    @property
    def epochs(self):
        for dic in self.spec_data.values():
            if 'epochs' in dic:
                return dic['epochs']

        return None

    @property
    def search_method(self):
        for dic in self.spec_data.values():
            if 'search_method' in dic:
                return dic['search_method']

        return None

    @property
    def augmentation_search_method(self):
        for dic in self.spec_data.values():
            if 'augmentation_search_method' in dic:
                return dic['augmentation_search_method']

        return None

    @property
    def name(self):
        for dic in self.spec_data.values():
            if 'model_name' in dic:
                return dic['model_name']

        return None

    @property
    def hp_space(self):
        with open(self.models_config_location) as f:
            models_data = json.load(f)
        return models_data[self.name]['hp_search_space']

    @property
    def training_configs(self):
        with open(self.models_config_location) as f:
            models_data = json.load(f)
        return models_data[self.name]['training_configs']

    @property
    def max_instances_at_once(self):
        for dic in self.spec_data.values():
            if 'max_instances_at_once' in dic:
                return dic['max_instances_at_once']

        return None

