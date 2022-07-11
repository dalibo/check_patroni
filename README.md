# check_patroni

A nagios plugin for patroni.

## Features

- Check presence of leader, replicas, node counts.
- Check each node for replication status.


```
Usage: check_patroni [OPTIONS] COMMAND [ARGS]...

  Nagios plugin for patroni.

Options:
  --config FILE         Read option defaults from the specified INI file
                        [default: config.ini]
  -e, --endpoints TEXT  API endpoint. Can be specified multiple times.
                        [default: http://127.0.0.1:8008]
  --cert_file TEXT      File with the client certificate.
  --key_file TEXT       File with the client key.
  --ca_file TEXT        The CA certificate.
  -v, --verbose         Increase verbosity -v (info)/-vv (warning)/-vvv
                        (debug)
  --version
  --timeout INTEGER     Timeout in seconds for the API queries (0 to disable)
                        [default: 2]
  --help                Show this message and exit.

Commands:
  cluster_config_has_changed  Check if the hash of the configuration has...
  cluster_has_leader          Check if the cluster has a leader.
  cluster_has_replica         Check if the cluster has healthy replicas.
  cluster_is_in_maintenance   Check if the cluster is in maintenance mode...
  cluster_node_count          Count the number of nodes in the cluster.
  node_is_alive               Check if the node is alive ie patroni is...
  node_is_pending_restart     Check if the node is in pending restart state.
  node_is_primary             Check if the node is the primary with the...
  node_is_replica             Check if the node is a running replica with...
  node_patroni_version        Check if the version is equal to the input
  node_tl_has_changed         Check if the timeline has changed.
```

## Install

check_patroni is licensed under PostgreSQL license.

```
$ pip install git+https://github.com/dalibo/check_patroni.git
```

Links:
* [pip & centos 7](https://linuxize.com/post/how-to-install-pip-on-centos-7/)
* [pip & debian10](https://linuxize.com/post/how-to-install-pip-on-debian-10/)

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

* a warning if there is less than 1 nodes, wich can be translated to outside of range [2;+INF[
* a critical if there are no nodes, wich can be translated to outside of range [1;+INF[

```
check_patroni -e https://10.20.199.3:8008 cluster_has_replica --warning 2: --critical 1:
```

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
  --help                 Show this message and exit.
```

### cluster_has_leader

```
Usage: check_patroni cluster_has_leader [OPTIONS]

  Check if the cluster has a leader.

  Note: there is no difference between a normal and standby leader.

  Check:
  * `OK`: if there is a leader node.
  * `CRITICAL`: otherwise

  Perfdata: `has_leader` is 1 if there is a leader node, 0 otherwise

Options:
  --help  Show this message and exit.
```

### cluster_has_replica

```
Usage: check_patroni cluster_has_replica [OPTIONS]

  Check if the cluster has healthy replicas.

  A healthy replica:
  * is in running state
  * has a replica role
  * has a lag lower or equal to max_lag

  Check:
  * `OK`: if the healthy_replica count and their lag are compatible with the replica count threshold.
  * `WARNING` / `CRITICAL`: otherwise

  Perfdata:
  * healthy_replica & unhealthy_replica count
  * the lag of each replica labelled with  "member name"_lag

Options:
  -w, --warning TEXT   Warning threshold for the number of healthy replica
                       nodes.
  -c, --critical TEXT  Critical threshold for the number of healthy replica
                       nodes.
  --max-lag TEXT       maximum allowed lag
  --help               Show this message and exit.
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

  Check:
  * Compares the number of nodes against the normal and running node warning and critical thresholds.
  * `OK`:  If they are not provided.

  Perfdata:
  * `members`: the member count.
  * all the roles of the nodes in the cluster with their number.
  * all the statuses of the nodes in the cluster with their number.

Options:
  -w, --warning TEXT       Warning threshold for the number of nodes.
  -c, --critical TEXT      Critical threshold for the number of nodes.
  --running-warning TEXT   Warning threshold for the number of running nodes.
  --running-critical TEXT  Critical threshold for the number of running nodes.
  --help                   Show this message and exit.
```

## Node services

### node_is_alive

```
Usage: check_patroni node_is_alive [OPTIONS]

  Check if the node is alive ie patroni is running.

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

  This situation can arise if the configuration has been modified but requiers
  a restart of PostgreSQL to take effect.

  Check:
  * `OK`: if the node has pending restart tag.
  * `CRITICAL`: otherwise

  Perfdata: `is_pending_restart` is 1 if the node has pending restart tag, 0
  otherwise.

Options:
  --help  Show this message and exit.
```

### node_is_primary

```
Usage: check_patroni node_is_primary [OPTIONS]

  Check if the node is the primary with the leader lock.

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

  Check if the node is a running replica with no noloadbalance tag.

  Check:
  * `OK`: if the node is a running replica with noloadbalance tag and the lag is under the maximum threshold.
  * `CRITICAL`:  otherwise

  Perfdata: `is_replica` is 1 if the node is a running replica with
  noloadbalance tag and the lag is under the maximum threshold, 0 otherwise.

Options:
  --max-lag TEXT  maximum allowed lag
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
  * `OK`: The timeline is the same as last time (`--state_file`) or the inputed timeline (`--timeline`)
  * `CRITICAL`: The tl is not the same.

  Perfdata:
  * `is_timeline_changed` is 1 if the tl has changed, 0 otherwise
  * the timeline

Options:
  --timeline TEXT        A timeline number to compare with.
  -s, --state-file TEXT  A state file to store the last tl number into.
  --help                 Show this message and exit.
```


