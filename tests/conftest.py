import os
import pytest

from tabdanc.config import TableDataSyncConfig


def delete_config_file_and_directory(test_config):
  if os.path.exists(test_config.config_file_path):
    os.remove(test_config.config_file_path)

  if os.path.exists(test_config.tabdanc_directory_path):
    if len(os.listdir(test_config.tabdanc_directory_path)) == 0:
      os.rmdir(test_config.tabdanc_directory_path)


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
  ), "Before execute test_ssh.py, input test_config info"

  return test_ssh_config
