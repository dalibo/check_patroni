# Change log

## check_patroni 2.0.0 - 2024-04-09

### Changed

* In `cluster_node_count`, a healthy standby, sync replica or standby leaders cannot be "in
  archive recovery" because this service doesn't check for lag and timelines.

### Added

* Add the timeline in the  `cluster_has_replica` perfstats. (#50)
* Add a mention about shell completion support and shell versions in the doc. (#53)
* Add the leader type and whether it's archiving to the `cluster_has_leader` perfstats. (#58)

### Fixed

* Add compatibility with [requests](https://requests.readthedocs.io)
  version 2.25 and higher.
* Fix what `cluster_has_replica` deems a healthy replica. (#50, reported by @mbanck)
* Fix `cluster_has_replica` to display perfstats for replicas whenever it's possible (healthy or not). (#50)
* Fix `cluster_has_leader` to correctly check for standby leaders. (#58, reported by @mbanck)
* Fix `cluster_node_count` to correctly manage replication states. (#50, reported by @mbanck)

### Misc

* Improve the documentation for `node_is_replica`.
* Improve test coverage by running an HTTP server to fake the Patroni API (#55
  by @dlax).
* Work around old pytest versions in type annotations in the test suite.
* Declare compatibility with click version 7.1 (or higher).
* In tests, work around nagiosplugin 1.3.2 not properly handling stdout
  redirection.

## check_patroni 1.0.0 - 2023-08-28

Check patroni is now tagged as Production/Stable.

### Added

* Add `sync_standby` as a valid replica type for `cluster_has_replica`. (contributed by @mattpoel)
* Add info and options (`--sync-warning` and `--sync-critical`) about sync replica to `cluster_has_replica`.
* Add a new service `cluster_has_scheduled_action` to warn of any scheduled switchover or restart.
* Add options to `node_is_replica` to check specifically for a synchronous (`--is-sync`) or asynchronous node (`--is-async`).
* Add `standby-leader` as a valid leader type for `cluster_has_leader`.
* Add a new service `node_is_leader` to check if a node is a leader (which includes standby leader nodes)

### Fixed

* Fix the `node_is_alive` check. (#31)
* Fix the `cluster_has_replica` and `cluster_node_count` checks to account for
  the new replica state `streaming` introduced in v3.0.4 (#28, reported by @log1-c)

### Misc

* Create CHANGELOG.md
* Add tests for the output of the scripts in addition to the return code
* Documentation in CONTRIBUTING.md

## check_patroni 0.2.0 - 2023-03-20

### Added

* Add a `--save` option when state files are used
* Modify `-e/--endpoints` to allow a comma separated list of endpoints (#21, reported by @lihnjo)
* Use requests instead of urllib3 (with extensive help from @dlax)
* Change the way logging is handled (with extensive help from @dlax)

### Fix

* Reverse the test for `node_is_pending`
* SSL handling

### Misc

* Several doc Fix and Updates
* Use spellcheck and isort
* Remove tests for python 3.6
* Add python tests for python 3.11

## check_patroni 0.1.1 - 2022-07-15

The initial release covers the following checks :

* check a cluster for
  + configuration change
  + presence of a leader
  + presence of a replica
  + maintenance status
* check a node for
  + liveness
  + pending restart status
  + primary status
  + replica status
  + tl change
  + patroni version

