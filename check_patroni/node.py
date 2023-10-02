from typing import Iterable

import nagiosplugin

from . import _log
from .types import APIError, ConnectionInfo, PatroniResource, handle_unknown


class NodeIsPrimary(PatroniResource):
    def probe(self) -> Iterable[nagiosplugin.Metric]:
        try:
            self.rest_api("primary")
        except APIError:
            return [nagiosplugin.Metric("is_primary", 0)]
        return [nagiosplugin.Metric("is_primary", 1)]


class NodeIsPrimarySummary(nagiosplugin.Summary):
    def ok(self, results: nagiosplugin.Result) -> str:
        return "This node is the primary with the leader lock."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        return "This node is not the primary with the leader lock."


class NodeIsLeader(PatroniResource):
    def __init__(
        self, connection_info: ConnectionInfo, check_is_standby_leader: bool
    ) -> None:
        super().__init__(connection_info)
        self.check_is_standby_leader = check_is_standby_leader

    def probe(self) -> Iterable[nagiosplugin.Metric]:
        apiname = "leader"
        if self.check_is_standby_leader:
            apiname = "standby-leader"

        try:
            self.rest_api(apiname)
        except APIError:
            return [nagiosplugin.Metric("is_leader", 0)]
        return [nagiosplugin.Metric("is_leader", 1)]


class NodeIsLeaderSummary(nagiosplugin.Summary):
    def __init__(self, check_is_standby_leader: bool) -> None:
        if check_is_standby_leader:
            self.leader_kind = "standby leader"
        else:
            self.leader_kind = "leader"

    def ok(self, results: nagiosplugin.Result) -> str:
        return f"This node is a {self.leader_kind} node."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        return f"This node is not a {self.leader_kind} node."


class NodeIsReplica(PatroniResource):
    def __init__(
        self,
        connection_info: ConnectionInfo,
        max_lag: str,
        check_is_sync: bool,
        check_is_async: bool,
    ) -> None:
        super().__init__(connection_info)
        self.max_lag = max_lag
        self.check_is_sync = check_is_sync
        self.check_is_async = check_is_async

    def probe(self) -> Iterable[nagiosplugin.Metric]:
        try:
            if self.check_is_sync:
                api_name = "synchronous"
            elif self.check_is_async:
                api_name = "asynchronous"
            else:
                api_name = "replica"

            if self.max_lag is None:
                self.rest_api(api_name)
            else:
                self.rest_api(f"{api_name}?lag={self.max_lag}")
        except APIError:
            return [nagiosplugin.Metric("is_replica", 0)]
        return [nagiosplugin.Metric("is_replica", 1)]


class NodeIsReplicaSummary(nagiosplugin.Summary):
    def __init__(self, lag: str, check_is_sync: bool, check_is_async: bool) -> None:
        self.lag = lag
        if check_is_sync:
            self.replica_kind = "synchronous replica"
        elif check_is_async:
            self.replica_kind = "asynchronous replica"
        else:
            self.replica_kind = "replica"

    def ok(self, results: nagiosplugin.Result) -> str:
        if self.lag is None:
            return (
                f"This node is a running {self.replica_kind} with no noloadbalance tag."
            )
        return f"This node is a running {self.replica_kind} with no noloadbalance tag and the lag is under {self.lag}."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        if self.lag is None:
            return f"This node is not a running {self.replica_kind} with no noloadbalance tag."
        return f"This node is not a running {self.replica_kind} with no noloadbalance tag and a lag under {self.lag}."


class NodeIsPendingRestart(PatroniResource):
    def probe(self) -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("patroni")

        is_pending_restart = item_dict.get("pending_restart", False)
        return [
            nagiosplugin.Metric(
                "is_pending_restart",
                1 if is_pending_restart else 0,
            )
        ]


class NodeIsPendingRestartSummary(nagiosplugin.Summary):
    def ok(self, results: nagiosplugin.Result) -> str:
        return "This node doesn't have the pending restart flag."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        return "This node has the pending restart flag."


class NodeTLHasChanged(PatroniResource):
    def __init__(
        self,
        connection_info: ConnectionInfo,
        timeline: str,  # Always contains the old timeline
        state_file: str,  # Only used to update the timeline in the state_file (when needed)
        save: bool,  # save timeline in state file
    ) -> None:
        super().__init__(connection_info)
        self.state_file = state_file
        self.timeline = timeline
        self.save = save

    def probe(self) -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("patroni")
        new_tl = item_dict["timeline"]

        _log.debug("save result: %(issave)s", {"issave": self.save})
        old_tl = self.timeline
        if self.state_file is not None and self.save:
            _log.debug(
                "saving new timeline to state file / cookie %(state_file)s",
                {"state_file": self.state_file},
            )
            cookie = nagiosplugin.Cookie(self.state_file)
            cookie.open()
            cookie["timeline"] = new_tl
            cookie.commit()
            cookie.close()

        _log.debug(
            "Tl data: old tl %(old_tl)s, new tl %(new_tl)s",
            {"old_tl": old_tl, "new_tl": new_tl},
        )

        # The actual check
        yield nagiosplugin.Metric(
            "is_timeline_changed",
            1 if str(new_tl) != str(old_tl) else 0,
        )

        # The performance data : the timeline number
        yield nagiosplugin.Metric("timeline", new_tl)


class NodeTLHasChangedSummary(nagiosplugin.Summary):
    def __init__(self, timeline: str) -> None:
        self.timeline = timeline

    def ok(self, results: nagiosplugin.Result) -> str:
        return f"The timeline is still {self.timeline}."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        return f"The expected timeline was {self.timeline} got {results['timeline'].metric}."


class NodePatroniVersion(PatroniResource):
    def __init__(self, connection_info: ConnectionInfo, patroni_version: str) -> None:
        super().__init__(connection_info)
        self.patroni_version = patroni_version

    def probe(self) -> Iterable[nagiosplugin.Metric]:
        item_dict = self.rest_api("patroni")

        version = item_dict["patroni"]["version"]
        _log.debug(
            "Version data: patroni version  %(version)s input version %(patroni_version)s",
            {"version": version, "patroni_version": self.patroni_version},
        )

        # The actual check
        return [
            nagiosplugin.Metric(
                "is_version_ok",
                1 if version == self.patroni_version else 0,
            )
        ]


class NodePatroniVersionSummary(nagiosplugin.Summary):
    def __init__(self, patroni_version: str) -> None:
        self.patroni_version = patroni_version

    def ok(self, results: nagiosplugin.Result) -> str:
        return f"Patroni's version is {self.patroni_version}."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        # FIXME find a way to make the following work, check is perf data can be strings
        # return f"The expected patroni version was {self.patroni_version} got {results['patroni_version'].metric}."
        return f"Patroni's version is not {self.patroni_version}."


class NodeIsAlive(PatroniResource):
    def probe(self) -> Iterable[nagiosplugin.Metric]:
        try:
            self.rest_api("liveness")
        except APIError:
            return [nagiosplugin.Metric("is_alive", 0)]
        return [nagiosplugin.Metric("is_alive", 1)]


class NodeIsAliveSummary(nagiosplugin.Summary):
    def ok(self, results: nagiosplugin.Result) -> str:
        return "This node is alive (patroni is running)."

    @handle_unknown
    def problem(self, results: nagiosplugin.Result) -> str:
        return "This node is not alive (patroni is not running)."
