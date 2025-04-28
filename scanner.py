import yaml
import glob, os
from typing import List, Dict, Tuple


class JobScanner:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.jobs = self.load_config()

    def load_config(self) -> List[Dict]:
        with open(self.config_path, "r") as file:
            config = yaml.safe_load(file)
            return config

    def _find_files(self, path: str, mode: str, extensions: List[str]) -> List[str]:
        matched_files = []
        recursive = mode == "recursive"

        for ext in extensions:
            pattern = f"**/*.{ext}" if recursive else f"*.{ext}"
            search_path = os.path.join(path, pattern)
            found = glob.glob(search_path, recursive=recursive)
            matched_files.extend([os.path.basename(f) for f in found])

        return matched_files

    def _normalize_paths(self, path_data) -> List[Tuple[str, str]]:
        if isinstance(path_data, list):
            return [(os.path.expandvars(p), "default") for p in path_data]
        elif isinstance(path_data, dict):
            return [(os.path.expandvars(p), mode) for p, mode in path_data.items()]
        return []

    def scan(self) -> Dict[str, List[Tuple[str, str, List[str]]]]:
        results = {}
        for job in self.jobs["jobs"]:
            job_type = job.get("types", "unknown")
            job_db = job.get("db", "unknown")
            extensions = job.get("extension", [])
            path_data = job.get("path", [])
            paths = self._normalize_paths(path_data)

            job_results = []
            for path, mode in paths:
                matched_files = self._find_files(path, mode, extensions)
                job_results.append((job_db, path, mode, matched_files))

            results[job_type] = job_results
        return results
