# Change log

## Unreleased

### Added

### Fixed

### Misc

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

