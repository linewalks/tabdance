import argparse
import csv
import json
import os
import pytest

from tabdanc.updownload.upload import Uploader


class UploadTestFile:
  def __init__(self, config):
    self.local_repo_path = config.get("PATH", "local_repo_path")

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


@pytest.fixture
def test_file(test_ssh_config):
  test_file = UploadTestFile(test_ssh_config)
  yield test_file
  test_file.remove_test_files()


@pytest.mark.parametrize(
    "args",
    [
        argparse.Namespace(command="upload", all=False, file=["tabdanc_test0"]),
        argparse.Namespace(command="upload", all=False, file=["tabdanc_test0", "tabdanc_test1"]),
        argparse.Namespace(command="upload", all=True, file=None)
    ]
)
def test_exist_all_files(test_file, args, test_ssh_config):
  test_file.setup_csv_meta_td_files()
  start_upload(args, test_ssh_config)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdanc_test0"])])
def test_not_exist_td(test_file, args, test_ssh_config):
  test_file.setup_csv_meta_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_ssh_config)
  assert f"No such file in {test_ssh_config.get('PATH','local_repo_path')}" in str(error.value)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdanc_test0"])])
def test_not_exist_meta(test_file, args, test_ssh_config):
  test_file.setup_csv_td_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_ssh_config)
  assert f"No such file:" in str(error.value)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdanc_test0"])])
def test_not_exist_csv(test_file, args, test_ssh_config):
  test_file.setup_meta_td_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_ssh_config)
  assert f"No such file:" in str(error.value)


def start_upload(args, config):
  try:
    uploader = Uploader(args, config)
    ssh_connector = uploader.ssh_connector
    ssh_connector.connect_sftp()
    uploader.upload()
  finally:
    remote_repo_path = config.get("PATH", "remote_repo_path")
    for file in ssh_connector.sftp.listdir(remote_repo_path):
      if "tabdanc_test" in file:
        ssh_connector.sftp.remove(remote_repo_path + "/" + file)  # OS 에 따라 파일경로 문자 수정
    ssh_connector.disconnect_sftp()
