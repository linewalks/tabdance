import csv
import json
import os
import pytest

from abc import ABCMeta, abstractmethod

from tabdanc.config import TableDataSyncConfig


def delete_config_file_and_directory(test_config):
  if os.path.exists(test_config.config_file_path):
    os.remove(test_config.config_file_path)

  if os.path.exists(test_config.tabdanc_directory_path):
    if len(os.listdir(test_config.tabdanc_directory_path)) == 0:
      os.rmdir(test_config.tabdanc_directory_path)
    else:
      raise Exception(f"Directory not empty: '{test_config.tabdanc_directory_path}'")


@pytest.fixture(scope="session")
def test_config():
  test_config = TableDataSyncConfig()
  test_config.tabdanc_directory_path = os.path.join(os.path.expanduser("~"), ".test_tabdanc/")
  test_config.config_file_path = os.path.join(test_config.tabdanc_directory_path, "test_tabdanc.cfg")

  yield test_config

  delete_config_file_and_directory(test_config)


@pytest.fixture(scope="session")
def test_ssh_config(test_config):
  test_config.create_config_file()
  test_ssh_config = test_config.get_config()

  test_ssh_config.set("PATH", "local_repo_path", test_config.tabdanc_directory_path)
  # NOTE: ssh 테스트 실행 전에 "" 부분 값 넣어주기
  test_ssh_config.set("PATH", "remote_repo_path", "")
  test_ssh_config.set("REMOTE_INFO", "remote_host_name", "")
  test_ssh_config.set("REMOTE_INFO", "remote_user_name", "")
  test_ssh_config.set("REMOTE_INFO", "remote_user_password", "")

  assert (
      test_ssh_config.get("PATH", "remote_repo_path") != ""
      and test_ssh_config.get("REMOTE_INFO", "remote_host_name") != ""
      and test_ssh_config.get("REMOTE_INFO", "remote_user_name") != ""
      and test_ssh_config.get("REMOTE_INFO", "remote_user_password") != ""
  ), "Before execute test file, input test_config info in 'conftest.py'"

  return test_ssh_config


class TestFileBase(metaclass=ABCMeta):
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


class UploadTestFile(TestFileBase):
  def __init__(self, config):
    self.local_repo_path = config.get("PATH", "local_repo_path")

  def create_csv_files(self, count):
    for i in range(count):
      csv_file = os.path.join(self.local_repo_path, f"tabdanc_test{i}.csv")
      with open(csv_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["col1", "col2", "col3"])

  def create_meta_files(self, count):
    for i in range(count):
      meta_file = os.path.join(self.local_repo_path, f"tabdanc_test{i}.meta")
      data = {
          "table_name": f"tabdanc_test_table{i}"
      }
      with open(meta_file, "w") as file:
        json.dump(data, file)

  def create_td_files(self, count):
    for i in range(count):
      td_file = os.path.join(self.local_repo_path, f"tabdanc_test_table{i}.td")
      data = {
          "columns": [
              {"name": "seq", "type": "int4"},
              {"name": "code", "type": "varchar"}
          ]
      }
      with open(td_file, "w") as file:
        json.dump(data, file)

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
