from dataclasses import dataclass
from typing import Optional

@dataclass
class Server:
    name: str
    search_name: str
    map: Optional[str] = None
    ip: Optional[str] = None
    
