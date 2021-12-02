import argparse
import math
import os
import sys

from configparser import ConfigParser


def get_config():
  """config 설정값 가져오기"""
  config = ConfigParser()
  #TODO: 현재 개발까지는 CLUE-Uploader/ 위치에서만 tds 명령어 실행해야함.
  config_path = os.path.join(os.getcwd(), "main", "tds.cfg")
  config.read(config_path)
  return config


def get_args():
  """스크립트 옵션 값 가져오는 함수"""
  parser = argparse.ArgumentParser(description="Table Data Sync Script",
                                   usage="tds mode [-h] [-f FILE [FILE ...]] [-a]")
  parser.add_argument("mode", help="Choose 'upload' or 'download' or 'update'")

  group = parser.add_mutually_exclusive_group()
  group.add_argument("-f", "--file", nargs="+", help="Write file name you want to download or upload")
  group.add_argument("-a", "--all", action="store_true", help="All file download or upload")

  args = parser.parse_args()
  if args.mode == "update":
    if args.file is not None or args.all is True:
      parser.error("update mode can't have options'")

  return args


def convert_size(file_size) -> str:
  """file size 변환"""
  if file_size == 0:
      return "0B"
  byte_unit = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
  index = int(math.log(file_size, 1024))
  byte_size = math.pow(1024, index)
  size = round(file_size / byte_size, 2)
  return f"{size} {byte_unit[index]}"


def callback_progressbar(size, total_size) -> None:
  """진행바 출력"""
  bar_len = 100
  filled_len = math.ceil(bar_len * size / float(total_size))
  percent = math.ceil(100.0 * size / float(total_size))
  bar = "#" * filled_len + " " * (bar_len - filled_len)
  file_size = convert_size(total_size)
  sys.stdout.write(f"\r\t|{bar}| {percent}% {file_size}")
