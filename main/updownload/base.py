import json
import paramiko

from main.base import callback_progressbar


class SSHConnector:
  def __init__(self, config) -> None:
    self.config = config
    self.ssh_client = None
    self.sftp = None

  def connect_sftp(self) -> None:
    self.ssh_client = paramiko.SSHClient()
    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh_client.connect(
        hostname=self.config["REMOTE_INFO"]["REMOTE_HOST_NAME"],
        username=self.config["REMOTE_INFO"]["REMOTE_USER_NAME"],
        password=self.config["REMOTE_INFO"]["REMOTE_USER_PASSWORD"]
    )
    self.sftp = self.ssh_client.open_sftp()

  def disconnect_sftp(self) -> None:
    self.sftp.close()
    self.ssh_client.close()

  def get_files(self, remote_path, local_path) -> None:
    self.sftp.get(remote_path, local_path, callback=callback_progressbar)

  def put_files(self, local_path, remote_path) -> None:
    self.sftp.put(local_path, remote_path, callback=callback_progressbar)

  def get_listdir(self, path) -> list:
    return self.sftp.listdir(path)

  def read_meta_file_and_return_td_file(self, meta_file_path) -> str:
    with self.sftp.open(meta_file_path, "r") as meta_file:
      td_file = json.load(meta_file)["table_name"] + ".td"
    return td_file


class UpDownLoaderBase:
  def __init__(self, args, config) -> None:
    self.args = args
    self.local_repo_path = config["PATH"]["LOCAL_REPO_PATH"]
    self.remote_repo_path = config["PATH"]["REMOTE_REPO_PATH"]
    self.ssh_connector = SSHConnector(config)

  def get_csv_meta_files_when_option_is_file(self, files_in_repo_path, files_input_by_user) -> list:
    files = []
    for file in files_input_by_user:
      csv_file = f"{file}.csv"
      meta_file = f"{file}.meta"

      if self.is_exists_file_in_file_list(csv_file, files_in_repo_path):
        files.append(csv_file)
      if self.is_exists_file_in_file_list(meta_file, files_in_repo_path):
        files.append(meta_file)

    return files

  def get_csv_meta_files_when_option_is_all(self, files_in_repo_path) -> list:
    files = []
    include_extensions = (".csv", ".meta")
    for file in files_in_repo_path:
      if file.endswith(include_extensions):
        files.append(file)
    return files

  def is_exists_file_in_file_list(self, file, file_list) -> bool:
    if file in file_list:
      return True
    raise Exception(f"No such file: {file}")

  def assert_error_if_empty_files(self, files) -> AssertionError:
    assert files != [], "No files to download"
