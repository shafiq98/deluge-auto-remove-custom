# This is a test python file to mess around with other things
# from dotenv import load_dotenv
import logging
import os
from dotenv import load_dotenv
import json
import datetime
import time

from deluge_client import DelugeRPCClient

log = logging.getLogger(__name__)

logging.basicConfig(
    # filename="debug.log",
    # filemode='w',
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()


def find_files_without_hardlink():
    list_of_files_without_hardlink = []

    target_path = "/data"
    file_list = [
        f
        for f in os.listdir(target_path)
        if os.path.isfile(os.path.join(target_path, f))
    ]

    for file in file_list:
        file_path: str = os.path.join(target_path, file)
        file_has_hardlink = True if (os.stat(file_path).st_nlink > 1) else False
        if not file_has_hardlink:
            list_of_files_without_hardlink.append(file)

    return list_of_files_without_hardlink


def find_folders_without_any_hardlinked_files():
    list_of_folders_without_hardlink = []

    target_path = "/data"
    folder_list = [f.path for f in os.scandir(target_path) if f.is_dir()]
    for folder in folder_list:
        if not find_any_hardlinked_files_in_folder(folder):
            list_of_folders_without_hardlink.append(
                folder.removeprefix(f"{target_path}/")
            )

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

    torrent_dict = client.call(
        "core.get_torrents_status",
        {},
        [
            "active_time",
            "all_time_download",
            # 'download_payload_rate',
            # 'finished_time',
            # 'hash',
            # 'label', # Available when the plugin 'label' is enabled
            "name",
            # 'num_peers',
            # 'num_seeds',
            # 'progress',
            # 'ratio',
            "seeding_time",
            # 'state',
            # 'time_added',
            # 'time_since_transfer',
            # 'total_peers',
            # 'total_seeds',
            # 'total_size',
            # 'total_uploaded',
            # 'trackers',
            # 'upload_payload_rate'
        ],
    )
    # log.info(json.dumps(torrent_dict, indent=4))
    # log.info(client.call('daemon.get_method_list'))
    return torrent_dict


def get_torrents_to_delete(torrent_dict: dict, list_of_content_to_delete) -> set[str]:
    MIN_TIME: int = 864000

    torrents_to_delete_dict = {}
    for key, value in torrent_dict.items():
        if (
            value.get("name") in list_of_content_to_delete
            and value.get("seeding_time") > MIN_TIME
        ):
            torrents_to_delete_dict[key] = value

    return torrents_to_delete_dict.keys()


def remove_torrents_by_torrent_id(
    client: DelugeRPCClient, torrent_ids_to_delete: list[str]
):
    # log.info(torrent_ids_to_delete)

    result = client.call("core.remove_torrents", torrent_ids_to_delete, True)
    # log.info(f"Torrents could be removed successfully: {result}")
    return result


def execute_deluge_agent() -> list[str]:
    list_of_content_to_delete = []

    list_of_files_without_hardlink = find_files_without_hardlink()
    # log.info(list_of_files_without_hardlink)
    list_of_folders_without_hardlink = find_folders_without_any_hardlinked_files()
    # log.info(list_of_folders_without_hardlink)

    list_of_content_to_delete = (
        list_of_files_without_hardlink + list_of_folders_without_hardlink
    )
    # log.info(list_of_content_to_delete)

    torrent_ids_to_delete: list[str] = []
    missed_torrents: list[str] = []
    try:
        client: DelugeRPCClient = DelugeRPCClient(
            os.getenv("DELUGE_HOST"),
            58846,
            os.getenv("DELUGE_RPC_USERNAME"),
            os.getenv("DELUGE_RPC_PASSWORD"),
            decode_utf8=True,
        )
        client.connect()

        torrent_dict = get_dict_of_all_torrents(client=client)
        # log.info(json.dumps(torrent_dict, indent=4))

        torrent_ids_to_delete.extend(
            list(
                get_torrents_to_delete(
                    torrent_dict=torrent_dict,
                    list_of_content_to_delete=list_of_content_to_delete,
                )
            )
        )
        log.info(f"Torrents to delete: {torrent_ids_to_delete}")
        if len(torrent_ids_to_delete) != 0:
            missed_torrents.extend(
                remove_torrents_by_torrent_id(
                    client=client, torrent_ids_to_delete=torrent_ids_to_delete
                )
            )
            log.info(f"These torrents need to be deleted but werent: {missed_torrents}")
        else:
            log.info("There are no torrents to delete")

    finally:
        client.disconnect()

    return missed_torrents


if __name__ == "__main__":
    last_run_time: datetime.datetime = datetime.datetime.now()
    backoff_period_seconds: int = 1 * 60 * 60  # 1 hour in seconds
    while True:
        now: datetime.datetime = datetime.datetime.now()
        last_run_seconds_ago = (now - last_run_time).seconds
        if last_run_seconds_ago > backoff_period_seconds:
            log.info("Cleaning up Deluge downloads now...")
            torrents_not_deleted: list[str] = execute_deluge_agent()
            log.info(f"Could not delete the following torrents: {torrents_not_deleted}")
            last_run_time = now
        else:
            time.sleep(backoff_period_seconds)
