# UX / Setup improvements

- [X] Przebudować kreator konfiguracji.
  - Po autoryzacji SUPLA przechodzić bezpośrednio do dashboardu.
  - Na dashboardzie najpierw sparować / dodać Garmin Watch.
  - Następnie wybierać z aktualnej listy SUPLA itemy, które mają być dostępne na zegarku.
  - Usunąć obowiązkowy etap osobnego wyboru bramy z kreatora.

- [X] Dodać konfigurację serwera GarminSupla z poziomu Garmin Connect / telefonu.
  - Użytkownik podaje adres serwera w ustawieniach aplikacji Connect IQ.
  - Dopiero po skonfigurowaniu serwera uruchamiane jest parowanie zegarka z GarminSupla.

- [X] Uporządkować flow ponownej autoryzacji SUPLA.
  - Ponowna autoryzacja nie powinna uruchamiać kreatora od początku.
  - Po poprawnym OAuth wracać do dashboardu przy istniejącej konfiguracji.

- [X] Pogrupować listę `Add from SUPLA` według typu urządzenia.
  - Bramy
  - Sceny
  - Pozostałe urządzenia

- [X] Przebudować layout `Watch items` w dashboardzie pod różne szerokości ekranu.
  - Desktop / laptop:
    - wyświetlać itemy jako kafelki w responsywnej siatce,
    - wykorzystywać całą dostępną szerokość strony,
    - unikać jednej długiej pionowej kolumny.
  - Telefon:
    - pozostawić itemy w jednej pionowej kolumnie,
    - akcje `Move up`, `Move down`, `Remove` układać tak, aby nie wychodziły poza kartę.

- [ ] Dodać obsługę wielu zegarków Garmin.
  - Zmienić model pojedynczego `watch` na kolekcję sparowanych zegarków.
  - Każdy zegarek powinien mieć własne:
    - `id`,
    - token,
    - nazwę,
    - status `enabled`,
    - `created_at`,
    - `last_seen_at`,
    - niezależną listę `Watch items`.
  - Każdy zegarek powinien mieć osobne:
    - parowanie,
    - ponowne parowanie,
    - usunięcie / unieważnienie,
    - konfigurację kolejności, ikon i confirmation dla itemów.
  - Dodać możliwość skopiowania konfiguracji `Watch items`:
    - z istniejącego zegarka do nowego,
    - opcjonalnie między już sparowanymi zegarkami.
  - Dashboard powinien wyświetlać osobne kafelki / sekcje dla każdego zegarka.

- [ ] Przygotować wspólną ikonę / logo GarminSupla.
  - Używać tego samego motywu graficznego w:
    - aplikacji Garmin Connect IQ,
    - launcherze aplikacji na zegarku,
    - dashboardzie WWW,
    - faviconie strony.
  - Przygotować warianty odpowiednie dla różnych rozmiarów i rozdzielczości.
  - Przygotować wersję czytelną na jasnym i ciemnym tle.
  - Dla Connect IQ przygotować launcher icon zgodną z wymaganiami obsługiwanych urządzeń, bez skalowania obecnej ikony 24×24.
  - Zachować jeden spójny motyw GarminSupla jako źródło dla wszystkich wariantów ikon.

# Watch UI

- [ ] Przebudować główny UI Connect IQ w kierunku natywnego stylu Garmin/Menu2.
- [ ] Przygotować spójny zestaw ikon dla typów itemów.
  - Dodać dedykowane ikony dla obsługiwanych typów, m.in.:
    - brama,
    - światło,
    - przełącznik,
    - roleta,
    - markiza,
    - scena.
  - Używać analogicznych ikon w aplikacji Connect IQ i dashboardzie.
  - W dashboardzie po wyborze ikony pokazywać dokładny odpowiednik używany na zegarku.
  - Uwzględnić czytelność ikon na małym ekranie oraz ograniczenia urządzeń Connect IQ.
  - Zachować ikonę `default` jako fallback dla nieobsługiwanych lub przyszłych typów.

 - Wykorzystać możliwości ekranów AMOLED/OLED:
    - przygotować kolorowe grafiki ikon,
    - preferować czarne tło i wysoki kontrast,
    - wykorzystywać kolor do prezentacji typu i stanu urządzenia,
    - przygotować różne warianty grafiki zależnie od stanu, np. ON/OFF, OPENED/CLOSED, ONLINE/OFFLINE,
    - zachować czytelność oraz rozsądne zużycie energii na ekranach AMOLED.

# SUPLA

- [X] Dodać obsługę scen SUPLA.
  - Pobieranie scen z `scenes_r`.
  - Wykonywanie scen z `scenes_ea`.
  - Pokazywać tylko aktywne i nieukryte sceny w `Add from SUPLA`.
