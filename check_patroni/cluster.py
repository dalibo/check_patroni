import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Union

import nagiosplugin

from . import _log
from .types import ConnectionInfo, PatroniResource, handle_unknown


def replace_chars(text: str) -> str:
    return text.replace("'", "").replace(" ", "_")


class ClusterNodeCount(PatroniResource):
    def probe(self) -> Iterable[nagiosplugin.Metric]:
        def debug_member(member: Any, health: str) -> None:
            _log.debug(
                "Node %(node_name)s is %(health)s: role %(role)s state %(state)s.",
                {
                    "node_name": member["name"],
                    "health": health,
                    "role": member["role"],
                    "state": member["state"],
                },
            )

        # get the cluster info
        item_dict = self.rest_api("cluster")

        role_counters: Counter[str] = Counter()
        roles = []
        status_counters: Counter[str] = Counter()
        statuses = []
        healthy_member = 0

        for member in item_dict["members"]:
            state, role = member["state"], member["role"]
            roles.append(replace_chars(role))
            statuses.append(replace_chars(state))

            if role == "leader" and state == "running":
                healthy_member += 1
                debug_member(member, "healthy")
                continue

            if role in ["standby_leader", "replica", "sync_standby"] and (
                (self.has_detailed_states() and state == "streaming")
                or (not self.has_detailed_states() and state == "running")
            ):
                healthy_member += 1
                debug_member(member, "healthy")
                continue

            debug_member(member, "unhealthy")
        role_counters.update(roles)
        status_counters.update(statuses)

        # The actual check: members, healthy_members
        yield nagiosplugin.Metric("members", len(item_dict["members"]))
        yield nagiosplugin.Metric("healthy_members", healthy_member)

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
    def probe(self) -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("cluster")

        is_leader_found = False
        is_standby_leader_found = False
        is_standby_leader_in_arc_rec = False
        for member in item_dict["members"]:
            if member["role"] == "leader" and member["state"] == "running":
                is_leader_found = True
                break

            if member["role"] == "standby_leader":
                if member["state"] not in ["streaming", "in archive recovery"]:
                    # for patroni >= 3.0.4 any state would be wrong
                    # for patroni <  3.0.4 a state different from running would be wrong
                    if self.has_detailed_states() or member["state"] != "running":
                        continue

                if member["state"] in ["in archive recovery"]:
                    is_standby_leader_in_arc_rec = True

                is_standby_leader_found = True
                break
        return [
            nagiosplugin.Metric(
                "has_leader",
                1 if is_leader_found or is_standby_leader_found else 0,
            ),
            nagiosplugin.Metric(
                "is_standby_leader_in_arc_rec",
                1 if is_standby_leader_in_arc_rec else 0,
            ),
            nagiosplugin.Metric(
                "is_standby_leader",
                1 if is_standby_leader_found else 0,
            ),
            nagiosplugin.Metric(
                "is_leader",
                1 if is_leader_found else 0,
            ),
        ]


class ClusterHasLeaderSummary(nagiosplugin.Summary):
    def ok(self, results: nagiosplugin.Result) -> str:
        return "The cluster has a running leader."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        return "The cluster has no running leader or the standby leader is in archive recovery."


class ClusterHasReplica(PatroniResource):
    def __init__(self, connection_info: ConnectionInfo, max_lag: Union[int, None]):
        super().__init__(connection_info)
        self.max_lag = max_lag

    def probe(self) -> Iterable[nagiosplugin.Metric]:
        def debug_member(member: Any, health: str) -> None:
            _log.debug(
                "Node %(node_name)s is %(health)s: lag %(lag)s, state %(state)s, tl %(tl)s.",
                {
                    "node_name": member["name"],
                    "health": health,
                    "lag": member["lag"],
                    "state": member["state"],
                    "tl": member["timeline"],
                },
            )

        # get the cluster info
        cluster_item_dict = self.rest_api("cluster")

        replicas = []
        healthy_replica = 0
        unhealthy_replica = 0
        sync_replica = 0
        leader_tl = None

        # Look for replicas
        for member in cluster_item_dict["members"]:
            if member["role"] in ["replica", "sync_standby"]:
                if member["lag"] == "unknown":
                    # This could happen if the node is stopped
                    # nagiosplugin doesn't handle strings in perfstats
                    # so we have to ditch all the stats in that case
                    debug_member(member, "unhealthy")
                    unhealthy_replica += 1
                    continue
                else:
                    replicas.append(
                        {
                            "name": member["name"],
                            "lag": member["lag"],
                            "timeline": member["timeline"],
                            "sync": 1 if member["role"] == "sync_standby" else 0,
                        }
                    )

                # Get the leader tl if we haven't already
                if leader_tl is None:
                    # If there are no leaders, we will loop here for all
                    # members because leader_tl will remain None. it's not
                    # a big deal since having no leader is rare.
                    for tmember in cluster_item_dict["members"]:
                        if tmember["role"] == "leader":
                            leader_tl = int(tmember["timeline"])
                            break

                    _log.debug(
                        "Patroni's leader_timeline is %(leader_tl)s",
                        {
                            "leader_tl": leader_tl,
                        },
                    )

                # Test for an unhealthy replica
                if (
                    self.has_detailed_states()
                    and not (
                        member["state"] in ["streaming", "in archive recovery"]
                        and int(member["timeline"]) == leader_tl
                    )
                ) or (
                    not self.has_detailed_states()
                    and not (
                        member["state"] == "running"
                        and int(member["timeline"]) == leader_tl
                    )
                ):
                    debug_member(member, "unhealthy")
                    unhealthy_replica += 1
                    continue

                if member["role"] == "sync_standby":
                    sync_replica += 1

                if self.max_lag is None or self.max_lag >= int(member["lag"]):
                    debug_member(member, "healthy")
                    healthy_replica += 1
                else:
                    debug_member(member, "unhealthy")
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
                f"{replica['name']}_timeline",
                replica["timeline"],
                context="replica_timeline",
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
        self,
        connection_info: ConnectionInfo,
        config_hash: str,  # Always contains the old hash
        state_file: str,  # Only used to update the hash in the state_file (when needed)
        save: bool = False,  # Save the configuration
    ):
        super().__init__(connection_info)
        self.state_file = state_file
        self.config_hash = config_hash
        self.save = save

    def probe(self) -> Iterable[nagiosplugin.Metric]:
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
    def __init__(self, config_hash: str) -> None:
        self.old_config_hash = config_hash

    # Note: It would be helpful to display the old / new hash here. Unfortunately, it's not a metric.
    # So we only have the old / expected one.
    def ok(self, results: nagiosplugin.Result) -> str:
        return f"The hash of patroni's dynamic configuration has not changed ({self.old_config_hash})."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        return f"The hash of patroni's dynamic configuration has changed. The old hash was {self.old_config_hash}."


class ClusterIsInMaintenance(PatroniResource):
    def probe(self) -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("cluster")

        # The actual check
        return [
            nagiosplugin.Metric(
                "is_in_maintenance",
                1 if "pause" in item_dict and item_dict["pause"] else 0,
            )
        ]


class ClusterHasScheduledAction(PatroniResource):
    def probe(self) -> Iterable[nagiosplugin.Metric]:
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
