import requests

class Hadoop():
    
    def __init__(self, ip: str = "hadoop") -> None:
        self.ip = ip
    
    def get_file(self, path) -> str | None:
        url = f"http://{self.ip}:9864/webhdfs/v1{path}?op=OPEN&namenoderpcaddress={self.ip}:9000"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
