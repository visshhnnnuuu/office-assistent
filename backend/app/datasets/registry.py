import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from ruamel.yaml import YAML
from backend.app.config import settings

class DatasetRegistry:
    _cached_config: Optional[Dict[str, Any]] = None

    @classmethod
    def _load_yaml(cls) -> Dict[str, Any]:
        if cls._cached_config is not None:
            return cls._cached_config

        config_path = settings.configs_path / "datasets.yaml"
        if not config_path.exists():
            return {"datasets": [], "governance": {}}

        yaml = YAML(typ='safe')
        with open(config_path, 'r', encoding='utf-8') as f:
            cls._cached_config = yaml.load(f) or {"datasets": []}
        return cls._cached_config

    @classmethod
    def get_dataset(cls, name: str) -> Optional[Dict[str, Any]]:
        cfg = cls._load_yaml()
        for ds in cfg.get("datasets", []):
            if ds.get("name") == name:
                return ds
        return None

    @classmethod
    def list_datasets(cls, category: Optional[str] = None, enabled_only: bool = False) -> List[Dict[str, Any]]:
        cfg = cls._load_yaml()
        datasets = cfg.get("datasets", [])

        results = []
        for ds in datasets:
            if category and ds.get("category") != category:
                continue
            if enabled_only and not ds.get("enabled", False):
                continue
            # Apply voice gating rule
            if ds.get("category") == "voice" and not settings.enable_voice_datasets:
                ds = dict(ds)
                ds["enabled"] = False
                ds["status_note"] = "Disabled by system policy (ENABLE_VOICE_DATASETS=false)"
            results.append(ds)

        return results
