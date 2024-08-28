# This is a test python file to mess around with other things
# from dotenv import load_dotenv
import logging
import os
from dotenv import load_dotenv
import json

from deluge_client import DelugeRPCClient

log = logging.getLogger(__name__)
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def find_files_without_hardlink():
    list_of_files_without_hardlink = []

    target_path = "./"
    file_list = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]

    for file in file_list:
        file_path: str = os.path.join(target_path, file)
        file_has_hardlink = True if os.stat(file_path).st_nlink > 1 else False
        if not file_has_hardlink:
            list_of_files_without_hardlink.append(file_path)


if __name__ == "__main__":
    file_list = find_files_without_hardlink()
    log.info(file_list)

    # client: DelugeRPCClient = DelugeRPCClient(os.getenv("DELUGE_HOST"), 58846, os.getenv("DELUGE_RPC_USERNAME"), os.getenv("DELUGE_RPC_PASSWORD"), decode_utf8 = True)
    # client.connect()

    # session_stats = client.call('core.get_session_status', [
    #     'payload_download_rate',
    #     'payload_upload_rate',
    #     'total_download',
    #     'total_upload',
    # ])

    # log.info(session_stats)

    # torrent_list = client.call('core.get_torrents_status', {}, [
    #     # 'active_time',
    #     # 'all_time_download',
    #     # 'download_payload_rate',
    #     # 'finished_time',
    #     # 'hash',
    #     # 'label', # Available when the plugin 'label' is enabled
    #     'name',
    #     # 'num_peers',
    #     # 'num_seeds',
    #     # 'progress',
    #     # 'ratio',
    #     'seeding_time',
    #     'state',
    #     # 'time_added',
    #     # 'time_since_transfer',
    #     # 'total_peers',
    #     # 'total_seeds',
    #     # 'total_size',
    #     # 'total_uploaded',
    #     # 'trackers',
    #     # 'upload_payload_rate',
    # ])

    # log.info(json.dumps(torrent_list, indent=4))

    # client.disconnect()