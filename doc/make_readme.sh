#!/bin/bash

if ! command -v check_patroni &>/dev/null; then
	echo "check_partroni must be installed to generate the documentation"
	exit 1
fi

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
## thresholds

The format for the threshold parameters is "[@][start:][end]".

* "start:" may be omitted if start==0
* "~:" means that start is negative infinity
* If `end` is omitted, infinity is assumed
* To invert the match condition, prefix the range expression with "@".

A match is found when : start <= VALUE <= end

For example, the followinf command will raise :

* a warning if there is less than 1 nodes, wich can be translated to outside of range [2;+INF[
* a critical if there are no nodes, wich can be translated to outside of range [1;+INF[

```
check_patroni -e https://10.20.199.3:8008 cluster_has_replica --warning 2: --critical 1:
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
