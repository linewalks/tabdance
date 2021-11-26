import hashlib
import json
import os
import pandas as pd
import time

from configparser import ConfigParser
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

  def load_sql(self, sql_path: str):
    with open(sql_path, "r") as fd:
      start_time = time.time()
      print(f"\n===========Start loading Sql script '{sql_path}'===========")
      sql = fd.read().format(schema_name=self.schema, table_name=self.table)
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
      self.load_sql(os.path.join(os.getcwd(), "sql", "base", f"init_{db_object}.sql"))

  def init_db_object(self):
    for required_obj, name in zip(["schema", "table"], [self.schema, self.table]):
      self.check_db_object(required_obj, name)

  def init_hash_table(self, row_list: list):
    print(f"\n===========Inserting data into {self.table}===========")
    for row in row_list:
      with self.engine.connect() as conn:
        sql = """
          INSERT INTO {schema_name}.{tds_version_table} VALUES (
            '{file_name}', '{table_name}', '{csv_hash}'
          )
          """
        sql = sql.format(
          schema_name=self.schema,
          tds_version_table=self.table,
          file_name=row["file_name"],
          table_name=row["table_name"],
          csv_hash=row["csv_hash"]
        )
        result = conn.execute(sql)
    print(f"\n===========End of inserting data into {self.table}===========")


class DBTableSync(DBTableBase):
  def __init__(self, config):
    super().__init__(config)

  def get_csv_version(self, file_dir: str) -> list:
    # Download csv to LOCAL_REPO_PATH must be first
    # Ex. tds download -a
    csv_list = sorted([csv for csv in os.listdir(file_dir) if csv.endswith(".csv")])
    meta_list = sorted([meta for meta in os.listdir(file_dir) if meta.endswith(".meta")])

    hash_row_list = []
    for csv, meta in zip(csv_list, meta_list):
      csv_meta_dict = dict()
      csv_meta_dict["file_name"] = csv
      csv_meta_dict["csv_hash"] = calculate_md5(os.path.join(file_dir, csv))
      with open(os.path.join(file_dir, meta), "r") as m:
        table = json.load(m)
      csv_meta_dict["table_name"] = table["table_name"]
      hash_row_list.append(csv_meta_dict)

    return hash_row_list

  def compare_csv_version(self, row_list: list):
    required_update_table = []  # Table list that needs synchronization
    required_update_hash = []   # Csv file list that needs to update a hash table
    for row in row_list:
      select_csv_sql = f"""
        select table_name, file_name
        from {self.schema}.{self.table}
        where
          file_name = '{row["file_name"]}'
          AND table_name = '{row["table_name"]}'
          AND csv_hash <> '{row["csv_hash"]}'
        """
      result = self.engine.execute(select_csv_sql).fetchone()
      if result:
        required_update_table.append(result[0])
        required_update_hash.append(result[1])

    # update to hash table
    if required_update_hash:
      for csv in required_update_hash:
        for row in row_list:
          if csv == row["file_name"]:
            update_hash_sql = f"""
              update {self.schema}.{self.table}
              set csv_hash = '{row["csv_hash"]}'
              where
                file_name = '{row["file_name"]}'
                AND table_name = '{row["table_name"]}'
                AND csv_hash <> '{row["csv_hash"]}'
            """
            self.engine.execute(update_hash_sql)

    # return required update table list
    if required_update_table:
      required_update_table = list(set(required_update_table))
    return required_update_table

  def sync_table(self):
    check_hash_table = self.engine.execute(f"select * from {self.schema}.{self.table}").fetchone()
    row_list = self.get_csv_version(os.path.join(os.getcwd(), "files"))
    if not check_hash_table:
      # Insert rows into hash table if there is no data
      super().init_hash_table(row_list)
      # TODO: .td로 맵핑한 DDL 스크립트 실행
    else:
      # Compare & update table
      self.compare_csv_version(row_list)
      # TODO: .td로 맵핑한 DDL 스크립트 실행 - update인 경우 drop 후 create

if __name__ == "__main__":
  # ./files 폴더에 존재하는 .csv의 Hash 값을 저장합니다
  config = get_config()
  DBTableBase(config).init_db_object()
  DBTableSync(config).sync_table()
