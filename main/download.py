import json
import paramiko

from base import (
    get_config,
    get_args,
    get_files,
    callback_progressbar
)


if __name__ == "__main__":
  config = get_config()
  host_name = config["REMOTE_INFO"]["REMOTE_HOST_NAME"]
  user_name = config["REMOTE_INFO"]["REMOTE_USER_NAME"]
  user_password = config["REMOTE_INFO"]["REMOTE_USER_PASSWORD"]
  local_repo_path = config["PATH"]["LOCAL_REPO_PATH"]
  remote_repo_path = config["PATH"]["REMOTE_REPO_PATH"]

  ssh_client = paramiko.SSHClient()
  ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh_client.connect(host_name, username=user_name, password=user_password)
  sftp = ssh_client.open_sftp()

  args = get_args()
  files = get_files(args, sftp.listdir(remote_repo_path))

  if not files:
    raise Exception("No files to download")

  # .meta 파일로부터 .td 파일명 추출
  td_files = []
  for file in files:
    if file.endswith(".meta"):
      with sftp.open(f"{remote_repo_path}/{file}", "r") as meta_file:
        table_name = json.load(meta_file)["table_name"] + ".td"

        if table_name not in sftp.listdir(remote_repo_path):
          raise Exception(f"Not exist file in REMOTE_REPO_PATH: '{table_name}'")

        if table_name not in td_files:
          td_files.append(table_name)

  files.extend(td_files)

  # file download
  try:
    for file in files:
      local_path = f"{local_repo_path}/{file}"
      remote_path = f"{remote_repo_path}/{file}"
      print(file)
      sftp.get(remote_path, local_path, callback=callback_progressbar)
      print()

    print(f"Successfully Download: {files}")

  except Exception as e:
    raise Exception(f"Download Fail: {e}")

  sftp.close()
  ssh_client.close()
