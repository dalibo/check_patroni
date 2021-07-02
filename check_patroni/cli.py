import requests


def check_is_master(address: str = "127.0.0.1", port: int = 8008):
    r = requests.get(f"{address}:{int(port)}/leader")
    return r.status_code == 200


def check_is_replica(address: str = "127.0.0.1", port: int = 8008):
    r = requests.get(f"{address}:{int(port)}/replica")
    return r.status_code == 200


def main() -> None:
    print(check_is_master())
    print(check_is_replica())
    print("allgood")
