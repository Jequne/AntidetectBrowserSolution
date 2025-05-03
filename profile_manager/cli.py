import asyncio
import logging
from aioconsole import ainput

from profile_manager.manager import ProfileManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def run_profile_manager():
    manager = ProfileManager()

import asyncio
import logging
from aioconsole import ainput
from pathlib import Path

from profile_manager.automation_manager import AutomationManager
from profile_manager.automation_script_base import AutomationScript
from helpers.create_script_utils import create_script

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AUTOMATION_SCRIPTS_PATH = Path(__file__).parent.parent / "automation_scripts"


async def run_profile_manager():
    manager = AutomationManager(automate_start=1, automate_end=1)

    
    async def handle_create_script():
        """Создаёт новый скрипт автоматизации."""
        script_name = await ainput('Enter the name of the new automation script: ')
        result = create_script(script_name, AUTOMATION_SCRIPTS_PATH)
        print(result)
        
    
    def get_available_scripts():
        """Возвращает список доступных скриптов автоматизации."""
        if not AUTOMATION_SCRIPTS_PATH.exists():
            print(
                f"\n[INFO] The folder for automation scripts does not exist.\n"
                f"Please create the folder at: {AUTOMATION_SCRIPTS_PATH}\n"
                f"Then add your Python scripts (*.py) for automation into this folder.\n"
            )
            return []

        scripts = [
            f.stem for f in AUTOMATION_SCRIPTS_PATH.glob("*.py")
            if f.is_file() and f.stem != "__init__"
        ]

        if not scripts:
            print(
                f"\n[INFO] No automation scripts found in the folder: {AUTOMATION_SCRIPTS_PATH}\n"
                f"Add your Python scripts (*.py) for automation into this folder.\n"
            )

        return scripts
    
    
    async def handle_create_profiles():
        """Создание профилей."""
        count = int(await ainput('Enter the number of profiles to create: '))
        proxy_file_path = await ainput('Enter the path to the proxy file (or leave empty): ')
        proxy_file = Path(proxy_file_path) if proxy_file_path else None

        try:
            await manager.create_profiles(count, proxy_file)
            print(f'{count} profiles created successfully!')
        except Exception as e:
            logger.exception(f'Error creating profiles: {e}')

    async def handle_run_automation():
        """Запуск автоматизации для диапазона профилей."""
        scripts = get_available_scripts()
        if not scripts:
            return
        
        print("\nAvailable automation scripts:")
        for script in scripts:
            print(f"- {script}")
        
        script_name = await ainput('Enter the automation script name: ')
        if script_name not in scripts:
            print(f"Error: Script '{script_name}' not found.")
            return

        start = int(await ainput('Enter the start profile index: '))
        end = int(await ainput('Enter the end profile index: '))

        try:
            # Импортируем скрипт автоматизации по имени
            script_module = __import__(f"automation_scripts.{script_name}", fromlist=[""])
            automation_script = script_module.MyAutomationScript()

            # Устанавливаем диапазон профилей
            manager.automate_start = start
            manager.automate_end = end

            # Запускаем автоматизацию через do_automation_for_profiles
            await manager.do_automation_for_profiles(
                                                    automation_script
                                                        )
            print("Automation completed successfully!")
        except Exception as e:
            logger.exception(f'Error running automation: {e}')

    
    async def handle_launch_profile():
        """Ручной запуск профиля."""
        if not manager.profiles:
            print("No profiles available. Create profiles first.")
            return

        print('\nAvailable profiles:')
        for name in manager.get_profile_names():
            print(f"- {name}")

        profile_name = await ainput('Enter profile name to launch: ')
        try:
            await manager.launch_profile(profile_name)
            print(f'Profile "{profile_name}" launched successfully!')
        except Exception as e:
            logger.exception(f'Error launching profile "{profile_name}": {e}')

    async def handle_update_profile():
        """Обновление прокси для профиля."""
        if not manager.profiles:
            print("No profiles available. Create profiles first.")
            return

        print('\nAvailable profiles:')
        for name in manager.get_profile_names():
            print(f"- {name}")

        profile_name = await ainput('Enter the profile name to update: ')
        proxy_str = await ainput(
            'Enter new proxy (protocol:host:port:user:pass) or leave empty to remove proxy: '
        )

        try:
            await manager.update_proxy(profile_name, proxy_str)
            print(f"Profile '{profile_name}' updated successfully!")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            logger.exception(f"Error updating profile '{profile_name}': {e}")

    async def input_handler():
        """Обработчик команд."""
        handlers = {
            '1': handle_create_profiles,
            '2': handle_run_automation,
            '3': handle_launch_profile,
            '4': handle_update_profile,
            '5': handle_create_script
        }

        while True:
            try:
                choice = await ainput(
                    '\n1. Create Profiles\n'
                    '2. Run Automation\n'
                    '3. Launch Profile Manually\n'
                    '4. Update Profile\n'
                    '5. Create New Automation Script\n'
                    '6. Exit\n'
                    '> '
                )

                if choice == '6':
                    print("Exiting...")
                    return

                if choice in handlers:
                    await handlers[choice]()
                else:
                    print('Invalid choice')
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                return

    await input_handler()

