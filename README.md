# GarminSupla

GarminSupla is a bridge between Garmin Connect IQ devices and the SUPLA REST API.

## Features

- Open gate
- Close gate
- Gate status
- OAuth2 authentication with SUPLA
- REST API for Garmin Connect IQ

## Project status

🚧 In development

## Requirements

- Docker
- Docker Compose

## First administrator account

On a fresh GarminSupla installation, the administrator account must be
created locally on the GarminSupla host.

Start the application and create the account with:

```bash
docker compose up -d

docker compose exec garminsupla-api \
    python -m scripts.create_admin
```

The command prompts for:

- administrator username,
- administrator password,
- password confirmation.

The password must contain at least 12 characters. The password is entered
without being displayed in the terminal and only its password hash is
stored.

Only one administrator account can be created. If an administrator
already exists, the command refuses to replace it.

Until the administrator account is created, the dashboard login page
displays the local account-creation command instead of the login form.

After creating the account, refresh the login page and sign in with the
configured credentials. Two-factor authentication is disabled initially
and can be enabled later from the dashboard.

## Dashboard administrator security

The GarminSupla dashboard is protected by an administrator account.

Optional two-factor authentication uses TOTP and is compatible with
standard authenticator applications. Enabling 2FA provides one-time
recovery codes. Recovery codes should be stored securely because they
are displayed only during enrollment.

Security-sensitive authentication changes invalidate existing
administrator sessions.

### Emergency 2FA reset

If access to the authenticator and recovery codes is lost, 2FA can be
reset locally from the GarminSupla host:

```bash
docker compose exec garminsupla-api \
    python -m scripts.reset_admin_2fa
```

The command requires the exact confirmation:

```text
RESET
```

The reset:

- disables administrator 2FA,
- removes the stored TOTP secret,
- removes all remaining recovery codes,
- invalidates all existing administrator sessions,
- does not change the administrator password.

After the reset, sign in with the existing administrator password and
configure 2FA again.

### Emergency administrator password reset

If the administrator password is lost, reset it locally from the
GarminSupla host:

```bash
docker compose exec garminsupla-api \
    python -m scripts.reset_admin_password
```

The command requires the exact confirmation:

```text
RESET
```

You will then be prompted to enter and confirm a new password. The
password must contain at least 12 characters.

The reset:

- replaces the administrator password,
- invalidates all existing administrator sessions,
- preserves the current 2FA configuration.

If 2FA was enabled before the password reset, it remains required when
signing in with the new password.

Both recovery commands require shell access to the GarminSupla host or
container and should be treated as privileged administrative operations.

## Documentation

- CHANGELOG.md
- ARCHITECTURE.md
- TODO.md
