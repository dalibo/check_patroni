import json
import logging

import nagiosplugin
from typing import Iterable

from .types import ConnectionInfo, handle_unknown, PatroniResource


_log = logging.getLogger("nagiosplugin")


class NodeIsPrimary(PatroniResource):
    def probe(self: "NodeIsPrimary") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("primary")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        return [nagiosplugin.Metric("is_primary", 1 if r.status == 200 else 0)]


class NodeIsPrimarySummary(nagiosplugin.Summary):
    def ok(self: "NodeIsPrimarySummary", results: nagiosplugin.Result) -> str:
        return "This node is the primary with the leader lock."

    @handle_unknown
    def problem(self: "NodeIsPrimarySummary", results: nagiosplugin.Result) -> str:
        return "This node is not the primary with the leader lock."


class NodeIsReplica(PatroniResource):
    def __init__(
        self: "NodeIsReplica", connection_info: ConnectionInfo, max_lag: str
    ) -> None:
        super().__init__(connection_info)
        self.max_lag = max_lag

    def probe(self: "NodeIsReplica") -> Iterable[nagiosplugin.Metric]:
        if self.max_lag is None:
            r = self.rest_api("replica")
        else:
            r = self.rest_api(f"replica?lag={self.max_lag}")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        return [nagiosplugin.Metric("is_replica", 1 if r.status == 200 else 0)]


class NodeIsReplicaSummary(nagiosplugin.Summary):
    def __init__(self: "NodeIsReplicaSummary", lag: str) -> None:
        self.lag = lag

    def ok(self: "NodeIsReplicaSummary", results: nagiosplugin.Result) -> str:
        if self.lag is None:
            return "This node is a running replica with no noloadbalance tag."
        return f"This node is a running replica with no noloadbalance tag and the lag is under {self.lag}."

    @handle_unknown
    def problem(self: "NodeIsReplicaSummary", results: nagiosplugin.Result) -> str:
        if self.lag is None:
            return "This node is not a running replica with no noloadbalance tag."
        return f"This node is not a running replica with no noloadbalance tag and a lag under {self.lag}."


class NodeIsPendingRestart(PatroniResource):
    def probe(self: "NodeIsPendingRestart") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("patroni")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)
        is_pending_restart = item_dict.get("pending_restart", False)
        return [
            nagiosplugin.Metric(
                "is_pending_restart",
                1 if is_pending_restart else 0,
            )
        ]


class NodeIsPendingRestartSummary(nagiosplugin.Summary):
    def ok(self: "NodeIsPendingRestartSummary", results: nagiosplugin.Result) -> str:
        return "This node doesn't have the pending restart flag."

    @handle_unknown
    def problem(
        self: "NodeIsPendingRestartSummary", results: nagiosplugin.Result
    ) -> str:
        return "This node has the pending restart flag."


class NodeTLHasChanged(PatroniResource):
    def __init__(
        self: "NodeTLHasChanged",
        connection_info: ConnectionInfo,
        timeline: str,  # Always contains the old timeline
        state_file: str,  # Only used to update the timeline in the state_file (when needed)
    ) -> None:
        super().__init__(connection_info)
        self.state_file = state_file
        self.timeline = timeline

    def probe(self: "NodeTLHasChanged") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("patroni")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)
        new_tl = item_dict["timeline"]

        old_tl = self.timeline
        if self.state_file is not None:
            _log.debug(f"Saving new timeline to state file / cookie {self.state_file}")
            cookie = nagiosplugin.Cookie(self.state_file)
            cookie.open()
            cookie["timeline"] = new_tl
            cookie.commit()
            cookie.close()

        _log.debug(f"Tl data: old tl {old_tl}, new tl {new_tl}")

        # The actual check
        yield nagiosplugin.Metric(
            "is_timeline_changed",
            1 if str(new_tl) != str(old_tl) else 0,
        )

        # The performance data : the timeline number
        yield nagiosplugin.Metric("timeline", new_tl)


class NodeTLHasChangedSummary(nagiosplugin.Summary):
    def __init__(self: "NodeTLHasChangedSummary", timeline: str) -> None:
        self.timeline = timeline

    def ok(self: "NodeTLHasChangedSummary", results: nagiosplugin.Result) -> str:
        return f"The timeline is still {self.timeline}."

    @handle_unknown
    def problem(self: "NodeTLHasChangedSummary", results: nagiosplugin.Result) -> str:
        return f"The expected timeline was {self.timeline} got {results['timeline'].metric}."


class NodePatroniVersion(PatroniResource):
    def __init__(
        self: "NodePatroniVersion",
        connection_info: ConnectionInfo,
        patroni_version: str,
    ) -> None:
        super().__init__(connection_info)
        self.patroni_version = patroni_version

    def probe(self: "NodePatroniVersion") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("patroni")

        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        item_dict = json.loads(r.data)
        version = item_dict["patroni"]["version"]
        _log.debug(
            f"Version data: patroni version  {version} input version {self.patroni_version}"
        )

        # The actual check
        return [
            nagiosplugin.Metric(
                "is_version_ok",
                1 if version == self.patroni_version else 0,
            )
        ]


class NodePatroniVersionSummary(nagiosplugin.Summary):
    def __init__(self: "NodePatroniVersionSummary", patroni_version: str) -> None:
        self.patroni_version = patroni_version

    def ok(self: "NodePatroniVersionSummary", results: nagiosplugin.Result) -> str:
        return f"Patroni's version is {self.patroni_version}."

    @handle_unknown
    def problem(self: "NodePatroniVersionSummary", results: nagiosplugin.Result) -> str:
        # FIXME find a way to make the following work, check is perf data can be strings
        # return f"The expected patroni version was {self.patroni_version} got {results['patroni_version'].metric}."
        return f"Patroni's version is not {self.patroni_version}."


class NodeIsAlive(PatroniResource):
    def probe(self: "NodeIsAlive") -> Iterable[nagiosplugin.Metric]:
        r = self.rest_api("liveness")
        _log.debug(f"api call status: {r.status}")
        _log.debug(f"api call data: {r.data}")

        return [nagiosplugin.Metric("is_alive", 1 if r.status == 200 else 0)]


class NodeIsAliveSummary(nagiosplugin.Summary):
    def ok(self: "NodeIsAliveSummary", results: nagiosplugin.Result) -> str:
        return "This node is alive (patroni is running)."

    @handle_unknown
    def problem(self: "NodeIsAliveSummary", results: nagiosplugin.Result) -> str:
        return "This node is not alive (patroni is not running)."
