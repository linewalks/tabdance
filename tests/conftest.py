import csv
import json
import os
import pytest

from abc import ABCMeta, abstractmethod

from tabdanc.config import TableDataSyncConfig
from tabdanc.updownload.ssh import SSHConnector


@pytest.fixture(scope="session")
def test_default_config():
  config = TableDataSyncConfig()
  config.tabdanc_directory_path = os.path.join(os.path.expanduser("~"), ".test_tabdanc/")
  config.config_file_path = os.path.join(config.tabdanc_directory_path, "test_tabdanc.cfg")
  yield config
  delete_config_file_and_directory(config)


def delete_config_file_and_directory(config):
  if os.path.exists(config.config_file_path):
    os.remove(config.config_file_path)

  if os.path.exists(config.tabdanc_directory_path):
    if len(os.listdir(config.tabdanc_directory_path)) == 0:
      os.rmdir(config.tabdanc_directory_path)
    else:
      raise Exception(f"Directory not empty: '{config.tabdanc_directory_path}'")


def pytest_addoption(parser):
  parser.addini("test_config_remote_repo_path", "PATH.REMOTE_REPO_PATH for Test")
  parser.addini("test_config_remote_host_name", "REMOTE_INFO.REMOTE_HOST_NAME for Test")
  parser.addini("test_config_remote_user_name", "REMOTE_INFO.REMOTE_USER_NAME for Test")
  parser.addini("test_config_remote_user_password", "REMOTE_INFO.REMOTE_USER_PASSWORD for Test")
  parser.addini("test_config_sqlalchemy_database_uri", "DB.SQLALCHEMY_DATABASE_URI for Test")
  parser.addini("test_config_schema", "DB.SCHEMA for Test")
  parser.addini("test_config_table", "DB.TABLE for Test")


@pytest.fixture(scope="session")
def test_tabdanc_config(request, test_default_config):
  test_default_config.create_config_file()
  config = test_default_config.get_config()

  config.set("PATH", "local_repo_path", test_default_config.tabdanc_directory_path)
  # NOTE: 테스트 실행 전에 pytest.ini 파일 확인
  config.set("PATH", "remote_repo_path", request.config.getini("test_config_remote_repo_path"))
  config.set("REMOTE_INFO", "remote_host_name", request.config.getini("test_config_remote_host_name"))
  config.set("REMOTE_INFO", "remote_user_name", request.config.getini("test_config_remote_user_name"))
  config.set("REMOTE_INFO", "remote_user_password",
             request.config.getini("test_config_remote_user_password"))
  config.set("DB", "sqlalchemy_database_uri", request.config.getini("test_config_sqlalchemy_database_uri"))
  config.set("DB", "schema", request.config.getini("test_config_schema"))
  config.set("DB", "table", request.config.getini("test_config_table"))

  assert (
      config.get("PATH", "remote_repo_path") != ""
      and config.get("REMOTE_INFO", "remote_host_name") != ""
      and config.get("REMOTE_INFO", "remote_user_name") != ""
      and config.get("REMOTE_INFO", "remote_user_password") != ""
      and config.get("DB", "sqlalchemy_database_uri") != ""
      and config.get("DB", "schema") != ""
      and config.get("DB", "table") != ""
  ), "Before execute test file, Create and Set 'pytest.ini' file"

  return config


class BaseTestFile(metaclass=ABCMeta):
  def __init__(self):
    self.csv_data = ["header1", "header2", "header3"]
    self.td_data = {
        "columns": [
            {"name": "col1", "type": "text"},
            {"name": "col2", "type": "text"},
            {"name": "col3", "type": "text"}
        ]
    }
    self.column_match = {
        "header1": "col1",
        "header2": "col2",
        "header3": "col3"
    }

  def setup_csv_meta_td_files(self):
    num = 3
    self.create_csv_files(num)
    self.create_meta_files(num)
    self.create_td_files(num)

  def setup_csv_meta_files(self):
    num = 1
    self.create_csv_files(num)
    self.create_meta_files(num)

  def setup_csv_td_files(self):
    num = 1
    self.create_csv_files(num)
    self.create_td_files(num)

  def setup_meta_td_files(self):
    num = 1
    self.create_meta_files(num)
    self.create_td_files(num)

  @abstractmethod
  def create_csv_files(self, count):
    pass

  @abstractmethod
  def create_meta_files(self, count):
    pass

  @abstractmethod
  def create_td_files(self, count):
    pass

  @abstractmethod
  def remove_test_files(self):
    pass


class UploadTestFile(BaseTestFile):
  def __init__(self, config):
    super().__init__()
    self.local_repo_path = config.get("PATH", "local_repo_path")

  def create_csv_files(self, count):
    for i in range(count):
      csv_file = os.path.join(self.local_repo_path, f"tabdanc_test{i}.csv")
      with open(csv_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(self.csv_data)

  def create_meta_files(self, count):
    for i in range(count):
      meta_file = os.path.join(self.local_repo_path, f"tabdanc_test{i}.meta")
      meta_data = {
          "table_name": f"tabdanc_test_table{i}",
          "column_match": self.column_match
      }
      with open(meta_file, "w") as file:
        json.dump(meta_data, file)

  def create_td_files(self, count):
    for i in range(count):
      td_file = os.path.join(self.local_repo_path, f"tabdanc_test_table{i}.td")
      with open(td_file, "w") as file:
        json.dump(self.td_data, file)

  def remove_test_files(self):
    test_files = os.listdir(self.local_repo_path)
    for file in test_files:
      file_path = os.path.join(self.local_repo_path, file)
      if file.endswith(".csv"):
        os.remove(file_path)
      elif file.endswith(".meta"):
        os.remove(file_path)
      elif file.endswith(".td"):
        os.remove(file_path)


class DownloadTestFile(BaseTestFile):
  def __init__(self, config):
    super().__init__()
    self.remote_repo_path = config.get("PATH", "remote_repo_path")
    self.ssh_connector = SSHConnector(config)

  def connect_sftp(self):
    self.ssh_connector.connect_sftp()

  def disconnect_sftp(self):
    self.ssh_connector.disconnect_sftp()

  def create_csv_files(self, count):
    for i in range(count):
      csv_file = self.remote_repo_path + "/" + f"tabdanc_test{i}.csv"
      with self.ssh_connector.sftp.open(csv_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(self.csv_data)

  def create_meta_files(self, count):
    for i in range(count):
      meta_file = self.remote_repo_path + "/" + f"tabdanc_test{i}.meta"
      meta_data = {
          "table_name": f"tabdanc_test_table{i}"
      }
      with self.ssh_connector.sftp.open(meta_file, "w") as file:
        json.dump(meta_data, file)

  def create_td_files(self, count):
    for i in range(count):
      td_file = self.remote_repo_path + "/" + f"tabdanc_test_table{i}.td"
      with self.ssh_connector.sftp.open(td_file, "w") as file:
        json.dump(self.td_data, file)

  def remove_test_files(self):
    test_files = self.ssh_connector.sftp.listdir(self.remote_repo_path)
    for file in test_files:
      if "tabdanc_test" in file:
        file_path = self.remote_repo_path + "/" + file
        self.ssh_connector.sftp.remove(file_path)
