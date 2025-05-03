from typing import Callable
from profile_manager.manager import ProfileManager
from profile_manager.structures import Profile

import asyncio
import logging
import pickle
from asyncio import Task
from pathlib import Path
import aiohttp

from browserforge.fingerprints import FingerprintGenerator
from browserforge.headers import Browser
from browserforge.injectors.utils import InjectFunction, only_injectable_headers
from playwright.async_api import Page, async_playwright

from profile_manager.path import StealthPlaywrightPatcher
from profile_manager.structures import Profile, Proxy
from profile_manager.automation_script_base import AutomationScript


logger = logging.getLogger(__name__)

USER_DATA_PATH = Path(__file__).parent.parent / 'user_data'

PROFILES_PATH = USER_DATA_PATH / 'profiles.pkl'
PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)

EXTENSIONS_PATH = Path(__file__).parent.parent / 'extensions'



class AutomationManager(ProfileManager):
    
    def __init__(self, automate_start: int, automate_end: int):
        super().__init__()
        self.automate_start = automate_start
        self.automate_end = automate_end
        self.failed_profiles = []
    


    async def create_profiles(self, count: int, proxy_file: Path = None):
        """Создает заданное количество профилей, используя метод из родительского класса."""
        proxies = []
        if proxy_file and proxy_file.exists():
            with proxy_file.open("r", encoding="utf-8") as f:
                proxies = [line.strip() for line in f.readlines() if line.strip()]
            
            proxies = await self._validate_proxies(proxies)

        if not proxies:
            logger.warning("Список прокси пуст или недоступен.")
            return

        profiles_info_path = USER_DATA_PATH / "profiles_info.txt"
        created_count = 0

        with profiles_info_path.open("a", encoding="utf-8") as profiles_file:  
            while created_count < count:
                profile_name = f"Profile_{len(self.profiles) + 1}"
                
                if profile_name in self.profiles:
                    logger.info(
                        f"Profile {profile_name} already exists. Skipping."
                        )
                    profiles_file.write(
                        f"{profile_name}: {self.profiles[profile_name].proxy}\n"
                        )
                    continue

                proxy_str = proxies.pop(0) if proxies else None
                proxies.append(proxy_str)  

                try:
                    await self.create_profile(profile_name, proxy_str)
                    created_count += 1
                    logger.info(
                        f"Profile {profile_name} created successfully."
                        )

                    proxy_info = proxy_str if proxy_str else "No Proxy"
                    profiles_file.write(f"{profile_name}: {proxy_info}\n")
                except ValueError as e:
                    logger.warning(
                        f"Failed to create profile {profile_name}: {e}"
                        )

        logger.info(
            f"Created {created_count} new profiles."
                "Total profiles: {len(self.profiles)}."
            )
    
    
    
    async def _validate_proxies(self, proxies: list[str]) -> list[str]:
        """Проверяет доступность прокси."""
        valid_proxies = []
        for proxy_data in proxies:
            try:
                # Используем метод parse_proxy из родительского класса
                proxy = self.parse_proxy(proxy_data)
                if await self._check_proxy(proxy):
                    valid_proxies.append(proxy_data)
            except (ValueError, IndexError) as e:
                logger.error(f"Invalid proxy format: {proxy_data} - {e}")
                continue
        return valid_proxies


    async def do_automation_for_profiles(self, automation_script: Callable):
        semaphore = asyncio.Semaphore(5)

        self.running_tasks = {
            name: task for name, task in self.running_tasks.items() \
                if not task.done()
            }
        sorted_profiles = sorted(
            self.profiles.items(), 
            key=lambda item: int(item[0].split("_")[1])
            )
        filtered_profiles = sorted_profiles[self.automate_start - 1 : self.automate_end]
        
        for index, (profile_name, profile) in \
            enumerate(filtered_profiles, start=self.automate_start):
            is_last_profile = (index == self.automate_end)  

            if profile.proxy and not await self._check_proxy(profile.proxy):
                logger.warning(
                    f"Skipping profile {profile_name} due to proxy failure."
                        "Ошибка с прокси "
                         f"{profile.proxy.server}:{profile.proxy.port}.")
                
                self.failed_profiles.append(
                    {
                        'profile_name': profile_name,
                        'error': f"Proxy {profile.proxy.server}:{profile.proxy.port} failed.",
                        "script": automation_script.__class__.__name__
                    }
                )
                continue
            
            task = asyncio.create_task(self._run_with_semaphore(
                profile_name, 
                automation_script, 
                semaphore, 
                is_last_profile))
            self.running_tasks[profile_name] = task

        await asyncio.gather(*self.running_tasks.values())
        self.generate_report(USER_DATA_PATH / "automation_report.txt")

    
    
    async def _run_with_semaphore(
            self, 
            profile_name: str, 
            automation_script: Callable, 
            semaphore: asyncio.Semaphore, 
            is_last_profile: bool
            ):
        async with semaphore:
            await self._run_automation(
                profile_name, 
                automation_script,
                is_last_profile
                )


    
    async def _check_proxy(self, proxy: Proxy) -> bool:
        """Проверяет доступность прокси."""
        if not proxy:
            logger.info("No proxy configured for this profile.")
            return True  # Если прокси нет, считаем, что проверка успешна

        # Проверяем, содержит ли proxy.server префикс http:// или https://
        if not proxy.server.startswith("http://") \
            and not proxy.server.startswith("https://"):
            proxy_url = f"http://{proxy.server}:{proxy.port}"
        else:
            proxy_url = f"{proxy.server}:{proxy.port}"

        proxy_auth = aiohttp.BasicAuth(proxy.username, proxy.password) \
            if proxy.username else None

        logger.info(f"Testing proxy: {proxy_url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://httpbin.org/ip",
                    proxy=proxy_url,
                    proxy_auth=proxy_auth,
                    timeout=10
                ) as response:
                    logger.info(f"Proxy {proxy.server}:{proxy.port}"
                                " responded with status {response.status}")
                    if response.status == 200:
                        logger.info(f"Proxy {proxy.server}:{proxy.port} is working.")
                        return True
                    else:
                        logger.warning(f"Proxy {proxy.server}:{proxy.port} "
                                       "returned status {response.status}.")
                        return False
        except Exception as e:
            logger.error(f"Proxy {proxy.server}:{proxy.port} "
                         "failed with exception: {e}")
            return False
        


    def generate_report(self, filepath: Path):
        """Генерирует полный отчет о выполнении."""
        with filepath.open("w", encoding="utf-8") as f:
            f.write("Automation Report\n")
            f.write("=" * 40 + "\n")
            
            # Успешные профили
            f.write("Successful Profiles:\n")
            for profile_name in self.profiles.keys():
                if profile_name not in \
                    [p['profile_name'] for p in self.failed_profiles]:
                    f.write(f"- {profile_name}\n")
            
            f.write("\nFailed Profiles:\n")
            for profile in self.failed_profiles:
                f.write(
                    f"- {profile['profile_name']}: {profile['error']}"
                        f": {profile['script']}\n"
                        )
            
            f.write("-" * 40 + "\n")
        logger.info(f"Report generated at {filepath}")
        
    
    
    async def _run_automation(
            self, profile_name: str, 
            automation_script: AutomationScript,
            is_last_profile: bool = False,
            max_retries: int = 3
        ):
        retries = 0
        
        if max_retries <= 0:
            max_retries = 1

        while retries < max_retries:
            try:
                profile = self.profiles[profile_name]
                
                async with async_playwright() as playwright:
                    user_data_path = USER_DATA_PATH / profile_name

                    proxy_config = None
                    if profile.proxy:
                        proxy_config = {
                            'server': f'{profile.proxy.server}:{profile.proxy.port}',
                            'username': profile.proxy.username,
                            'password': profile.proxy.password
                        }

                    context = await playwright.chromium.launch_persistent_context(
                        user_data_dir=user_data_path,
                        channel='chrome',
                        headless=False,
                        user_agent=profile.fingerprint.navigator.userAgent,
                        color_scheme='dark',
                        viewport={
                            'width': profile.fingerprint.screen.width,
                            'height': profile.fingerprint.screen.height
                        },
                        extra_http_headers=only_injectable_headers(headers={
                            'Accept-Language': profile.fingerprint.headers.get(
                                'Accept-Language',
                                'en-US,en;q=0.9'
                            ),
                            **profile.fingerprint.headers,
                        }, browser_name='chrome'),
                        proxy=proxy_config,
                        ignore_default_args=[
                            '--enable-automation',
                            '--no-sandbox',
                            '--disable-blink-features=AutomationControlled',
                        ],
                        args=self.get_extensions_args(),
                    )

                    await context.add_init_script(
                        InjectFunction(profile.fingerprint),
                    )

                    # Закрываем стартовую about:blank
                    for page in context.pages:
                        if page.url == 'about:blank':
                            _ = asyncio.create_task(
                                self.close_page_with_delay(page, delay=0.25),
                            )

                    page = await context.new_page()
                    await automation_script.run(page)

                    if is_last_profile:
                        logger.info(
                            f"Browser for profile {profile_name} "
                                "left open for inspection.\n"
                                "Последний профиль, ждем 10 секунд перед закрытием."
                            )
                        await asyncio.sleep(10)  
                    else:
                        await context.close()

                    return

            except Exception as e:
                retries += 1
                logger.warning(
                    f"Retry {retries}/{max_retries} "
                        f"for profile {profile_name} due to error: {e}"
                    )
                if retries >= max_retries:
                    logger.error(
                        f"Profile {profile_name} "
                            f"failed after {max_retries} retries."
                                 )
                    self.failed_profiles.append(
                        {
                            'profile_name': profile_name,
                            'error': str(e),
                            "script": automation_script.__class__.__name__
                        }
                    )
            finally:
                _ = self.running_tasks.pop(profile_name, None)
                self.save_profiles()