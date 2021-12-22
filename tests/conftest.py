import csv
import json
import os
import pytest

from abc import ABCMeta, abstractmethod

from tabdanc.config import TableDataSyncConfig
from tabdanc.updownload.ssh import SSHConnector


@pytest.fixture(scope="session")
def test_config():
  test_config = TableDataSyncConfig()
  test_config.tabdanc_directory_path = os.path.join(os.path.expanduser("~"), ".test_tabdanc/")
  test_config.config_file_path = os.path.join(test_config.tabdanc_directory_path, "test_tabdanc.cfg")
  yield test_config
  delete_config_file_and_directory(test_config)


def delete_config_file_and_directory(test_config):
  if os.path.exists(test_config.config_file_path):
    os.remove(test_config.config_file_path)

  if os.path.exists(test_config.tabdanc_directory_path):
    if len(os.listdir(test_config.tabdanc_directory_path)) == 0:
      os.rmdir(test_config.tabdanc_directory_path)
    else:
      raise Exception(f"Directory not empty: '{test_config.tabdanc_directory_path}'")


def pytest_addoption(parser):
  parser.addini("test_config_remote_repo_path", "PATH.REMOTE_REPO_PATH for Test")
  parser.addini("test_config_remote_host_name", "REMOTE_INFO.REMOTE_HOST_NAME for Test")
  parser.addini("test_config_remote_user_name", "REMOTE_INFO.REMOTE_USER_NAME for Test")
  parser.addini("test_config_remote_user_password", "REMOTE_INFO.REMOTE_USER_PASSWORD for Test")


@pytest.fixture(scope="session")
def test_ssh_config(request, test_config):
  test_config.create_config_file()
  test_ssh_config = test_config.get_config()

  test_ssh_config.set("PATH", "local_repo_path", test_config.tabdanc_directory_path)
  # NOTE: 테스트 실행 전에 pytest.ini 파일 확인
  test_ssh_config.set("PATH", "remote_repo_path", request.config.getini("test_config_remote_repo_path"))
  test_ssh_config.set("REMOTE_INFO", "remote_host_name", request.config.getini("test_config_remote_host_name"))
  test_ssh_config.set("REMOTE_INFO", "remote_user_name", request.config.getini("test_config_remote_user_name"))
  test_ssh_config.set("REMOTE_INFO", "remote_user_password", request.config.getini("test_config_remote_user_password"))

  assert (
      test_ssh_config.get("PATH", "remote_repo_path") != ""
      and test_ssh_config.get("REMOTE_INFO", "remote_host_name") != ""
      and test_ssh_config.get("REMOTE_INFO", "remote_user_name") != ""
      and test_ssh_config.get("REMOTE_INFO", "remote_user_password") != ""
  ), "Before execute test file, Create and Set 'pytest.ini' file"

  return test_ssh_config


class BaseTestFile(metaclass=ABCMeta):
  def __init__(self):
    self.csv_data = ["col1", "col2", "col3"]
    self.td_data = {
        "columns": [
            {"name": "col1", "type": "int4"},
            {"name": "col2", "type": "text"},
            {"name": "col3", "type": "varchar(255)"}
        ]
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
          "table_name": f"tabdanc_test_table{i}"
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
