import os
import pytest


def test_decorator_check_config(test_config):
  error_message = "Not exists config file, First create and set a config file"

  with pytest.raises(AssertionError) as error:
    test_config.get_config()
  assert str(error.value) == error_message

  with pytest.raises(AssertionError) as error:
    test_config.print_config()
  assert str(error.value) == error_message

  with pytest.raises(AssertionError) as error:
    test_config.set_config()
  assert str(error.value) == error_message


def check_section_and_options(config):
  sections = ["PATH", "REMOTE_INFO", "DB"]
  options = [
      "local_repo_path",
      "remote_repo_path",
      "remote_host_name",
      "remote_user_name",
      "remote_user_password",
      "sqlalchemy_database_uri",
      "schema",
      "table"
  ]
  output_config_options = []

  for section in sections:
    assert config.has_section(section)
    for option in config.options(section):
      output_config_options.append(option)
  assert set(options) == set(output_config_options)


def test_read_default_config(test_config):
  default_config = test_config.read_default_config_for_inital_setup()
  check_section_and_options(default_config)


def test_create_config_file(test_config):
  test_config.create_config_file()
  assert os.path.exists(test_config.config_file_path)


def test_get_config(test_config):
  test_config.create_config_file()
  config = test_config.get_config()
  check_section_and_options(config)


def test_print_config(test_config):
  test_config.create_config_file()
  test_config.print_config()
