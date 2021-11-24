import json
import os
import paramiko

from main.base import (
    get_args,
    get_config,
    callback_progressbar
)


class UpDownLoader:
  def __init__(self, args, config) -> None:
    """init"""
    self.args = args
    self.config = config
    self.local_repo_path = config["PATH"]["LOCAL_REPO_PATH"]
    self.remote_repo_path = config["PATH"]["REMOTE_REPO_PATH"]

  def connect_sftp(self) -> None:
    """SFTP Connect"""
    self.ssh_client = paramiko.SSHClient()
    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh_client.connect(
        hostname=self.config["REMOTE_INFO"]["REMOTE_HOST_NAME"],
        username=self.config["REMOTE_INFO"]["REMOTE_USER_NAME"],
        password=self.config["REMOTE_INFO"]["REMOTE_USER_PASSWORD"]
    )
    self.sftp = self.ssh_client.open_sftp()

  def disconnect_sftp(self) -> None:
    """SFTP Disconnect"""
    self.sftp.close()
    self.ssh_client.close()

  def get_files(self, exists_file_list) -> list:
    """Download/Upload 할 파일 추출하는 함수"""
    if self.args.file is not None:
      # -f: 입력한 파일
      files = []
      for file in self.args.file:
        csv_file = f"{file}.csv"
        meta_file = f"{file}.meta"

        if csv_file in exists_file_list:
          files.append(csv_file)
        else:
            raise Exception(f"Not exist file: '{csv_file}'")

        if meta_file in exists_file_list:
          files.append(meta_file)
        else:
            raise Exception(f"Not exist file: '{meta_file}'")

    elif self.args.all:
      # TODO: gitignore처럼 무시할 파일 리스트 or 단순히 첫번째 문자가 .인 경우는 모두 제외하는 방법 고려
      if ".DS_Store" in exists_file_list:
        exists_file_list.remove(".DS_Store")

      files = []
      for file in exists_file_list:
        if not file.endswith(".td"):
          files.append(file)

    return files

  def download(self) -> None:
    """File Download"""
    files = self.get_files(self.sftp.listdir(self.remote_repo_path))

    if not files:
      raise Exception("No files to download")

    # .meta 파일로부터 .td 파일명 추출
    td_files = []
    for file in files:
      if file.endswith(".meta"):
        with self.sftp.open(f"{self.remote_repo_path}/{file}", "r") as meta_file:
          table_name = json.load(meta_file)["table_name"] + ".td"

          if table_name not in self.sftp.listdir(self.remote_repo_path):
            raise Exception(f"Not exist file in REMOTE_REPO_PATH: '{table_name}'")

          if table_name not in td_files:
            td_files.append(table_name)

    files.extend(td_files)

    try:
      for file in files:
        local_path = os.path.join(self.local_repo_path, file)
        remote_path = f"{self.remote_repo_path}/{file}"
        print(file)
        self.sftp.get(remote_path, local_path, callback=callback_progressbar)
        print()

      print(f"Successfully Download: {files}")

    except Exception as e:
      raise Exception(f"Download Fail: {e}")

  def upload(self) -> None:
    """File Upload"""
    files = self.get_files(os.listdir(self.local_repo_path))

    if not files:
      raise Exception("No files to upload")

    # .meta 파일로부터 .td 파일명 추출
    td_files = []
    for file in files:
      if file.endswith(".meta"):
        with open(os.path.join(self.local_repo_path, file), "r") as meta_file:
          table_name = json.load(meta_file)["table_name"] + ".td"

          if table_name not in os.listdir(self.local_repo_path):
            raise Exception(f"Not exist file in LOCAL_REPO_PATH: '{table_name}'")

          if table_name not in td_files:
            td_files.append(table_name)

    files.extend(td_files)

    try:
      for file in files:
        local_path = os.path.join(self.local_repo_path, file)
        remote_path = f"{self.remote_repo_path}/{file}"
        print(file)
        self.sftp.put(local_path, remote_path, callback=callback_progressbar)
        print()

      print(f"Successfully Upload: {files}")

    except Exception as e:
      raise Exception(f"Upload Fail: {e}")


def main():
  """main"""
  args = get_args()
  config = get_config()

  updownloader = UpDownLoader(args, config)
  updownloader.connect_sftp()

  if args.load_type == "upload":
    updownloader.upload()

  elif args.load_type == "download":
    updownloader.download()

  updownloader.disconnect_sftp()
