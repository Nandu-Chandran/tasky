from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
import os
from datetime import datetime


sqlite_path = "/database/data.db"
sqlite_url = f"sqlite:///{sqlite_path}"
connect_args = {"check_same_thread": False}


def create_dynamic_model(table_name: str):
    class DynamicTable(SQLModel, table=True):
        __table_name__ = table_name

        id: Optional[int] = Field(default=None, primary_key=True)
        job_type: str
        file_path: str = Field(index=True)
        file_name: str
        extension: str
        scanned_at: Optional[str] = Field(default=None)

    return DynamicTable


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, echo=False)
        self.models = {}

    def connect_db():
        engine = create_engine(sqlite_url, connect_args=connect_args)

        try:
            with engine.connect() as connection:
                print("Connected to the database successfully!")
        except Exception as e:
            print(f"Failed to connect to the database: {e}")

    def create_table_if_not_found(self, table_name):
        if table_name not in self.models:
            Model = create_dynamic_model(table_name)
            Model.metadata.create_all(self.engine)
            self.models[table_name] = Model

    def insert_files(self, table_name, job_type: str, files: list[str]):
        self.create_table_if_not_found(table_name)
        Model = self.models[table_name]
        session = Session(self.engine)

        for file_path in files:
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_path)[1].strip(".")

            existing = session.exec(
                select(Model).where(Model.file_path == file_path)
            ).first()
            if existing:
                continue

            file_record = Model(
                job_type=job_type,
                file_name=file_name,
                extension=file_ext,
                scanned_at=datetime.now().isoformat(),
            )
            print(file_record)
            session.add(file_record)

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Eroor inserting files: {e}")
        finally:
            session.close()
