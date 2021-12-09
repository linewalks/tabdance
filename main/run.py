from main.command import CommandParser
from main.config import TDSConfig
from main.update import DBTableBase, DBTableSync
from main.updownload.download import Downloader
from main.updownload.upload import Uploader


def main():
  args = CommandParser().get_args()
  if args.command == "config":
    run_tds_config(args)
  elif args.command == "download":
    run_tds_download(args)
  elif args.command == "upload":
    run_tds_upload(args)
  elif args.command == "update":
    run_tds_update()


def run_tds_config(args):
  tds_config = TDSConfig()
  if args.create:
    tds_config.create_config_file()
  elif args.list:
    tds_config.print_config()
  elif args.update:
    section = args.update[0].split(".")[0]
    option = args.update[0].split(".")[1]
    value = args.update[1]
    tds_config.set_config(section, option, value)


def run_tds_download(args):
  tds_config = TDSConfig()
  tds_config.assert_error_if_not_exists_config_info_for_updownload()
  config = tds_config.get_config()

  downloader = Downloader(args, config)
  downloader.ssh_connector.connect_sftp()
  downloader.download()
  downloader.ssh_connector.disconnect_sftp()


def run_tds_upload(args):
  tds_config = TDSConfig()
  tds_config.assert_error_if_not_exists_config_info_for_updownload()
  config = tds_config.get_config()

  uploader = Uploader(args, config)
  uploader.ssh_connector.connect_sftp()
  uploader.upload()
  uploader.ssh_connector.disconnect_sftp()


def run_tds_update():
  tds_config = TDSConfig()
  tds_config.assert_error_if_not_exists_config_info_for_update()
  config = tds_config.get_config()
  DBTableBase(config).init_db_object()
  DBTableSync(config).sync_table()
