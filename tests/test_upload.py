import argparse
import pytest

from tests.conftest import UploadTestFile
from tabdanc.updownload.upload import Uploader


@pytest.fixture
def upload_test_file(test_tabdanc_config):
  test_file = UploadTestFile(test_tabdanc_config)
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
def test_exist_all_files(upload_test_file, args, test_tabdanc_config):
  upload_test_file.setup_csv_meta_td_files()
  start_upload(args, test_tabdanc_config)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdanc_test0"])])
def test_not_exist_td(upload_test_file, args, test_tabdanc_config):
  upload_test_file.setup_csv_meta_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_tabdanc_config)
  assert f"No such file in {test_tabdanc_config.get('PATH','local_repo_path')}" in str(error.value)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdanc_test0"])])
def test_not_exist_meta(upload_test_file, args, test_tabdanc_config):
  upload_test_file.setup_csv_td_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_tabdanc_config)
  assert f"No such file:" in str(error.value)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdanc_test0"])])
def test_not_exist_csv(upload_test_file, args, test_tabdanc_config):
  upload_test_file.setup_meta_td_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_tabdanc_config)
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
