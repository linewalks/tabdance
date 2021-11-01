import argparse
import os
import paramiko

from configparser import ConfigParser
from tqdm import tqdm


def get_config():
  """config 설정값 가져오기"""
  config = ConfigParser()
  config_path = os.path.join(os.getcwd(), "dvm.cfg")
  config.read(config_path)
  return config


def get_args():
  """스크립트 옵션 값 가져오는 함수"""
  parser = argparse.ArgumentParser(description="DVM Script")
  parser.add_argument("-u", "--upload", action="store_true", help="upload file")
  parser.add_argument("-d", "--download", action="store_true", help="download file")
  parser.add_argument("-f", "--file", nargs="+", help="write file name you want to download or upload")
  parser.add_argument("-a", "--all", action="store_true", help="all file download or upload")
  args = parser.parse_args()

  if args.upload is False and args.download is False:
    parser.error("You must select at least one of options '--upload' or '--download'")
  elif args.upload is True and args.download is True:
    parser.error("You must choose only one of option '--upload' or '--download'")

  if args.file is None and args.all is False:
    parser.error("You must select at least one of options '-f' or '-a'")
  elif args.file is not None and args.all is True:
    parser.error("You must choose only one of options '-f' or '-a'")

  return args


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
  if args.all is True:
    if args.upload is True:
      files = os.listdir(local_repo_path)
    elif args.download is True:
      files = sftp.listdir(remote_repo_path)
  elif args.file is not None:
    files = []
    for file in args.file:
      #TODO: "-f file_name" 처럼 확장자 없이 입력 받을 때 자동으로 그에 관련된 필요한 파일 up/down 되도록 (.meta, .csv)
      files.append(file)

  if not files:
    raise Exception("No files to download or upload")

  for file in tqdm(files):
    local_path = f"{local_repo_path}/{file}"
    remote_path = f"{remote_repo_path}/{file}"
    if args.upload is True:
      sftp.put(local_path, remote_path)
    elif args.download is True:
      sftp.get(remote_path, local_path)

  sftp.close()
  ssh_client.close()
