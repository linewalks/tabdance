import argparse
import os

from configparser import ConfigParser


def get_config():
  """config 설정값 가져오기"""
  config = ConfigParser()
  config_path = os.path.join(os.getcwd(), "dvm.cfg")
  config.read(config_path)
  return config


def get_args():
  """스크립트 옵션 값 가져오는 함수"""
  parser = argparse.ArgumentParser(description="DVM Script")
  parser.add_argument("-f", "--file", nargs="+", help="write file name you want to download or upload")
  parser.add_argument("-a", "--all", nargs="?", default=False, help="all file download or upload")
  args = parser.parse_args()

  if args.file is None and args.all is False:
    parser.error("You must select at least one of options '-f' or '-a'")
  elif args.file is not None and args.all is not False:
    parser.error("You must choose only one of options '-f' or '-a'")

  return args


def get_files(args, exists_file_list) -> list:
  """Download/Upload 할 파일 추출하는 함수"""
  args = get_args()
  if args.file is not None:
    # -f: 입력한 파일
    files = []
    for file in args.file:
      csv_file = f"{file}.csv"
      meta_file = f"{file}.meta"

      if csv_file in exists_file_list:
         files.append(csv_file)
      else:
          print(f"Not Exist '{csv_file}'")

      if meta_file in exists_file_list:
        files.append(meta_file)
      else:
          print(f"Not Exist '{meta_file}'")

  elif args.all is None:
    # -a: 확장자 구분없이 모든 파일
    # TODO: gitignore처럼 무시할 파일 리스트 or 단순히 첫번째 문자가 .인 경우는 모두 제외하는 방법 고려
    if ".DS_Store" in exists_file_list:
      exists_file_list.remove(".DS_Store")  
    files = exists_file_list

  elif args.all is not None and args.all is not False:
    # -a: 특정 확장자의 모든 파일
    files = [file for file in exists_file_list if file.endswith(args.all)]

  return files
