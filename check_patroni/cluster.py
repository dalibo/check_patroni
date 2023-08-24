import hashlib
import json
from collections import Counter
from typing import Iterable, Union

import nagiosplugin

from . import _log
from .types import ConnectionInfo, PatroniResource, handle_unknown


def replace_chars(text: str) -> str:
    return text.replace("'", "").replace(" ", "_")


class ClusterNodeCount(PatroniResource):
    def probe(self: "ClusterNodeCount") -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("cluster")
        role_counters: Counter[str] = Counter()
        roles = []
        status_counters: Counter[str] = Counter()
        statuses = []

        for member in item_dict["members"]:
            roles.append(replace_chars(member["role"]))
            statuses.append(replace_chars(member["state"]))
        role_counters.update(roles)
        status_counters.update(statuses)

        # The actual check: members, healthy_members
        yield nagiosplugin.Metric("members", len(item_dict["members"]))
        yield nagiosplugin.Metric(
            "healthy_members",
            status_counters["running"] + status_counters.get("streaming", 0),
        )

        # The performance data : role
        for role in role_counters:
            yield nagiosplugin.Metric(
                f"role_{role}", role_counters[role], context="member_roles"
            )

        # The performance data : statuses (except running)
        for state in status_counters:
            yield nagiosplugin.Metric(
                f"state_{state}", status_counters[state], context="member_statuses"
            )


class ClusterHasLeader(PatroniResource):
    def probe(self: "ClusterHasLeader") -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("cluster")

        is_leader_found = False
        for member in item_dict["members"]:
            if (
                member["role"] in ("leader", "standby_leader")
                and member["state"] == "running"
            ):
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
        item_dict = self.rest_api("cluster")

        replicas = []
        healthy_replica = 0
        unhealthy_replica = 0
        sync_replica = 0
        for member in item_dict["members"]:
            # FIXME are there other acceptable states
            if member["role"] in ["replica", "sync_standby"]:
                # patroni 3.0.4 changed the standby state from running to streaming
                if (
                    member["state"] in ["running", "streaming"]
                    and member["lag"] != "unknown"
                ):
                    replicas.append(
                        {
                            "name": member["name"],
                            "lag": member["lag"],
                            "sync": 1 if member["role"] == "sync_standby" else 0,
                        }
                    )

                    if member["role"] == "sync_standby":
                        sync_replica += 1

                    if self.max_lag is None or self.max_lag >= int(member["lag"]):
                        healthy_replica += 1
                        continue
                unhealthy_replica += 1

        # The actual check
        yield nagiosplugin.Metric("healthy_replica", healthy_replica)
        yield nagiosplugin.Metric("sync_replica", sync_replica)

        # The performance data : unhealthy replica count, replicas lag
        yield nagiosplugin.Metric("unhealthy_replica", unhealthy_replica)
        for replica in replicas:
            yield nagiosplugin.Metric(
                f"{replica['name']}_lag", replica["lag"], context="replica_lag"
            )
            yield nagiosplugin.Metric(
                f"{replica['name']}_sync", replica["sync"], context="replica_sync"
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
        save: bool = False,  # Save the configuration
    ):
        super().__init__(connection_info)
        self.state_file = state_file
        self.config_hash = config_hash
        self.save = save

    def probe(self: "ClusterConfigHasChanged") -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("config")

        new_hash = hashlib.md5(json.dumps(item_dict).encode()).hexdigest()

        _log.debug("save result: %(issave)s", {"issave": self.save})
        old_hash = self.config_hash
        if self.state_file is not None and self.save:
            _log.debug(
                "saving new hash to state file / cookie %(state_file)s",
                {"state_file": self.state_file},
            )
            cookie = nagiosplugin.Cookie(self.state_file)
            cookie.open()
            cookie["hash"] = new_hash
            cookie.commit()
            cookie.close()

        _log.debug(
            "hash info: old hash %(old_hash)s, new hash %(new_hash)s",
            {"old_hash": old_hash, "new_hash": new_hash},
        )

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
        return f"The hash of patroni's dynamic configuration has changed. The old hash was {self.old_config_hash}."


class ClusterIsInMaintenance(PatroniResource):
    def probe(self: "ClusterIsInMaintenance") -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("cluster")

        # The actual check
        return [
            nagiosplugin.Metric(
                "is_in_maintenance",
                1 if "pause" in item_dict and item_dict["pause"] else 0,
            )
        ]


class ClusterHasScheduledAction(PatroniResource):
    def probe(self: "ClusterIsInMaintenance") -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("cluster")

        scheduled_switchover = 0
        scheduled_restart = 0
        if "scheduled_switchover" in item_dict:
            scheduled_switchover = 1

        for member in item_dict["members"]:
            if "scheduled_restart" in member:
                scheduled_restart += 1

        # The actual check
        yield nagiosplugin.Metric(
            "has_scheduled_actions",
            1 if (scheduled_switchover + scheduled_restart) > 0 else 0,
        )

        # The performance data : scheduled_switchover, scheduled action count
        yield nagiosplugin.Metric("scheduled_switchover", scheduled_switchover)
        yield nagiosplugin.Metric("scheduled_restart", scheduled_restart)
