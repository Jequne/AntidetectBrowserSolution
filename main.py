import asyncio
from pathlib import Path


from profile_manager.cli import run_profile_manager
from automation_scripts import test_script
from profile_manager.automation_manager import AutomationManager
from profile_manager.structures import Profile


async def main():
    auto_manager = AutomationManager(automate_start=1, automate_end=5)
    automation_script = test_script.MyAutomationScript()
    await auto_manager.do_automation_for_profiles(automation_script)

    # auto_manager = AutomationManager(automate_start=1, automate_end=5)
    # proxy_file = Path('user_data/proxies.txt')  # Преобразуем строку в Path
    # await auto_manager.create_profiles(5, proxy_file=proxy_file)

if __name__ == '__main__':
    # try:
    #     asyncio.run(run_profile_manager())
    # except KeyboardInterrupt:
    #     pass

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass



