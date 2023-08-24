#!/bin/bash

if [[ -z "$1" ]]; then
    echo "usage: $0 PATRONI_END_POINT"
    exit 1
fi

echo "-- Running patroni checks using endpoint $1"
echo "-- Cluster checks"
check_patroni -e "$1" cluster_config_has_changed --state-file cluster.sate_file --save
check_patroni -e "$1" cluster_has_leader
check_patroni -e "$1" cluster_has_replica
check_patroni -e "$1" cluster_is_in_maintenance
check_patroni -e "$1" cluster_has_scheduled_action
check_patroni -e "$1" cluster_node_count
echo "-- Node checks"
check_patroni -e "$1" node_is_alive
check_patroni -e "$1" node_is_pending_restart
check_patroni -e "$1" node_is_primary
check_patroni -e "$1" node_is_leader --is-standby-leader
check_patroni -e "$1" node_is_replica
check_patroni -e "$1" node_is_replica --is-sync
check_patroni -e "$1" node_patroni_version --patroni-version 3.1.0
check_patroni -e "$1" node_tl_has_changed --state-file cluster.sate_file --save
