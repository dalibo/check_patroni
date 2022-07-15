#!/usr/bin/env bash

info (){
	echo "$1"
}

ORIGIN=$1

set -o errexit
set -o nounset
set -o pipefail

info "#============================================================================="
info "# check_patroni"
info "#============================================================================="

DEBIAN_FRONTEND=noninteractive apt install -q -y git python3-pip
pip3 install --upgrade pip

case "$ORIGIN" in
	"test")
		cd /check_patroni
		pip3 install .
		ln -s /usr/local/bin/check_patroni /usr/lib/nagios/plugins/check_patroni 
		;;
	"official")
		pip3 install check_patroni
		;;
	*)
		echo "Origin : [$ORIGIN] is not supported"
		exit 1
esac

check_patroni --version
