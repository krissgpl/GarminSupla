# UX / Setup improvements

- [ ] Przebudować kreator konfiguracji.
  - Po autoryzacji SUPLA przechodzić bezpośrednio do dashboardu.
  - Na dashboardzie najpierw sparować / dodać Garmin Watch.
  - Następnie wybierać z aktualnej listy SUPLA itemy, które mają być dostępne na zegarku.
  - Usunąć obowiązkowy etap osobnego wyboru bramy z kreatora.

- [ ] Dodać konfigurację serwera GarminSupla z poziomu Garmin Connect / telefonu.
  - Użytkownik podaje adres serwera w ustawieniach aplikacji Connect IQ.
  - Dopiero po skonfigurowaniu serwera uruchamiane jest parowanie zegarka z GarminSupla.

- [ ] Uporządkować flow ponownej autoryzacji SUPLA.
  - Ponowna autoryzacja nie powinna uruchamiać kreatora od początku.
  - Po poprawnym OAuth wracać do dashboardu przy istniejącej konfiguracji.

- [ ] Pogrupować listę `Add from SUPLA` według typu urządzenia.
  - Bramy
  - Sceny
  - Pozostałe urządzenia

- [ ] Przebudować layout `Watch items` w dashboardzie pod różne szerokości ekranu.
  - Desktop / laptop:
    - wyświetlać itemy jako kafelki w responsywnej siatce,
    - wykorzystywać całą dostępną szerokość strony,
    - unikać jednej długiej pionowej kolumny.
  - Telefon:
    - pozostawić itemy w jednej pionowej kolumnie,
    - akcje `Move up`, `Move down`, `Remove` układać tak, aby nie wychodziły poza kartę.

# Watch UI

- [ ] Przebudować główny UI Connect IQ w kierunku natywnego stylu Garmin/Menu2.
- [ ] Dodać ikony dla typów itemów i ich stanów.

# SUPLA

- [X] Dodać obsługę scen SUPLA.
  - Pobieranie scen z `scenes_r`.
  - Wykonywanie scen z `scenes_ea`.
  - Pokazywać tylko aktywne i nieukryte sceny w `Add from SUPLA`.
