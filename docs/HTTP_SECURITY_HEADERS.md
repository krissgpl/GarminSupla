# HTTP security headers — dashboard test deployment

## Scope

This document records the tested security response headers
configured in Nginx Proxy Manager (NPM) for the GarminSupla
administrator dashboard.

The dashboard is currently a test deployment, not a certified
production release.

The settings are specific to the NPM proxy host used for the
dashboard. They are not automatically configured by GarminSupla
and do not establish protection for other hosts, the direct
upstream, or the separately deployed Watch API.

The application running during the SECURITY-04 tests used
backend/dashboard version 0.5.1. Version 0.6.0-beta.1 is
a separate, pending test release.

## Active NPM Advanced configuration

The verified dashboard NPM proxy host uses these directives
in its Advanced configuration:

```nginx
set_real_ip_from 127.0.0.1;

more_set_headers "X-Content-Type-Options: nosniff";
more_set_headers "Referrer-Policy: strict-origin-when-cross-origin";
more_set_headers "X-Frame-Options: DENY";
more_set_headers "Strict-Transport-Security: max-age=86400";

more_set_headers "Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net; style-src-elem 'self' https://cdn.jsdelivr.net; style-src-attr 'unsafe-inline'; img-src 'self' data:; font-src 'self' https://cdn.jsdelivr.net; connect-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'";
```

The directives use OpenResty's headers-more module, supported
by the tested NPM deployment.

Do not copy the `set_real_ip_from` setting into an unrelated
proxy deployment without separately validating its trust
boundary and forwarded-client-IP configuration.

## Header behavior

- `X-Content-Type-Options: nosniff` prevents MIME sniffing.
- `Referrer-Policy: strict-origin-when-cross-origin` limits
  referrer information for cross-origin requests.
- `X-Frame-Options: DENY` blocks framing in supported browsers.
- `Strict-Transport-Security: max-age=86400` instructs browsers
  to prefer HTTPS for 24 hours after receiving the header.
  This policy does not use `includeSubDomains` or `preload`.
- `Content-Security-Policy` is enforced, not Report-Only.
  It includes `frame-ancestors 'none'` and `object-src 'none'`.

## CSP design decisions

- JavaScript is limited to the same origin and jsDelivr.
  No JavaScript `unsafe-inline` or `unsafe-eval` is permitted.
- CSS elements may load stylesheets from the same origin
  and jsDelivr.
- Inline style attributes remain permitted through
  `style-src-attr 'unsafe-inline'` for existing UI behavior.
  This is a deliberate exception and should be revisited
  if the application removes its inline style attributes.
- Images may load from the same origin or `data:` URLs.
  The latter is required by the 2FA QR-code SVG implementation.
- Bootstrap Icons fonts may load from jsDelivr.
- `connect-src 'self'` limits application connections to
  the dashboard origin; jsDelivr is not allowed here.
- Form submissions and base URLs are restricted to the same
  origin; framing is prohibited.
- No CSP reporting endpoint is configured.

## Verification record

The following checks completed successfully:

- SECURITY-04B: isolated OpenResty response-header tests.
- SECURITY-04D: CSP Report-Only response checks.
- SECURITY-04F2: pre-enforcement NPM backup created.
- SECURITY-04F3B: isolated restoration of the backup verified,
  including the NPM MariaDB data and Advanced host settings.
- SECURITY-04G1: isolated enforced-CSP OpenResty checks.
- SECURITY-04G3: active HTTPS, TLS, redirects, CSS, JS, HTTP
  200/404, header uniqueness and Nginx syntax checks.
- SECURITY-04G4–04G7: Firefox troubleshooting-mode checks of
  login, 2FA authentication, dashboard, SUPLA list, details,
  2FA page and setup page without CSP or JavaScript errors.
- SECURITY-04G8: Edge InPrivate functional checks passed.
  Edge DevTools reported blocked Bootstrap source maps.
- SECURITY-04G9: after disabling JavaScript/CSS source maps
  in Edge DevTools, the UI continued working without CSP
  violations or JavaScript errors.

Edge DevTools source maps are diagnostic resources.
The blocked `.css.map` and `.js.map` requests did not
require expanding `connect-src` to the CDN.

Edge Tracking Prevention messages were separate from CSP.
A mistyped `//setup` URL and a missing `/favicon.ico`
also produced unrelated HTTP 404 responses.

## Limitations

These checks do not constitute a complete application or
network security audit.

In particular, recent enforced-CSP tests did not exercise
new 2FA enrollment, 2FA recovery-code generation, watch
pairing, or every state-changing setup operation.

The dashboard HSTS policy has a 24-hour max-age and must
not be expanded to subdomains or preload without a separate
assessment.

Security headers configured on this proxy host do not
substitute for backend authentication, CSRF defenses,
input validation, authorization or network isolation.

## Rollback to CSP Report-Only

If enforced CSP causes a functional regression:

1. Open NPM and edit only the affected dashboard proxy host.
2. Open **Advanced** and replace its content with the
   complete configuration below.
3. Save and verify the resulting Nginx configuration.
4. Verify HTTPS login, expected application responses and
   the presence of the Report-Only header.
5. Confirm that the enforced `Content-Security-Policy`
   header is absent before concluding that rollback worked.

```nginx
set_real_ip_from 127.0.0.1;

more_set_headers "X-Content-Type-Options: nosniff";
more_set_headers "Referrer-Policy: strict-origin-when-cross-origin";
more_set_headers "X-Frame-Options: DENY";
more_set_headers "Strict-Transport-Security: max-age=86400";

more_set_headers "Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net; style-src-elem 'self' https://cdn.jsdelivr.net; style-src-attr 'unsafe-inline'; img-src 'self' data:; font-src 'self' https://cdn.jsdelivr.net; connect-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'";
```

Rollback retains the four other security headers and the
verified Real IP directive. It changes only the CSP
header from enforcement to observation.

Changing CSP does not clear an HSTS policy already cached
in a browser; the configured HSTS max-age is 86400 seconds.

The verified pre-enforcement backup is stored outside Git
on the private NPM container host under:

`/root/garminsupla-security-04/04F2-pre-enforcement/`

The backup includes confidential database contents.
Never commit, publish or copy it to this documentation
repository. Restore it only through a separately verified
recovery procedure.

## Follow-up

Recheck security headers and browser functionality whenever
the dashboard templates, external dependencies, proxy rules
or application authentication flows change.

A full security audit and validation of state-changing
workflows remain separate tasks.
