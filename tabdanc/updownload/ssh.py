import json
import paramiko

from tabdanc.base import callback_progressbar


class SSHConnector:
  def __init__(self, config) -> None:
    self.config = config
    self.ssh_client = None
    self.sftp = None

  def connect_sftp(self) -> None:
    # TODO: 연결되지 않았을 때 오류 메시지 출력 ex) VPN 연결되지 않음.
    self.ssh_client = paramiko.SSHClient()
    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh_client.connect(
        hostname=self.config["REMOTE_INFO"]["REMOTE_HOST_NAME"],
        username=self.config["REMOTE_INFO"]["REMOTE_USER_NAME"],
        password=self.config["REMOTE_INFO"]["REMOTE_USER_PASSWORD"]
    )
    self.sftp = self.ssh_client.open_sftp()

  def decorator_raise_exception_if_sftp_is_none(func):
    def decorate(*args, **kwargs):
      self = args[0]
      if self.sftp is None:
        raise Exception("SSH is not connect, sftp is none")
      func(*args, **kwargs)
    return decorate

  @decorator_raise_exception_if_sftp_is_none
  def disconnect_sftp(self) -> None:
    self.sftp.close()
    self.ssh_client.close()

  @decorator_raise_exception_if_sftp_is_none
  def get_files(self, remote_path, local_path) -> None:
    self.sftp.get(remote_path, local_path, callback=callback_progressbar)

  @decorator_raise_exception_if_sftp_is_none
  def put_files(self, local_path, remote_path) -> None:
    self.sftp.put(local_path, remote_path, callback=callback_progressbar)

  @decorator_raise_exception_if_sftp_is_none
  def get_listdir(self, path) -> list:
    return self.sftp.listdir(path)

  @decorator_raise_exception_if_sftp_is_none
  def read_meta_file_and_return_td_file(self, meta_file_path) -> str:
    with self.sftp.open(meta_file_path, "r") as meta_file:
      td_file = json.load(meta_file)["table_name"] + ".td"
    return td_file
