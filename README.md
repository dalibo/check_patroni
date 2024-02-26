# check_patroni

A nagios plugin for patroni.

## Features

- Check presence of leader, replicas, node counts.
- Check each node for replication status.


```
Usage: check_patroni [OPTIONS] COMMAND [ARGS]...

  Nagios plugin that uses Patroni's REST API to monitor a Patroni cluster.

Options:
  --config FILE         Read option defaults from the specified INI file
                        [default: config.ini]
  -e, --endpoints TEXT  Patroni API endpoint. Can be specified multiple times
                        or as a list of comma separated addresses. The node
                        services checks the status of one node, therefore if
                        several addresses are specified they should point to
                        different interfaces on the same node. The cluster
                        services check the status of the cluster, therefore
                        it's better to give a list of all Patroni node
                        addresses.  [default: http://127.0.0.1:8008]
  --cert_file PATH      File with the client certificate.
  --key_file PATH       File with the client key.
  --ca_file PATH        The CA certificate.
  -v, --verbose         Increase verbosity -v (info)/-vv (warning)/-vvv
                        (debug)
  --version
  --timeout INTEGER     Timeout in seconds for the API queries (0 to disable)
                        [default: 2]
  --help                Show this message and exit.

Commands:
  cluster_config_has_changed    Check if the hash of the configuration...
  cluster_has_leader            Check if the cluster has a leader.
  cluster_has_replica           Check if the cluster has healthy replicas...
  cluster_has_scheduled_action  Check if the cluster has a scheduled...
  cluster_is_in_maintenance     Check if the cluster is in maintenance...
  cluster_node_count            Count the number of nodes in the cluster.
  node_is_alive                 Check if the node is alive ie patroni is...
  node_is_leader                Check if the node is a leader node.
  node_is_pending_restart       Check if the node is in pending restart...
  node_is_primary               Check if the node is the primary with the...
  node_is_replica               Check if the node is a replica with no...
  node_patroni_version          Check if the version is equal to the input
  node_tl_has_changed           Check if the timeline has changed.
```

## Install

check_patroni is licensed under PostgreSQL license.

```
$ pip install git+https://github.com/dalibo/check_patroni.git
```

check_patroni works on python 3.6, we keep it that way because patroni also
supports it and there are still lots of RH 7 variants around. That being said
python 3.6 has been EOL for ages and there is no support for it in the github
CI.

## Support

If you hit a bug or need help, open a [GitHub
issue](https://github.com/dalibo/check_patroni/issues/new). Dalibo has no
commitment on response time for public free support. Thanks for you
contribution !

## Config file

All global and service specific parameters can be specified via a config file has follows:

```
[options]
endpoints = https://10.20.199.3:8008, https://10.20.199.4:8008,https://10.20.199.5:8008
cert_file = ./ssl/my-cert.pem
key_file = ./ssl/my-key.pem
ca_file = ./ssl/CA-cert.pem
timeout = 0

[options.node_is_replica]
lag=100
```
## Thresholds

The format for the threshold parameters is `[@][start:][end]`.

* `start:` may be omitted if `start == 0`
* `~:` means that start is negative infinity
* If `end` is omitted, infinity is assumed
* To invert the match condition, prefix the range expression with `@`.

A match is found when: `start <= VALUE <= end`.

For example, the following command will raise:

* a warning if there is less than 1 nodes, which can be translated to outside of range [2;+INF[
* a critical if there are no nodes, which can be translated to outside of range [1;+INF[

```
check_patroni -e https://10.20.199.3:8008 cluster_has_replica --warning 2: --critical 1:
```

## SSL

Several options are available:

* the server's CA certificate is not available or trusted by the client system:
  * `--ca_cert`: your certification chain `cat CA-certificate server-certificate > cabundle`
* you have a client certificate for authenticating with Patroni's REST API:
  * `--cert_file`: your certificate or the concatenation of your certificate and private key
  * `--key_file`: your private key (optional)

## Shell completion

We use the [click] library which supports shell completion natively.

Shell completion can be added by typing the following command or adding it to
a file spécific to your shell of choice.

* for Bash (add to `~/.bashrc`):
  ```
  eval "$(_CHECK_PATRONI_COMPLETE=bash_source check_patroni)"
  ```
* for Zsh  (add to `~/.zshrc`):
  ```
  eval "$(_CHECK_PATRONI_COMPLETE=zsh_source check_patroni)"
  ```
* for Fish (add to `~/.config/fish/completions/check_patroni.fish`):
  ```
  eval "$(_CHECK_PATRONI_COMPLETE=fish_source check_patroni)"
  ```

Please note that shell completion is not supported far all shell versions, for
example only Bash versions older than 4.4 are supported.

[click]: https://click.palletsprojects.com/en/8.1.x/shell-completion/

## Cluster services

### cluster_config_has_changed

```
Usage: check_patroni cluster_config_has_changed [OPTIONS]

  Check if the hash of the configuration has changed.

  Note: either a hash or a state file must be provided for this service to
  work.

  Check:
  * `OK`: The hash didn't change
  * `CRITICAL`: The hash of the configuration has changed compared to the input (`--hash`) or last time (`--state_file`)

  Perfdata:
  * `is_configuration_changed` is 1 if the configuration has changed

Options:
  --hash TEXT            A hash to compare with.
  -s, --state-file TEXT  A state file to store the hash of the configuration.
  --save                 Set the current configuration hash as the reference
                         for future calls.
  --help                 Show this message and exit.
```

### cluster_has_leader

```
Usage: check_patroni cluster_has_leader [OPTIONS]

  Check if the cluster has a leader.

  This check applies to any kind of leaders including standby leaders.

  A leader is a node with the "leader" role and a "running" state.

  A standby leader is a node with a "standby_leader" role and a "streaming" or
  "in archive recovery" state. Please note that log shipping could be stuck
  because the WAL are not available or applicable. Patroni doesn't provide
  information about the origin cluster (timeline or lag), so we cannot check
  if there is a problem in that particular case. That's why we issue a warning
  when the node is "in archive recovery". We suggest using other supervision
  tools to do this (eg. check_pgactivity).

  Check:
  * `OK`: if there is a leader node.
  * 'WARNING': if there is a stanby leader in archive mode.
  * `CRITICAL`: otherwise.

  Perfdata:
  * `has_leader` is 1 if there is any kind of leader node, 0 otherwise
  * `is_standby_leader_in_arc_rec` is 1 if the standby leader node is "in
     archive recovery", 0 otherwise
  * `is_standby_leader` is 1 if there is a standby leader node, 0 otherwise
  * `is_leader` is 1 if there is a "classical" leader node, 0 otherwise

Options:
  --help  Show this message and exit.
```

### cluster_has_replica

```
Usage: check_patroni cluster_has_replica [OPTIONS]

  Check if the cluster has healthy replicas and/or if some are sync standbies

  For patroni (and this check):
  * a replica is `streaming` if the `pg_stat_wal_receiver` say's so.
  * a replica is `in archive recovery`, if it's not `streaming` and has a `restore_command`.

  A healthy replica:
  * has a `replica` or `sync_standby` role
  * has the same timeline as the leader and
    * is in `running` state (patroni < V3.0.4)
    * is in `streaming` or `in archive recovery` state (patroni >= V3.0.4)
  * has a lag lower or equal to `max_lag`

  Please note that replica `in archive recovery` could be stuck because the
  WAL are not available or applicable (the server's timeline has diverged for
  the leader's). We already detect the latter but we will miss the former.
  Therefore, it's preferable to check for the lag in addition to the healthy
  state if you rely on log shipping to help lagging standbies to catch up.

  Since we require a healthy replica to have the same timeline as the leader,
  it's possible that we raise alerts when the cluster is performing a
  switchover or failover and the standbies are in the process of catching up
  with the new leader. The alert shouldn't last long.

  Check:
  * `OK`: if the healthy_replica count and their lag are compatible with the replica count threshold.
          and if the sync_replica count is compatible with the sync replica count threshold.
  * `WARNING` / `CRITICAL`: otherwise

  Perfdata:
  * healthy_replica & unhealthy_replica count
  * the number of sync_replica, they are included in the previous count
  * the lag of each replica labelled with "member name"_lag
  * the timeline of each replica labelled with "member name"_timeline
  * a boolean to tell if the node is a sync stanbdy labelled with "member name"_sync

Options:
  -w, --warning TEXT    Warning threshold for the number of healthy replica
                        nodes.
  -c, --critical TEXT   Critical threshold for the number of healthy replica
                        nodes.
  --sync-warning TEXT   Warning threshold for the number of sync replica.
  --sync-critical TEXT  Critical threshold for the number of sync replica.
  --max-lag TEXT        maximum allowed lag
  --help                Show this message and exit.
```

### cluster_has_scheduled_action

```
Usage: check_patroni cluster_has_scheduled_action [OPTIONS]

  Check if the cluster has a scheduled action (switchover or restart)

  Check:
  * `OK`: If the cluster has no scheduled action
  * `CRITICAL`: otherwise.

  Perfdata:
  * `scheduled_actions` is 1 if the cluster has scheduled actions.
  * `scheduled_switchover` is 1 if the cluster has a scheduled switchover.
  * `scheduled_restart` counts the number of scheduled restart in the cluster.

Options:
  --help  Show this message and exit.
```

### cluster_is_in_maintenance

```
Usage: check_patroni cluster_is_in_maintenance [OPTIONS]

  Check if the cluster is in maintenance mode or paused.

  Check:
  * `OK`: If the cluster is in maintenance mode.
  * `CRITICAL`: otherwise.

  Perfdata:
  * `is_in_maintenance` is 1 the cluster is in maintenance mode,  0 otherwise

Options:
  --help  Show this message and exit.
```

### cluster_node_count

```
Usage: check_patroni cluster_node_count [OPTIONS]

  Count the number of nodes in the cluster.

  The role refers to the role of the server in the cluster. Possible values
  are:
  * master or leader
  * replica
  * standby_leader
  * sync_standby
  * demoted
  * promoted
  * uninitialized

  The state refers to the state of PostgreSQL. Possible values are:
  * initializing new cluster, initdb failed
  * running custom bootstrap script, custom bootstrap failed
  * starting, start failed
  * restarting, restart failed
  * running, streaming, in archive recovery
  * stopping, stopped, stop failed
  * creating replica
  * crashed

  The "healthy" checks only ensures that:
  * a leader has the running state
  * a standby_leader has the running or streaming (V3.0.4) state
  * a replica or sync-standby has the running or streaming (V3.0.4) state

  Since we dont check the lag or timeline, "in archive recovery" is not
  considered a valid state for this service. See cluster_has_leader and
  cluster_has_replica for specialized checks.

  Check:
  * Compares the number of nodes against the normal and healthy nodes warning and critical thresholds.
  * `OK`:  If they are not provided.

  Perfdata:
  * `members`: the member count.
  * `healthy_members`: the running and streaming member count.
  * all the roles of the nodes in the cluster with their count (start with "role_").
  * all the statuses of the nodes in the cluster with their count (start with "state_").

Options:
  -w, --warning TEXT       Warning threshold for the number of nodes.
  -c, --critical TEXT      Critical threshold for the number of nodes.
  --healthy-warning TEXT   Warning threshold for the number of healthy nodes
                           (running + streaming).
  --healthy-critical TEXT  Critical threshold for the number of healthy nodes
                           (running + streaming).
  --help                   Show this message and exit.
```

## Node services

### node_is_alive

```
Usage: check_patroni node_is_alive [OPTIONS]

  Check if the node is alive ie patroni is running. This is a liveness check
  as defined in Patroni's documentation.

  Check:
  * `OK`: If patroni is running.
  * `CRITICAL`: otherwise.

  Perfdata:
  * `is_running` is 1 if patroni is running, 0 otherwise

Options:
  --help  Show this message and exit.
```

### node_is_pending_restart

```
Usage: check_patroni node_is_pending_restart [OPTIONS]

  Check if the node is in pending restart state.

  This situation can arise if the configuration has been modified but requires
  a restart of PostgreSQL to take effect.

  Check:
  * `OK`: if the node has no pending restart tag.
  * `CRITICAL`: otherwise

  Perfdata: `is_pending_restart` is 1 if the node has pending restart tag, 0
  otherwise.

Options:
  --help  Show this message and exit.
```

### node_is_leader

```
Usage: check_patroni node_is_leader [OPTIONS]

  Check if the node is a leader node.

  This check applies to any kind of leaders including standby leaders. To
  check explicitly for a standby leader use the `--is-standby-leader` option.

  Check:
  * `OK`: if the node is a leader.
  * `CRITICAL:` otherwise

  Perfdata: `is_leader` is 1 if the node is a leader node, 0 otherwise.

Options:
  --is-standby-leader  Check for a standby leader
  --help               Show this message and exit.
```

### node_is_primary

```
Usage: check_patroni node_is_primary [OPTIONS]

  Check if the node is the primary with the leader lock.

  This service is not valid for a standby leader, because this kind of node is
  not a primary.

  Check:
  * `OK`: if the node is a primary with the leader lock.
  * `CRITICAL:` otherwise

  Perfdata: `is_primary` is 1 if the node is a primary with the leader lock, 0
  otherwise.

Options:
  --help  Show this message and exit.
```

### node_is_replica

```
Usage: check_patroni node_is_replica [OPTIONS]

  Check if the node is a replica with no noloadbalance tag.

  It is possible to check if the node is synchronous or asynchronous. If
  nothing is specified any kind of replica is accepted.  When checking for a
  synchronous replica, it's not possible to specify a lag.

  This service is using the following Patroni endpoints: replica, asynchronous
  and synchronous. The first two implement the `lag` tag. For these endpoints
  the state of a replica node doesn't reflect the replication state
  (`streaming` or `in archive recovery`), we only know if it's `running`. The
  timeline is also not checked.

  Therefore, if a cluster is using asynchronous replication, it is recommended
  to check for the lag to detect a divegence as soon as possible.

  Check:
  * `OK`: if the node is a running replica with noloadbalance tag and the lag is under the maximum threshold.
  * `CRITICAL`:  otherwise

  Perfdata: `is_replica` is 1 if the node is a running replica with
  noloadbalance tag and the lag is under the maximum threshold, 0 otherwise.

Options:
  --max-lag TEXT  maximum allowed lag
  --is-sync       check if the replica is synchronous
  --is-async      check if the replica is asynchronous
  --help          Show this message and exit.
```

### node_patroni_version

```
Usage: check_patroni node_patroni_version [OPTIONS]

  Check if the version is equal to the input

  Check:
  * `OK`: The version is the same as the input `--patroni-version`
  * `CRITICAL`: otherwise.

  Perfdata:
  * `is_version_ok` is 1 if version is ok, 0 otherwise

Options:
  --patroni-version TEXT  Patroni version to compare to  [required]
  --help                  Show this message and exit.
```

### node_tl_has_changed

```
Usage: check_patroni node_tl_has_changed [OPTIONS]

  Check if the timeline has changed.

  Note: either a timeline or a state file must be provided for this service to
  work.

  Check:
  * `OK`: The timeline is the same as last time (`--state_file`) or the inputted timeline (`--timeline`)
  * `CRITICAL`: The tl is not the same.

  Perfdata:
  * `is_timeline_changed` is 1 if the tl has changed, 0 otherwise
  * the timeline

Options:
  --timeline TEXT        A timeline number to compare with.
  -s, --state-file TEXT  A state file to store the last tl number into.
  --save                 Set the current timeline number as the reference for
                         future calls.
  --help                 Show this message and exit.
```


