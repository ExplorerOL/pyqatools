from allure_commons import hookimpl, plugin_manager
from allure_commons.model2 import Status


class AllureStepStatusHandler:
    @hookimpl(tryfirst=True)
    def report_result(self, result):
        self.update_step_statuses(result.steps)

    def update_step_statuses(self, steps):
        for step in steps:
            # recursively update children first
            self.update_step_statuses(step.steps)
            child_statuses = {s.status for s in step.steps}

            if Status.FAILED in child_statuses:
                step.status = Status.FAILED


def configure_allure(config):
    def cleanup():
        name = plugin_manager.get_name(plugin)
        plugin_manager.unregister(name=name)

    plugin = AllureStepStatusHandler()
    plugin_manager.register(plugin)
    config.add_cleanup(cleanup)
