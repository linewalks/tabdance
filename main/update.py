import hashlib
import json
import os
import pandas as pd
import time

from configparser import ConfigParser
from sqlalchemy import create_engine

from base import get_config


def calculate_md5(csv_path: str) -> hex:
  with open(csv_path, "rb") as f:
    file_hash = hashlib.md5()
    while chunk := f.read(8192):
      file_hash.update(chunk)
  return file_hash.hexdigest()


class DBBase:
  def __init__(self, config: ConfigParser):
    self.uri = config["DB"]["SQLALCHEMY_DATABASE_URI"]
    self.schema = config["DB"]["SCHEMA"]
    self.engine = create_engine(self.uri)

  def load_sql(self, sql_path: str):
    with open(sql_path, "r") as fd:
      start_time = time.time()
      print(f"\n===========Start loading Sql script '{sql_path}'===========")
      sql = fd.read().format(schema_name=self.schema)
      self.engine.execute(sql)
      end_time = time.time()
      print(f"Time for loading sql script: {end_time-start_time:.2f}secs")
      print(f"\n===========Finished loading Sql script '{sql_path}'===========")

  def init_schema(self, sql_dir: str):
    for script in sorted(os.listdir(sql_dir)):
      # Check for Schema
      self.load_sql(sql_path=os.path.join(sql_dir, script))

  def init_hash_table(self, file_dir: str, hash_table_name: str):
    self.init_schema(os.path.join(os.getcwd(), "sql", "base"))

    # Download csv to LOCAL_REPO_PATH must be first
    # Ex. python download.py -a

    csv_list = sorted([csv for csv in os.listdir(file_dir) if csv.endswith(".csv")])
    meta_list = sorted([meta for meta in os.listdir(file_dir) if meta.endswith(".meta")])

    hash_table = dict()
    csv_hash_list = []
    table_name_list = []

    for csv, meta in zip(csv_list, meta_list):
      csv_hash_list.append(calculate_md5(os.path.join(file_dir, csv)))

      with open(os.path.join(file_dir, meta), "r") as m:
        table = json.load(m)
      table_name_list.append(table["table_name"])

    hash_table["file_name"] = csv_list
    hash_table["csv_hash"] = csv_hash_list
    hash_table["table_name"] = table_name_list

    df = pd.DataFrame(hash_table)
    df.to_sql(
      hash_table_name,
      self.engine,
      schema=self.schema,
      if_exists="replace",
      index=False
    )


if __name__ == "__main__":
  # ./files 폴더에 존재하는 .csv의 Hash 값을 저장합니다
  # TODO: Hash 테이블(mdwalks_table_version)이 처음 입력될 때만 실행되도록 수정
  config = get_config()
  DBBase(config).init_hash_table(os.path.join(os.getcwd(), "files"), "mdwalks_table_version")

  # df와 DB hash 테이블 (mdwalks_table_version)과 비교 후 변경된 해시가 있는 경우
  # 1. Hash 테이블 업데이트
  # 2. 변경된 csv로 생성된 기존 테이블 drop
  # 3. ./files의 csv COPY하여 테이블 생성
  #  |_ 테이블 생성하는 경우: "table_name"과 같은 .td 파일을 읽고 테이블을 생성한다.
