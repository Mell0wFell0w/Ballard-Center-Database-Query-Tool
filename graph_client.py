import msal, os, requests
from typing import Optional

class GraphClient:
    def __init__(self, tenant_id: str, client_id: str, scopes: list[str]):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.scopes = scopes
        self._token: Optional[str] = None

    def get_token_device_code(self) -> str:
        app = msal.PublicClientApplication(self.client_id, authority=f"https://login.microsoftonline.com/{self.tenant_id}")
        flow = app.initiate_device_flow(scopes=[f"https://graph.microsoft.com/{s}" for s in self.scopes])
        if "user_code" not in flow:
            raise RuntimeError("Device code flow failed to start. Check app registration & scopes.")
        print(f"To sign in, visit: {flow['verification_uri']} and enter code: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            raise RuntimeError(f"Token acquisition failed: {result}")
        self._token = result["access_token"]
        return self._token

    @property
    def token(self) -> str:
        if not self._token:
            return self.get_token_device_code()
        return self._token

    def get(self, url: str, params: dict | None = None) -> dict:
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            params=params or {}
        )
        resp.raise_for_status()
        return resp.json()
