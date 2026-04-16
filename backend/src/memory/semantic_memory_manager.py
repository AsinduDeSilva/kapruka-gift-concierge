import json
import os

from loguru import logger

from src.infrastructure.config import PROJECT_ROOT


class SemanticMemoryManager:
    def __init__(self, file_path=f"{PROJECT_ROOT}/data/semantic_memory/profiles.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f)

    def get_profile(self, user_id):
        with open(self.file_path, "r") as f:
            data = json.load(f)
        return data.get(user_id, {})

    def save_profile(self, user_id, updated_profile_data):
        with open(self.file_path, "r") as f:
            data = json.load(f)

        data[user_id] = updated_profile_data

        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Semantic Memory updated for {user_id}.")