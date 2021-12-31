# Icinga

## Install

Create the VM:

```
make
```

## IcingaWeb

Configure Icingaweb : 

```
http://$IP/icingaweb2/setup
```

* Screen 1: Welcome

  Use the icinga token given a the end of the `icinga2-setup` provision, or:

  ```
  sudo icingacli setup token show
  ```

  Next

* Screen 2: Modules

  Activate Monitor (already set)
 
  Next

* Screen 3: Icinga Web 2

  Next

* Screen 4: Authentication

  Next

* Screen 5: Database Resource

  Database Name: icingaweb_db
  Username: supervisor
  Password: th3Pass
  Charset: UTF8

  Validate
  Next

* Screen 6: Authentication Backend

  Next

* Screen 7: Administration

  Fill the blanks
  Next

* Screen 8: Application Configuration

  Next

* Screen 9: Summary

  Next

* Screen 10: Welcome ... again

  Next

* Screen 11: Monitoring IDO Resource

  Database Name: icinga2
  Username: supervisor
  Password: th3Pass
  Charset: UTF8

  Validate
  Next

* Screen 12: Command Transport

  Transaport name: icinga2
  Transport Type: API
  Host: 127.0.0.1
  Port: 5665
  User: icinga_api
  Password: th3Pass

  Next

* Screen 13: Monitoring Security

  Next

* Screen 14: Summary

  Finish

* Screen 15: Hopefuly success

  Login

## Add servers to icinga

``` 
# Connect to the vm 
vagrant ssh s1

# Create /etc/icinga2/conf.d/check_patroni.conf
sudo /vagrant/provision/director.bash init cluster1 p1=10.20.89.54 p2=10.20.89.55

# Check and load conf
sudo icinga2 daemon -C
sudo systemctl restart icinga2.service
```

# Grafana

Connect to: http://10.20.89.52:3000/login
User / pass: admin/admin

Import the dashboards for the grafana directory. They are created for cluster1,
and servers p1, p2.
