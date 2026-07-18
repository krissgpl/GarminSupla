# GarminSupla Architecture

## ADR-001 - API i panel administracyjny

- FastAPI nasłuchuje na porcie 8008.
- API przeznaczone jest wyłącznie dla aplikacji Garmin.
- Panel administracyjny udostępniany jest przez Nginx Proxy Manager.
- Dostęp do panelu zabezpiecza MikroTik oraz HTTP Basic Auth.

---

## ADR-002 - OAuth

- OAuth obsługiwany jest przez backend.
- Tokeny przechowywane są w data/tokens.json.

---

## ADR-003 - Konfiguracja

- Konfiguracja urządzeń znajduje się w config/devices.json.
- Dane użytkownika nie są zapisywane w .env.
