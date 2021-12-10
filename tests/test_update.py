from tabdanc.config import TableDataSyncConfig
from tabdanc.update import DBTableBase, DBTableSync

import pytest


@pytest.fixture
def config():
  tabdanc_config = TableDataSyncConfig()
  tabdanc_config.assert_error_if_not_exists_config_info_for_updownload()
  return tabdanc_config.get_config()


def test_init_db(config):
  DBTableBase(config).init_db_object()


def test_table_sync(config):
  DBTableSync(config).sync_table()
