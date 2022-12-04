from dataclasses import dataclass

@dataclass
class Server:
    name: str
    search_name: str
    map: str
    ip: str = None
    
