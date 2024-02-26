import logging
import re
from configparser import ConfigParser
from typing import List

import click
import nagiosplugin

from . import __version__, _log
from .cluster import (
    ClusterConfigHasChanged,
    ClusterConfigHasChangedSummary,
    ClusterHasLeader,
    ClusterHasLeaderSummary,
    ClusterHasReplica,
    ClusterHasScheduledAction,
    ClusterIsInMaintenance,
    ClusterNodeCount,
)
from .convert import size_to_byte
from .node import (
    NodeIsAlive,
    NodeIsAliveSummary,
    NodeIsLeader,
    NodeIsLeaderSummary,
    NodeIsPendingRestart,
    NodeIsPendingRestartSummary,
    NodeIsPrimary,
    NodeIsPrimarySummary,
    NodeIsReplica,
    NodeIsReplicaSummary,
    NodePatroniVersion,
    NodePatroniVersionSummary,
    NodeTLHasChanged,
    NodeTLHasChangedSummary,
)
from .types import ConnectionInfo, Parameters

DEFAULT_CFG = "config.ini"
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
_log.addHandler(handler)


def print_version(ctx: click.Context, param: str, value: str) -> None:
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"Version {__version__}")
    ctx.exit()


def configure(ctx: click.Context, param: str, filename: str) -> None:
    """Use a config file for the parameters
    stolen from https://jwodder.github.io/kbits/posts/click-config/
    """
    # FIXME should use click-configfile / click-config-file ?
    cfg = ConfigParser()
    cfg.read(filename)
    ctx.default_map = {}
    for sect in cfg.sections():
        command_path = sect.split(".")
        if command_path[0] != "options":
            continue
        defaults = ctx.default_map
        for cmdname in command_path[1:]:
            defaults = defaults.setdefault(cmdname, {})
        defaults.update(cfg[sect])
        try:
            # endpoints is an array of addresses separated by ,
            if isinstance(defaults["endpoints"], str):
                defaults["endpoints"] = re.split(r"\s*,\s*", defaults["endpoints"])
        except KeyError:
            pass


@click.group()
@click.option(
    "--config",
    type=click.Path(dir_okay=False),
    default=DEFAULT_CFG,
    callback=configure,
    is_eager=True,
    expose_value=False,
    help="Read option defaults from the specified INI file",
    show_default=True,
)
@click.option(
    "-e",
    "--endpoints",
    "endpoints",
    type=str,
    multiple=True,
    default=["http://127.0.0.1:8008"],
    help=(
        "Patroni API endpoint. Can be specified multiple times or as a list "
        "of comma separated addresses. "
        "The node services checks the status of one node, therefore if "
        "several addresses are specified they should point to different "
        "interfaces on the same node. The cluster services check the "
        "status of the cluster, therefore it's better to give a list of "
        "all Patroni node addresses."
    ),
    show_default=True,
)
@click.option(
    "--cert_file",
    "cert_file",
    type=click.Path(exists=True),
    default=None,
    help="File with the client certificate.",
)
@click.option(
    "--key_file",
    "key_file",
    type=click.Path(exists=True),
    default=None,
    help="File with the client key.",
)
@click.option(
    "--ca_file",
    "ca_file",
    type=click.Path(exists=True),
    default=None,
    help="The CA certificate.",
)
@click.option(
    "-v",
    "--verbose",
    "verbose",
    count=True,
    default=0,
    help="Increase verbosity -v (info)/-vv (warning)/-vvv (debug)",
    show_default=False,
)
@click.option(
    "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True
)
@click.option(
    "--timeout",
    "timeout",
    default=2,
    type=int,
    help="Timeout in seconds for the API queries (0 to disable)",
    show_default=True,
)
@click.pass_context
@nagiosplugin.guarded
def main(
    ctx: click.Context,
    endpoints: List[str],
    cert_file: str,
    key_file: str,
    ca_file: str,
    verbose: int,
    timeout: int,
) -> None:
    """Nagios plugin that uses Patroni's REST API to monitor a Patroni cluster."""
    # FIXME Not all "is/has" services have the same return code for ok. Check if it's ok

    # We use this to pass parameters instead of ctx.parent.params because the
    # latter is typed as Optional[Context] and mypy complains with the following
    # error unless we test if ctx.parent is none which looked ugly.
    #
    # error: Item "None" of "Optional[Context]" has an attribute "params"  [union-attr]

    # The config file allows endpoints to be specified as a comma separated list of endpoints
    # To avoid confusion, We allow the same in command line parameters
    tendpoints: List[str] = []
    for e in endpoints:
        tendpoints += re.split(r"\s*,\s*", e)
    endpoints = tendpoints

    if verbose == 3:
        logging.getLogger("urllib3").addHandler(handler)
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
        _log.setLevel(logging.DEBUG)

    connection_info: ConnectionInfo
    if cert_file is None and key_file is None:
        connection_info = ConnectionInfo(endpoints, None, ca_file)
    else:
        connection_info = ConnectionInfo(endpoints, (cert_file, key_file), ca_file)

    ctx.obj = Parameters(
        connection_info,
        timeout,
        verbose,
    )


@main.command(name="cluster_node_count")  # required otherwise _ are converted to -
@click.option(
    "-w",
    "--warning",
    "warning",
    type=str,
    help="Warning threshold for the number of nodes.",
)
@click.option(
    "-c",
    "--critical",
    "critical",
    type=str,
    help="Critical threshold for the number of nodes.",
)
@click.option(
    "--healthy-warning",
    "healthy_warning",
    type=str,
    help="Warning threshold for the number of healthy nodes (running + streaming).",
)
@click.option(
    "--healthy-critical",
    "healthy_critical",
    type=str,
    help="Critical threshold for the number of healthy nodes (running + streaming).",
)
@click.pass_context
@nagiosplugin.guarded
def cluster_node_count(
    ctx: click.Context,
    warning: str,
    critical: str,
    healthy_warning: str,
    healthy_critical: str,
) -> None:
    """Count the number of nodes in the cluster.

    \b
    The role refers to the role of the server in the cluster. Possible values
    are:
    * master or leader
    * replica
    * standby_leader
    * sync_standby
    * demoted
    * promoted
    * uninitialized

    \b
    The state refers to the state of PostgreSQL. Possible values are:
    * initializing new cluster, initdb failed
    * running custom bootstrap script, custom bootstrap failed
    * starting, start failed
    * restarting, restart failed
    * running, streaming, in archive recovery
    * stopping, stopped, stop failed
    * creating replica
    * crashed

    \b
    The "healthy" checks only ensures that:
    * a leader has the running state
    * a standby_leader has the running or streaming (V3.0.4) state
    * a replica or sync-standby has the running or streaming (V3.0.4) state

    Since we dont check the lag or timeline, "in archive recovery" is not considered a valid state
    for this service. See cluster_has_leader and cluster_has_replica for specialized checks.

    \b
    Check:
    * Compares the number of nodes against the normal and healthy nodes warning and critical thresholds.
    * `OK`:  If they are not provided.

    \b
    Perfdata:
    * `members`: the member count.
    * `healthy_members`: the running and streaming member count.
    * all the roles of the nodes in the cluster with their count (start with "role_").
    * all the statuses of the nodes in the cluster with their count (start with "state_").
    """
    check = nagiosplugin.Check()
    check.add(
        ClusterNodeCount(ctx.obj.connection_info),
        nagiosplugin.ScalarContext(
            "members",
            warning,
            critical,
        ),
        nagiosplugin.ScalarContext(
            "healthy_members",
            healthy_warning,
            healthy_critical,
        ),
        nagiosplugin.ScalarContext("member_roles"),
        nagiosplugin.ScalarContext("member_statuses"),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="cluster_has_leader")
@click.pass_context
@nagiosplugin.guarded
def cluster_has_leader(ctx: click.Context) -> None:
    """Check if the cluster has a leader.

    This check applies to any kind of leaders including standby leaders.

    A leader is a node with the "leader" role and a "running" state.

    A standby leader is a node with a "standby_leader" role and a "streaming"
    or "in archive recovery" state. Please note that log shipping could be
    stuck because the WAL are not available or applicable. Patroni doesn't
    provide information about the origin cluster (timeline or lag), so we
    cannot check if there is a problem in that particular case. That's why we
    issue a warning when the node is "in archive recovery". We suggest using
    other supervision tools to do this (eg. check_pgactivity).

    \b
    Check:
    * `OK`: if there is a leader node.
    * 'WARNING': if there is a stanby leader in archive mode.
    * `CRITICAL`: otherwise.

    \b
    Perfdata:
    * `has_leader` is 1 if there is any kind of leader node, 0 otherwise
    * `is_standby_leader_in_arc_rec` is 1 if the standby leader node is "in
       archive recovery", 0 otherwise
    * `is_standby_leader` is 1 if there is a standby leader node, 0 otherwise
    * `is_leader` is 1 if there is a "classical" leader node, 0 otherwise

    """
    check = nagiosplugin.Check()
    check.add(
        ClusterHasLeader(ctx.obj.connection_info),
        nagiosplugin.ScalarContext("has_leader", None, "@0:0"),
        nagiosplugin.ScalarContext("is_standby_leader_in_arc_rec", "@1:1", None),
        nagiosplugin.ScalarContext("is_leader", None, None),
        nagiosplugin.ScalarContext("is_standby_leader", None, None),
        ClusterHasLeaderSummary(),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="cluster_has_replica")
@click.option(
    "-w",
    "--warning",
    "warning",
    type=str,
    help="Warning threshold for the number of healthy replica nodes.",
)
@click.option(
    "-c",
    "--critical",
    "critical",
    type=str,
    help="Critical threshold for the number of healthy replica nodes.",
)
@click.option(
    "--sync-warning",
    "sync_warning",
    type=str,
    help="Warning threshold for the number of sync replica.",
)
@click.option(
    "--sync-critical",
    "sync_critical",
    type=str,
    help="Critical threshold for the number of sync replica.",
)
@click.option("--max-lag", "max_lag", type=str, help="maximum allowed lag")
@click.pass_context
@nagiosplugin.guarded
def cluster_has_replica(
    ctx: click.Context,
    warning: str,
    critical: str,
    sync_warning: str,
    sync_critical: str,
    max_lag: str,
) -> None:
    """Check if the cluster has healthy replicas and/or if some are sync standbies

    \b
    For patroni (and this check):
    * a replica is `streaming` if the `pg_stat_wal_receiver` say's so.
    * a replica is `in archive recovery`, if it's not `streaming` and has a `restore_command`.

    \b
    A healthy replica:
    * has a `replica` or `sync_standby` role
    * has the same timeline as the leader and
      * is in `running` state (patroni < V3.0.4)
      * is in `streaming` or `in archive recovery` state (patroni >= V3.0.4)
    * has a lag lower or equal to `max_lag`

    Please note that replica `in archive recovery` could be stuck because the WAL
    are not available or applicable (the server's timeline has diverged for the
    leader's). We already detect the latter but we will miss the former.
    Therefore, it's preferable to check for the lag in addition to the healthy
    state if you rely on log shipping to help lagging standbies to catch up.

    Since we require a healthy replica to have the same timeline as the
    leader, it's possible that we raise alerts when the cluster is performing a
    switchover or failover and the standbies are in the process of catching up with
    the new leader. The alert shouldn't last long.

    \b
    Check:
    * `OK`: if the healthy_replica count and their lag are compatible with the replica count threshold.
            and if the sync_replica count is compatible with the sync replica count threshold.
    * `WARNING` / `CRITICAL`: otherwise

    \b
    Perfdata:
    * healthy_replica & unhealthy_replica count
    * the number of sync_replica, they are included in the previous count
    * the lag of each replica labelled with "member name"_lag
    * the timeline of each replica labelled with "member name"_timeline
    * a boolean to tell if the node is a sync stanbdy labelled with "member name"_sync
    """

    tmax_lag = size_to_byte(max_lag) if max_lag is not None else None
    check = nagiosplugin.Check()
    check.add(
        ClusterHasReplica(ctx.obj.connection_info, tmax_lag),
        nagiosplugin.ScalarContext(
            "healthy_replica",
            warning,
            critical,
        ),
        nagiosplugin.ScalarContext(
            "sync_replica",
            sync_warning,
            sync_critical,
        ),
        nagiosplugin.ScalarContext("unhealthy_replica"),
        nagiosplugin.ScalarContext("replica_lag"),
        nagiosplugin.ScalarContext("replica_timeline"),
        nagiosplugin.ScalarContext("replica_sync"),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="cluster_config_has_changed")
@click.option("--hash", "config_hash", type=str, help="A hash to compare with.")
@click.option(
    "-s",
    "--state-file",
    "state_file",
    type=str,
    help="A state file to store the hash of the configuration.",
)
@click.option(
    "--save",
    "save_config",
    is_flag=True,
    default=False,
    help="Set the current configuration hash as the reference for future calls.",
)
@click.pass_context
@nagiosplugin.guarded
def cluster_config_has_changed(
    ctx: click.Context, config_hash: str, state_file: str, save_config: bool
) -> None:
    """Check if the hash of the configuration has changed.

    Note: either a hash or a state file must be provided for this service to work.

    \b
    Check:
    * `OK`: The hash didn't change
    * `CRITICAL`: The hash of the configuration has changed compared to the input (`--hash`) or last time (`--state_file`)

    \b
    Perfdata:
    * `is_configuration_changed` is 1 if the configuration has changed
    """
    # Note: hash cannot be in the perf data = not a number
    if (config_hash is None and state_file is None) or (
        config_hash is not None and state_file is not None
    ):
        raise click.UsageError(
            "Either --hash or --state-file should be provided for this service", ctx
        )

    old_config_hash = config_hash
    if state_file is not None:
        cookie = nagiosplugin.Cookie(state_file)
        cookie.open()
        old_config_hash = cookie.get("hash")
        cookie.close()

    check = nagiosplugin.Check()
    check.add(
        ClusterConfigHasChanged(
            ctx.obj.connection_info, old_config_hash, state_file, save_config
        ),
        nagiosplugin.ScalarContext("is_configuration_changed", None, "@1:1"),
        ClusterConfigHasChangedSummary(old_config_hash),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="cluster_is_in_maintenance")
@click.pass_context
@nagiosplugin.guarded
def cluster_is_in_maintenance(ctx: click.Context) -> None:
    """Check if the cluster is in maintenance mode or paused.

    \b
    Check:
    * `OK`: If the cluster is in maintenance mode.
    * `CRITICAL`: otherwise.

    \b
    Perfdata:
    * `is_in_maintenance` is 1 the cluster is in maintenance mode,  0 otherwise
    """
    check = nagiosplugin.Check()
    check.add(
        ClusterIsInMaintenance(ctx.obj.connection_info),
        nagiosplugin.ScalarContext("is_in_maintenance", None, "0:0"),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="cluster_has_scheduled_action")
@click.pass_context
@nagiosplugin.guarded
def cluster_has_scheduled_action(ctx: click.Context) -> None:
    """Check if the cluster has a scheduled action (switchover or restart)

    \b
    Check:
    * `OK`: If the cluster has no scheduled action
    * `CRITICAL`: otherwise.

    \b
    Perfdata:
    * `scheduled_actions` is 1 if the cluster has scheduled actions.
    * `scheduled_switchover` is 1 if the cluster has a scheduled switchover.
    * `scheduled_restart` counts the number of scheduled restart in the cluster.
    """
    check = nagiosplugin.Check()
    check.add(
        ClusterHasScheduledAction(ctx.obj.connection_info),
        nagiosplugin.ScalarContext("has_scheduled_actions", None, "0:0"),
        nagiosplugin.ScalarContext("scheduled_switchover"),
        nagiosplugin.ScalarContext("scheduled_restart"),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="node_is_primary")
@click.pass_context
@nagiosplugin.guarded
def node_is_primary(ctx: click.Context) -> None:
    """Check if the node is the primary with the leader lock.

    This service is not valid for a standby leader, because this kind of node is not a primary.

    \b
    Check:
    * `OK`: if the node is a primary with the leader lock.
    * `CRITICAL:` otherwise

    Perfdata: `is_primary` is 1 if the node is a primary with the leader lock, 0 otherwise.
    """
    check = nagiosplugin.Check()
    check.add(
        NodeIsPrimary(ctx.obj.connection_info),
        nagiosplugin.ScalarContext("is_primary", None, "@0:0"),
        NodeIsPrimarySummary(),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="node_is_leader")
@click.option(
    "--is-standby-leader",
    "check_standby_leader",
    is_flag=True,
    default=False,
    help="Check for a standby leader",
)
@click.pass_context
@nagiosplugin.guarded
def node_is_leader(ctx: click.Context, check_standby_leader: bool) -> None:
    """Check if the node is a leader node.

    This check applies to any kind of leaders including standby leaders.
    To check explicitly for a standby leader use the `--is-standby-leader` option.

    \b
    Check:
    * `OK`: if the node is a leader.
    * `CRITICAL:` otherwise

    Perfdata: `is_leader` is 1 if the node is a leader node, 0 otherwise.
    """
    check = nagiosplugin.Check()
    check.add(
        NodeIsLeader(ctx.obj.connection_info, check_standby_leader),
        nagiosplugin.ScalarContext("is_leader", None, "@0:0"),
        NodeIsLeaderSummary(check_standby_leader),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="node_is_replica")
@click.option("--max-lag", "max_lag", type=str, help="maximum allowed lag")
@click.option(
    "--is-sync",
    "check_is_sync",
    is_flag=True,
    default=False,
    help="check if the replica is synchronous",
)
@click.option(
    "--is-async",
    "check_is_async",
    is_flag=True,
    default=False,
    help="check if the replica is asynchronous",
)
@click.pass_context
@nagiosplugin.guarded
def node_is_replica(
    ctx: click.Context, max_lag: str, check_is_sync: bool, check_is_async: bool
) -> None:
    """Check if the node is a replica with no noloadbalance tag.

    It is possible to check if the node is synchronous or asynchronous. If
    nothing is specified any kind of replica is accepted.  When checking for a
    synchronous replica, it's not possible to specify a lag.

    This service is using the following Patroni endpoints: replica, asynchronous
    and synchronous. The first two implement the `lag` tag. For these endpoints
    the state of a replica node doesn't reflect the replication state
    (`streaming` or `in archive recovery`), we only know if it's `running`. The
    timeline is also not checked.

    Therefore, if a cluster is using asynchronous replication, it is
    recommended to check for the lag to detect a divegence as soon as possible.

    \b
    Check:
    * `OK`: if the node is a running replica with noloadbalance tag and the lag is under the maximum threshold.
    * `CRITICAL`:  otherwise

    Perfdata: `is_replica` is 1 if the node is a running replica with noloadbalance tag and the lag is under the maximum threshold, 0 otherwise.
    """

    if check_is_sync and max_lag is not None:
        raise click.UsageError(
            "--is-sync and --max-lag cannot be provided at the same time for this service",
            ctx,
        )

    if check_is_sync and check_is_async:
        raise click.UsageError(
            "--is-sync and --is-async cannot be provided at the same time for this service",
            ctx,
        )

    check = nagiosplugin.Check()
    check.add(
        NodeIsReplica(ctx.obj.connection_info, max_lag, check_is_sync, check_is_async),
        nagiosplugin.ScalarContext("is_replica", None, "@0:0"),
        NodeIsReplicaSummary(max_lag, check_is_sync, check_is_async),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="node_is_pending_restart")
@click.pass_context
@nagiosplugin.guarded
def node_is_pending_restart(ctx: click.Context) -> None:
    """Check if the node is in pending restart state.

    This situation can arise if the configuration has been modified but
    requires a restart of PostgreSQL to take effect.

    \b
    Check:
    * `OK`: if the node has no pending restart tag.
    * `CRITICAL`: otherwise

    Perfdata: `is_pending_restart` is 1 if the node has pending restart tag, 0 otherwise.
    """
    check = nagiosplugin.Check()
    check.add(
        NodeIsPendingRestart(ctx.obj.connection_info),
        nagiosplugin.ScalarContext("is_pending_restart", None, "0:0"),
        NodeIsPendingRestartSummary(),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="node_tl_has_changed")
@click.option(
    "--timeline", "timeline", type=str, help="A timeline number to compare with."
)
@click.option(
    "-s",
    "--state-file",
    "state_file",
    type=str,
    help="A state file to store the last tl number into.",
)
@click.option(
    "--save",
    "save_tl",
    is_flag=True,
    default=False,
    help="Set the current timeline number as the reference for future calls.",
)
@click.pass_context
@nagiosplugin.guarded
def node_tl_has_changed(
    ctx: click.Context, timeline: str, state_file: str, save_tl: bool
) -> None:
    """Check if the timeline has changed.

    Note: either a timeline or a state file must be provided for this service to work.

    \b
    Check:
    * `OK`: The timeline is the same as last time (`--state_file`) or the inputted timeline (`--timeline`)
    * `CRITICAL`: The tl is not the same.

    \b
    Perfdata:
    * `is_timeline_changed` is 1 if the tl has changed, 0 otherwise
    * the timeline
    """
    if (timeline is None and state_file is None) or (
        timeline is not None and state_file is not None
    ):
        raise click.UsageError(
            "Either --timeline or --state-file should be provided for this service", ctx
        )

    old_timeline = timeline
    if state_file is not None:
        cookie = nagiosplugin.Cookie(state_file)
        cookie.open()
        old_timeline = cookie.get("timeline")
        cookie.close()

    check = nagiosplugin.Check()
    check.add(
        NodeTLHasChanged(ctx.obj.connection_info, old_timeline, state_file, save_tl),
        nagiosplugin.ScalarContext("is_timeline_changed", None, "@1:1"),
        nagiosplugin.ScalarContext("timeline"),
        NodeTLHasChangedSummary(old_timeline),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="node_patroni_version")
@click.option(
    "--patroni-version",
    "patroni_version",
    type=str,
    help="Patroni version to compare to",
    required=True,
)
@click.pass_context
@nagiosplugin.guarded
def node_patroni_version(ctx: click.Context, patroni_version: str) -> None:
    """Check if the version is equal to the input

    \b
    Check:
    * `OK`: The version is the same as the input `--patroni-version`
    * `CRITICAL`: otherwise.

    \b
    Perfdata:
    * `is_version_ok` is 1 if version is ok, 0 otherwise
    """
    # TODO the version cannot be written in perfdata find something else ?
    check = nagiosplugin.Check()
    check.add(
        NodePatroniVersion(ctx.obj.connection_info, patroni_version),
        nagiosplugin.ScalarContext("is_version_ok", None, "@0:0"),
        nagiosplugin.ScalarContext("patroni_version"),
        NodePatroniVersionSummary(patroni_version),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)


@main.command(name="node_is_alive")
@click.pass_context
@nagiosplugin.guarded
def node_is_alive(ctx: click.Context) -> None:
    """Check if the node is alive ie patroni is running. This is
    a liveness check as defined in Patroni's documentation.

    \b
    Check:
    * `OK`: If patroni is running.
    * `CRITICAL`: otherwise.

    \b
    Perfdata:
    * `is_running` is 1 if patroni is running, 0 otherwise
    """
    check = nagiosplugin.Check()
    check.add(
        NodeIsAlive(ctx.obj.connection_info),
        nagiosplugin.ScalarContext("is_alive", None, "@0:0"),
        NodeIsAliveSummary(),
    )
    check.main(verbose=ctx.obj.verbose, timeout=ctx.obj.timeout)
