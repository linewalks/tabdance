import hashlib
import json
import os
import pandas as pd
import time

from configparser import ConfigParser
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector

from base import get_config


def calculate_md5(csv_path: str) -> hex:
  with open(csv_path, "rb") as f:
    file_hash = hashlib.md5()
    while chunk := f.read(8192):
      file_hash.update(chunk)
  return file_hash.hexdigest()


class DBTableBase:
  def __init__(self, config: ConfigParser):
    self.uri = config["DB"]["SQLALCHEMY_DATABASE_URI"]
    self.schema = config["DB"]["SCHEMA"]
    self.table = config["DB"]["TABLE"]
    self.engine = create_engine(self.uri)

  def load_sql(self, sql_path: str, **kwargs):
    with open(sql_path, "r") as fd:
      start_time = time.time()
      print(f"\n===========Start loading Sql script '{sql_path}'===========")
      sql = fd.read().format(
        schema_name=self.schema,
        tds_version_table=self.table,
        file_name=kwargs.get("file_name"),
        table_name=kwargs.get("table_name"),
        csv_hash=kwargs.get("csv_hash")
      )
      self.engine.execute(sql)
      end_time = time.time()
      print(f"Time for loading sql script: {end_time-start_time:.2f}secs")
      print(f"\n===========Finished loading Sql script '{sql_path}'===========")

  def check_db_object(self, db_object: str, object_name: str):
    inspector = Inspector.from_engine(self.engine)
    if db_object == "schema":
      db_object_list = inspector.get_schema_names()
    elif db_object == "table":
      db_object_list = inspector.get_table_names(schema=self.schema)

    if object_name not in db_object_list:
      path = Path(Path(__file__).resolve().parent, os.path.join("sql", "base", f"init_{db_object}.sql"))
      self.load_sql(path)

  def init_db_object(self):
    for required_obj, name in zip(["schema", "table"], [self.schema, self.table]):
      self.check_db_object(required_obj, name)

  def init_tds_version(self, row_list: list):
    print(f"\n===========Inserting data into {self.table}===========")
    for row in row_list:
      with self.engine.connect() as conn:
        path = Path(Path(__file__).resolve().parent, os.path.join("sql", "base", "init_tds_version.sql"))
        self.load_sql(
          path,
          file_name=row["file_name"],
          table_name=row["table_name"],
          csv_hash=row["csv_hash"]
        )
    print(f"\n===========End of inserting data into {self.table}===========")


class DBTableSync(DBTableBase):
  def __init__(self, config):
    super().__init__(config)

  def get_tds_version(self, file_dir: str) -> list:
    # Download csv to LOCAL_REPO_PATH must be first
    # Ex. tds download -a
    csv_list = sorted([csv for csv in os.listdir(file_dir) if csv.endswith(".csv")])
    meta_list = sorted([meta for meta in os.listdir(file_dir) if meta.endswith(".meta")])

    hash_row_list = []
    for csv, meta in zip(csv_list, meta_list):
      csv_meta_dict = {}
      csv_meta_dict["file_name"] = csv
      csv_meta_dict["csv_hash"] = calculate_md5(os.path.join(file_dir, csv))
      with open(os.path.join(file_dir, meta), "r") as m:
        table = json.load(m)
      csv_meta_dict["table_name"] = table["table_name"]
      hash_row_list.append(csv_meta_dict)

    return hash_row_list

  def compare_tds_version(self, row_list: list):
    required_update_table = []  # Table list that needs synchronization
    required_update_hash = []   # Csv file list that needs to update a tds_version table
    path = Path(Path(__file__).resolve().parent, os.path.join("sql", "compare_tds_version.sql"))
    for row in row_list:
      with open(path, "r") as fd:
        select_csv_sql = fd.read().format(
          schema_name=self.schema,
          tds_version_table=self.table,
          file_name=row["file_name"],
          table_name=row["table_name"],
          csv_hash=row["csv_hash"]
        )
        result = self.engine.execute(select_csv_sql).fetchone()
        if result:
          required_update_table.append(result[0])
          required_update_hash.append(result[1])

    # update to tds_version table
    if required_update_hash:
      for csv in required_update_hash:
        for row in row_list:
          if csv == row["file_name"]:
            path = Path(Path(__file__).resolve().parent, os.path.join("sql", "update_tds_version.sql"))
            self.load_sql(
              path,
              file_name=row["file_name"],
              table_name=row["table_name"],
              csv_hash=row["csv_hash"]
            )

    # return required update table list
    if required_update_table:
      required_update_table = list(set(required_update_table))
    return required_update_table

  def sync_table(self):
    path = Path(Path(__file__).resolve().parent, os.path.join("sql", "select_tds_version.sql"))
    with open(path, "r") as fd:
      select_sql = fd.read().format(schema_name=self.schema, tds_version_table=self.table)
      check_tds_table = self.engine.execute(select_sql).fetchone()

    row_list = self.get_tds_version(Path(Path(__file__).resolve().parent, os.path.join("files")))
    if not check_tds_table:
      # Insert rows into tds_version table if there is no data
      super().init_tds_version(row_list)
      # TODO: .td로 맵핑한 DDL 스크립트 실행
    else:
      # Compare & update table
      self.compare_tds_version(row_list)
      # TODO: .td로 맵핑한 DDL 스크립트 실행 - update인 경우 drop 후 create

if __name__ == "__main__":
  # ./files 폴더에 존재하는 .csv의 Hash 값을 저장합니다
  config = get_config()
  DBTableBase(config).init_db_object()
  DBTableSync(config).sync_table()
