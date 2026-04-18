import datetime
import inspect
from functools import wraps
from pathlib import Path
from typing import Callable, Generator, Iterable, ParamSpec, TypeVar

import allure

from pyqatools.reporters.allure.reporter_allure_step_context import (
    allure_step_context_with_params,
)
from pyqatools.reporters.reporter_protocol import (
    ReporterProtocol,
)

PT = ParamSpec('PT')  # param type
YT = TypeVar('YT')  # yield type
ST = TypeVar('ST')  # send type
RT = TypeVar('RT')  # return type


allure.step = allure_step_context_with_params


class ReporterAllure(ReporterProtocol):
    __ENV_FILE_NAME = 'environment.properties'
    __report_all_methods = False
    __step_name_prefix = 'Step: '
    __static_step_name_prefix = 'Static step: '
    __method_name_prefix = 'Method: '
    __static_method_name_prefix = 'Static method: '
    # Заголовок отчета
    report_title: str = 'Report title'
    # Информация для добавления в отчет
    aut_info_for_report_dict: dict = {}

    @property
    def report_methods(self) -> bool:
        return self.__report_all_methods

    @report_methods.setter
    def report_methods(self, new_value: bool) -> None:
        self.__report_all_methods = new_value

    @property
    def is_current_stage_passed(self) -> bool:
        return self.__IS_CURRENT_STAGE_PASSED

    @is_current_stage_passed.setter
    def is_current_stage_passed(self, value: bool) -> None:
        self.__IS_CURRENT_STAGE_PASSED = value

    def create_file_with_env_info(self, allure_results_path_str: str):
        if Path(allure_results_path_str).exists():
            env_file = Path(allure_results_path_str) / self.__ENV_FILE_NAME
            with env_file.open('w', encoding='utf-8') as file:
                file.write(f'Date = {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n')
                for key, value in self.aut_info_for_report_dict.items():
                    file.write(f'{str(key).replace(" ", "_")} = {value}\n')

    def configure_step_prefixes(
        self,
        step_name_prefix: str | None = None,
        static_step_name_prefix: str | None = None,
        method_name_prefix: str | None = None,
        static_method_name_prefix: str | None = None,
    ) -> None:
        if step_name_prefix is not None:
            self.__step_name_prefix = step_name_prefix
        if static_step_name_prefix is not None:
            self.__static_step_name_prefix = static_step_name_prefix
        if method_name_prefix is not None:
            self.__method_name_prefix = method_name_prefix
        if static_method_name_prefix is not None:
            self.__static_method_name_prefix = static_method_name_prefix

    def step(self, name: str, params: dict | None = None):
        return allure.step(name, params)

    def attach_text(self, text: str, name: str = 'Info') -> None:
        # по непонятным причинам может возникать KeyError у allure - ее игнорировать
        try:
            allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)
        except KeyError:
            pass

    def attach_image(self, source, name) -> None:
        allure.attach(source, name=name, attachment_type=allure.attachment_type.PNG)

    def attach_zip(self, source, name) -> None:
        allure.attach(source, name=name, extension='zip')

    def attach_link(self, name: str, url: str) -> None:
        allure.attach(url, name=name, attachment_type=allure.attachment_type.URI_LIST)

    def attach_tms_link(self, name: str, url: str) -> None:
        allure.dynamic.testcase(name=name, url=url)

    def _step_wrapper(self, func: Callable[PT, RT], name_prefix: str = 'Step: ') -> Callable[PT, RT]:
        __tracebackhide__ = True

        @wraps(func)
        def wrapper(*args, **kwargs):
            __tracebackhide__ = True
            args_dict_attachment = {'args': repr(args[1:])} if args[1:] else {}
            kwargs_dict_attachments = {key: repr(value) for key, value in kwargs.items()}
            all_params_dict_attachment = {
                **args_dict_attachment,
                **kwargs_dict_attachments,
            }
            step_self = args[0]
            first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''
            with self.step(
                name=f'{name_prefix}{first_line_from_docstring} | {step_self.__module__} -> {step_self.__class__.__name__} -> {func.__name__}',  # noqa E501
                params=all_params_dict_attachment,
            ):
                result = func(*args, **kwargs)
                if result is not None and result is not step_self:
                    self.attach_text(name='Result', text=f'{result!r}')
            return result

        return wrapper

    def report_step(self, func: Callable[PT, RT]) -> Callable[PT, RT]:
        """Декоратор репортера для шагов."""
        return self._step_wrapper(func=func, name_prefix=self.__step_name_prefix)

    def report_method(self, func: Callable[PT, RT]) -> Callable[PT, RT]:
        """Декоратор репортера для методов."""
        return self._step_wrapper(func=func, name_prefix=self.__method_name_prefix)

    def _static_step_wrapper(self, func: Callable[PT, RT], name_prefix: str = 'Static step: ') -> Callable[PT, RT]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            __tracebackhide__ = True
            first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''
            # для статических методов пришлось реализовывать кастомную логику добавления параметров
            # использование шага аллюр как декоратора вызывает ошибку TypeError: unsupported callable модуля inspect.py
            args_dict_attachment = {'args': repr(args)} if args else {}
            kwargs_dict_attachments = {key: repr(value) for key, value in kwargs.items()}
            all_params_dict_attachment = {
                **args_dict_attachment,
                **kwargs_dict_attachments,
            }
            with self.step(
                name=f'{name_prefix}{first_line_from_docstring} | {func.__module__} -> {func.__class__.__name__} -> {func.__name__}',  # noqa E501
                params=all_params_dict_attachment,
            ):
                result = func(*args, **kwargs)
                # При использовании статического декоратора при запуске тестов возникает ошибка KeyError: None
                # Однако если ее игнорировать, то все работает. Причина не ясна
                try:
                    if result is not None:
                        self.attach_text(name='Result', text=f'{result!r}')
                except KeyError:
                    pass
            return result

        return wrapper

    def report_static_step(self, func: Callable[PT, RT]) -> Callable[PT, RT]:
        """Декоратор репортера для статических шагов."""
        return self._static_step_wrapper(func=func, name_prefix=self.__static_step_name_prefix)

    def report_static_method(self, func: Callable[PT, RT]) -> Callable[PT, RT]:
        """Декоратор репортера для статических методов."""
        return self._static_step_wrapper(func=func, name_prefix=self.__static_method_name_prefix)

    def report_fixture(
        self,
        func: Callable[PT, RT] | Generator[YT, ST, RT],
    ) -> Callable[PT, RT] | Generator[YT, ST, RT]:
        """Логгирование фикстуры."""
        # Для логирования фикстуры-генератора сделана специальная обертка, иначе фикстура не выполняется

        @wraps(func)  # type: ignore
        def func_wrapper(*args, **kwargs):
            __tracebackhide__ = True
            first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''
            self.attach_text(
                name=first_line_from_docstring,
                text=f'{func.__module__} -> {func.__class__.__name__} -> {func.__name__}',
            )
            if args or kwargs:
                self.attach_text(name='Args', text=f'args={repr(args)}, kwargs={repr(kwargs)}')

            result = func(*args, **kwargs)  # type: ignore
            if result is not None:
                self.attach_text(
                    name='Result',
                    text=f'{result!r}',
                )
            return result

        @wraps(func)  # type: ignore
        def gen_wrapper(*args, **kwargs):
            __tracebackhide__ = True
            first_line_from_docstring = str(func.__doc__).split('\n')[0] if func.__doc__ else ''
            self.attach_text(
                name=first_line_from_docstring,
                text=f'{func.__module__} -> {func.__class__.__name__} -> {func.__name__}',
            )
            if args or kwargs:
                self.attach_text(name='Args', text=f'args={repr(args)}, kwargs={repr(kwargs)}')

            for result in func(*args, **kwargs):  # type: ignore
                if result is not None:
                    self.attach_text(
                        name='Result',
                        text=f'{result!r}',
                    )
                yield result

        return gen_wrapper if inspect.isgeneratorfunction(func) else func_wrapper

    def set_test_description(self, test_description: str) -> None:
        allure.description(test_description=test_description)

    def set_parent_suite(self, parent_suite_name: str) -> None:
        return allure.dynamic.parent_suite(parent_suite_name=parent_suite_name)

    def set_suite(self, suite_name: str) -> None:
        return allure.dynamic.suite(suite_name=suite_name)

    def set_feature(self, features_names: Iterable[str]) -> None:
        return allure.dynamic.feature(features_names)

    def set_story(self, stories_names: Iterable[str]) -> None:
        return allure.dynamic.story(stories_names)

    def set_title(self, title: str) -> None:
        return allure.dynamic.title(test_title=title)

    def set_sub_suite(self, sub_suite_name: str) -> None:
        return allure.dynamic.sub_suite(sub_suite_name=sub_suite_name)
