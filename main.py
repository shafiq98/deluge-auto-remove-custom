# This is a test python file to mess around with other things
# from dotenv import load_dotenv
import logging
import os
from dotenv import load_dotenv
import json

from deluge_client import DelugeRPCClient

log = logging.getLogger(__name__)

logging.basicConfig(
    # filename="debug.log",
    # filemode='w',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

load_dotenv()

def find_files_without_hardlink():
    list_of_files_without_hardlink = []

    target_path = "/data"
    file_list = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]

    for file in file_list:
        file_path: str = os.path.join(target_path, file)
        file_has_hardlink = True if (os.stat(file_path).st_nlink > 1) else False
        if not file_has_hardlink:
            list_of_files_without_hardlink.append(file)
    
    return list_of_files_without_hardlink

def find_folders_without_any_hardlinked_files():
    list_of_folders_without_hardlink = []

    target_path = "/data"
    folder_list = [ f.path for f in os.scandir(target_path) if f.is_dir() ]
    for folder in folder_list:
        if not find_any_hardlinked_files_in_folder(folder):
            list_of_folders_without_hardlink.append(folder.removeprefix(f"{target_path}/"))

    return list_of_folders_without_hardlink

def find_any_hardlinked_files_in_folder(folder_path: str) -> bool:
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Get the link count of the file
            link_count = os.stat(file_path).st_nlink
            if link_count > 1:
                return True
    return False

def get_dict_of_all_torrents(client: DelugeRPCClient) -> dict:
    # session_stats = client.call('core.get_session_status', [
    #     'payload_download_rate',
    #     'payload_upload_rate',
    #     'total_download',
    #     'total_upload'
    # ])

    # log.info(session_stats)

    torrent_dict = client.call('core.get_torrents_status', {}, [
        'active_time',
        'all_time_download',
        # 'download_payload_rate',
        # 'finished_time',
        # 'hash',
        # 'label', # Available when the plugin 'label' is enabled
        'name',
        # 'num_peers',
        # 'num_seeds',
        # 'progress',
        # 'ratio',
        'seeding_time',
        # 'state',
        # 'time_added',
        # 'time_since_transfer',
        # 'total_peers',
        # 'total_seeds',
        # 'total_size',
        # 'total_uploaded',
        # 'trackers',
        # 'upload_payload_rate'
    ])
    # log.info(json.dumps(torrent_dict, indent=4))
    # log.info(client.call('daemon.get_method_list'))
    return torrent_dict

def get_torrents_to_delete(torrent_dict: dict, list_of_content_to_delete) -> list[str]:
    MIN_TIME: int = 864000

    torrents_to_delete_dict = {}
    for key, value in torrent_dict.items():
        if value.get('name') in list_of_content_to_delete and value.get('seeding_time') > MIN_TIME:
            torrents_to_delete_dict[key] = value

    return torrents_to_delete_dict.keys()

def remove_torrents_by_torrent_id(client: DelugeRPCClient, torrent_ids_to_delete: list[str]):
    # log.info(torrent_ids_to_delete)

    result = client.call('core.remove_torrents', torrent_ids_to_delete, True)
    # log.info(f"Torrents could be removed successfully: {result}")
    return result
    

if __name__ == "__main__":
    list_of_content_to_delete = []

    list_of_files_without_hardlink = find_files_without_hardlink()
    # log.info(list_of_files_without_hardlink)
    list_of_folders_without_hardlink = find_folders_without_any_hardlinked_files()
    # log.info(list_of_folders_without_hardlink)

    list_of_content_to_delete = list_of_files_without_hardlink + list_of_folders_without_hardlink
    # log.info(list_of_content_to_delete)

    # torrent_ids_to_delete = ['a863f6f87d4a9112655112fabc72682b4cb52da0', '345e75687e93934b1be57326d3709fa1476a3fed', 'a4746e0a9633514e63fef4ff51dfa571bf396471', 'd7da3a3919fb958ee1ce70b2bff91796f3788150', '66c8eb4c202ec79c6eef9094d63d93d013b1f2eb']
    
    try:
        client: DelugeRPCClient = DelugeRPCClient(os.getenv("DELUGE_HOST"), 58846, os.getenv("DELUGE_RPC_USERNAME"), os.getenv("DELUGE_RPC_PASSWORD"), decode_utf8 = True)
        client.connect()
    
        result = ""
        
        torrent_dict = get_dict_of_all_torrents(client=client)
        # log.info(json.dumps(torrent_dict, indent=4))

        torrent_ids_to_delete = list(get_torrents_to_delete(torrent_dict=torrent_dict, list_of_content_to_delete=list_of_content_to_delete))
        log.info(f"Torrents to delete: {torrent_ids_to_delete}")
        if (len(torrent_ids_to_delete) != 0):
            result = remove_torrents_by_torrent_id(client=client, torrent_ids_to_delete=torrent_ids_to_delete)
            log.info(f"These torrents need to be deleted but werent: {result}")
        else:
            log.info("There are no torrents to delete")

    finally:
        client.disconnect()
    
