from fastapi.responses import JSONResponse
from fastapi import FastAPI

from scanner import JobScanner
from db import Database

app = FastAPI()

sqlite_path = "/database/data.db"
sqlite_url = f"sqlite:///{sqlite_path}"


@app.get("/scan")
def runJobs():
    scanner = JobScanner(config_path="config.yaml")
    db = Database(sqlite_url)
    results = scanner.scan()
    print(results)
    for job_type, entries in results.items():
        for entry in entries:
            db_name, base_path, mode, files = entry
            for file in files:
                # print(f"Inserting {file} files into {db_name} for job {job_type}")
                db.insert_files(table_name=db_name, job_type=job_type, files=[file])
    # print(results)
    # return JSONResponse(content=results)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
