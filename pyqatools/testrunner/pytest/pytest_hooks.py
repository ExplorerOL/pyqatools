# from pyqatools.reporters.allure.reporter_allure import allure
import pytest

# from support.loggers.testrun_logger import testrun_logger
from _pytest.logging import _remove_ansi_escape_sequences

from pyqatools.config.config_pyqatools import config_pyqatools
from pyqatools.exceptions.general_exceptions import UnexpectedValueError
from pyqatools.reporters.allure.reporter_allure_step_status_handler import (
    configure_allure,
)


def pytest_runtest_logstart(nodeid, location):
    """Хук перед запуском setup теста."""
    config_pyqatools.logger.test(f'>>>>> Начало теста: {nodeid}:{location[1]} >>>>>')


def pytest_runtest_logfinish(nodeid, location):
    """Хук после запуска teardown теста."""
    config_pyqatools.logger.test(f'##### Конец теста: {nodeid}:{location[1]} #####')


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    """Хук перед вызовом фикстуры перед выполнением теста."""
    if not hasattr(request.config, '_decorated_fixtures'):
        request.config._decorated_fixtures = set()

    if fixturedef.func not in request.config._decorated_fixtures:
        if config_pyqatools.reporter is not None:
            fixturedef.func = config_pyqatools.reporter.report_fixture(fixturedef.func)
        if config_pyqatools.logger is not None:
            fixturedef.func = config_pyqatools.logger.log_fixture(fixturedef.func)

        request.config._decorated_fixtures.add(fixturedef.func)

    yield


def pytest_exception_interact(report):
    """Хук обработки исключений pytest."""
    if config_pyqatools.logger is not None:
        backtrace = getattr(report, 'longreprtext', None)
        if backtrace is not None:
            msg = f'Ошибка при выполнении теста:\n{report.longreprtext}'
            msg_without_ansi_symbols = _remove_ansi_escape_sequences(msg)

            config_pyqatools.logger.debug(msg=msg_without_ansi_symbols)


def pytest_runtest_teardown(item):
    """Хук завершения теста."""
    docstring = item.function.__doc__

    if not docstring:
        raise UnexpectedValueError(f'No docstring found for {item.function.__name__}')
    test_path = item.location[0]
    docstring_lines = docstring.split('\n')
    first_line_from_docstring = docstring_lines[0].strip()
    other_lines_from_docstring = docstring_lines[2:]
    test_path_parts = str(test_path).removesuffix('.py').replace('\\', '/').split('/')

    test_class = getattr(item, 'cls', '')
    test_class_name = getattr(test_class, '__name__', '')

    if not test_class_name:
        raise UnexpectedValueError(f'No class name found for {item.function}')

    test_title = first_line_from_docstring
    param_names = []
    callspec = getattr(item, 'callspec', None)
    if callspec:
        param_names = callspec.params
        if param_names:
            params_str = [f'{k}={v}' for k, v in param_names.items()]
            test_title = f'{test_title} {params_str}'

    test_description = '\n'.join(other_lines_from_docstring)
    test_feature_name = test_class_name.removeprefix('Test').removesuffix('Negative')
    test_story_name = 'Negative' if item.function.__name__.startswith('test_try_') else 'Positive'
    test_suite_name = f'{str(test_path_parts[-1]).capitalize()}'

    config_pyqatools.reporter.set_title(test_title)
    config_pyqatools.reporter.set_description(test_description)
    config_pyqatools.reporter.set_feature(test_feature_name)
    config_pyqatools.reporter.set_story(test_story_name)
    config_pyqatools.reporter.set_suite(test_suite_name)


def pytest_runtest_logreport(report):
    if config_pyqatools.reporter:
        log_lines = []
        if report.failed:
            for section in report.sections:
                section_header = section[0]
                section_content = section[1]
                log_lines.append(section_header)
                log_lines.append(section_content)
                log_lines.append('\n')
            logs_text = _remove_ansi_escape_sequences('\n'.join(log_lines))
            config_pyqatools.reporter.attach_text(text=logs_text, name='Test logs')


def pytest_configure(config):
    configure_allure(config)
