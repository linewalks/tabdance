import pytest

from tabdanc.command import CommandParser


class TestUpDownLoad:
  @pytest.fixture(scope="class")
  def command_parser(self):
    command_parser = CommandParser()
    command_parser.add_updownload_command()
    return command_parser

  @pytest.mark.parametrize(
      "command_type, option, file_names",
      [
          ("upload", "-f", ["file1", "file2"]),
          ("download", "-f", ["file1"])
      ]
  )
  def test_updownload_file(self, command_parser, command_type, option, file_names):
    args = command_parser.parser.parse_args([command_type, option, *file_names])
    assert args.command == command_type
    assert args.all is False
    assert isinstance(args.file, list) and len(args.file) > 0

  @pytest.mark.parametrize(
      "command_type, option",
      [
          ("upload", "-a"),
          ("download", "-a")
      ]
  )
  def test_updownload_all(self, command_parser, command_type, option):
    args = command_parser.parser.parse_args([command_type, option])
    assert args.command == command_type
    assert args.all is True
    assert args.file is None


class TestUpdate:
  @pytest.fixture(scope="class")
  def command_parser(self):
    command_parser = CommandParser()
    command_parser.add_update_command()
    return command_parser

  def test_update(self, command_parser):
    command_type = "update"
    args = command_parser.parser.parse_args([command_type])
    assert args.command == command_type


class TestConfig:
  @pytest.fixture(scope="class")
  def command_parser(self):
    command_parser = CommandParser()
    command_parser.add_config_command()
    return command_parser

  def test_config_create(self, command_parser):
    command_type = "config"
    option = "--create"

    args = command_parser.parser.parse_args([command_type, option])
    assert args.command == command_type
    assert args.create is True
    assert args.list is False
    assert args.update is None

  def test_config_list(self, command_parser):
    command_type = "config"
    option = "--list"

    args = command_parser.parser.parse_args([command_type, option])
    assert args.command == command_type
    assert args.create is False
    assert args.list is True
    assert args.update is None

  @pytest.mark.parametrize(
      "command_type, option, section_option, value",
      [
          ("config", "--update", "PATH.local_repo_path", "~/Downloads"),
          ("config", "--update", "REMOTE_INFO.remote_host_name", "localhost"),
          ("config", "--update", "DB.TABLE", "test_table_name")
      ]
  )
  def test_config_update(self, command_parser, command_type, option, section_option, value):
    args = command_parser.parser.parse_args([command_type, option, section_option, value])
    assert args.command == command_type
    assert args.create is False
    assert args.list is False
    assert isinstance(args.update, list) and len(args.update) == 2
