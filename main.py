import yaml
import glob,os
import subprocess
from datetime import date
from typing import Annotated, Union

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from urllib.parse import quote
from pydantic import BaseModel
from datetime import datetime, date, time
from fastapi import FastAPI

config_path = 'config.yaml'
sqlite_path = "/database/data.db"
sqlite_url = f"sqlite:///{sqlite_path}"
connect_args= {"check_same_thread": False}

app = FastAPI()

class JobScanner:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.jobs = self.load_config()
    
    def load_config(self) -> List[Dict]:
        with open(config_path, 'r') as file:
         config = yaml.safe_load(file)
         return config
    
def connect_db():
    engine= create_engine(sqlite_url, connect_args= connect_args) 

    try:
        with engine.connect() as connection:
            print("Connected to the database successfully!")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")

class StateResponse(BaseModel):
    name: str
    data: str
    date: date

class Stats(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    data: str
    date: int | None = None


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session,Depends(get_session)]



def write_stats(db,job_name,job_data):
    with Session(engine) as session:
        statement = Stats(name=job_name,data=job_data)
        session.add(statement)
        session.commit()
        session.close()

def get_file_list(directory:str,searchType:str,filetype:list):
    files_list=[]

    pattern= f"*.{{{','.join(filetype)}}}"
    
    if searchType != "full":
        os.chdir(dir)
        files_list= glob.glob(pattern)
    else:
        files_list= glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    return files_list


@app.get("/stats",response_model=list[StateResponse])
def readStats():
    stats=[]
    with Session(engine) as session:
        statement = select(Stats)
        result= session.exec(statement).all()
        print(result) 
    return result

@app.get("/update")
def runJobs(config):
    for job in config["jobs"]:
        print(job)
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

connect_db()      
config=load_config()
#readStats()
runJobs(config)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
