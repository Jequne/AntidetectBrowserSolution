from profile_manager.automation_script_base import AutomationScript
from playwright.async_api import Page

class Script_example(AutomationScript):
    async def run(self, page: Page):
        """Реализация пользовательской логики автоматизации."""
        # TODO: Напишите вашу логику здесь
        await page.goto("https://example.com")
        print("Visited example.com")
