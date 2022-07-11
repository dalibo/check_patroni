import hashlib
import json
import logging
from collections import Counter

import nagiosplugin
from typing import Iterable, Union

from .types import PatroniResource, ConnectionInfo, handle_unknown

_log = logging.getLogger("nagiosplugin")


def replace_chars(text: str) -> str:
    return text.replace("'", "").replace(" ", "_")


class ClusterNodeCount(PatroniResource):
    def probe(self: "ClusterNodeCount") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("cluster")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)
        role_counters: Counter[str] = Counter()
        roles = []
        status_counters: Counter[str] = Counter()
        statuses = []

        for member in item_dict["members"]:
            roles.append(replace_chars(member["role"]))
            statuses.append(replace_chars(member["state"]))
        role_counters.update(roles)
        status_counters.update(statuses)

        # The actual check: members, running state
        yield nagiosplugin.Metric("members", len(item_dict["members"]))
        yield nagiosplugin.Metric("state_running", status_counters["running"])

        # The performance data : role
        for role in role_counters:
            yield nagiosplugin.Metric(
                f"role_{role}", role_counters[role], context="member_roles"
            )

        # The performance data : statuses (except running)
        for state in status_counters:
            if state != "running":
                yield nagiosplugin.Metric(
                    f"state_{state}", status_counters[state], context="member_statuses"
                )


class ClusterHasLeader(PatroniResource):
    def probe(self: "ClusterHasLeader") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("cluster")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)
        is_leader_found = False
        for member in item_dict["members"]:
            if member["role"] == "leader" and member["state"] == "running":
                is_leader_found = True
                break

        return [
            nagiosplugin.Metric(
                "has_leader",
                1 if is_leader_found else 0,
            )
        ]


class ClusterHasLeaderSummary(nagiosplugin.Summary):
    def ok(self: "ClusterHasLeaderSummary", results: nagiosplugin.Result) -> str:
        return "The cluster has a running leader."

    @handle_unknown
    def problem(self: "ClusterHasLeaderSummary", results: nagiosplugin.Result) -> str:
        return "The cluster has no running leader."


class ClusterHasReplica(PatroniResource):
    def __init__(
        self: "ClusterHasReplica",
        connection_info: ConnectionInfo,
        max_lag: Union[int, None],
    ):
        super().__init__(connection_info)
        self.max_lag = max_lag

    def probe(self: "ClusterHasReplica") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("cluster")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)
        replicas = []
        healthy_replica = 0
        unhealthy_replica = 0
        for member in item_dict["members"]:
            # FIXME are there other acceptable states
            if member["role"] == "replica":
                if member["state"] == "running" and member["lag"] != "unknown":
                    replicas.append({"name": member["name"], "lag": member["lag"]})
                    if self.max_lag is None or self.max_lag >= int(member["lag"]):
                        healthy_replica += 1
                        continue
                unhealthy_replica += 1

        # The actual check
        yield nagiosplugin.Metric("healthy_replica", healthy_replica)

        # The performance data : unhealthy replica count, replicas lag
        yield nagiosplugin.Metric("unhealthy_replica", unhealthy_replica)
        for replica in replicas:
            yield nagiosplugin.Metric(
                f"{replica['name']}_lag", replica["lag"], context="replica_lag"
            )


# FIXME is this needed ??
# class ClusterHasReplicaSummary(nagiosplugin.Summary):
#     def ok(self, results):
#     def problem(self, results):


class ClusterConfigHasChanged(PatroniResource):
    def __init__(
        self: "ClusterConfigHasChanged",
        connection_info: ConnectionInfo,
        config_hash: str,  # Always contains the old hash
        state_file: str,  # Only used to update the hash in the state_file (when needed)
    ):
        super().__init__(connection_info)
        self.state_file = state_file
        self.config_hash = config_hash

    def probe(self: "ClusterConfigHasChanged") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("config")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        new_hash = hashlib.md5(r.data).hexdigest()

        old_hash = self.config_hash
        if self.state_file is not None:
            _log.debug(f"Saving new hash to state file / cookie {self.state_file}")
            cookie = nagiosplugin.Cookie(self.state_file)
            cookie.open()
            cookie["hash"] = new_hash
            cookie.commit()
            cookie.close()

        _log.debug(f"hash info: old hash {old_hash}, new hash {new_hash}")

        return [
            nagiosplugin.Metric(
                "is_configuration_changed",
                1 if new_hash != old_hash else 0,
            )
        ]


class ClusterConfigHasChangedSummary(nagiosplugin.Summary):
    def __init__(self: "ClusterConfigHasChangedSummary", config_hash: str) -> None:
        self.old_config_hash = config_hash

    # Note: It would be helpful to display the old / new hash here. Unfortunately, it's not a metric.
    # So we only have the old / expected one.
    def ok(self: "ClusterConfigHasChangedSummary", results: nagiosplugin.Result) -> str:
        return f"The hash of patroni's dynamic configuration has not changed ({self.old_config_hash})."

    @handle_unknown
    def problem(
        self: "ClusterConfigHasChangedSummary", results: nagiosplugin.Result
    ) -> str:
        return "The hash of patroni's dynamic configuration has changed. The old hash was {self.old_config_hash}."


class ClusterIsInMaintenance(PatroniResource):
    def probe(self: "ClusterIsInMaintenance") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("cluster")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)

        # The actual check
        return [
            nagiosplugin.Metric(
                "is_in_maintenance",
                1 if "pause" in item_dict and item_dict["pause"] else 0,
            )
        ]
