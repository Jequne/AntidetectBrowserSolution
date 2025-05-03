from dataclasses import dataclass, field

from browserforge.fingerprints import Fingerprint


@dataclass
class Proxy:
    server: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    
    def __str__(self):
        if self.username and self.password:
            return f"http://{self.server}:{self.port}:{self.username}:{self.password}"
        return f"http://{self.server}:{self.port}"


@dataclass
class Profile:
    fingerprint: Fingerprint
    proxy: Proxy | None = None
    page_urls: list[str] = field(default_factory=list)
