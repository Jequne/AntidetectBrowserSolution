from pathlib import Path

def create_script(script_name: str, scripts_path: Path):
    """Создаёт новый скрипт автоматизации на основе шаблона."""
    script_path = scripts_path / f"{script_name}.py"

    if script_path.exists():
        return f"Error: Script '{script_name}' already exists."

    script_template = f"""from profile_manager.automation_script_base import AutomationScript
from playwright.async_api import Page

class {script_name.capitalize()}(AutomationScript):
    async def run(self, page: Page):
        \"\"\"Реализация пользовательской логики автоматизации.\"\"\"
        # TODO: Напишите вашу логику здесь
        await page.goto("https://example.com")
        print("Visited example.com")
"""

    try:
        script_path.write_text(script_template, encoding="utf-8")
        return f"Script '{script_name}' created successfully at {script_path}"
    except Exception as e:
        return f"Error creating script: {e}"