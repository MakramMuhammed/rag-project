from aiofiles import os

from .BaseController import BaseController
from fastapi import UploadFile
from models.enums import ResponseSignal
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # Convert MB to bytes

    def validate_uploaded_file(self,file: UploadFile):
        if file.content_type not in self.settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value        
        if file.size > self.settings.FILE_MAX_SIZE_MB * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value        
        return True, ResponseSignal.FILE_VALIDATION_SUCCESS.value
    
    def generate_unique_filepath(self, original_filename: str, project_id: str):
        random_filename = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_filename = self.get_clean_file_name(original_filename=original_filename)

        new_file_path = os.path.join(project_path, f"{random_filename}_{cleaned_filename}")

        while os.path.exists(new_file_path):
            random_filename = self.generate_random_string()
            new_file_path = os.path.join(project_path, f"{random_filename}_{cleaned_filename}")

        return new_file_path, random_filename + "_" + cleaned_filename

     
 
    def get_clean_file_name(self, original_filename: str):
        # Remove any special characters from the filename, except _ and .
        cleaned_filename = re.sub(r'[^a-zA-Z0-9_.]', '', original_filename)

        # replace spaces with underscores
        cleaned_filename = cleaned_filename.replace(' ', '_')

        return cleaned_filename

        