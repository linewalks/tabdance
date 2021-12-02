from main.base import get_args, get_config
from main.update import DBTableBase, DBTableSync
from main.updownload import UpDownLoader


def main():
  """main"""
  args = get_args()
  config = get_config()

  if args.mode == "update":
    DBTableBase(config).init_db_object()
    # TODO: LOCAL_REPO_PATH 관련해서 논의 후 주석 해제
    # DBTableSync(config).sync_table()

  else:
    updownloader = UpDownLoader(args, config)
    updownloader.connect_sftp()

    if args.mode == "upload":
      updownloader.upload()

    elif args.mode == "download":
      updownloader.download()

    updownloader.disconnect_sftp()
