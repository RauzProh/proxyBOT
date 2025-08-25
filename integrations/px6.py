# integrations/px6.py
import httpx

from config import PX6_API_KEY


PX6_API_KEY = PX6_API_KEY

BASE_URL = f"https://px6.link/api/{PX6_API_KEY}"

class PX6API:
    def __init__(self):
        self.base_url = BASE_URL
        self.api_key = PX6_API_KEY

    async def request(self, method: str, params: dict = None):
        params = params or {}
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"{self.base_url}/{method}"
            print(url, params)
            response = await client.get(url, params=params)
            data = response.json()
            if data.get("status") == "no":
                raise ValueError(f"PX6 API error {data.get('error_id')}: {data.get('error')}")
            print(data)
            return data

    # Методы API
    async def get_price(self, count: int, period: int, version: int = 6):
        return await self.request("getprice", {"count": count, "period": period, "version": version})

    async def get_count(self, country: str, version: int = 6):
        return await self.request("getcount", {"country": country, "version": version})

    async def get_country(self, version: int = 6):
        return await self.request("getcountry", {"version": version})

    async def get_proxy(self, state: str = "all", page: int = 1, limit: int = 1000, descr: str = None):
        params = {"state": state, "page": page, "limit": limit}
        if descr:
            params["descr"] = descr
        return await self.request("getproxy", params)

    async def buy(self, count: int, period: int, country: str, version: int = 6, type_: str = "http", descr: str = None, auto_prolong: bool = False):
        params = {
            "count": count,
            "period": period,
            "country": country,
            "version": version,
            "type": type_,
        }
        if descr:
            params["descr"] = descr
        if auto_prolong:
            params["auto_prolong"] = ""
        return await self.request("buy", params)

    async def prolong(self, ids: list[int], period: int):
        return await self.request("prolong", {"ids": ",".join(map(str, ids)), "period": period})

    async def delete(self, ids: list[int]):
        return await self.request("delete", {"ids": ",".join(map(str, ids))})

    async def check(self, ids: list[int] = None, proxy: str = None):
        params = {}
        if ids:
            params["ids"] = ",".join(map(str, ids))
        if proxy:
            params["proxy"] = proxy
        return await self.request("check", params)
