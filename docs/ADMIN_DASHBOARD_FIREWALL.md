# Production administrator dashboard firewall

This document records the verified firewall protection for the
GarminSupla administrator dashboard in the audited LXC deployment.

This is deployment-specific configuration, not a default installation
requirement. Adapt addresses, interface names and service paths for
other environments.

## Network layout

The IPv4 addresses in this guide are illustrative TEST-NET-1
examples (`192.0.2.0/24`), not production addresses.
Replace them with deployment-specific values before running
commands. Ports, service names and verified behavior describe
the audited installation.

- GarminSupla Docker host: LXC, `192.0.2.12`.
- Nginx Proxy Manager (NPM): separate CT, `192.0.2.10`.
- Administrator dashboard: `192.0.2.12:8009`, HTTP upstream.
- Watch API HTTPS: `192.0.2.12:8008`.
- Internal Watch API: `127.0.0.1:18008`.

The dashboard must be accessed through the separately secured
HTTPS reverse proxy, not directly over its HTTP upstream port.

NPM must retain access to port 8009. Other LAN clients must not
be able to connect directly to that port.

## Firewall implementation

Docker uses `iptables-nft`, with a `DOCKER-USER` chain reached
from `FORWARD`.

Docker translates host port 8009 to container port 8008 before
the packet reaches `DOCKER-USER`.

The rule therefore uses connection tracking to match the original
destination address and port rather than the container IP:

- Incoming interface: `eth0`.
- Allowed source: `192.0.2.10/32` (NPM).
- Original destination: `192.0.2.12`.
- Original destination TCP port: `8009`.
- Other matching sources: rejected with a TCP reset.

The rule does not depend on the dynamic IP address of the Docker
container. It does not target the Watch API listener on host port
8008.

The installed rule is maintained by:

- `/usr/local/sbin/garminsupla-admin8009-firewall`
- `/etc/systemd/system/garminsupla-admin8009-firewall.service`

The script supports `apply`, `remove` and `status`.

The main service is a systemd oneshot service, enabled under
`docker.service`, with `RemainAfterExit=yes` and
`PartOf=docker.service`.

## Periodic verification

The following units implement the watchdog:

- `/etc/systemd/system/garminsupla-admin8009-watchdog.service`
- `/etc/systemd/system/garminsupla-admin8009-watchdog.timer`

The timer is enabled and uses `OnCalendar=minutely`.

When Docker is active, the watchdog invokes the existing firewall
script with `apply`. If the exact rule already exists, no duplicate
is added.

## Operational checks

Run these commands as root inside the Docker-host LXC:

```bash
systemctl status garminsupla-admin8009-firewall.service --no-pager
systemctl status garminsupla-admin8009-watchdog.timer --no-pager
systemctl list-timers --all garminsupla-admin8009-watchdog.timer
/usr/local/sbin/garminsupla-admin8009-firewall status
iptables -S DOCKER-USER
iptables -n -v -x -L DOCKER-USER --line-numbers
journalctl -u garminsupla-admin8009-watchdog.service -n 20 --no-pager
```

Expected: both main service and timer enabled, exactly one firewall
rule, and successful periodic watchdog executions.

From the NPM CT, check that the HTTP upstream remains accessible:

```bash
curl --noproxy '*' -sS -o /dev/null -w '%{http_code}\n' \
  http://192.0.2.12:8009/login
```

Expected HTTP status: `200`.

From an independent LAN client, verify that port 8009 is blocked
and Watch API HTTPS port 8008 remains reachable.

## Disable or roll back the protection

These commands intentionally remove the port 8009 restriction.
Only use them when an alternative access control is in place or
when performing a controlled rollback.

Run as root inside the Docker-host LXC:

```bash
systemctl disable --now garminsupla-admin8009-watchdog.timer
systemctl disable --now garminsupla-admin8009-firewall.service
/usr/local/sbin/garminsupla-admin8009-firewall remove
/usr/local/sbin/garminsupla-admin8009-firewall status
```

Disable the watchdog first: otherwise it may restore a removed rule
at its next scheduled execution.

After rollback, verify service states and the contents of
`DOCKER-USER`. Do not flush the entire firewall ruleset.

## Verified tests

The following checks passed on 20-21 November 2026:

- Direct dashboard access from a Windows LAN client was blocked.
- NPM retained HTTP 200 access to the dashboard upstream.
- Watch API HTTPS port 8008 remained reachable.
- Internal Watch API port 18008 was not reachable from the laptop.
- Connection counters recorded rejected packets.
- Two temporary firewall rollback mechanisms executed successfully.
- The main systemd service installed one correct rule.
- Two manual watchdog executions created no duplicates.
- The enabled timer executed three successful periodic checks.
- The main firewall service and watchdog timer were enabled.

## Limitations and follow-up

- No production Docker or CT restart was performed to test recovery.
- Automatic repair after deliberate rule removal was not tested.
- The watchdog reduces the duration of a missing-rule condition,
  but cannot guarantee uninterrupted protection.
- The mechanism is specific to the current IPv4 address and NPM
  source address. Revalidate after network changes.
- An externally reachable dashboard must also be protected by
  appropriate reverse-proxy HTTPS and authentication controls.
- Full Internet exposure, external attack-surface testing and the
  remaining security audit items are not completed by this work.

The audited LXC also has an enabled `nftables.service` whose configuration
contains `flush ruleset`. Do not restart or reload nftables on the
running Docker host without a separate impact and recovery plan.
