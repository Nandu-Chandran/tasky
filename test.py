import yaml
import glob,os
import subprocess
from datetime import date
from typing import Annotated, Union,Tuple,List,Dict

from urllib.parse import quote
from datetime import datetime, date, time

config_path = 'config.yaml'
sqlite_path = "/database/data.db"
sqlite_url = f"sqlite:///{sqlite_path}"
connect_args= {"check_same_thread": False}


class JobScanner:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.jobs = self.load_config()
    
    def load_config(self) -> List[Dict]:
        with open(config_path, 'r') as file:
         config = yaml.safe_load(file)
         return config
    def _find_files(self, path: str, mode: str, extensions: List[str]) -> List[str]:
        matched_files = []
        recursive = mode == "recursive"

        for ext in extensions:
            pattern = f"**/*.{ext}" if recursive else f"*.{ext}"
            search_path = os.path.join(path, pattern)
            print(f"Searching: {search_path} (recursive={recursive})")
            found = glob.glob(search_path, recursive=recursive)
            matched_files.extend(found) 
        return matched_files
    def _normalize_paths(self, path_data) -> List[Tuple[str, str]]:
        if isinstance(path_data, list):
            return [(os.path.expandvars(p), "default") for p in path_data]
        elif isinstance(path_data, dict):
            return [(os.path.expandvars(p), mode) for p, mode in path_data.items()]
        return []
        
    def scan(self) ->  Dict[str, List[Tuple[str, str, List[str]]]]:
        results={}
        for job in self.jobs["jobs"]:
            job_type = job.get('types',"unknown")
            extensions= job.get('extension',[])
            path_data= job.get('path',[])
            paths= self._normalize_paths(path_data)
        
            job_results=[]
            for path, mode in paths:
                print('Searching for mode')
                matched_files = self._find_files(path,mode,extensions)
                print(matched_files)
                job_results.append((path,mode,matched_files))
       
            results[job_type] = job_results
        return results

             
def connect_db():
    engine= create_engine(sqlite_url, connect_args= connect_args) 

    try:
        with engine.connect() as connection:
            print("Connected to the database successfully!")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")


def get_file_list(directory:str,searchType:str,filetype:list):
    files_list=[]

    pattern= f"*.{{{','.join(filetype)}}}"
    
    if searchType != "full":
        os.chdir(dir)
        files_list= glob.glob(pattern)
    else:
        files_list= glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    return files_list


def runJobs(config):
    for job in config["jobs"]:
        types = job['types']
        db_name = job['db']
        extensions= job['extension']
        
        paths= job["path"]
        
        path_list = (
                    [(os.path.expandvars(p), "default") for p in paths]
                    if isinstance(paths, list) 
                    else [(os.path.expandvars(p), mode) for p, mode in paths.items()] )
       
        for path, mode in path_list:
            print(f"Scanning {path} ({mode}) for {types} files with extensions {extensions}")

# connect_db()      
# config=load_config()
# #readStats()
# runJobs(config)

def main():
    print("Exists:", os.path.exists("/home/nc/media/video songs"))
    results = glob.glob("/home/nc/media/video songs/**/*.mkv", recursive=True)
    print("Found:", results)
    scanner = JobScanner(config_path="config.yaml")
    results = scanner.scan()
    print(results)
if __name__ == "__main__":
    # uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
    main()
