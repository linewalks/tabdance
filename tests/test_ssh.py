import os
import pytest

from tabdanc.updownload.ssh import SSHConnector


@pytest.fixture(scope="class")
def ssh_connector(test_tabdanc_config):
  ssh_connector = SSHConnector(test_tabdanc_config)
  return ssh_connector


class TestDecorator:
  error_message = "SSH is not connect, sftp is none"

  def test_disconnect_sftp(self, ssh_connector):
    with pytest.raises(AssertionError) as error:
      ssh_connector.disconnect_sftp()
    assert str(error.value) == TestDecorator.error_message

  def test_get_files(self, ssh_connector):
    with pytest.raises(AssertionError) as error:
      ssh_connector.get_files("test_remote_path", "test_local_path")
    assert str(error.value) == TestDecorator.error_message

  def test_put_files(self, ssh_connector):
    with pytest.raises(AssertionError) as error:
      ssh_connector.put_files("test_local_path", "test_remote_path")
    assert str(error.value) == TestDecorator.error_message

  def test_get_listdir(self, ssh_connector):
    with pytest.raises(AssertionError) as error:
      ssh_connector.get_listdir("test_path")
    assert str(error.value) == TestDecorator.error_message

  def test_read_meta_file_and_return_td_file(self, ssh_connector):
    with pytest.raises(AssertionError) as error:
      ssh_connector.read_meta_file_and_return_td_file("test_meta_file_path")
    assert str(error.value) == TestDecorator.error_message


class TestConnection:
  def test_connect_sftp(self, ssh_connector):
    ssh_connector.connect_sftp()
    assert ssh_connector.ssh_client is not None, "After create sftp, ssh_clinet is none"
    assert ssh_connector.sftp is not None, "After create sftp, sftp is none"

  def test_disconnect_sftp(self, ssh_connector):
    ssh_connector.connect_sftp()
    ssh_connector.disconnect_sftp()
    with pytest.raises(OSError) as error:
      ssh_connector.sftp.listdir()
    assert str(error.value) == "Socket is closed"


class TestFileUpDownLoad:
  @pytest.fixture(scope="class")
  def test_data(self, test_tabdanc_config):
    local_repo_path = test_tabdanc_config.get("PATH", "local_repo_path")
    remote_repo_path = test_tabdanc_config.get("PATH", "remote_repo_path")

    file_name = "test_tabdanc.cfg"
    local_path = os.path.join(local_repo_path, file_name)
    remote_path = f"{remote_repo_path}/{file_name}"   # OS 에 따라 파일경로 문자 수정

    return {
        "local_repo_path": local_repo_path,
        "remote_repo_path": remote_repo_path,
        "file_name": file_name,
        "local_path": local_path,
        "remote_path": remote_path
    }

  def test_put_files(self, ssh_connector, test_data):
    try:
      print()
      ssh_connector.connect_sftp()
      ssh_connector.put_files(test_data["local_path"], test_data["remote_path"])
      assert test_data["file_name"] in ssh_connector.sftp.listdir(test_data["remote_repo_path"])
    finally:
      if os.path.exists(test_data["local_path"]):
        os.remove(test_data["local_path"])
      ssh_connector.disconnect_sftp()

  def test_get_files(self, ssh_connector, test_data):
    try:
      print()
      ssh_connector.connect_sftp()
      ssh_connector.get_files(test_data["remote_path"], test_data["local_path"])
      assert test_data["file_name"] in os.listdir(test_data["local_repo_path"])
    finally:
      if test_data["file_name"] in ssh_connector.sftp.listdir(test_data["remote_repo_path"]):
        ssh_connector.sftp.remove(test_data['remote_path'])
      ssh_connector.disconnect_sftp()
