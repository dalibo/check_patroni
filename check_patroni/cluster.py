from collections import Counter
import hashlib
import json
import logging
import nagiosplugin
from typing import Iterable

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
                f"role_{role}", role_counters[role], context="members_roles"
            )

        # The performance data : statuses (except running)
        for state in status_counters:
            if state != "running":
                yield nagiosplugin.Metric(
                    f"state_{state}", status_counters[state], context="members_statuses"
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
    def probe(self: "ClusterHasReplica") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("cluster")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)
        replicas = []
        for member in item_dict["members"]:
            # FIXME are there other acceptable states
            if member["role"] == "replica" and member["state"] == "running":
                # FIXME which lag ?
                replicas.append({"name": member["name"], "lag": member["lag"]})
                break

        # The actual check
        yield nagiosplugin.Metric("replica_count", len(replicas))

        # The performance data : replicas lag
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
        config_hash: str,
        state_file: str,
    ):
        super().__init__(connection_info)
        self.state_file = state_file
        self.config_hash = config_hash

    def probe(self: "ClusterConfigHasChanged") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("config")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        new_hash = hashlib.md5(r.data).hexdigest()

        if self.state_file is not None:
            _log.debug(f"Using state file / cookie {self.state_file}")
            cookie = nagiosplugin.Cookie(self.state_file)
            cookie.open()
            old_hash = cookie.get("hash")
            cookie["hash"] = new_hash
            cookie.commit()
        else:
            _log.debug(f"Using input value {self.config_hash}")
            old_hash = self.config_hash

        _log.debug(f"hash info: old hash {old_hash}, new hash {new_hash}")

        return [
            nagiosplugin.Metric(
                "is_configuration_changed",
                1 if new_hash != old_hash else 0,
            )
        ]


class ClusterConfigHasChangedSummary(nagiosplugin.Summary):
    def ok(self: "ClusterConfigHasChangedSummary", results: nagiosplugin.Result) -> str:
        return "The hash of patroni's dynamic configuration has not changed."

    @handle_unknown
    def problem(
        self: "ClusterConfigHasChangedSummary", results: nagiosplugin.Result
    ) -> str:
        return "The hash of patroni's dynamic configuration has changed."


class ClusterIsInMaintenance(PatroniResource):
    def probe(self: "ClusterIsInMaintenance") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("cluster")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)

        # The actual check
        return [nagiosplugin.Metric("is_in_maintenance", 1 if "pause" in item_dict and item_dict["pause"] else 0)]
