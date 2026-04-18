from allure_commons._allure import StepContext


def allure_step_context_with_params(title, params: dict | None = None):
    """Шаг allure с параметрами."""
    params = params or {}
    if callable(title):
        return StepContext(title=title.__name__, params=params)(title)
    else:
        return StepContext(title=title, params=params)
