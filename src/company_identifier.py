import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
import yaml
from unicodedata import category

YAML_URL = (
    "https://bitbucket.org/bluetooth-SIG/public/raw/"
    "main/assigned_numbers/company_identifiers/company_identifiers.yaml"
)


def clean_yaml_text(text: str) -> str:
    # Elimina caracteres de control no imprimibles (excepto tab, newline y carriage return)
    return "".join(c for c in text if category(c)[0] != "C" or c in "\t\n\r")


class CompanyIdentifiers:
    def __init__(self, yaml_url: Optional[str] = None, cache_days: int = 7):
        self.yaml_url = yaml_url or YAML_URL
        self.cache_days = cache_days

        # Ruta del cache: ~/.cache/bluetooth/company_ids.json
        self.cache_dir = (
            Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")) / "bluetooth"
        )
        self.cache_file = self.cache_dir / "company_ids.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _is_cache_valid(self) -> bool:
        if not self.cache_file.exists():
            return False
        last_modified = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        return datetime.now() - last_modified < timedelta(days=self.cache_days)

    def _download_and_cache(self) -> dict:
        response = requests.get(self.yaml_url)
        response.raise_for_status()
        cleaned_text = clean_yaml_text(response.text)
        parsed = yaml.safe_load(cleaned_text)

        company_map = {
            str(entry["value"]): entry["name"]
            for entry in parsed.get("company_identifiers", [])
        }

        with self.cache_file.open("w", encoding="utf-8") as f:
            json.dump(company_map, f)

        return company_map

    def _load(self) -> dict:
        if self._is_cache_valid():
            with self.cache_file.open("r", encoding="utf-8") as f:
                return json.load(f)
        return self._download_and_cache()

    def get(self, company_id: int, default: str = "Unknown") -> str:
        data = self._load()
        return data.get(str(company_id), default)

    def force_reload(self) -> dict:
        return self._download_and_cache()
