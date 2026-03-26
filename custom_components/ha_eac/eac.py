# Chrome DevTools -> Network tab to find actual API endpoints and payloads
# F12 -> Network -> Filter by XHR to see API calls


import logging
import requests
import json
import os
import time
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

_LOGGER = logging.getLogger(__name__)

class EACClient:

    @dataclass
    class ActiveMeter:
        spId: str
        mcId_Exp: str = None
        mcId_Imp: str = None
        info: dict = None

    @dataclass
    class ActiveMeterReading:
        spId: str
        exp: int = None
        imp: int = None
        info: dict = None

    def __init__(self, username, password):
        self.base_url = "https://meterreading-dso.eac.com.cy/api/portal/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        self.username = username
        self.password = password
        self.jwt_token = None
        self.active_meters: list[EACClient.ActiveMeter] = []


    def login(self):
        """
        Login to EAC portal and store JWT token
        """
        payload = {
            "email": self.username,
            "password": self.password
        }
        
        status_code, data = self._make_api_call("login", method='POST', req_data=payload)
        
        if data:
            token = data.get('jwt')
            if token:
                self.set_token(token)        
                #print("✓ Login successful!")
                #print(f"Token: {self.jwt_token[:50]}...")
                return True
            else:
                #print("✗ Login Failed: No JWT token in response")
                return False
        else:
            #print("✗ Login Failed: No response data")
            return False

    
    def set_token(self, token):
        """
        Set JWT token and update authorization header
        """
        if token is None:
            _LOGGER.error("✗ No token provided")
            return
        #print(f"Setting JWT token: {token[:50]}...")
        self.jwt_token = token
        self.session.headers.update({
            'Authorization': f'Bearer {self.jwt_token}'
        })

    
    def _make_api_call(self, endpoint, method='GET', req_data=None):
        """
        Generic API call method for any endpoint 
        """
        url = f"{self.base_url}{endpoint}"
        _LOGGER.debug(f"→ {method} {url}")
        
        # if req_data:
        #     print("Request Data:")
        #     pprint(req_data)
        
        # print("Headers:")
        # pprint(dict(self.session.headers))
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=req_data)
            elif method == 'PUT':
                response = self.session.put(url, json=req_data)
            
            elapsed_ms = (time.time() - start_time) * 1000
            _LOGGER.debug(f"← {response.status_code} ({elapsed_ms:.2f}ms)")
            
            #response.raise_for_status()
            return response.status_code, response.json()
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else 'N/A'
            _LOGGER.debug(f"✗ API call failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                _LOGGER.debug(f"Response: {e.response.text}")
            return None, None
    
    #Safe api call that handles token expiration and retries once after re-login
    def api_call(self, endpoint, method='GET', req_data=None):
        status_code, data = self._make_api_call(endpoint, method, req_data)
        if status_code == 401:
            if self.login():  # Re-login to refresh token
                status_code, data = self._make_api_call(endpoint, method, req_data)               
        
        return data


    def userDetails(self):
        """
        Get user details from portal
        """
        data = self.api_call("userDetails", method='GET')
        if data:
            _LOGGER.debug(f"User Details Data: {data}")
        return data

    def servicePoints(self, service_point_id=None):
        """
        Get service points from portal
        """
        if service_point_id:
            url = f"servicePoints/{service_point_id}"
        else:
            url = "servicePoints"
        data = self.api_call(url, method='GET')
        if data:
            # pprint(data)
            _LOGGER.debug(f"Service Points Data: {data}")
        return data

    #Req:
    # '{"spId":"42........41","mcId":"83.......90","startDate":"2026-01-31T22:00:00.000Z","endDate":"2026-02-12T22:00:00.000Z"}'
    #Resp:
    # [{'id': '83.......90',
    #   'readings': [{'dt': '2026-02-01T00:00:00', 'reading': 1873.0, 'value': 14.0},
    #                {'dt': '2026-02-02T00:00:00', 'reading': 1887.0, 'value': 14.0},
    #                {'dt': '2026-02-03T00:00:00', 'reading': 1896.0, 'value': 9.0},
    def fetchLastMeterReading(self, spId: str, mcId: str):
        """
        Get meter readings for a specific service point, meter, configuration, and measurement
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(hours=48)
        
        payload = {
            "spId": spId,
            "mcId": mcId,
            "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endDate": end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        }
        data = self.api_call("readings/list", method='POST', req_data=payload)
        #if data:
        #    print(data)
        if data:
            _LOGGER.debug(f"Meter Readings Data for spId {spId} mcId {mcId}: {data}")
            if len(data) > 0:
                rd = data[0]
                if 'readings' in rd and len(rd['readings']) > 0:
                    if 'reading' in rd['readings'][-1] :
                        latest_reading = rd['readings'][-1]['reading']
                        return latest_reading

        return None

    
    def fetchActiveMeters(self):
        #Fetch service points to find active one and get meter details to find active measurement ID, then store active spId and mcId for later use in fetching readings

        activeMeters = []
        servicePoints = self.servicePoints()
    
        
        for sp in servicePoints:
            if sp.get('active') == True:
                sp_id = sp.get('id')
    
                service_point_data = self.servicePoints(service_point_id=sp_id)
                #print(f"Service point data: {service_point_data}")
            
                for meter in service_point_data:
                    active_status = True
                    if 'removalDate' in meter and meter['removalDate'] is not None:
                        active_status = False
                    #print(f"Model: {meter.get('model')}, Serial: {meter.get('serialNumber')}, Active: {active_status}")

                    if active_status:
                        for conf in meter.get('configurationsList', []):
                            config_active_status = True
                            if "endDate" in conf and conf["endDate"] is not None:
                                config_active_status = False
                            #print(f" Config ID: {conf.get('configurationId')}, Active: {config_active_status}")
                            if config_active_status:
                                active_meter = EACClient.ActiveMeter(spId=sp_id)
                                for measurement in conf.get('mcList', []):
                                    #print(f"  - Measurement Type: {measurement.get('type')}")
                                    if measurement.get('type') == 'S-KWH-NET-IMP-MMTR':
                                        active_measurement_id = measurement.get('id')
                                        #print("    → Found active S-KWH-NET-IMP-MMTR measurement, ID:", active_measurement_id)
                                        active_meter.mcId_Imp = active_measurement_id
                                    elif measurement.get('type') == 'S-KWH-NET-EXP-MMTR':
                                        active_measurement_id = measurement.get('id')
                                        #print("    → Found active S-KWH-NET-EXP-MMTR measurement, ID:", active_measurement_id)
                                        active_meter.mcId_Exp = active_measurement_id

                                if active_meter.mcId_Exp or active_meter.mcId_Imp:
                                    active_meter.info = sp
                                    activeMeters.append(active_meter)

        if not activeMeters:
            _LOGGER.error("No active service point found!")
            return False
        
        self.active_meters = activeMeters
        return True
        
    def fetchMetersData(self):
        if not self.active_meters:
            if not self.fetchActiveMeters():
                return None
        
        meters_data = []
        for meter in self.active_meters:
            spId = meter.spId
            mcId_Exp = meter.mcId_Exp
            mcId_Imp = meter.mcId_Imp

            reading = self.ActiveMeterReading(spId=spId)
            reading.info = meter.info
            if mcId_Exp:
                reading.exp = self.fetchLastMeterReading(spId, mcId_Exp)
            if mcId_Imp:
                reading.imp = self.fetchLastMeterReading(spId, mcId_Imp)

            meters_data.append(reading)
        
        return meters_data
    

# # Usage Example
# if __name__ == "__main__":
#     client = EACClient()

#     loadCache()

#     if 'jwt_token' in g_cache_data:
#         client.set_token(g_cache_data.get('jwt_token'))
#     else:
#         client.login(email=g_email, password=g_password)
#         g_cache_data['jwt_token'] = client.jwt_token
#         saveCache()

#     #if 'userDetails' not in g_cache_data:
#     userDetails = client.userDetails() 
#     #g_cache_data['userDetails'] = userDetails
#     #saveCache()

#     # if 'servicePoints' not in g_cache_data:
#     #     servicePoints = client.servicePoints()  # Try to get service points with existing token (if any)
#     #     g_cache_data['servicePoints'] = servicePoints
#     #     saveCache()
    
#     client.findMeters(force_refresh=False)
#     #saveCache()

#     client.meterReadings()
        
