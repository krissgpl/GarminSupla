# GarminSupla — First installation

This guide covers the first installation of the GarminSupla
backend, administrator dashboard, SUPLA OAuth integration,
and Garmin Watch API.

For detailed HTTPS configuration, see [Watch API HTTPS](WATCH_API_HTTPS.md).

## 1. Requirements

Prepare a Linux server with:

- Docker Engine and Docker Compose.
- Python 3 with support for virtual environments.
- Git.
- A DNS hostname and TLS certificate for Watch API.
- A separately secured HTTPS URL for the administrator dashboard.
- Access to a SUPLA Cloud account.
- A Garmin watch with the GarminSupla Connect IQ application installed.

The Connect IQ application installation/distribution process
is not covered by this guide.

## 2. Download GarminSupla

```bash
git clone https://github.com/krissgpl/GarminSupla.git
cd GarminSupla
```

Run the remaining commands from the repository directory.

## 3. Generate local configuration

```bash
mkdir -p data
python3 -m scripts.init_env
python3 -m scripts.init_deploy
```

These commands create:

- `.env`
- `docker-compose.yml`
- `deploy/caddy/Caddyfile`

Existing files are preserved.

The `.env` initializer generates ADMIN_SESSION_SECRET
automatically. Do not replace the generated value after
administrator sessions have been established.

SUPLA OAuth credentials do not need to be entered into `.env`.

### Non-root installation permissions

Clone the repository and initialize GarminSupla as a regular
Linux user. Do not run the setup commands with `sudo`.

During first initialization, `scripts.init_env` detects the
current user's UID and GID and saves them in `.env`:

```dotenv
GARMIN_SUPLA_RUN_UID=1000
GARMIN_SUPLA_RUN_GID=1000
```

These are example values. Actual values are determined from
the user running the initializer.

The initializer rejects UID 0 or GID 0 for a new configuration
unless non-root identifiers are explicitly supplied.

The generated `.env` has permissions `0600` and must remain
readable by the configured application user.

The `data/` directory must be owned by and writable to the
configured application UID. On a fresh clone created by the
installing user, `mkdir -p data` prepares this directory.

Check the installation user and file ownership:

```bash
id -u
id -g
stat -c '%u:%g %a %n' .env data
test -r .env
test -w data
```

The UID/GID shown for `.env` and `data/` should match the
installing user's identifiers. If they do not, correct the
ownership before starting the containers.

Do not make configuration files world-readable or use
`chmod 777` to resolve permission problems.

Both Python services run as the configured non-root UID/GID.
The application code is mounted read-only at `/app`, while
persistent data is mounted read-write at `/app/data`.

Existing `.env` files are preserved by the initializer.
Changing UID/GID on an existing installation requires
separate verification of persistent file ownership.

## 4. Configure Watch API HTTPS

Edit `.env` and add your own values:

```dotenv
GARMIN_SUPLA_WATCH_DOMAIN=watch.example.com
GARMIN_SUPLA_CERT_DIR=/srv/garminsupla/certs
```

The certificate directory must contain:

- `fullchain.pem`
- `private.key`

The certificate must cover the Watch API hostname, and
its private key must match.

The example Caddy deployment terminates HTTPS on port 8008.

IMPORTANT: The current Connect IQ application automatically
adds port 8008 to serverUrl if that port is missing.

Therefore the watch must be able to reach the configured
hostname on external HTTPS port 8008.

Do not assume that making the service available only on
port 443 will work with the current Connect IQ application.

The example Docker Compose binds Watch API to 127.0.0.1
by default. Public access requires an explicitly secured
network path, such as suitable proxying and firewall rules.

Do not publicly expose the administrator dashboard.

For the full networking and certificate configuration,
see [Watch API HTTPS](WATCH_API_HTTPS.md).

## 5. Validate configuration

The HTTPS preflight script runs on the Docker host.

Prepare an isolated Python environment if the required
packages are not already installed:

```bash
python3 -m venv .venv

.venv/bin/python -m pip install \
  'cryptography>=50.0.2,<51.0.0' \
  'python-dotenv==1.2.4'
```

Run local validation:

```bash
.venv/bin/python -m scripts.check_deploy
docker compose config --quiet
```

The HTTPS checker does not verify DNS resolution, external
reachability, certificate chain trust or successful TLS
operation inside Caddy.

Resolve any reported errors before starting the deployment.

## 6. Start GarminSupla

```bash
docker compose up -d --build
docker compose ps
```

The example deployment starts:

- garminsupla-api: administrator dashboard and backend API.
- garminsupla-watch: Garmin Watch API.
- garminsupla-watch-proxy: Caddy HTTPS proxy.

By default, the administrator service binds to
127.0.0.1:8009 on the Docker host.

The administrator dashboard must be accessed through a
trusted connection. HTTPS is required for the secure
administrator session and OAuth state cookies.

Do not expose the administrator port directly to the Internet.

## 7. Create the administrator

Create the initial account from the server terminal:

```bash
docker compose exec garminsupla-api \
  python -m scripts.create_admin
```

Enter a username and password when prompted.

The password must contain at least 12 characters.

Only the password hash is stored. The command refuses
to replace an existing administrator account.

Open the administrator dashboard through its separately
secured HTTPS address and sign in.

Two-factor authentication can be configured later.

## 8. Register SUPLA OAuth integration

Log in to your SUPLA Cloud server and register an OAuth
application through the integration settings.

Prepare:

- SUPLA server URL.
- OAuth Client ID.
- OAuth Client Secret.
- HTTPS redirect URI for the GarminSupla administrator
  dashboard.

The redirect URI must end exactly in:

```text
/oauth/callback
```

Example:

```text
https://dashboard.example.com/oauth/callback
```

The redirect URI points to the dashboard, not the Watch API.

Do not use the Watch API port 8008 as the OAuth callback.

The default GarminSupla OAuth scopes are:

```text
iodevices_r channels_r channels_ea scenes_r scenes_ea offline_access
```

Existing installations can override the scope with
SUPLA_SCOPE in `.env`.

## 9. Complete the SUPLA setup wizard

After administrator login, open:

```text
/setup
```

Enter:

- SUPLA server URL.
- Client ID.
- Client Secret.
- OAuth redirect URI.

The wizard can suggest the HTTPS address of the current
dashboard. Confirm that it exactly matches the callback
registered for the SUPLA application.

Save the configuration and complete SUPLA authorization.

After successful OAuth authorization, GarminSupla redirects
to the dashboard.

## 10. Configure the Garmin Connect IQ application

In the Connect IQ application settings on the phone,
configure GarminSupla `serverUrl` with the public Watch API
HTTPS address.

Example:

```text
https://watch.example.com
```

The current application adds `:8008` automatically and uses
the `/api/v1` API prefix.

Do not append `/api/v1` or `/api/v1/watch` yourself.

The Watch API address is different from the administrator
dashboard address.

Make sure the configured hostname resolves and HTTPS
port 8008 is reachable from the watch's network path.

## 11. Pair the first Garmin watch

Start GarminSupla on the watch.

The application initiates pairing and displays a six-digit
pairing code.

In the administrator dashboard:

1. Open the Garmin watch section.
2. Choose to configure or add a watch.
3. Enter the six-digit code displayed on the watch.
4. Approve pairing.
5. Complete the pairing process on the watch.

Pairing codes expire. If one expires, use the new code
displayed by the application.

The watch receives its own authentication token when the
approved pairing session is consumed.

## 12. Configure watch items

After pairing, select the configured watch in the dashboard.

Use "Add from SUPLA" to select supported channels or scenes.

Configure the desired items and choose:

```text
Save watch configuration
```

Refresh the watch configuration and verify that the selected
items appear on the Garmin device.

Test a harmless supported action before relying on the
integration for routine use.

## 13. Verify connectivity

Confirm that:

- The dashboard is reachable through its secure HTTPS URL.
- SUPLA authorization has completed successfully.
- The public Watch API is reachable on HTTPS port 8008.
- The watch pairs successfully.
- The watch receives the saved configuration.
- SUPLA actions and state updates work.
- Wi-Fi Sync works where supported by the Garmin device.

If the watch cannot connect, check DNS, certificate validity,
port 8008 reachability, firewall and NAT configuration.

Do not disable TLS certificate verification as a workaround.

## 14. Protect persistent data

The example Compose mounts the repository read-only at
`/app` and persistent application data read-write at
`/app/data`. Both Python services use the non-root UID/GID
configured during installation.

Persistent application data includes:

- `.env`
- `data/config.json`
- `data/admin.json`
- TLS certificates and private keys
- Local deployment configuration

These files must not be committed to Git.

Back up administrator and SUPLA configuration securely before
upgrading or migrating an existing installation.

The example deployment is not yet a fully hardened production
Compose configuration. Review the project's security and
deployment TODO items before exposing services publicly.
