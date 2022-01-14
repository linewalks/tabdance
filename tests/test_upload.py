import argparse
import pytest

from tests.conftest import UploadTestFile
from tabdance.updownload.upload import Uploader


@pytest.fixture
def upload_test_file(test_tabdance_config):
  test_file = UploadTestFile(test_tabdance_config)
  yield test_file
  test_file.remove_test_files()


@pytest.mark.parametrize(
    "args",
    [
        argparse.Namespace(command="upload", all=False, file=["tabdance_test0"]),
        argparse.Namespace(command="upload", all=False, file=["tabdance_test0", "tabdance_test1"]),
        argparse.Namespace(command="upload", all=True, file=None)
    ]
)
def test_exist_all_files(upload_test_file, args, test_tabdance_config):
  upload_test_file.setup_csv_meta_td_files()
  start_upload(args, test_tabdance_config)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdance_test0"])])
def test_not_exist_td(upload_test_file, args, test_tabdance_config):
  upload_test_file.setup_csv_meta_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_tabdance_config)
  assert f"No such file in {test_tabdance_config.get('PATH','local_repo_path')}" in str(error.value)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdance_test0"])])
def test_not_exist_meta(upload_test_file, args, test_tabdance_config):
  upload_test_file.setup_csv_td_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_tabdance_config)
  assert f"No such file:" in str(error.value)


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=False, file=["tabdance_test0"])])
def test_not_exist_csv(upload_test_file, args, test_tabdance_config):
  upload_test_file.setup_meta_td_files()

  with pytest.raises(Exception) as error:
    start_upload(args, test_tabdance_config)
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
      if "tabdance_test" in file:
        ssh_connector.sftp.remove(remote_repo_path + "/" + file)  # OS 에 따라 파일경로 문자 수정
    ssh_connector.disconnect_sftp()


@pytest.mark.parametrize("args", [argparse.Namespace(command="upload", all=True, file=None)])
def test_check_column_match(upload_test_file, args, test_tabdance_config):
  upload_test_file.setup_csv_meta_td_files()
  files = ["tabdance_test0.meta", "tabdance_test1.meta", "tabdance_test2.meta"]
  uploader = Uploader(args, test_tabdance_config)
  uploader.check_column_match_in_meta_file(files)
