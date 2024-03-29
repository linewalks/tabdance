import os
import csv
import pytest

from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector

from tests.conftest import UploadTestFile
from tabdance.update import DBTableBase, DBTableSync


class TestInitDB:
  def test_init_db(self, test_tabdance_config):
    try:
      table_base = DBTableBase(test_tabdance_config)
      table_base.init_db_object()
      assert table_base.check_db_object("schema", table_base.schema) is None
      assert table_base.check_db_object("table", table_base.table) is None

    finally:
      drop_schema(test_tabdance_config)


class TestTableSync:
  @pytest.fixture(scope="class")
  def setup_table_sync(self, test_tabdance_config):
    test_file = UploadTestFile(test_tabdance_config)
    test_file.setup_csv_meta_td_files()

    table_base = DBTableBase(test_tabdance_config)
    table_base.init_db_object()
    yield test_file

    test_file.remove_test_files()
    drop_schema(test_tabdance_config)

  def test_table_sync(self, setup_table_sync, test_tabdance_config):
    table_sync = DBTableSync(test_tabdance_config)
    table_sync.sync_table()

    csv_files = [csv_file for csv_file in os.listdir(setup_table_sync.local_repo_path) if csv_file.endswith(".csv")]
    stored_file_names = [row["file_name"] for row in table_sync.get_tds_version()]
    for csv_file in csv_files:
      assert csv_file in stored_file_names

  def test_table_sync_after_csv_file_changes(self, setup_table_sync, test_tabdance_config):
    table_sync = DBTableSync(test_tabdance_config)
    table_sync.sync_table()
    prev_tabdance_versions = table_sync.get_tds_version()

    # NOTE: setup_csv_meta_td_files() 로 인해 3개의 파일을 생성했기 때문에 3개의 파일 변경 후 테스트
    for i in range(3):
      file_name = f"tabdance_test{i}.csv"
      pre_csv_file = os.path.join(setup_table_sync.local_repo_path, file_name)
      with open(pre_csv_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(setup_table_sync.csv_data)
        writer.writerow(setup_table_sync.csv_data)

    table_sync.sync_table()
    current_tabdance_versions = table_sync.get_tds_version()

    # get_tds_version()에서 sort & set을 하기 때문에 zip으로 사용 가능
    for prev_csv_hash, current_csv_hash in zip(prev_tabdance_versions, current_tabdance_versions):
      assert prev_csv_hash["csv_hash"] != current_csv_hash["csv_hash"]

  def test_table_sync_when_table_is_empty(self, setup_table_sync, test_tabdance_config):
    table_sync = DBTableSync(test_tabdance_config)
    table_sync.sync_table()
    prev_tabdance_versions = table_sync.get_tds_version()

    # NOTE: setup_csv_meta_td_files() 생성된 파일 내용으로 생성된 테이블이 empty 인 경우 update 대상이 되는지 테스트
    table_sync.sync_table()
    current_tabdance_versions = table_sync.get_tds_version()
    assert prev_tabdance_versions == current_tabdance_versions


def drop_schema(config):
  engine = create_engine(config.get("DB", "sqlalchemy_database_uri"))
  inspector = Inspector.from_engine(engine)

  schemas = inspector.get_schema_names()
  schema = config.get("DB", "schema")
  if schema in schemas:
    conn = engine.connect()
    for table in inspector.get_table_names(schema):
      conn.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
    conn.execute(f"DROP SCHEMA  IF EXISTS {schema};")
    conn.close()
