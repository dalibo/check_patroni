#!/bin/bash

README="../README.md"
function readme(){
	echo "$1" >> $README
}

function helpme(){
	readme
	readme "\`\`\`"
	check_patroni $1 --help >> $README
	readme "\`\`\`"
	readme
}

cat << _EOF_ > $README
# check_patroni
_EOF_
helpme
readme "## cluster services" 
readme "### cluster_config_has_changed"
helpme cluster_config_has_changed
readme "### cluster_has_leader"
helpme cluster_has_leader
readme "### cluster_has_replica"
helpme cluster_has_replica
readme "### cluster_is_in_maintenance"
helpme  cluster_is_in_maintenance
readme "### cluster_node_count"
helpme  cluster_node_count
readme "## node services" 
readme "### node_is_alive"
helpme node_is_alive
readme "### node_is_pending_restart"
helpme node_is_pending_restart
readme "### node_is_primary"
helpme node_is_primary
readme "### node_is_replica"
helpme node_is_replica
readme "### node_patroni_version"
helpme node_patroni_version
readme "### node_tl_has_changed"
helpme node_tl_has_changed
cat << _EOF_ >> $README

_EOF_
