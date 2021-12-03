from main.base import get_config
from main.update import DBTableBase, DBTableSync

import pytest


@pytest.fixture
def config():
  return get_config()


def test_init_db(config):
  DBTableBase(config).init_db_object()


def test_table_sync(config):
  DBTableSync(config).sync_table()
