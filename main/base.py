import argparse
import math
import os
import sys

from configparser import ConfigParser


def get_config():
  """config 설정값 가져오기"""
  config = ConfigParser()
  config_path = os.path.join(os.getcwd(), "main", "dvm.cfg")
  config.read(config_path)
  return config


def get_args():
  """스크립트 옵션 값 가져오는 함수"""
  parser = argparse.ArgumentParser(description="DVM Script")
  parser = argparse.ArgumentParser(description="DVM Script", usage="dvm load_type [-h] [-f FILE [FILE ...]] [-a]")
  parser.add_argument("load_type", help="Choose 'upload' or 'download'")

  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("-f", "--file", nargs="+", help="Write file name you want to download or upload")
  group.add_argument("-a", "--all", action="store_true", help="All file download or upload")

  args = parser.parse_args()
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
