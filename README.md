# PyQATools

A collection of useful tools for automated testing projects in Python.

## Table of Contents

- [Basic Information](#basic-information)
- [Stack Description](#stack-description)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Main Commands and Settings](#main-commands-and-settings)
- [Features](#features)
- [Links to Additional Information](#links-to-additional-information)

## Basic Information

**PyQATools** is a Python library designed to enhance automated testing workflows by providing reusable components for logging, reporting, assertions, retries, and integration with popular testing frameworks.

- **Version:** 1.0.0 (according to pyproject.toml)
- **Programming Language:** Python ≥3.10
- **License:** GNU GPL v3
- **Status:** Active development

## Stack Description

The project is built on the following technologies and libraries:

- **Python** – core language.
- **pytest** – framework for writing and running tests (integration via custom hooks and fixtures).
- **Allure-pytest** – integration with Allure for detailed test reporting.
- **tenacity** & **retrying** – libraries for implementing retry logic.
- **logging** – standard Python logging module with custom extensions.
- **uv** – modern Python package and project manager (used via uv.lock).
- **pre-commit** & **ruff** – code quality tools for linting and formatting.
- **assertpy** – fluent assertion library (optional).
- **pytest-xdist** – parallel test execution.
- **pytest-rerunfailures** – automatic retry of failed tests.
- **pytest-check** – soft assertions support.

PyQATools itself does not enforce strict dependencies; most integrations are optional and can be used as needed.

## Project Structure

```
pyqatools/
├── assertions/           # Assertion utilities (soft asserts, step assertions)
├── config/              # Configuration classes
├── exceptions/          # Custom exceptions
├── generators/          # Data generators (e.g., strings)
├── integrations/        # Integrations with external systems (TMS, etc.)
│   └── tms/
├── loggers/             # Logging framework with custom levels and decorators
│   └── logging_classes/
├── reporters/           # Reporting abstractions (Allure implementation)
│   └── allure/
├── retryers/            # Retry utilities (tenacity, retrying wrappers)
├── testrunner/          # pytest integration (hooks, base test template)
│   └── pytest/
└── waiters/             # Time‑waiting utilities
├── .pre-commit-config.yaml    # Конфигурация pre-commit и pre-push хуков git
├── CHANGELOG.md               # История изменений
├── pyproject.toml             # Зависимости и метаданные проекта
├── README.md                  # Документация проекта
├── ruff.toml                  # Конфигурация линтера Ruff
├── uv.lock                    # Lock-файл зависимостей uv
```

## Getting Started

### Prerequisites

- Python 3.10 or higher.
- Package manager `uv` (recommended) or `pip`.
- Git (for cloning the repository).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ExplorerOL/pyqatools.git
   cd pyqatools
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv sync
   ```
   or using pip:
   ```bash
   pip install -e .
   ```

3. (Optional) Install pre‑commit hooks:
   ```bash
   pre-commit install
   ```

### Basic Configuration

PyQATools uses a central configuration object `config_pyqatools` that can be customized with your own logger, reporter, retryer, and soft‑assert context manager.

Example:
```python
from pyqatools.config.config_pyqatools import config_pyqatools
from pyqatools.loggers.logger_logging import LoggerLogging
from pyqatools.reporters.allure.reporter_allure import ReporterAllure

config_pyqatools.logger = LoggerLogging(log_file_path=Path('./reports/log.txt'))
config_pyqatools.reporter = ReporterAllure()
```

## Main Commands and Settings

### Running Tests with PyQATools

When using PyQATools in your pytest project, you can leverage its fixtures and hooks automatically. Ensure `pyqatools` is installed and your `conftest.py` imports the necessary modules.

- **Enable Allure reporting:**
  ```bash
  pytest --alluredir ./reports/allure-results
  ```

- **Run tests in parallel:**
  ```bash
  pytest -n auto
  ```

- **Retry failed tests:**
  ```bash
  pytest --reruns 1 --reruns-delay 0
  ```

### Using Assert Steps

The `assert_step` context manager combines logging, reporting, and soft‑assert capabilities:

```python
from pyqatools.assertions.assert_step import assert_step

with assert_step("Verify user creation", soft=True):
    assert user.name == "John"
```

### Logging

PyQATools provides a rich logging facade with custom levels (STEP, FIXTURE, TEST, SUCCESS, etc.) and decorators for automatic logging of fixtures, steps, and methods.

```python
from pyqatools.loggers.logger_logging import LoggerLogging

logger = LoggerLogging(log_file_path=Path('./reports/log.txt'))
logger.step("Starting test scenario")
```

### Reporting (Allure)

The Allure reporter attaches steps, parameters, and attachments to your test report.

```python
from pyqatools.reporters.allure.reporter_allure import ReporterAllure

reporter = ReporterAllure()
with reporter.step("Login"):
    # ... action
    reporter.attach_text("Login successful", name="Info")
```

### Retry Mechanisms

Retryers wrap any callable with configurable retry logic (using tenacity or retrying).

```python
from pyqatools.retryers.retryer_tenacity import RetryerTenacity

retryer = RetryerTenacity(stop_after_attempt=3, wait_fixed=1.0)
result = retryer.execute(lambda: unreliable_function())
```

## Features

- **Unified Test Context:** Central configuration for logger, reporter, and retryer.
- **Step‑wise Assertions:** Combine assertions with logging and reporting in a single step.
- **Soft Asserts:** Use `assert_soft` to continue test execution after a failure.
- **Extensible Logging:** Custom log levels, decorators for fixtures/steps/methods, and parallel‑run support (xdist).
- **Allure Integration:** Automatic step nesting, parameter attachment, and environment file generation.
- **Retry Utilities:** Ready‑to‑use retry wrappers based on tenacity and retrying.
- **Data Generators:** Helpers for generating test data (e.g., random strings).
- **Time Waiters:** Utilities for smart polling and waiting.
- **TMS Integration:** Support for TestIT and other test management systems.
- **pytest Hooks:** Seamless integration with pytest lifecycle (setup, teardown, reporting).

## Links to Additional Information

- [PyQATools GitHub Repository](https://github.com/ExplorerOL/pyqatools)
- [Official pytest Documentation](https://docs.pytest.org/)
- [Allure Framework Documentation](https://docs.qameta.io/allure/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [uv Documentation](https://docs.astral.sh/uv/)

---

*PyQATools is developed to promote best practices in test automation and to provide a solid foundation for building reliable, maintainable test suites.*