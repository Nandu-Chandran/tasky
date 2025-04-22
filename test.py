import yaml
from glob import glob
from typing import List, Dict, Tuple

def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)["jobs"]
    
def scan_jobs(jobs_config: List[Dict]) -> Dict[str, List[Tuple[str, str, List[str]]]]:
    results = {}
    print(jobs_config)
    for job in jobs_config:
        job_type = job.get("types", "unknown")
        extensions = job.get("extension", [])
        paths = job.get("path", {})

        print(paths,job_type,extensions)

obj= load_config()
print(obj)
#scan_jobs(obj)