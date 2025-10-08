import json
from typing import Any, Literal, Optional

import requests
from PaulsLoggerManagement import setup_logger

from GembaFileUpToDater.epicor_communications import EpicorCommunicator

logger = setup_logger("AccessGembaFiles")

class BAQMethod:

    @staticmethod
    def get_records(url: str,
                    company_ID: Optional[str]=None,
                    API_key: Optional[str]=None,
                    user_pass: Optional[str]=None,
                    timeout: float=60.0) -> list[dict]:
        """
        Execute the BAQ without updates.
        """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)

        headers = BAQMethod.__get_headers(API_key, has_content=False)

        response: requests.Response
        response = EpicorCommunicator.get_request(url,
                                                  headers=headers,
                                                  timeout=timeout)

        data: list = response.json().get('value', [])
        return data

    @staticmethod
    def patch_record(url: str,
                     payload: dict,
                     company_ID: Optional[str]=None,
                     API_key: Optional[str]=None,
                     user_pass: Optional[str]=None,
                     timeout: float=60.0) -> dict[Literal['value'], list[dict[str, Any]]]:
        """ Strict patch with a record """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)

        headers = BAQMethod.__get_headers(API_key, has_content=True)

        response: requests.Response
        response = EpicorCommunicator.patch_request(url,
                                                    headers=headers,
                                                    data=json.dumps(payload),
                                                    timeout=timeout)

        data = response.json()
        return data

    @staticmethod
    def get_new(url: str,
                company_ID: Optional[str]=None,
                API_key: Optional[str]=None,
                user_pass: Optional[str]=None,
                timeout: float=60.0) -> dict[str, Any]:
        """ Get a new record.
            
            I'm pretty sure you can just PATCH in a new record if you want to,
            but getting a new record like this will work with whatever GetNew
            method directives are set up.
        """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)

        headers = BAQMethod.__get_headers(API_key, has_content=False)

        response: requests.Response
        response = EpicorCommunicator.get_request(url,
                                                headers=headers,
                                                timeout=timeout)
        data = response.json()
        if 'value' not in data:
            logger.error('Response for GetNew did not contain data')
            raise Exception('Missing data in response')
        
        
        result: list[dict[str, Any]] = data.get('value', [])
        if len(result) == 0:
            logger.warning('No data in "get_new" response')
        
        return result[0]

    @staticmethod
    def __get_headers(API_key: str, user_pass: Optional[str]=None, has_content=False) -> dict[str, str]:

        if API_key is None:
            API_key = EpicorCommunicator.API_key
        
        if user_pass is None:
            user_pass = EpicorCommunicator.user_pass

        ret = {
            'accept': 'application/json',
            'X-API-Key': API_key,
            "Authorization": f"Basic {user_pass}",
        }
        if has_content:
            ret['Content-Type'] = 'application/json'
        return ret
