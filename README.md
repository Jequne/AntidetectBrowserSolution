# Antidetect Browser Solution

Antidetect Browser Solution — это проект для управления профилями браузеров и автоматизации действий с использованием Playwright. Он позволяет создавать профили, запускать автоматизацию через пользовательские скрипты и управлять прокси.

---

## 📂 Структура проекта

- **`profile_manager/`** — Основная логика управления профилями и автоматизацией.
  - `automation_manager.py` — Класс `AutomationManager` для управления профилями и выполнения автоматизации.
  - `automation_script_base.py` — Базовый класс `AutomationScript` для создания пользовательских скриптов.
- **`automation_scripts/`** — Папка для пользовательских скриптов автоматизации.
- **`user_data/`** — Данные профилей и отчёты об автоматизации (игнорируются в `.gitignore`).
- **`extensions/`** — Папка для расширений браузера (игнорируется в `.gitignore`).

---

## 🚀 Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-repo/antidetect-browser-solution.git
   cd antidetect-browser-solution


2. Установите виртуальное окружение:
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate

3. Установите зависимости:
    pip install -r requirements.txte



🛠️ Основные команды CLI
После запуска проекта через cli.py доступны следующие команды:

1. Создание профилей
Создаёт новые профили браузера.
Запросит количество профилей и путь к файлу с прокси (опционально).
2. Запуск автоматизации
Запускает автоматизацию для заданного диапазона профилей.
Запросит имя пользовательского скрипта и диапазон профилей.
3. Ручной запуск профиля
Позволяет вручную запустить любой профиль из списка доступных.
4. Обновление прокси для профиля
Позволяет обновить или удалить прокси для существующего профиля.
5. Создание нового скрипта автоматизации
Автоматически создаёт файл с шаблоном для нового пользовательского скрипта.


📜 Как создать пользовательский скрипт?

Выберите команду Create New Automation Script в CLI.
Введите имя нового скрипта (например, my_script).
В папке automation_scripts/ будет создан файл my_script.py с базовым шаблоном:

from profile_manager.automation_script_base import AutomationScript
from playwright.async_api import Page

class My_script(AutomationScript):
    async def run(self, page: Page):
        """Реализация пользовательской логики автоматизации."""
        # TODO: Напишите вашу логику здесь
        await page.goto("https://example.com")
        print("Visited example.com")

Добавьте свою логику в метод run.


📊 Отчёты об автоматизации
После выполнения автоматизации создаётся файл отчёта automation_report.txt в папке user_data/. Пример содержимого:

Automation Report
========================================
Successful Profiles:
- Profile_4
- Profile_5
- Profile_6

Failed Profiles:
- Profile_1: Метод 'run' должен быть переопределен в пользовательском скрипте.: AutomationScript
----------------------------------------