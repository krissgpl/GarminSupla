# Watch API — HTTPS deployment

This guide describes the HTTPS configuration used by the
GarminSupla example Docker Compose deployment.

## 1. Prerequisites

Prepare:

- A DNS hostname for the Garmin Watch API.
- A valid TLS certificate for that hostname.
- The matching private key.
- A secure network path from Garmin devices to the Watch API.

The example deployment uses Caddy for TLS termination.

The example configuration does not automatically obtain or
renew certificates. Certificate provisioning and renewal must
be configured separately.

## 2. Initialize deployment files

From the GarminSupla repository directory:

```bash
python3 -m scripts.init_env
python3 -m scripts.init_deploy
```

These commands do not overwrite existing configuration files.

They prepare:

- `.env`
- `docker-compose.yml`
- `deploy/caddy/Caddyfile`

## 3. Configure the Watch API hostname

Edit `.env` and add:

```dotenv
GARMIN_SUPLA_WATCH_DOMAIN=watch.example.com
GARMIN_SUPLA_CERT_DIR=/srv/garminsupla/certs
```

Replace the example values with your own hostname and
absolute certificate directory on the Docker host.

Use a hostname only for `GARMIN_SUPLA_WATCH_DOMAIN`:
do not include `https://`, a port or a URL path.

Do not delete the generated `ADMIN_SESSION_SECRET`.
Keep `.env` private.

## 4. Install TLS certificates

The host directory configured by
`GARMIN_SUPLA_CERT_DIR` must contain:

```text
/srv/garminsupla/certs/
├── fullchain.pem
└── private.key
```

The certificate must cover the configured Watch API hostname.

The certificate and private key must match.

The files must be readable by the Caddy container.
Protect the private key against unauthorized access.

Docker Compose mounts this directory read-only inside the
Caddy container at:

```text
/run/garminsupla-watch-certs
```

The Caddyfile uses these exact paths:

```text
/run/garminsupla-watch-certs/fullchain.pem
/run/garminsupla-watch-certs/private.key
```

## 5. Network exposure

The example Docker Compose configuration uses:

```dotenv
GARMIN_SUPLA_WATCH_BIND_IP=127.0.0.1
```

This is the default even when the variable is omitted.

Therefore port 8008 is accessible only from the Docker host
unless an additional network forwarding mechanism is configured.

A public deployment requires an appropriate reverse proxy,
TLS-aware forwarding or explicitly secured network exposure.

If another proxy forwards to the Caddy HTTPS listener, its
upstream configuration must preserve working TLS and the
correct hostname/SNI.

Do not expose the administrative dashboard as part of the
public Watch API.

The Caddyfile routes only:

```text
/api/v1/watch/*
```

Other paths return HTTP 404.

Port 8080 in the Caddyfile is an internal HTTP listener and
is not published by the example Docker Compose configuration.

## 6. Administrative dashboard and OAuth

The administrator dashboard is a separate service.

Its default host binding is:

```text
127.0.0.1:8009
```

Remote dashboard access requires a separately secured HTTPS
reverse proxy or another trusted access method.

When registering the application in SUPLA, the OAuth callback
must point to the publicly reachable HTTPS dashboard address
and end with:

```text
/oauth/callback
```

The dashboard HTTPS address may differ from the Watch API
hostname.

## 7. Validate before starting

Check that both certificate files exist and are readable
from the Docker host.

Validate the Docker Compose configuration without displaying
resolved environment values:

```bash
docker compose config --quiet
```

If validation succeeds, follow the installation instructions
for starting the services and creating the administrator.

Do not change a running production deployment solely to
test this guide.

## 8. Security notes

- Keep `.env` and TLS private keys out of Git.
- Do not expose the dashboard directly to the Internet.
- Configure DNS, firewall and router/NAT rules deliberately.
- Ensure certificates are renewed before expiration.
- Test the external HTTPS connection before pairing a watch.
- Do not disable TLS certificate verification to make an
  invalid certificate work.
