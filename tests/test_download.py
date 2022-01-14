import argparse
import os
import pytest

from tests.conftest import DownloadTestFile
from tabdance.updownload.download import Downloader


@pytest.fixture
def download_test_file(test_tabdance_config):
  test_file = DownloadTestFile(test_tabdance_config)
  test_file.connect_sftp()
  yield test_file
  test_file.remove_test_files()
  test_file.disconnect_sftp()


@pytest.mark.parametrize(
    "args",
    [
        argparse.Namespace(command="download", all=False, file=["tabdance_test0"]),
        argparse.Namespace(command="download", all=False, file=["tabdance_test0", "tabdance_test1"]),
        argparse.Namespace(command="download", all=True, file=None)
    ]
)
def test_exist_all_files(download_test_file, args, test_tabdance_config):
  download_test_file.setup_csv_meta_td_files()
  start_download(args, test_tabdance_config)


@pytest.mark.parametrize("args", [argparse.Namespace(command="download", all=False, file=["tabdance_test0"])])
def test_not_exist_td(download_test_file, args, test_tabdance_config):
  download_test_file.setup_csv_meta_files()

  with pytest.raises(Exception) as error:
    start_download(args, test_tabdance_config)
  assert f"No such file in {test_tabdance_config.get('PATH','remote_repo_path')}" in str(error.value)


@pytest.mark.parametrize("args", [argparse.Namespace(command="download", all=False, file=["tabdance_test0"])])
def test_not_exist_meta(download_test_file, args, test_tabdance_config):
  download_test_file.setup_csv_td_files()

  with pytest.raises(Exception) as error:
    start_download(args, test_tabdance_config)
  assert f"No such file:" in str(error.value)


@pytest.mark.parametrize("args", [argparse.Namespace(command="download", all=False, file=["tabdance_test0"])])
def test_not_exist_csv(download_test_file, args, test_tabdance_config):
  download_test_file.setup_meta_td_files()

  with pytest.raises(Exception) as error:
    start_download(args, test_tabdance_config)
  assert f"No such file:" in str(error.value)


def start_download(args, config):
  try:
    downloader = Downloader(args, config)
    ssh_connector = downloader.ssh_connector
    ssh_connector.connect_sftp()
    downloader.download()
  finally:
    local_repo_path = config.get("PATH", "local_repo_path")
    for file in os.listdir(local_repo_path):
      if file.endswith(".csv") or file.endswith(".meta") or file.endswith(".td"):
        os.remove(os.path.join(local_repo_path, file))
    ssh_connector.disconnect_sftp()
