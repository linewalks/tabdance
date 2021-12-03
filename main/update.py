import hashlib
import json
import os
import pandas as pd
import time

from configparser import ConfigParser
from csv import reader
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector

from main.base import get_config


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
    self.sql_base_path = (
        Path(__file__).resolve().parent).joinpath("sql", "base")

  def load_sql(self, sql_path: str, **kwargs):
    with open(sql_path, "r") as fd:
      start_time = time.time()
      print(f"\n===========Start loading Sql script '{sql_path}'===========")
      sql = fd.read().format(
          schema_name=self.schema,
          table_name=kwargs.get("table_name"),
          tds_file_name=kwargs.get("tds_file_name"),
          tds_table_name=kwargs.get("tds_table_name"),
          tds_csv_hash=kwargs.get("tds_csv_hash"),
          column_info=kwargs.get("column_info")
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
      return object_name

  def init_db_object(self):
    for required_obj, name in zip(["schema", "table"], [self.schema, self.table]):
      required_obj_name = self.check_db_object(required_obj, name)
      if required_obj_name:
        self.load_sql(self.sql_base_path.joinpath(
            f"init_{required_obj}.sql"), table_name=required_obj_name)
      else:
        pass

  def init_tds_version(self, row_list: list):
    print(f"\n===========Inserting data into {self.table}===========")
    for row in row_list:
      with self.engine.connect() as conn:
        self.load_sql(
            self.sql_base_path.joinpath("init_tds_version.sql"),
            table_name=self.table,
            tds_file_name=row["file_name"],
            tds_table_name=row["table_name"],
            tds_csv_hash=row["csv_hash"]
        )
    print(f"\n===========End of inserting data into {self.table}===========")


class DBTableSync(DBTableBase):
  def __init__(self, config):
    super().__init__(config)
    self.sql_path = (Path(__file__).resolve().parent).joinpath("sql")
    self.sql_td_path = (Path(__file__).resolve().parent).joinpath("sql", "td")
    self.file_path = config["PATH"]["LOCAL_REPO_PATH"]

  def get_tds_version(self) -> list:
    # Download csv to LOCAL_REPO_PATH must be first
    # Ex. tds download -a
    csv_list = sorted(
        [csv for csv in os.listdir(self.file_path) if csv.endswith(".csv")])
    meta_list = sorted(
        [meta for meta in os.listdir(self.file_path) if meta.endswith(".meta")])

    hash_row_list = []
    for csv, meta in zip(csv_list, meta_list):
      csv_meta_dict = {}
      csv_meta_dict["file_name"] = csv
      csv_meta_dict["csv_hash"] = calculate_md5(
          os.path.join(self.file_path, csv))
      with open(os.path.join(self.file_path, meta), "r") as m:
        table = json.load(m)
      csv_meta_dict["table_name"] = table["table_name"]
      hash_row_list.append(csv_meta_dict)

    return hash_row_list

  def get_sql_result(self, sql_path, **kwargs):
    with open(sql_path, "r") as sql:
      sql_string = sql.read().format(
          schema_name=self.schema,
          table_name=kwargs.get("table_name"),
          tds_file_name=kwargs.get("tds_file_name"),
          tds_table_name=kwargs.get("tds_table_name"),
          tds_csv_hash=kwargs.get("tds_csv_hash")
      )
    return self.engine.execute(sql_string).fetchone()

  def compare_tds_version(self, row_list: list):
    # tds_version 테이블에 값이 없는 경우: required_update_table, required_update_csv에 값 입력
    # tds_version 테이블에 값이 있는 경우: compare_tds_version.sql 실행 후 리턴되는 table, csv 입력
    required_update_table = []  # Table list that needs synchronization
    required_update_csv = []   # Csv file list that needs to update a tds_version table

    for row in row_list:
      result = self.get_sql_result(
          self.sql_path.joinpath("compare_tds_version.sql"),
          table_name=self.table,
          tds_file_name=row["file_name"],
          tds_table_name=row["table_name"],
          tds_csv_hash=row["csv_hash"])
      if result:
        required_update_table.append(result[0])
        required_update_csv.append(result[1])

    # update to tds_version table
    if required_update_csv:
      for csv in required_update_csv:
        for row in row_list:
          if csv == row["file_name"]:
            self.load_sql(
                self.sql_path.joinpath("update_tds_version.sql"),
                table_name=self.table,
                tds_file_name=row["file_name"],
                tds_table_name=row["table_name"],
                tds_csv_hash=row["csv_hash"]
            )

    # return required update table list
    return list(set(required_update_table))

  def create_target_table(self, table: str):
    # create target table from table definition(.td)
    with open(os.path.join(self.file_path, f"{table}.td"), "r") as td:
      table_def = json.load(td)
      column_info = ",".join(
          [f"{col['name']} {col['type']}" for col in table_def["columns"]])
      cast_column = ",".join(
          [f"CAST({col['name']} AS {col['type']})" for col in table_def["columns"]])

    self.load_sql(
        self.sql_path.joinpath("create_table.sql"),
        table_name=table,
        column_info=column_info
    )

    # Input only the columns specified in .td into target table
    # The column type of the target table must be cast as a column type of .td
    self.load_sql(
        os.path.join(self.sql_td_path, "insert_target_from_temp.sql"),
        table_name=table,
        column_info=cast_column
    )

  def create_temp_target_table(self, csv: str, table: str):
    # Create temp table
    # create a temporary table with column of text type by reading the header of csv
    conn = self.engine.raw_connection()
    csv = os.path.join(self.file_path, csv)
    first_line = 0
    with open(csv, "r") as csvfile:
      csv_reader = reader(csvfile, delimiter=",")
      for row in csv_reader:
        while first_line == 0:
          header = row
          first_line += 1

    # When table:csv = 1:n, the number of headers of the csv files should be the same.
    if self.check_db_object("table", f"temp_{table}"):
      temp_column_info = ",".join(
          [" ".join(i) for i in list(zip(header, ["text"] * len(header)))])
      self.load_sql(
          self.sql_path.joinpath("create_table.sql"),
          table_name=f"temp_{table}",
          column_info=temp_column_info
      )

    # Copy csv
    with open(os.path.join(self.sql_td_path, "copy_csv_to_table.sql"), "r") as sql:
      copy_sql = sql.read().format(
          schema_name=self.schema, table_name=f"temp_{table}")

    with open(csv) as f:
      conn.cursor().copy_expert(copy_sql, f)
    conn.commit()

  def insert_target_table(self, table_list: list, tds_version_list: list):
    for table in table_list:
      for row in tds_version_list:
        if row["table_name"] == table:
          print(f"\n===========Inserting data into temp_{table}===========")
          self.create_temp_target_table(row["file_name"], row["table_name"])
          print(f"\n===========End of inserting data into temp_{table}===========")
        else:
          continue

    for table in table_list:
      print(f"\n===========Inserting data into {table}===========")
      self.create_target_table(table)
      print(f"\n===========End of inserting data into {table}===========")

    for table in table_list:
      self.drop_table(f"temp_{table}")

  def drop_table(self, table: str):
    print(f"\n===========Drop Table {table}===========")
    self.load_sql(os.path.join(self.sql_path, "drop_table.sql"), table_name=table)

  def sync_table(self):
    row_list = self.get_tds_version()
    check_tds_version = self.get_sql_result(
        self.sql_path.joinpath("select_table.sql"),
        table_name=self.table
    )

    # Initialize target_table to the file name of the .td extension
    td_list = [td[:-3]
               for td in os.listdir(self.file_path) if td.endswith(".td")]
    table_list = []
    # Check whether the target_table is created or not
    for td_name in td_list:
      required_obj_name = self.check_db_object("table", td_name)
      if required_obj_name:
        table_list.append(required_obj_name)
    table_list = list(set(table_list))

    if not check_tds_version:
      # Insert rows into tds_version table if there is no data
      super().init_tds_version(row_list)
      # Create target table from .td
      self.insert_target_table(table_list, row_list)
    else:
      if table_list:
        # When target_table is not created
        self.insert_target_table(table_list, row_list)
      else:
        # Compare & update tds_version table
        table_list = self.compare_tds_version(row_list)
        # If the csv file is changed, delete the table and recreate it
        for table in table_list:
          self.drop_table(table)
        self.insert_target_table(table_list, row_list)


if __name__ == "__main__":
  # ./files 폴더에 존재하는 .csv의 Hash 값을 저장합니다
  config = get_config()
  DBTableBase(config).init_db_object()
  DBTableSync(config).sync_table()
