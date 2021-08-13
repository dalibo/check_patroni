#!/bin/bash

README="../README.md"
function readme(){
	echo "$1" >> $README
}

function helpme(){
	readme
	readme '```'
	check_patroni $1 --help >> $README
	readme '```'
	readme
}

cat << '_EOF_' > $README
# check_patroni
_EOF_
helpme
cat << '_EOF_' >> $README
## install

The check requers python3. Using a virtual env is advised for testing :

```
pip -m venv ~/venv
source ~venv/bin/activate
```

Clone the repo, then install with pip3 from it :

```
pip3 install .
pip3 install .[dev]
pip3 install .[test]
```

Links : 
* [pip & centos 7](https://linuxize.com/post/how-to-install-pip-on-centos-7/)
* [pip & debian10](https://linuxize.com/post/how-to-install-pip-on-debian-10/)

## config file

All global and service specific parameters can be specified via a config file has follows:

```
[options]
endpoints = https://10.20.199.3:8008, https://10.20.199.4:8008,https://10.20.199.5:8008
cert_file = ./ssl/benoit-dalibo-cert.pem
key_file = ./ssl/benoit-dalibo-key.pem
ca_file = ./ssl/CA-cert.pem
timeout = 0

[options.node_is_replica]
lag=100
```
_EOF_
readme
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
