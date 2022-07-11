#!/usr/bin/env bash

info(){
	echo "$1"
}

usage(){
	echo "$0 ACTION CLUSTER_NAME [NODE..]"
	echo ""
	echo " ACTION: init | add"
	echo " CLUSTER: cluster name"
	echo " NODE: HOST=IP"
	echo "   HOST: any name for icinga"
	echo "   IP: the IP"
}

if [ "$#" -le "3" ]; then 
	usage
	exit 1
fi

ACTION="$1"
shift
CLUSTER="$1"
shift
NODES=( "$@" )

TARGET="/etc/icinga2/conf.d/check_patroni.conf"

#set -o errexit
set -o nounset
set -o pipefail

init(){
	cat << '__EOF__' > "$TARGET"
# ===================================================================
# Check Commands
# ===================================================================
template CheckCommand "check_patroni" {
  command = [ PluginDir + "/check_patroni" ]

  arguments = {
    "--endpoints" = {
      value = "$endpoints$"
      order = -2
      repeat_key = true
    }
    "--timeout" = {
      value = "$timeout$"
      order = -1
    }
  }
}

object CheckCommand "check_patroni_node_is_alive" {
  import "check_patroni"

  arguments += {
    "node_is_alive" = {
      order = 1
    }
  }
}

object CheckCommand "check_patroni_node_is_primary" {
  import "check_patroni"

  arguments += {
    "node_is_primary" = {
      order = 1
    }
  }
}

object CheckCommand "check_patroni_node_is_replica" {
  import "check_patroni"

  arguments += {
    "node_is_replica" = {
      order = 1
    }
  }
}

object CheckCommand "check_patroni_node_is_pending_restart" {
  import "check_patroni"

  arguments += {
    "node_is_pending_restart" = {
      order = 1
    }
  }
}

object CheckCommand "check_patroni_node_patroni_version" {
  import "check_patroni"

  arguments += {
    "node_patroni_version" = {
      order = 1
    }
    "--patroni-version" = {
      value = "$patroni_version$"
      order = 2
    }
  }
}

object CheckCommand "check_patroni_node_tl_has_changed" {
  import "check_patroni"

  arguments += {
    "node_tl_has_changed" = {
      order = 1
    }
    "--state-file" = {
      value = "/tmp/$state_file$"  # a quick and dirty way for this poc
      order = 2
    }
  }
}

# -------------------------------------------------------------------

object CheckCommand "check_patroni_cluster_has_leader" {
  import "check_patroni"

  arguments += {
    "cluster_has_leader" = {
      order = 1
    }
  }
}

object CheckCommand "check_patroni_cluster_has_replica" {
  import "check_patroni"

  arguments += {
    "cluster_has_replica" = {
      order = 1
    }
    "--warning" = {
			value = "$has_replica_warning$"
			order = 2
    }
    "--critical" = {
			value = "$has_replica_critical$"
			order = 3
    }
  }
}

object CheckCommand "check_patroni_cluster_config_has_changed" {
  import "check_patroni"

  arguments += {
    "cluster_config_has_changed" = {
      order = 1
    }
    "--state-file" = {
      value = "/tmp/$state_file$"  # a quick and dirty way for this poc
      order = 2
    }
  }
}

object CheckCommand "check_patroni_cluster_is_in_maintenance" {
  import "check_patroni"

  arguments += {
    "cluster_is_in_maintenance" = {
      order = 1
    }
	}
}

object CheckCommand "check_patroni_cluster_node_count" {
  import "check_patroni"

  arguments += {
    "cluster_node_count" = {
      order = 1
    }
    "--warning" = {
			value = "$node_count_warning$"
			order = 2
    }
    "--critical" = {
			value = "$node_count_critical$"
			order = 3
    }
    "--running-warning" = {
			value = "$node_count_running_warning$"
			order = 4
    }
    "--running-critical" = {
			value = "$node_count_running_critical$"
			order = 5
    }
  }
}

# ===================================================================
# Services
# ===================================================================
template Service "check_patroni" {
  max_check_attempts = 3
  check_interval = 1m     # we spam a little for the sake of testing
  retry_interval = 15     # we spam a little for the sake of testing
  enable_perfdata = true
  vars.timeout = 10
}

apply Service "check_patroni_node_is_alive" {
  import "check_patroni"
  check_command = "check_patroni_node_is_alive"

  assign where "patroni_servers" in host.groups
}

apply Service "check_patroni_node_is_primary" {
  import "check_patroni"
  check_command = "check_patroni_node_is_primary"

  assign where "patroni_servers" in host.groups
}

apply Service "check_patroni_node_is_replica" {
  import "check_patroni"
  check_command = "check_patroni_node_is_replica"

  assign where "patroni_servers" in host.groups
}

apply Service "check_patroni_node_is_pending_restart" {
  import "check_patroni"
  check_command = "check_patroni_node_is_pending_restart"

  assign where "patroni_servers" in host.groups
}

apply Service "check_patroni_node_patroni_version" {
  import "check_patroni"
  check_command = "check_patroni_node_patroni_version"

  assign where "patroni_servers" in host.groups
}

apply Service "check_patroni_node_tl_has_changed" {
  import "check_patroni"
  vars.state_file = host.name + ".state"
  check_command = "check_patroni_node_tl_has_changed"

  assign where "patroni_servers" in host.groups
}

# -------------------------------------------------------------------

apply Service "check_patroni_cluster_has_leader" {
  import "check_patroni"
  check_command = "check_patroni_cluster_has_leader"

  assign where "patroni_clusters" in host.groups
}

apply Service "check_patroni_cluster_has_replica" {
  import "check_patroni"
  check_command = "check_patroni_cluster_has_replica"

  assign where "patroni_clusters" in host.groups
}

apply Service "check_patroni_cluster_config_has_changed" {
  import "check_patroni"
  vars.state_file = host.name + ".state"
  check_command = "check_patroni_cluster_config_has_changed"

  assign where "patroni_clusters" in host.groups
}

apply Service "check_patroni_cluster_is_in_maintenance" {
  import "check_patroni"
  check_command = "check_patroni_cluster_is_in_maintenance"

  assign where "patroni_clusters" in host.groups
}

apply Service "check_patroni_cluster_node_count" {
  import "check_patroni"
  check_command = "check_patroni_cluster_node_count"

  assign where "patroni_clusters" in host.groups
}

# ===================================================================
# Hosts meta
# ===================================================================
object HostGroup "patroni_servers" {
  display_name = "patroni servers"
}

template Host "patroni_servers" {
  groups = [ "patroni_servers" ]
  check_command = "hostalive"

  vars.patroni_version = "2.1.2"
}

# -------------------------------------------------------------------

object HostGroup "patroni_clusters" {
  display_name = "patroni clusters"
}

template Host "patroni_clusters" {
  groups = [ "patroni_clusters" ]
  check_command = "dummy"
}

# ===================================================================
# Hosts meta
# ===================================================================
__EOF__
}

add_hosts(){
	NODES=$@
	for N in "${NODES[@]}"; do
		IP="${N##*=}"
		HOST="${N%=*}"

		cat << __EOF__ >> "$TARGET"

object Host "$HOST" {
  import "patroni_servers"

  display_name = "Server patroni $HOST"
  address = "$IP"

  vars.endpoints = [ "http://" + address + ":8008" ]
}
__EOF__
	done
}

add_cluster(){
	CLUSTER=$1
	NODES=$2

	NAME=""
	IPS=" "
	for N in "${NODES[@]}"; do
		IP="${N##*=}"
		HOST="${N%=*}"

		NAME="$NAME $HOST"
		IPS="$IPS\"http://${IP}:8008\", "
	done

	cat << __EOF__ >> "$TARGET"

object Host "$CLUSTER" {
  import "patroni_clusters"

  display_name = "Cluster: $CLUSTER ($NAME )"

  vars.endpoints = [$IPS ]
  vars.has_replica_warning = "1:"
  vars.has_replica_critical = "1:"
  vars.node_count_warning = "2:"
  vars.node_count_critical = "1:"
  vars.node_count_running_warning = "2:"
  vars.node_count_running_critical = "1:"
}
__EOF__
}

case "$ACTION" in
	"init")
		init
		add_hosts "$NODES"
		add_cluster "$CLUSTER" "$NODES"
		;;
	"add")
		add_hosts "$NODES"
		add_cluster "$CLUSTER" "$NODES"
		;;
	*)
		usage
		echo "error: invalid action"
		exit 1
esac
