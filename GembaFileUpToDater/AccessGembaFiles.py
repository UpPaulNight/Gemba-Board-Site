from datetime import datetime
from typing import Any, Literal, Optional, TypedDict

from PaulsLoggerManagement import setup_logger

from GembaFileUpToDater.BAQMethod import BAQMethod
from GembaFileUpToDater.epicor_communications import EpicorCommunicator

from GembaFileUpToDater.parse_args import should_show_debug
import logging
logger = setup_logger("AccessGembaFiles", level=(logging.DEBUG if should_show_debug() else logging.INFO))

class GembaFileReference(TypedDict):
    Company: str
    FileSysRowID: str
    FileName: str
    PostDate: str
    Key2: str
    Delete: bool
    RowMod: Literal['U', 'A', 'D', '']
    RowIdent: str
    SysRowID: str

class AccessGembaFiles:
    
    @staticmethod
    def parse_raw_result(raw: dict) -> GembaFileReference:
        return {
            'Company': raw['UD05_Company'],
            'FileName': raw['UD05_Character01'],
            'PostDate': raw['UD05_ShortChar01'],
            'FileSysRowID': raw['UD05_Key1'],
            'Key2': raw['UD05_Key2'],
            'Delete': raw['UD05_CheckBox02'],
            'RowMod': raw['RowMod'] or '',
            'RowIdent': raw['RowIdent'],
            'SysRowID': raw['SysRowID'],
        }
    
    @staticmethod
    def stringify_GembaFile(gemba_file: GembaFileReference) -> dict:
        return {
            'UD05_Company': gemba_file['Company'],
            'UD05_Key1': gemba_file['FileSysRowID'],
            'UD05_Key2': gemba_file['Key2'],
            'UD05_Character01': gemba_file['FileName'],
            'UD05_CheckBox02': gemba_file['Delete'],
            'UD05_ShortChar01': gemba_file['PostDate'],
            'RowMod': gemba_file['RowMod'],
            'RowIdent': gemba_file['RowIdent'],
            'SysRowID': gemba_file['SysRowID'],
        }
    
    @staticmethod
    def get_records(company_ID: Optional[str]=None,
                    API_key: Optional[str]=None,
                    user_pass: Optional[str]=None,
                    timeout: float=60.0) -> list[GembaFileReference]:
        """ Execute the BAQ without updates. """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)
        url = AccessGembaFiles.__get_url(odata_method='Data')

        logger.debug('Sending GET request for AccessGembaFiles UBAQ')

        data = BAQMethod.get_records(url, company_ID, API_key, user_pass, timeout)
        
        if len(data) == 0:
            logger.warning('No data in response.')

        return [AccessGembaFiles.parse_raw_result(g) for g in data]

    @staticmethod
    def delete_record(gemba_record: GembaFileReference,
                      company_ID: Optional[str]=None,
                      API_key: Optional[str]=None,
                      user_pass: Optional[str]=None,
                      timeout: float=60.0) -> None:
        """ Delete a record by setting the Delete flag set up for this.

        This returns no data because it is a standard directive that actually
        does the deleting and it does not appear in the results.
        """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)

        # Set the delete flag and set RowMod
        gemba_record['Delete'] = True
        gemba_record['RowMod'] = 'D'

        AccessGembaFiles.patch_record(gemba_record, company_ID, API_key, user_pass, timeout)

    @staticmethod
    def get_new(company_ID: Optional[str]=None,
                API_key: Optional[str]=None,
                user_pass: Optional[str]=None,
                timeout: float=60.0) -> GembaFileReference:
        """ Get a new record.
            
            I'm pretty sure you can just PATCH in a new record if you want to,
            but getting a new record like this will work with whatever GetNew
            method directives are set up.
        """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)
        url = AccessGembaFiles.__get_url(odata_method='GetNew')

        logger.debug('Sending GET request for AccessGembaFiles UBAQ')

        new_record = BAQMethod.get_new(url, company_ID, API_key, user_pass, timeout)
        
        gemba_file = AccessGembaFiles.parse_raw_result(new_record)
        gemba_file['PostDate'] = datetime.now().isoformat()

        return gemba_file

    @staticmethod
    def patch_record(gemba_record: GembaFileReference,
                     company_ID: Optional[str]=None,
                     API_key: Optional[str]=None,
                     user_pass: Optional[str]=None,
                     timeout: float=60.0) -> dict[Literal['value'], list[dict[str, Any]]]:
        """ Strict patch with a record """

        company_ID, API_key, user_pass = EpicorCommunicator.get_id_api_pass(company_ID, API_key, user_pass)
        url = AccessGembaFiles.__get_url(odata_method='Data')

        logger.debug('Sending PATCH request for AccessGembaFiles UBAQ')

        payload = AccessGembaFiles.stringify_GembaFile(gemba_record)

        return BAQMethod.patch_record(url, payload, company_ID, API_key, user_pass, timeout)
    
    @staticmethod
    def __get_url(odata_method: str,
                domain: Optional[str]=None,
                app_path: Optional[str]=None,
                company_id: Optional[str]=None):

        domain = domain or EpicorCommunicator.url_domain
        app_path = app_path or EpicorCommunicator.url_app_path
        company_id = company_id or EpicorCommunicator.company_ID
        return f"{domain}/{app_path}/api/v2/odata/{company_id}/BaqSvc/AccessGembaFiles/{odata_method}"

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
