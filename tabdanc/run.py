from tabdanc.command import CommandParser
from tabdanc.config import TableDataSyncConfig
from tabdanc.update import DBTableBase, DBTableSync
from tabdanc.updownload.download import Downloader
from tabdanc.updownload.upload import Uploader


def main():
  args = CommandParser().get_args()
  if args.command == "config":
    run_tabdanc_config(args)
  elif args.command == "download":
    run_tabdanc_download(args)
  elif args.command == "upload":
    run_tabdanc_upload(args)
  elif args.command == "update":
    run_tabdanc_update()


def run_tabdanc_config(args):
  tabdanc_config = TableDataSyncConfig()
  if args.create:
    tabdanc_config.create_config_file()
  elif args.list:
    tabdanc_config.print_config()
  elif args.update:
    section = args.update[0].split(".")[0]
    option = args.update[0].split(".")[1]
    value = args.update[1]
    tabdanc_config.set_config(section, option, value)


def run_tabdanc_download(args):
  tabdanc_config = TableDataSyncConfig()
  tabdanc_config.assert_error_if_not_exists_config_info_for_updownload()
  config = tabdanc_config.get_config()

  downloader = Downloader(args, config)
  downloader.ssh_connector.connect_sftp()
  downloader.download()
  downloader.ssh_connector.disconnect_sftp()


def run_tabdanc_upload(args):
  tabdanc_config = TableDataSyncConfig()
  tabdanc_config.assert_error_if_not_exists_config_info_for_updownload()
  config = tabdanc_config.get_config()

  uploader = Uploader(args, config)
  uploader.ssh_connector.connect_sftp()
  uploader.upload()
  uploader.ssh_connector.disconnect_sftp()


def run_tabdanc_update():
  tabdanc_config = TableDataSyncConfig()
  tabdanc_config.assert_error_if_not_exists_config_info_for_update()
  config = tabdanc_config.get_config()
  DBTableBase(config).init_db_object()
  DBTableSync(config).sync_table()
