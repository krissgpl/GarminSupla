# Administrator login rate limiting

## Scope

GarminSupla supports optional, process-local rate limiting of failed
administrator authentication attempts.

Protected endpoints:

- `POST /login` — invalid username or password.
- `POST /login/totp` — rejected TOTP verification.
- `POST /login/totp/recovery` — rejected recovery code.

The three endpoints share one failure budget per resolved client IP.

Default limits:

- 8 failed attempts per client IP.
- Sliding window: 300 seconds.
- Blocked requests return HTTP `429` with `Retry-After`.
- At most 4096 client entries are retained in process memory.

`GET /login` is not blocked by the authentication limiter.

Counters are not persisted and reset on application restart. The
implementation is per process; using multiple Uvicorn workers requires
a shared-state limiter or equivalent deployment protection.

## Configuration

Environment variables:

- `ADMIN_LOGIN_RATE_LIMIT_ENABLED` — `false` by default.
- `ADMIN_LOGIN_TRUSTED_PROXY_IPS` — empty by default; comma-separated
  exact IPv4/IPv6 addresses of trusted immediate reverse proxies.

An enabled limiter requires at least one valid trusted proxy IP.
Invalid, duplicate, unspecified, multicast and CIDR entries are
rejected. The configured list permits at most 16 addresses.

Configure deployment-specific values only in the private `.env` file,
not in Git. The file must be protected against unauthorized access.

For example, using the documentation-only TEST-NET address:

```dotenv
ADMIN_LOGIN_RATE_LIMIT_ENABLED=true
ADMIN_LOGIN_TRUSTED_PROXY_IPS=192.0.2.10
```

Replace the example with the verified immediate proxy address for
the actual deployment.

## Client IP trust boundary

FastAPI uses the peer IP unless the immediate peer is in the trusted
proxy list. Only for such a peer may it use `X-Real-IP`.

The reverse proxy must overwrite `X-Real-IP` with its verified
`$remote_addr` value and must not pass a client-supplied value through.
Do not trust arbitrary `X-Forwarded-For` input.

The reverse proxy's Real IP trust settings require separate review.
Do not assume a forwarded address is trustworthy merely because a
header is present.

Users sharing one public IP address (for example through NAT) can
share one failure budget.

## Production activation

Before activation:

1. Verify the current image, Compose configuration and proxy path.
2. Run unit, integration and authentication regression tests.
3. Back up `.env` and Docker Compose to a private location.
4. Validate the new environment configuration in a separate process.
5. Record the existing application and Watch container identities.

After changing `.env`, recreate only the administrator application:

```bash
docker compose -f docker-compose.yml up -d \
  --no-deps --no-build --force-recreate garminsupla-api
```

A plain `docker compose restart` does not reliably apply newly
configured environment variables to an existing container.

After recreation, verify:

- `garminsupla-api` is running.
- Local `GET /login` returns HTTP 200.
- HTTPS `GET /login` through the proxy returns HTTP 200.
- Invalid credentials produce HTTP 401 before the threshold.
- The next request after the threshold produces HTTP 429 and
  a numeric `Retry-After`.
- Spoofing `X-Real-IP` does not evade the limit.
- Watch API and Watch Proxy container identities are unchanged.

Do not send real passwords, TOTP values or recovery codes during
security tests.

## Rollback

The verified deployment used a private pre-activation copy of `.env`.
To disable limiting, restore that file (or set
`ADMIN_LOGIN_RATE_LIMIT_ENABLED=false`) while preserving other
application settings.

Then recreate **only** `garminsupla-api`:

```bash
docker compose -f docker-compose.yml up -d \
  --no-deps --no-build --force-recreate garminsupla-api
```

Verify local and HTTPS `GET /login` return HTTP 200 and that the
limiter is disabled in the new container.

Do not restart NPM, the Watch API or Watch Proxy to roll back only
this setting.

The pre-activation configuration backup contains secrets; keep it
outside Git with restricted filesystem permissions.

## Verification record

- Code commit: `9cf6b80`.
- Validation: 44 unit, integration and login regression tests passed.
- Production activation: `SECURITY-02AH2` passed.
- Production request test: `SECURITY-02AI2` passed.
- Requests 1–8 with fictitious credentials returned HTTP 401.
- Request 9 with a spoofed `X-Real-IP` returned HTTP 429.
- Observed `Retry-After`: 285 seconds.
- Subsequent `GET /login` returned HTTP 200.
- Watch API and Watch Proxy were not recreated during activation.

## Limitations and outstanding work

- Protection is per client IP and per application process.
- The in-memory client limit can evict older counters under high
  client-IP churn. It is not distributed denial-of-service protection.
- An attacker can temporarily exhaust the failure budget of another
  user sharing the same public IP.
- Distributed attacks across multiple IPs require additional controls.
- The deployed dashboard did not send a
  `Strict-Transport-Security` response header during the audit.
  HSTS is a separate outstanding review item.
- Full application, network and dependency security audits remain open.
