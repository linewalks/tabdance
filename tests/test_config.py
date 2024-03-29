import os
import pytest


class TestDecorator:
  error_message = "Not exists config file, First create and set a config file"

  def test_get_config(self, test_default_config):
    with pytest.raises(AssertionError) as error:
      test_default_config.get_config()
    assert str(error.value) == TestDecorator.error_message

  def test_print_config(self, test_default_config):
    with pytest.raises(AssertionError) as error:
      test_default_config.print_config()
    assert str(error.value) == TestDecorator.error_message

  def test_set_config(self, test_default_config):
    with pytest.raises(AssertionError) as error:
      test_default_config.set_config()
    assert str(error.value) == TestDecorator.error_message


class TestConfigData:
  sections_options = [
      ("PATH", ["local_repo_path", "remote_repo_path"]),
      ("REMOTE_INFO", ["remote_host_name", "remote_user_name", "remote_user_password"]),
      ("DB", ["sqlalchemy_database_uri", "schema", "table"])
  ]

  @pytest.mark.parametrize("section, options", sections_options)
  def test_read_default_config(self, test_default_config, section, options):
    default_config = test_default_config.read_default_config_for_inital_setup()
    self.check_section_and_options(default_config, section, options)

  @pytest.mark.parametrize("section, options", sections_options)
  def test_get_config(self, test_default_config, section, options):
    test_default_config.create_config_file()
    config = test_default_config.get_config()
    self.check_section_and_options(config, section, options)

  def check_section_and_options(self, config, section, options):
    assert config.has_section(section), f"Not exist section: {section}"
    for option in options:
      assert config.has_option(section, option), f"Not exists option: {option}"


def test_create_config_file(test_default_config):
  test_default_config.create_config_file()
  assert os.path.exists(test_default_config.config_file_path)


def test_print_config(test_default_config):
  test_default_config.create_config_file()
  test_default_config.print_config()


class TestAssertError:
  def test_updownload(self, test_default_config):
    test_default_config.create_config_file()
    with pytest.raises(AssertionError):
      test_default_config.assert_error_if_not_exists_config_info_for_updownload()
  
  def test_update(self, test_default_config):
    test_default_config.create_config_file()
    with pytest.raises(AssertionError):
      test_default_config.assert_error_if_not_exists_config_info_for_update()
