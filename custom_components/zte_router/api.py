"""API client for ZTE Router."""
from __future__ import annotations

import hashlib
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

# Unauthenticated session ID used by the router
UNAUTHENTICATED_SESSION = "00000000000000000000000000000000"


class ZTERouterAPI:
    """ZTE Router API client."""
    
    def __init__(self, host: str, password: str | None = None) -> None:
        """Initialize the API client."""
        self.host = host
        self.password = password
        self.base_url = f"http://{host}/ubus/"
        self.session_id = UNAUTHENTICATED_SESSION
        self._session: aiohttp.ClientSession | None = None
        self._request_id = 1
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            # Create connector that doesn't verify SSL
            connector = aiohttp.TCPConnector(ssl=False, force_close=False)
            self._session = aiohttp.ClientSession(
                connector=connector,
                headers={
                    "Content-Type": "text/plain;charset=UTF-8",
                    "Origin": f"http://{self.host}",
                    "Referer": f"http://{self.host}/",
                },
            )
        return self._session
    
    async def close(self) -> None:
        """Close the API session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _create_rpc_request(
        self, namespace: str, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a JSON-RPC 2.0 request."""
        if params is None:
            params = {}
        
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "call",
            "params": [self.session_id, namespace, method, params]
        }
        self._request_id += 1
        return request
    
    async def _call_api(
        self, namespace: str, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Make a single API call."""
        session = await self._get_session()
        request = self._create_rpc_request(namespace, method, params)
        
        # Add timestamp to URL (required by router)
        import time
        url = f"{self.base_url}?t={int(time.time() * 1000)}"
        
        try:
            async with session.post(
                url, 
                json=[request], 
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
                
                # Validate response is a list
                if not isinstance(data, list):
                    _LOGGER.error("API returned non-list response: %s", type(data))
                    return None
                
                if data and len(data) > 0:
                    result = data[0].get("result", [])
                    if isinstance(result, list) and len(result) > 1:
                        return result[1]
                
                return None
        except Exception as err:
            _LOGGER.error("API call failed for %s.%s: %s", namespace, method, err)
            return None
    
    async def _call_api_batch(
        self, calls: list[tuple[str, str, dict[str, Any] | None]]
    ) -> list[dict[str, Any] | None]:
        """Make multiple API calls in a single request."""
        session = await self._get_session()
        requests = [
            self._create_rpc_request(namespace, method, params)
            for namespace, method, params in calls
        ]
        
        # Add timestamp to URL (required by router)
        import time
        url = f"{self.base_url}?t={int(time.time() * 1000)}"
        
        try:
            async with session.post(
                url, 
                json=requests, 
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
                
                # Validate response is a list
                if not isinstance(data, list):
                    _LOGGER.error("API returned non-list response: %s (type: %s)", data, type(data))
                    return [None] * len(calls)
                
                results = []
                access_denied_count = 0
                
                for idx, item in enumerate(data):
                    if not isinstance(item, dict):
                        results.append(None)
                        continue
                    
                    # Check for errors in response
                    if "error" in item:
                        error_code = item["error"].get("code")
                        if error_code == -32002:
                            access_denied_count += 1
                            # Access denied is normal during session expiration, log at debug level
                            _LOGGER.debug(
                                "API call %d (%s.%s) returned Access Denied (session may have expired)",
                                idx,
                                calls[idx][0] if idx < len(calls) else "unknown",
                                calls[idx][1] if idx < len(calls) else "unknown",
                            )
                        else:
                            # Other errors are unexpected, log as warning
                            _LOGGER.warning(
                                "API call %d (%s.%s) returned error: %s",
                                idx,
                                calls[idx][0] if idx < len(calls) else "unknown",
                                calls[idx][1] if idx < len(calls) else "unknown",
                                item["error"]
                            )
                        results.append(None)
                        continue
                    
                    result = item.get("result", [])
                    if isinstance(result, list) and len(result) > 1:
                        results.append(result[1])
                    else:
                        results.append(None)
                
                # If we got Access Denied on multiple calls and we're using an authenticated session,
                # the session likely expired - reset it
                if access_denied_count >= 2 and self.session_id != UNAUTHENTICATED_SESSION:
                    _LOGGER.info(
                        "Session expired (Access Denied on %d calls), resetting session for re-authentication",
                        access_denied_count
                    )
                    self.session_id = UNAUTHENTICATED_SESSION
                
                return results
        except Exception as err:
            _LOGGER.error("Batch API call failed: %s", err)
            return [None] * len(calls)
    
    async def async_login(self) -> bool:
        """Authenticate with the router."""
        if not self.password:
            _LOGGER.error("Password is required for authentication")
            return False
        
        try:
            # Get login info (includes salt)
            login_info = await self._call_api("zwrt_web", "web_login_info")
            if not login_info or "zte_web_sault" not in login_info:
                _LOGGER.error("Could not get login info")
                return False
            
            salt = login_info["zte_web_sault"]
            
            # Hash password with salt (double SHA256, uppercase at each step)
            hashed = hashlib.sha256(self.password.encode()).hexdigest().upper()
            hashed_with_salt = hashlib.sha256((hashed + salt).encode()).hexdigest().upper()
            
            # Attempt login
            login_result = await self._call_api(
                "zwrt_web", "web_login", {"password": hashed_with_salt.upper()}
            )
            
            if login_result:
                result_code = login_result.get("result")
                
                # Result can be string "0" or integer 0 for success
                if result_code in ("0", 0):
                    self.session_id = login_result.get("ubus_rpc_session", self.session_id)
                    _LOGGER.info("Successfully authenticated to ZTE router")
                    return True
                elif result_code in (1, "1"):
                    # Login failed - wrong password or other auth error
                    fail_num = login_result.get("login_fail_num", "unknown")
                    _LOGGER.error(
                        "Authentication failed: incorrect password (attempt %s/5). Message: %s",
                        fail_num,
                        login_result.get("msg", "unknown error")
                    )
                    return False
                elif result_code in (2, "2"):
                    # Login locked due to too many attempts
                    locktime = login_result.get("login_fail_lock_lefttime", "unknown")
                    _LOGGER.warning(
                        "Router login is locked (too many attempts). Wait %s seconds before retrying",
                        locktime
                    )
                    return False
                else:
                    _LOGGER.warning(
                        "Authentication failed with result %s: %s",
                        result_code,
                        login_result.get("msg", "unknown error")
                    )
                    return False
            else:
                _LOGGER.warning("Authentication failed: no response from router")
                return False
                
        except Exception as err:
            _LOGGER.error("Login failed: %s", err)
            return False
    
    async def async_get_router_status(self) -> dict[str, Any] | None:
        """Get router status information."""
        # Use the no_auth variant if not authenticated
        method = "router_get_status" if self.session_id != UNAUTHENTICATED_SESSION else "router_get_status_no_auth"
        return await self._call_api("zwrt_router.api", method)
    
    async def async_get_network_info(self) -> dict[str, Any] | None:
        """Get network information (signal, operator, etc.)."""
        return await self._call_api("zte_nwinfo_api", "nwinfo_get_netinfo")
    
    async def async_get_data_usage(self) -> dict[str, Any] | None:
        """Get data usage statistics."""
        return await self._call_api(
            "zwrt_data",
            "get_wwandst",
            {"source_module": "web", "cid": 1, "type": 4}
        )
    
    async def async_update(self) -> dict[str, Any]:
        """Update all router data."""
        # Authenticate if we have a password and aren't logged in yet
        if self.password and self.session_id == UNAUTHENTICATED_SESSION:
            _LOGGER.debug("Attempting to authenticate...")
            login_success = await self.async_login()
            if login_success:
                _LOGGER.info("Authentication successful, session ID: %s", self.session_id[:8] + "...")
            else:
                _LOGGER.warning("Authentication failed, using unauthenticated access")
        
        # Determine which router status method to use
        router_method = "router_get_status" if self.session_id != UNAUTHENTICATED_SESSION else "router_get_status_no_auth"
        
        _LOGGER.debug("Using method: %s, session: %s", router_method, self.session_id[:8] + "...")
        
        # Make batch call for efficiency
        # Note: Some APIs work without auth, others require it
        calls = [
            ("zwrt_router.api", router_method, None),  # Status - works with or without auth
            ("zte_nwinfo_api", "nwinfo_get_netinfo", None),  # Network info - works without auth
            ("zwrt_data", "get_wwandst", {"source_module": "web", "cid": 1, "type": 4}),  # Data usage - requires auth
            ("zwrt_router.api", "router_get_user_list_num", None),  # Device count - requires auth
            ("zwrt_wlan", "report", None),  # WiFi info - requires auth
        ]
        
        results = await self._call_api_batch(calls)
        
        # Check if we're missing data after the call
        missing_data = []
        if not results[0]:
            missing_data.append("router_status")
        if not results[1]:
            missing_data.append("network_info")
        if not results[2]:
            missing_data.append("data_usage")
        if not results[3]:
            missing_data.append("device_info")
        if not results[4]:
            missing_data.append("wlan_info")
        
        # Log what we got
        _LOGGER.debug(
            "Update results - router_status: %s, network_info: %s, data_usage: %s, device_info: %s, wlan_info: %s",
            "OK" if results[0] else "MISSING",
            "OK" if results[1] else "MISSING",
            "OK" if results[2] else "MISSING",
            "OK" if results[3] else "MISSING",
            "OK" if results[4] else "MISSING",
        )
        
        # Warn if we're authenticated but still missing data (likely a real problem)
        if missing_data and self.session_id != UNAUTHENTICATED_SESSION:
            _LOGGER.warning(
                "Failed to retrieve data despite authentication: %s",
                ", ".join(missing_data)
            )
        
        if results[2]:
            _LOGGER.debug("Speed data: TX=%s, RX=%s", results[2].get("real_tx_speed"), results[2].get("real_rx_speed"))
        
        return {
            "router_status": results[0] or {},
            "network_info": results[1] or {},
            "data_usage": results[2] or {},
            "device_info": results[3] or {},
            "wlan_info": results[4] or {},
        }
