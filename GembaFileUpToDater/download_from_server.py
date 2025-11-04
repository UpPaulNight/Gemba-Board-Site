import json
import os
from typing import TypedDict
from PaulsLoggerManagement import setup_logger
import pandas as pd
from GembaFileUpToDater.epicor_communications import File_Operations, Ice_LIB_FileStoreSvc, EpicorCommunicator
from GembaFileUpToDater.AccessGembaFiles import AccessGembaFiles
from dotenv import dotenv_values

class FileIDPair(TypedDict):
    SysID: str
    FileName: str

from GembaFileUpToDater.parse_args import should_show_debug
import logging
logger = setup_logger("AccessGembaFiles", level=(logging.DEBUG if should_show_debug() else logging.INFO))
ID_FILE = 'downloaded_ids.json'

my_dotenv_values: dict[str, str] = dotenv_values('.env') # type: ignore[reportAssignmentType, assignment]
EpicorCommunicator.API_key = my_dotenv_values['DOWNLOAD_KEY']
EpicorCommunicator.user_pass = my_dotenv_values['DOWNLOAD_PASS']
EpicorCommunicator.company_ID = 'PAUL01'
EpicorCommunicator.url_domain = 'https://kinetic.paulsmachine.com'
EpicorCommunicator.url_app_path = 'Kinetic'

def __get_downloaded_file_ids() -> list[FileIDPair]:
    
    if not os.path.exists(ID_FILE):
        return []
    
    try:
        with open(ID_FILE, 'r') as f:
            return json.load(f)

    except json.JSONDecodeError:
        return []
    
def __store_downloaded_file_ids(id_pairs: list[FileIDPair]) -> None:

    with open(ID_FILE, 'w+') as f:
        return json.dump(id_pairs, f)

def download_new_files() -> None:

    # Get a list of the existing files already downloaded and a list of those on
    # the server.
    existing_files = __get_downloaded_file_ids()
    online_files = AccessGembaFiles.get_records()
    logger.info(f'Found {len(existing_files)} local files and {len(online_files)} files on the server.')

    # Put those into a DataFrame then sort the DataFrame so that we can get the
    # list of newest files.
    server_files_df = pd.DataFrame(online_files)
    server_files_df = server_files_df.astype({'PostDate': 'datetime64[ns]'})
    server_files_df = server_files_df.sort_values(['FileName', 'PostDate'], ascending=[True, False])
    newest_files_df_2 = server_files_df.groupby(['FileName']).head(1)
    newest_files: list[FileIDPair] = [
        {'FileName': row['FileName'], 'SysID': row['FileSysRowID']}
        for _, row in newest_files_df_2.iterrows()
    ]

    # Get a list of old files that we have downloaded. Old files will be those
    # where the SysID is not in the newest ids.
    newest_ids = [f['SysID'] for f in newest_files]
    old_files = [f for f in existing_files if f['SysID'] not in newest_ids]
    logger.info(f'{len(old_files)} are not the latest on the server')


    # Files we need to download will be those not in the old list
    old_file_names = [o['FileName'] for o in old_files]
    files_need_updating = [g for g in newest_files if g['FileName'] in old_file_names]

    # There also may be new files. Get a list of the files that we don't have
    # but are on the server.
    existing_file_names = [e['FileName'] for e in existing_files]
    files_dont_have = [f for f in newest_files if f['FileName'] not in existing_file_names]
    logger.info(f'There are {len(files_dont_have)} new files that are not yet local.')

    
    # Lastly, files not updated are files that are not "old"
    files_not_updated = [f for f in existing_files if f not in old_files]
    logger.info(f'{len(files_not_updated)} will remain unchanged.')
    
    # Make the svg_files folder if it doesn't exist
    os.makedirs('svg_files', exist_ok=True)

    # Loop over all of those files and download them
    files_updated: list[FileIDPair] = []
    for file in files_need_updating + files_dont_have:

        file_bytes = Ice_LIB_FileStoreSvc.read_all_bytes(file['SysID'])
        if file_bytes is None:
            logger.warning(f'Failed to download {file["FileName"]} at {file["SysID"]}')
            continue
        
        logger.info(f'Updating {file["FileName"]}')
        write_to = f'svg_files/{file["FileName"]}'
        bytes_str = file_bytes['returnObj']
        File_Operations.decode_file(contents=bytes_str, path=write_to)

        files_updated.append(file)


    # Update the record of what files we have
    __store_downloaded_file_ids(files_updated + files_not_updated)
