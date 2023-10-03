#!/usr/bin/env bash

info (){
	echo "$1"
}

#set -o errexit
set -o nounset
set -o pipefail

NODENAME="$1"
shift

PG_ICINGA_USER_NAME="supervisor"
PG_ICINGA_USER_PWD="th3Pass"
PG_ICINGAWEB_USER_NAME="supervisor"
PG_ICINGAWEB_USER_PWD="th3Pass"
PG_DIRECTOR_USER_NAME="supervisor"
PG_DIRECTOR_USER_PWD="th3Pass"
PG_OPM_USER_NAME="opm"
PG_OPM_USER_PWD="th3Pass"
PG_GRAFANA_USER_NAME="supervisor"
PG_GRAFANA_USER_PWD="th3Pass"

set_hostname(){
	info "#============================================================================="
	info "# hostname and /etc/hosts setup"
	info "#============================================================================="
	hostnamectl set-hostname "${NODENAME}"
	sed --in-place -e "s/\(127\.0\.0\.1\s*localhost$\)/\1 ${NODENAME}/" /etc/hosts
}

packages(){
	info "#============================================================================="
	info "# install required repos and packages"
	info "#============================================================================="
	apt-get update || true
	apt-get -y install apt-transport-https wget gnupg software-properties-common 

	DIST=$(awk -F"[)(]+" '/VERSION=/ {print $2}' /etc/os-release)
	echo "deb https://packages.icinga.com/debian icinga-${DIST} main" > "/etc/apt/sources.list.d/${DIST}-icinga.list"
	echo "deb-src https://packages.icinga.com/debian icinga-${DIST} main" >> "/etc/apt/sources.list.d/${DIST}-icinga.list"
	echo "deb https://packages.grafana.com/oss/deb stable main" > /etc/apt/sources.list.d/grafana.list
	echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

	wget -q -O - https://packages.icinga.com/icinga.key | apt-key add -
	wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
	wget -q -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

	apt-get update || true

	PACKAGES=(
		grafana 
		icinga2 icinga2-ido-pgsql icingaweb2 icingaweb2-module-monitoring icingacli 
		postgresql-client postgresql-14 
		php7.3-pgsql php7.3-imagick php7.3-intl
		nagios-plugins  
	)
	DEBIAN_FRONTEND=noninteractive apt install -q -y "${PACKAGES[@]}"

	systemctl --quiet --now enable postgresql@14
}

icinga_setup(){
	info "#============================================================================="
	info "# Icinga setup"
	info "#============================================================================="

## this part is already done by the standard icinga install with the user icinga2
## and a random password, here we dont really care

	cat << __EOF__ | sudo -u postgres psql 
DROP ROLE IF EXISTS supervisor;
DROP DATABASE IF EXISTS icinga2;
CREATE ROLE ${PG_ICINGA_USER_NAME} WITH LOGIN SUPERUSER PASSWORD '${PG_ICINGA_USER_PWD}';
CREATE DATABASE icinga2;
__EOF__
	echo "*:*:*:${PG_ICINGA_USER_NAME}:${PG_ICINGA_USER_PWD}" > ~postgres/.pgpass
	chown postgres:postgres ~postgres/.pgpass
	chmod 600 ~postgres/.pgpass
	PGPASSFILE=~postgres/.pgpass psql -U $PG_ICINGA_USER_NAME -h 127.0.0.1 -d icinga2 -f /usr/share/icinga2-ido-pgsql/schema/pgsql.sql

	icingacli setup config directory --group icingaweb2
	icingacli setup token create

## this part is already done by the standard icinga install with the user icinga2
	cat << __EOF__ > /etc/icinga2/features-available/ido-pgsql.conf 
/**
 * The db_ido_pgsql library implements IDO functionality
 * for PostgreSQL.
 */

library "db_ido_pgsql"

object IdoPgsqlConnection "ido-pgsql" {
  user = "${PG_ICINGA_USER_NAME}",
  password = "${PG_ICINGA_USER_PWD}",
  host = "localhost",
  database = "icinga2"
}
__EOF__
	icinga2 feature enable ido-pgsql
	icinga2 feature enable command
	icinga2 feature enable perfdata

#icinga2 node wizard
	icinga2 node setup --master --cn s1 --zone master

	systemctl restart icinga2.service
}

icinga_API(){
	info "#============================================================================="
	info "# Icinga API"
	info "#============================================================================="
	icinga2 api setup

	cat <<__EOF__ >>  /etc/icinga2/conf.d/api-users.conf
object ApiUser "icingaapi" {
  password = "th3Pass"
  permissions = [ "*" ]
}
__EOF__
	systemctl restart icinga2.service
}

icinga_web(){
	info "#============================================================================="
	info "# Icinga2 Web"
	info "#============================================================================="
	if [ "$PG_ICINGA_USER_NAME" != "$PG_ICINGAWEB_USER_NAME" ]; then
		sudo -u postgres psql -c "CREATE ROLE ${PG_ICINGAWEB_USER_NAME} WITH LOGIN PASSWORD '${PG_ICINGAWEB_USER_PWD}';"
	fi
	sudo -u postgres psql -c "CREATE DATABASE icingaweb_db OWNER ${PG_ICINGAWEB_USER_NAME};"

	sed --in-place -e "s/;date\.timezone =/date.timezone =  europe\/paris/" /etc/php/7.3/apache2/php.ini 
	a2enconf icingaweb2
	a2enmod rewrite
	a2dismod mpm_event
	a2enmod php7.3

	systemctl restart apache2
}

director(){
	info "#============================================================================="
	info "# Icinga director"
	info "#============================================================================="
# Create the database
	if [ "$PG_ICINGA_USER_NAME" != "$PG_DIRECTOR_USER_NAME" ]; then
		sudo -u postgres psql -c "CREATE ROLE ${PG_DIRECTOR_USER_NAME} WITH LOGIN PASSWORD '${PG_DIRECTOR_USER_PWD}';"
	fi
	sudo -u postgres psql -c "CREATE DATABASE director_db OWNER ${PG_DIRECTOR_USER_NAME};"
	sudo -iu postgres psql -d director_db -c "CREATE EXTENSION pgcrypto;"

## Prereq
	MODULE_NAME=incubator
	MODULE_VERSION=v0.11.0
	MODULES_PATH="/usr/share/icingaweb2/modules"
	MODULE_PATH="${MODULES_PATH}/${MODULE_NAME}"
	RELEASES="https://github.com/Icinga/icingaweb2-module-${MODULE_NAME}/archive"
	mkdir "$MODULE_PATH" \
	&& wget -q $RELEASES/${MODULE_VERSION}.tar.gz -O - \
	   | tar xfz - -C "$MODULE_PATH" --strip-components 1
	icingacli module enable "${MODULE_NAME}"

## Director
	MODULE_VERSION="1.8.1"
	ICINGAWEB_MODULEPATH="/usr/share/icingaweb2/modules"
	REPO_URL="https://github.com/icinga/icingaweb2-module-director"
	TARGET_DIR="${ICINGAWEB_MODULEPATH}/director"
	URL="${REPO_URL}/archive/v${MODULE_VERSION}.tar.gz"

	useradd -r -g icingaweb2 -d /var/lib/icingadirector -s /bin/false icingadirector
	install -d -o icingadirector -g icingaweb2 -m 0750 /var/lib/icingadirector
	install -d -m 0755 "${TARGET_DIR}"
	wget -q -O - "$URL" | tar xfz - -C "${TARGET_DIR}" --strip-components 1
	cp "${TARGET_DIR}/contrib/systemd/icinga-director.service" /etc/systemd/system/

	icingacli module enable director
	systemctl daemon-reload
	systemctl enable icinga-director.service
	systemctl start icinga-director.service
	
# The permission have to be like this to let icingaweb activate modules
	chown -R www-data:icingaweb2 /etc/icingaweb2
}

grafana(){
	info "#============================================================================="
	info "# Grafana"
	info "#============================================================================="
	if [ "$PG_ICINGA_USER_NAME" != "$PG_GRAFANA_USER_NAME" ]; then
		sudo -u postgres psql -c "CREATE ROLE ${PG_GRAFANA_USER_NAME} WITH LOGIN PASSWORD '${PG_GRAFANA_USER_PWD}';"
	fi
	sudo -u postgres psql -c "CREATE DATABASE grafana OWNER ${PG_GRAFANA_USER_NAME};"

	cat << __EOF__ > /etc/grafana/grafana.ini 
[database]
# You can configure the database connection by specifying type, host, name, user and password
# as separate properties or as on string using the url property.

# Either "mysql", "postgres" or "sqlite3", it's your choice
type = postgres
host = 127.0.0.1:5432
name = grafana
user = $PG_GRAFANA_USER_NAME
password = $PG_GRAFANA_USER_PWD
__EOF__
	systemctl --quiet --now enable grafana-server.service
}

opm(){
	info "#============================================================================="
	info "# OPM"
	info "#============================================================================="

## OPM Install

	DEBIAN_FRONTEND=noninteractive apt install -q -y postgresql-server-dev-10 libdbd-pg-perl git build-essential

	cd /usr/local/src || exit 1
	git clone https://github.com/OPMDG/opm-core.git
	git clone https://github.com/OPMDG/opm-wh_nagios.git
	cd /usr/local/src/opm-wh_nagios/pg/ || exit 1
	make install
	cd /usr/local/src/opm-core/pg/ || exit 1
	make install

## OPM db setup

	cat << __EOF__ | sudo -iu postgres psql 
CREATE ROLE ${PG_OPM_USER_NAME} WITH LOGIN PASSWORD '${PG_OPM_USER_PWD}';
CREATE DATABASE opm OWNER ${PG_OPM_USER_NAME};
__EOF__
	cat << __EOF__ | sudo -iu postgres psql -d opm
CREATE EXTENSION opm_core;
CREATE EXTENSION wh_nagios CASCADE;
SELECT * FROM grant_dispatcher('wh_nagios', 'opm');
__EOF__

## OPM dispatcher

	cat <<EOF > /etc/opm_dispatcher.conf
daemon=0
directory=/var/spool/icinga2/perfdata
frequency=5
db_connection_string=dbi:Pg:dbname=opm host=localhost
db_user=${PG_OPM_USER_NAME}
db_password=${PG_OPM_USER_PWD}
debug=0
syslog=1
hostname_filter = /^$/ # Empty hostname. Never happens
service_filter = /^$/ # Empty service
label_filter = /^$/ # Empty label
EOF

	cat <<'EOF' > /etc/systemd/system/opm_dispatcher.service
[Unit]
Description=dispatcher nagios, import perf files from icinga to opm

[Service]
User=nagios
Group=nagios
ExecStart=/usr/local/src/opm-wh_nagios/bin/nagios_dispatcher.pl -c /etc/opm_dispatcher.conf

# start right after boot
Type=simple
# restart on crash
Restart=always
# after 10s
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

## OPM planned task

	cat <<'EOF' > /etc/systemd/system/opm_dispatch_record.service
[Unit]
Description=Run wh_nagios.dispatch_record() on OPM database

[Service]
Type=oneshot
User=postgres
Group=postgres
SyslogIdentifier=opm_dispatch_record
ExecStart=/usr/bin/psql -U postgres -d opm -c "SELECT * FROM wh_nagios.dispatch_record()"
EOF

	cat <<'EOF' > /etc/systemd/system/opm_dispatch_record.timer 
[Unit]
Description=Timer to run wh_nagios.dispatch_record() on OPM

[Timer]
OnBootSec=60s
OnUnitInactiveSec=1min

[Install]
WantedBy=timers.target
EOF

	systemctl daemon-reload
	systemctl enable opm_dispatcher
	systemctl start opm_dispatcher
	systemctl enable opm_dispatch_record.timer
	systemctl start opm_dispatch_record.timer

## To check once everything is setup (icingaweb is setup)
# sudo journalctl -fu opm_dispatcher
# sudo ournalctl -ft opm_dispatch_record

## Grants for graphana

	sudo -iu postgres psql -c "CREATE ROLE grafana WITH LOGIN PASSWORD 'th3Pass'"
	cat <<EOQ | sudo -iu postgres psql -d opm
GRANT CONNECT ON DATABASE opm TO ${PG_GRAPHANA_USER_NAME};
GRANT SELECT ON ALL TABLES IN SCHEMA public,wh_nagios TO ${PG_GRAPHANA_USER_NAME};
ALTER DEFAULT PRIVILEGES IN SCHEMA public, wh_nagios GRANT SELECT ON TABLES TO ${PG_GRAPHANA_USER_NAME};
GRANT USAGE ON SCHEMA public,wh_nagios TO ${PG_GRAPHANA_USER_NAME};
GRANT EXECUTE ON FUNCTION wh_nagios.get_metric_data(bigint, timestamptz, timestamptz) TO ${PG_GRAPHANA_USER_NAME};
GRANT USAGE ON SCHEMA pr_dalibo TO ${PG_GRAPHANA_USER_NAME};
GRANT EXECUTE ON FUNCTION pr_dalibo.variation_taille_service(p_hostname text, p_service text,
  p_label text, p_tstamp_debut timestamp with time zone, p_duree interval,
  OUT v_compteur_debut numeric, OUT v_compteur_fin numeric,
  OUT v_compteur_delta numeric, OUT v_type_corr text, OUT v_corr double precision,
  OUT v_taille_un_mois numeric) TO ${PG_GRAPHANA_USER_NAME};
GRANT EXECUTE ON FUNCTION pr_dalibo.pg_taille_jolie(p_valeur bigint, OUT v_jolie text) TO ${PG_GRAPHANA_USER_NAME};
EOQ
}

set_hostname
packages
icinga_setup
icinga_API
icinga_web
#director     ## Not needed anymore, kept for reference
grafana
opm

# "icingacli setup" doesnt work when the icinga2 web setup is finished
info "#============================================================================="
info "# Icinga Web -- $(icingacli setup token show)"
info "#============================================================================="

exit 0
