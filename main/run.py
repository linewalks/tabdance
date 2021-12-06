from main.base import get_config
from main.command import CommandParser
from main.update import DBTableBase, DBTableSync
from main.updownload import UpDownLoader


def main():
  """main"""
  args = CommandParser().get_args()
  config = get_config()

  # tds upload or download 실행
  if args.command == "upload" or args.command == "download":
    updownloader = UpDownLoader(args, config)
    updownloader.connect_sftp()

    if args.command == "upload":
      updownloader.upload()
    elif args.command == "download":
      updownloader.download()

    updownloader.disconnect_sftp()

  # tds update 실행
  elif args.command == "update":
    DBTableBase(config).init_db_object()
    DBTableSync(config).sync_table()

  # tds config 실행
  elif args.command == "config":
    # TODO: config 명령어 실행시 CRUD 기능 개발
    pass
