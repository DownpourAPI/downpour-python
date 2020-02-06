import requests
from typing import List, Union


#################
# Model Classes #
#################
class Torrent:
    def __init__(self, torrent_hash: str, torrent_details: dict):
        self.torrent_hash: str = torrent_hash
        self.max_download_speed: int = torrent_details.get("max_download_speed", None)
        self.upload_payload_rate: int = torrent_details.get("upload_payload_rate", None)
        self.download_payload_rate: int = torrent_details.get("download_payload_rate", None)
        self.num_peers: int = torrent_details.get("num_peers", None)
        self.ratio: float = torrent_details.get("ratio", None)
        self.total_peers: int = torrent_details.get("total_peers", None)
        self.max_upload_speed: int = torrent_details.get("max_upload_speed", None)
        self.state: str = torrent_details.get("state", None)
        self.distributed_copies: float = torrent_details.get("distributed_copies", None)
        self.save_path: str = torrent_details.get("save_path", None)
        self.progress: float = torrent_details.get("progress", None)
        self.time_added: float = torrent_details.get("time_added", None)
        self.tracker_host: str = torrent_details.get("tracker_host", None)
        self.total_uploaded: int = torrent_details.get("total_uploaded", None)
        self.total_done: int = torrent_details.get("total_done", None)
        self.total_wanted: int = torrent_details.get("total_wanted", None)
        self.total_seeds: int = torrent_details.get("total_seeds", None)
        self.seeds_peers_ratio: float = torrent_details.get("seeds_peers_ratio", None)
        self.num_seeds: int = torrent_details.get("num_seeds", None)
        self.name: str = torrent_details.get("name", None)
        self.is_auto_managed: bool = torrent_details.get("is_auto_managed", None)
        self.queue: int = torrent_details.get("queue", None)
        self.eta: int = torrent_details.get("eta", None)

    def __repr__(self):
        return f"{self.name} - {self.progress}% Complete - Ratio: {self.ratio}"


class Error:
    def __init__(self, error: dict):
        self.message: str = error.get("message", None)
        self.code: int = error.get("code", None)


class Stats:
    def __init__(self, stats_block: dict):
        self.upload_protocol_rate: int = stats_block.get("upload_protocol_rate", None)
        self.max_upload: float = stats_block.get("max_upload", None)
        self.download_protocol_rate: int = stats_block.get("download_protocol_rate", None)
        self.download_rate: int = stats_block.get("download_rate", None)
        self.has_incoming_connections: bool = stats_block.get("has_incoming_connections", None)
        self.num_connections: int = stats_block.get("num_connections", None)
        self.max_download: float = stats_block.get("max_download", None)
        self.upload_rate: int = stats_block.get("", None)
        self.dht_nodes: int = stats_block.get("upload_rate", None)
        self.free_space: int = stats_block.get("free_space", None)
        self.max_num_connections: int = stats_block.get("max_num_connections", None)


class StatusResult:
    def __init__(self, status_block: dict):
        self.stats: Stats = Stats(status_block.get("stats", None))
        self.connected: bool = status_block.get("connected", False)

        all_torrents: List[Torrent] = []
        for torrent_hash, details in status_block.get("torrents", None).items():  # TODO: Test for None
            all_torrents.append(Torrent(
                torrent_hash,
                details
            ))
        self.torrents: List[Torrent] = all_torrents


class ApiResponse:
    def __init__(self, response_json: dict):
        response_id = response_json.get("id", None)
        result = parse_result(response_json.get("result", None))
        error = response_json.get("error", None)

        self.id: int = response_id
        self.result: Union[None, bool, StatusResult] = result
        self.error: Error = Error(error) if error else None
        self.success: bool = self.result and not self.error


def parse_result(result):
    if result is None or type(result) == bool:
        return result

    return StatusResult(result)


######################
# Main Session Class #
######################
class DelugeWebUISession:
    def __init__(self, api_endpoint: str, password: str):
        """Initialise a DelugeWebSession which is authenticated to the provided endpoint"""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.api_endpoint = api_endpoint
        self.login(api_endpoint, password)

    def login(self, api_endpoint: str, password: str):
        """Makes an auth request to the provided endpoint and adds the Session Cookie to this Session's Headers dict"""
        payload = {
            "method": "auth.login",
            "params": [password],
            "id": 1
        }

        login_response = requests.post(api_endpoint, json=payload, headers=self.headers)

        api_response = ApiResponse(login_response.json())

        if api_response.success:
            session_id = requests.utils.dict_from_cookiejar(login_response.cookies)["_session_id"]
            self.headers["Cookie"] = f"_session_id={session_id}"

    def add_magnet(self, magnet_link: str):
        """Add a magnet to a Deluge session."""
        payload = {
            {
                "method": "web.add_torrents",
                "params":
                    [
                        [
                            {
                                "path": magnet_link,
                                "options":
                                    {
                                        "file_priorities": [],
                                        "add_paused": False,
                                        "compact_allocation": False,
                                        "download_location": "",
                                        "move_completed": False,
                                        "move_completed_path": "",
                                        "max_connections": -1,
                                        "max_download_speed": -1,
                                        "max_upload_slots": -1,
                                        "max_upload_speed": -1,
                                        "prioritize_first_last_pieces": False
                                    }
                            }
                        ]
                    ],
                "id": 1
            }
        }

        add_magnet_result = ApiResponse(requests.post(self.api_endpoint, json=payload, headers=self.headers).json())

        if add_magnet_result.success:
            pass
        else:
            raise

    def add_torrent_file(self, torrent_file_path: str):
        raise NotImplementedError

    def get_torrent_details(self, torrent_hash):
        raise NotImplementedError

    def set_max_ratio(self, torrent_hash: str, max_ratio: int):
        payload = {
            "method": "core.set_torrent_options",
            "params":
                [
                    [torrent_hash],
                    {
                        "stop_at_ratio": True,
                        "stop_ratio": max_ratio
                    }
                ],
            "id": 1
        }

        set_ratio_response = ApiResponse(requests.post(self.api_endpoint, json=payload, headers=self.headers).json())

        if set_ratio_response.success:
            pass
        else:
            raise

    def list_all_torrents(self) -> List[Torrent]:
        payload = {
            "method": "web.update_ui",
            "params":
                [
                    [
                        "queue",
                        "name",
                        "total_wanted",
                        "state",
                        "progress",
                        "num_seeds",
                        "total_seeds",
                        "num_peers",
                        "total_peers",
                        "download_payload_rate",
                        "upload_payload_rate",
                        "eta",
                        "ratio",
                        "distributed_copies",
                        "is_auto_managed",
                        "time_added",
                        "tracker_host",
                        "save_path",
                        "total_done",
                        "total_uploaded",
                        "max_download_speed",
                        "max_upload_speed",
                        "seeds_peers_ratio"
                    ],
                    {}
                ],
            "id": 1
        }

        info_result = ApiResponse(requests.post(self.api_endpoint, json=payload, headers=self.headers).json())

        if info_result.success:
            return info_result.result.torrents

    def remove_torrent(self, torrent_hash: str):
        payload = {
            "method": "core.remove_torrent",
            "params": [
                torrent_hash,
                True
            ],
            "id": 1
        }

        remove_torrent_response = ApiResponse(requests.post(self.api_endpoint, json=payload, headers=self.headers).json())

        if remove_torrent_response.success:
            pass
        else:
            raise

    def pause_torrent(self, torrent_hash: str):
        raise NotImplementedError

    def resume_torrent(self, torrent_hash: str):
        raise NotImplementedError
