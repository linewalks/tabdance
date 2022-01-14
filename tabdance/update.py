import hashlib
import json
import os
import time

from configparser import ConfigParser
from csv import reader
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector


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
        Path(__file__).resolve().parent
    ).joinpath(
        "sql", "base"
    )

  def load_crud_sql(self, sql_path: str, **kwargs) -> None:
    with open(sql_path, "r") as fd:
      start_time = time.time()
      print(f"Start loading Sql script '{sql_path.name}'")
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
      print(f"Finished loading Sql script '{sql_path.name}'")

  def check_db_object(self, db_object: str, object_name: str) -> str:
    inspector = Inspector.from_engine(self.engine)
    if db_object == "schema":
      db_object_list = inspector.get_schema_names()
    elif db_object == "table":
      db_object_list = inspector.get_table_names(schema=self.schema)

    if object_name not in db_object_list:
      return object_name

  def init_db_object(self) -> None:
    for required_obj, name in zip(["schema", "table"], [self.schema, self.table]):
      required_obj_name = self.check_db_object(required_obj, name)
      if required_obj_name:
        self.load_crud_sql(self.sql_base_path.joinpath(
            f"init_{required_obj}.sql"), table_name=required_obj_name)


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

  def get_sql_result(self, sql_path, **kwargs) -> tuple:
    with open(sql_path, "r") as sql:
      sql_string = sql.read().format(
          schema_name=self.schema,
          table_name=kwargs.get("table_name"),
          tds_file_name=kwargs.get("tds_file_name"),
          tds_table_name=kwargs.get("tds_table_name"),
          tds_csv_hash=kwargs.get("tds_csv_hash")
      )
    return self.engine.execute(sql_string).fetchone()

  def insert_tds_version(self, table_list: list, row_list: list) -> None:
    print(f"### Inserting data into {self.table}")
    for table in table_list:
      for row in row_list:
        if row["table_name"] == table:
          with self.engine.connect() as conn:
            self.load_crud_sql(
                self.sql_path.joinpath("insert_tds_version.sql"),
                table_name=self.table,
                tds_file_name=row["file_name"],
                tds_table_name=row["table_name"],
                tds_csv_hash=row["csv_hash"]
            )
    print(f"### End of inserting data into {self.table}\n")

  def compare_tds_version(self, row_list: list) -> list:
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
      elif not self.check_db_object(
          "table", row["table_name"]
      ) and not self.get_sql_result(
          self.sql_path.joinpath("select_table.sql"),
          table_name=row["table_name"]
      ):
        # The target_table is empty and csv file has no changes
        required_update_table.append(row["table_name"])

    # update to tds_version table
    if required_update_csv:
      print(f"### Update data set from {self.table}")
      for csv in required_update_csv:
        for row in row_list:
          if csv == row["file_name"]:
            self.load_crud_sql(
                self.sql_path.joinpath("update_tds_version.sql"),
                table_name=self.table,
                tds_file_name=row["file_name"],
                tds_table_name=row["table_name"],
                tds_csv_hash=row["csv_hash"]
            )
      print(f"### End of update into {self.table}\n")

    # return required update table list
    return list(set(required_update_table))

  def create_target_table(self, table: str) -> None:
    # create target table from table definition(.td)
    with open(os.path.join(self.file_path, f"{table}.td"), "r") as td:
      table_schema = json.load(td)
      column_info = ",".join(
          [f"{col['name']} {col['type']}" for col in table_schema["columns"]])
      cast_column = ",".join(
          [f"CAST({col['name']} AS {col['type']})" for col in table_schema["columns"]])

    self.load_crud_sql(
        self.sql_path.joinpath("create_table.sql"),
        table_name=table,
        column_info=column_info
    )

    # Input only the columns specified in .td into target table
    # The column type of the target table must be cast as a column type of .td
    self.load_crud_sql(
        self.sql_td_path.joinpath("insert_target_from_temp.sql"),
        table_name=table,
        column_info=cast_column
    )

  def create_temp_target_table(self, csv: str, table: str) -> None:
    # Create temp table
    # create a temporary table with column of text type by reading the header of csv
    conn = self.engine.raw_connection()
    csv = os.path.join(self.file_path, csv)
    with open(csv, "r") as csvfile:
      csv_reader = reader(csvfile, delimiter=",")
      headers = next(csv_reader)

    # Mapping between csv header and table column, if 'column_match' key exists in .meta
    meta = os.path.join(self.file_path, f"{os.path.splitext(csv)[0]}.meta")
    with open(meta, "r") as metafile:
      meta_datas = json.load(metafile)

    if "column_match" in meta_datas.keys():
      for i in range(len(headers)):
        if headers[i] in meta_datas["column_match"].keys():
          headers[i] = meta_datas["column_match"][headers[i]]

    # When table:csv = 1:n, the number of headers of the csv files should be the same.
    if self.check_db_object("table", f"temp_{table}"):
      temp_column_info = ",".join([f"{header} text" for header in headers])
      self.load_crud_sql(
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
    print(f"### COPY temp_{table} FROM {csv}")

  def insert_target_table(self, table_list: list, tds_version_list: list) -> None:
    for table in table_list:
      print(f"============={table}=============")
      for row in tds_version_list:
        if row["table_name"] == table:
          print(f"### Inserting data into temp_{table}")
          self.create_temp_target_table(row["file_name"], row["table_name"])
          print(f"### End of inserting data into temp_{table}\n")
      print(f"### Inserting data into {table}")
      self.create_target_table(table)
      print(f"### End of inserting data into {table}\n")
      self.drop_table(f"temp_{table}")
      print(f"==================================\n")

  def drop_table(self, table: str) -> None:
    print(f"### Drop Table {table}")
    self.load_crud_sql(self.sql_path.joinpath("drop_table.sql"), table_name=table)

  def sync_table(self) -> None:
    row_list = self.get_tds_version()

    # Initialize target_table to the file name of the .td extension
    td_list = [
        td[:-3]
        for td in os.listdir(self.file_path)
        if td.endswith(".td")
    ]
    create_table_list = []
    # Check whether the target_table is created or not
    for td_name in td_list:
      required_obj_name = self.check_db_object("table", td_name)
      if required_obj_name:
        create_table_list.append(required_obj_name)
    create_table_list = list(set(create_table_list))

    print("=============tds_version=============")
    # Insert csv version of table from create_table_list into the tds_version
    self.insert_tds_version(create_table_list, row_list)
    # Compare & update tds_version table
    update_table_list = self.compare_tds_version(row_list)

    # Create target table from .td
    self.insert_target_table(create_table_list, row_list)
    if update_table_list:
      print("### Update the table")
      # If the csv file is changed, delete the table and recreate it
      for table in update_table_list:
        self.drop_table(table)
      self.insert_target_table(update_table_list, row_list)