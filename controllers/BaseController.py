import os
from helpers.config import get_settings, Settings
import random
import string

class BaseController:
    def __init__(self):
        self.settings = get_settings()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_dir = self.base_dir + "/../assets/files"

    def generate_random_string(self, length: int = 12) -> str:    
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
