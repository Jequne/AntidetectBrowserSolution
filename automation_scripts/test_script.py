from profile_manager.automation_script_base import AutomationScript
from playwright.async_api import Page

class MyAutomationScript(AutomationScript):
    async def run(self, page: Page):
        await page.goto("https://youtube.com")
        title = await page.title()
        print(f"Page title: {title}")