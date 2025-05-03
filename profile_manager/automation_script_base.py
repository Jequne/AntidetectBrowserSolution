from playwright.async_api import Page

class AutomationScript:
    """Базовый класс для пользовательских скриптов автоматизации."""
    
    async def run(self, page: Page):
        """Метод, который пользователь должен переопределить."""
        raise NotImplementedError("Метод 'run' должен быть переопределен в пользовательском скрипте.")