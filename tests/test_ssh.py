import os
import pytest

from tabdanc.updownload.ssh import SSHConnector


def test_check_sftp(test_ssh_config):
  ssh_connector = SSHConnector(test_ssh_config)
  error_message = "SSH is not connect, sftp is none"

  with pytest.raises(AssertionError) as error:
    ssh_connector.disconnect_sftp()
  assert str(error.value) == error_message

  with pytest.raises(AssertionError) as error:
    ssh_connector.get_files("remote_path", "local_path")
  assert str(error.value) == error_message

  with pytest.raises(AssertionError) as error:
    ssh_connector.put_files("local_path", "remote_path")
  assert str(error.value) == error_message

  with pytest.raises(AssertionError) as error:
    ssh_connector.get_listdir("path")
  assert str(error.value) == error_message

  with pytest.raises(AssertionError) as error:
    ssh_connector.read_meta_file_and_return_td_file("meta_file_path")
  assert str(error.value) == error_message


def test_connect_sftp(test_ssh_config):
  ssh_connector = SSHConnector(test_ssh_config)
  ssh_connector.connect_sftp()
  assert ssh_connector.ssh_client is not None, "After create sftp, ssh_clinet is none"
  assert ssh_connector.sftp is not None, "After create sftp, sftp is none"


def test_disconnect_sftp(test_ssh_config):
  ssh_connector = SSHConnector(test_ssh_config)
  ssh_connector.connect_sftp()
  ssh_connector.disconnect_sftp()
  with pytest.raises(OSError) as error:
    ssh_connector.sftp.listdir()
  assert str(error.value) == "Socket is closed"


def test_put_get_files(test_ssh_config):
  ssh_connector = SSHConnector(test_ssh_config)
  ssh_connector.connect_sftp()

  local_repo_path = test_ssh_config.get("PATH", "local_repo_path")
  remote_repo_path = test_ssh_config.get("PATH", "remote_repo_path")

  file_name = "test_tabdanc.cfg"
  local_path = os.path.join(local_repo_path, file_name)
  remote_path = f"{remote_repo_path}/{file_name}"   # OS 에 따라 파일경로 문자 수정

  try:
    print() # 공백 만들어주기 위해 작성
    ssh_connector.put_files(local_path, remote_path)
    assert file_name in ssh_connector.sftp.listdir(remote_repo_path)
    print()
    ssh_connector.get_files(remote_path, local_path)
    assert file_name in os.listdir(local_repo_path)

  finally:
    if os.path.exists(local_path):
      os.remove(local_path)
    if file_name in ssh_connector.sftp.listdir(remote_repo_path):
      ssh_connector.ssh_client.exec_command(f"rm -r {remote_path}")
    ssh_connector.disconnect_sftp()
