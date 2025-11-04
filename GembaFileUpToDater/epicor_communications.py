from __future__ import annotations

import base64
import json
import time
from typing import Any, Literal, Optional, TypedDict

import requests
from PaulsLoggerManagement import setup_logger
from PIL.ImageFile import ImageFile
from requests.exceptions import HTTPError

from GembaFileUpToDater.parse_args import should_show_debug
import logging
logger = setup_logger("AccessGembaFiles", level=(logging.DEBUG if should_show_debug() else logging.INFO))

class EpicorImage(TypedDict):
    Company: str
    ImageID: str
    ImageFileName: str
    ImageCategoryID: str
    CreatedBy: str
    Width: float
    Height: float
    FileType: str
    ImageContent: str
    ThumbnailContent: str
    image: ImageFile

class ReadAllBytesResults(TypedDict):
    returnObj: str
    parameters: dict[Literal['fileName'], str]

class StoredFile(TypedDict):
    SysRowID: str
    FileName: str
    Contents: str

class EpicorCommunicator:
    company_ID: str = ''
    url_domain: str = ''
    url_app_path: str = ''
    API_key: str = ''
    user_pass: str = ''

    @staticmethod
    def get_id_api_pass(company_ID: str | None, API_key: str | None, user_pass: str | None) -> tuple[str, str, str]:

        company_ID = company_ID or EpicorCommunicator.company_ID
        API_key = API_key or EpicorCommunicator.API_key
        user_pass = user_pass or EpicorCommunicator.user_pass

        return company_ID, API_key, user_pass

    @staticmethod
    def get_id_api(company_ID: str | None, API_key: str | None) -> tuple[str, str]:

        company_ID = company_ID or EpicorCommunicator.company_ID
        API_key = API_key or EpicorCommunicator.API_key

        return company_ID, API_key

    @staticmethod
    def patch_request(url: str, headers: dict[str, Any], timeout: float, data: Optional[str] = None) -> requests.Response:
        response: requests.Response

        try:
            Reporting_Statistics.initialize_reporting()
            response = requests.patch(url,
                                      headers=headers,
                                      data=data,
                                      timeout=timeout)
            Reporting_Statistics.log_timing_metrics(response)

            if not response.ok:
                logger.warning(f'Response returned status of {response.status_code}')

            response.raise_for_status()

            return response

        except requests.HTTPError as e:
            logger.error(f"Request failed: {e}")
            logger.info(f'Headers: {headers}')
            logger.info(f'Timeout: {timeout}')
            raise
        
    @staticmethod
    def get_request(url: str, headers: dict[str, Any], timeout: float, data: Optional[str] = None) -> requests.Response:
        response: requests.Response

        try:
            Reporting_Statistics.initialize_reporting()
            response = requests.get(url,
                                    headers=headers,
                                    data=data,
                                    timeout=timeout)
            Reporting_Statistics.log_timing_metrics(response)

            if not response.ok:
                logger.warning(f'Response returned status of {response.status_code}')

            response.raise_for_status()

            return response

        except requests.HTTPError as e:
            logger.error(f"Request failed: {e}")
            logger.info(f'Headers: {headers}')
            logger.info(f'Timeout: {timeout}')
            raise


class Ice_LIB_FileStoreSvc:
    """
    File storage on the server.
    """
    
    @staticmethod
    def create(local_path: str,
               file_name: str,
               related_to_schema_name: str='',
               related_to_table: str='',
               tenant_ID: str='',
               sec_code: str='',
               company_ID: Optional[str]=None,
               API_key: Optional[str]=None,
               user_pass: Optional[str]=None,
               timeout: float=60.0) -> str:
        """ Create a new file. """
        
        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)

        logger.debug('Sending POST request for Ice.LIB.FileStoreService/Create')
        url = Ice_LIB_FileStoreSvc.get_url(method_name='Create')
        headers = Ice_LIB_FileStoreSvc.get_headers(API_key, user_pass, has_content=True)
        payload = {
            'bytes': File_Operations.encode_file(local_path),
            'foreignSysRowID': '00000000-0000-0000-0000-000000000000',
            'relatedToSchemaName': related_to_schema_name,
            'relatedToTable': related_to_table,
            'fileName': file_name,
            'companyID': company_ID,
            'tenantID': tenant_ID,
            'secCode': sec_code,
        }

        response: requests.Response
        try:
            Reporting_Statistics.initialize_reporting()
            response = requests.post(url,
                                     headers=headers,
                                     data=json.dumps(payload),
                                     timeout=timeout)
            Reporting_Statistics.log_timing_metrics(response)

            if not response.ok:
                logger.warning(f'Response returned status of {response.status_code}')
            
            response.raise_for_status()

            data = response.json().get('returnObj', '')

            # Check to see if there is data returned with the result
            if len(data) == 0:
                raise ValueError('No data returned, file may not have been created')
            
            return data

        except HTTPError as e:
            logger.error(f"Request failed: {e}")
            raise

        except requests.JSONDecodeError as e:
            logger.error("Didn't receive valid JSON in response")
            logger.error(e)
            raise

    @staticmethod
    def read_all_bytes(id: str,
                       company_ID: Optional[str]=None,
                       API_key: Optional[str]=None,
                       user_pass: Optional[str]=None,
                       timeout: float=60.0) -> ReadAllBytesResults | None:
        """ Read a file. """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)

        logger.debug('Sending POST request for Ice.LIB.FileStoreService/ReadAllBytes')
        url = Ice_LIB_FileStoreSvc.get_url(method_name='ReadAllBytes')
        headers = Ice_LIB_FileStoreSvc.get_headers(API_key, user_pass, has_content=True)
        payload = { 'id': id }

        response: requests.Response
        try:
            Reporting_Statistics.initialize_reporting()
            response = requests.post(url,
                                     headers=headers,
                                     data=json.dumps(payload),
                                     timeout=timeout)
            Reporting_Statistics.log_timing_metrics(response)

            if not response.ok:
                logger.warning(f'Response returned status of {response.status_code}')
            
            response.raise_for_status()

            data = response.json()

            if len(data.get('returnObj', '')) == 0:
                raise FileNotFoundError(f'No file was associated with id: {id}')
            
            return data

        except HTTPError as e:
            logger.error(f"Request failed: {e}")
            raise

        except requests.JSONDecodeError as e:
            logger.error("Didn't receive valid JSON in response")
            logger.error(e)
            raise

    @staticmethod
    def delete(id: str,
               company_ID: Optional[str]=None,
               API_key: Optional[str]=None,
               user_pass: Optional[str]=None,
               timeout: float=60.0) -> None:
        """ Deletes the specified file. """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)

        logger.debug('Sending POST request for Ice.LIB.FileStoreService/Delete')
        url = Ice_LIB_FileStoreSvc.get_url(method_name='Delete')
        headers = Ice_LIB_FileStoreSvc.get_headers(API_key, user_pass, has_content=True)
        payload = { 'id': id }

        response: requests.Response
        try:
            Reporting_Statistics.initialize_reporting()
            response = requests.post(url,
                                     headers=headers,
                                     data=json.dumps(payload),
                                     timeout=timeout)
            Reporting_Statistics.log_timing_metrics(response)

            if not response.ok:
                logger.warning(f'Response returned status of {response.status_code}')
            
            response.raise_for_status()

        except HTTPError as e:
            logger.error(f"Request failed: {e}")
            raise

    @staticmethod
    def read_all_files(foreign_sys_row_ID="00000000-0000-0000-0000-000000000000",
                       company_ID: Optional[str]=None,
                       API_key: Optional[str]=None,
                       user_pass: Optional[str]=None,
                       timeout: float=60.0) -> list[StoredFile]:
        """ Read the contents of all files with the given foreign SysRowID. """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)

        logger.debug('Sending POST request for Ice.LIB.FileStoreService/ReadAllFiles')
        url = Ice_LIB_FileStoreSvc.get_url(method_name='ReadAllFiles')
        headers = Ice_LIB_FileStoreSvc.get_headers(API_key, user_pass, has_content=True)
        payload = { 'foreignSysRowID': foreign_sys_row_ID }

        response: requests.Response
        try:
            Reporting_Statistics.initialize_reporting()
            response = requests.post(url,
                                     headers=headers,
                                     data=json.dumps(payload),
                                     timeout=timeout)
            Reporting_Statistics.log_timing_metrics(response)

            if not response.ok:
                logger.warning(f'Response returned status of {response.status_code}')
            
            response.raise_for_status()

            data = response.json().get('returnObj', [])

            if len(data) == 0:
                raise Exception('No data returned in response')
            
            return data

        except HTTPError as e:
            logger.error(f"Request failed: {e}")
            raise

        except requests.JSONDecodeError as e:
            logger.error("Didn't receive valid JSON in response")
            logger.error(e)
            raise

    @staticmethod
    def get_headers(API_key: Optional[str]=None, user_pass: Optional[str]=None, has_content=False) -> dict[str, str]:

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

    @staticmethod
    def get_url(method_name: str,
                domain: Optional[str]=None,
                app_path: Optional[str]=None,
                company_id: Optional[str]=None):

        domain = domain or EpicorCommunicator.url_domain
        app_path = app_path or EpicorCommunicator.url_app_path
        company_id = company_id or EpicorCommunicator.company_ID
        return f"{domain}/{app_path}/api/v2/odata/{company_id}/Ice.LIB.FileStoreSvc/{method_name}"


class Reporting_Statistics:

    start_time: float

    @staticmethod
    def initialize_reporting():
        Reporting_Statistics.start_time = time.time()

    @staticmethod
    def log_timing_metrics(response: requests.Response):

        total_time: float   = round(time.time() - Reporting_Statistics.start_time, 3)
        elapsed_sec: float  = round(response.elapsed.total_seconds(), 3)
        content_size: float = round(len(response.content) / 2 ** 20, 3)

        logger.debug(f"Server took {elapsed_sec} seconds. Request took {total_time} seconds. Returned {content_size} MiB")


class File_Operations:

    @staticmethod
    def encode_file(path: str) -> str:

        with open(path, 'rb') as f:
            ret = base64.b64encode(f.read()).decode(encoding='utf-8')
        
        return ret

    @staticmethod
    def decode_file(contents: str, path: str) -> None:

        image_data = base64.b64decode(contents)
        
        with open(path, 'wb') as f:
            f.write(image_data)
