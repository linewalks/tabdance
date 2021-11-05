import paramiko

from tqdm import tqdm

from base import (
    get_config,
    get_args,
    get_files
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
    print("No files to download")
  else:
    for file in tqdm(files):
      local_path = f"{local_repo_path}/{file}"
      remote_path = f"{remote_repo_path}/{file}"
      sftp.get(remote_path, local_path)

  sftp.close()
  ssh_client.close()
