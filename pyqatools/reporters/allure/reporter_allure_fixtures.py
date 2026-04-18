import pytest

from pyqatools.config.config_pyqatools import config_pyqatools


@pytest.fixture(scope='session', autouse=True)
def generate_allure_reports_env_data_file(pytestconfig):
    """Фикстура генерации данных оркужения для репортера Allure"""
    # обработка опции --alluredir создание файла с данными окружения для allure
    allure_dir_path_str = pytestconfig.getoption('--alluredir')
    if allure_dir_path_str is not None and config_pyqatools.reporter:
        config_pyqatools.reporter.create_file_with_env_info(
            allure_results_path_str=allure_dir_path_str,
        )
