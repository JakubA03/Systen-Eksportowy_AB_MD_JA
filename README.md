**System Ekspertowy Oparty na Logice Rozmytej – Ocena Jakości Środowiska**

Projekt prezentuje prosty system ekspertowy w Pythonie, który ocenia jakość środowiska (powietrza) na podstawie reguł rozmytych (Mamdani). Wejścia to PM2.5, prędkość wiatru, temperatura i wilgotność; wyjściem jest indeks 0–100 oraz etykieta słowna (np. „dobra”, „umiarkowana”).

**Wymagania**
- Python 3.13 


**Szybki Start (Windows, PowerShell)**
- Wejście do katalogu repo: `cd "<ścieżka do repo>"`
- Utworzenie i aktywacja wirtualnego środowiska:
  - `py -3.13 -m venv .venv`
  - `.venv\Scripts\Activate.ps1`
  - Jeśli blokada: `Set-ExecutionPolicy -Scope Process Bypass; .venv\Scripts\Activate.ps1`
- Instalacja zależności:
  - `python -m pip install -U pip setuptools wheel`
  - `python -m pip install numpy scipy pandas scikit-fuzzy packaging networkx`
- Uruchomienie aplikacji (z katalogu repo): `python main.py`

**Struktura Projektu**
- `main.py` – punkt wejścia; uruchamia interfejs konsolowy.
- `simple_fuzzy.py` – silnik logiki rozmytej: zmienne, funkcje przynależności, reguły, wnioskowanie, etykiety.
- `src/Ui.py` – interfejs konsolowy: tryb ręczny i tryb CSV (filtrowanie po strefie/sezonie/porze dnia).
- `src/Types.py` – model danych `EnvironmentalSample` i mapowanie z CSV.
- `data/data.csv` – przykładowe dane wejściowe do testów.

**Zmiennie i Zakresy Wejść**
- `PM2.5` [µg/m³]: 0–200 (etykiety: very_low, low, moderate, high, very_high)
- `Wiatr` [m/s]: 0–18 (calm, breeze, windy, gusty)
- `Temperatura` [°C]: −20–40 (freezing, cold, mild, warm, hot)
- `Wilgotność` [%]: 0–100 (very_dry, dry, comfortable, humid, saturated)
- Wyjście `quality` [0–100]: alarmowa → wyjatkowa

Funkcje przynależności: trapezowe (trapmf) oraz gaussowskie (gaussmf). Definicje i uniwersa w `simple_fuzzy.py`.

**Reguły Rozmyte (skrót)**
- Wysokie PM2.5 → gorsza jakość (np. very_high → alarmowa)
- Umiarkowane PM2.5 + wiatr/wilgotność modyfikują wynik (np. windy → lepiej, humid → gorzej)
- Niskie PM2.5 przy komfortowej wilgotności i łagodnej temperaturze → bardzo dobra/wyjątkowa

Pełna lista reguł znajduje się w `simple_fuzzy.py` w budowie systemu sterowania.

**Jak Korzystać (UI)**
- Uruchom `python main.py` i wybierz tryb:
  - `1` – podaj ręcznie PM2.5, wiatr, temperaturę, wilgotność
  - `2` – użyj `data/data.csv`, opcjonalnie przefiltruj po: `Strefa`, `Sezon`, `Pora_dnia`
- Wynik: etykieta jakości + indeks (0–100)

**Interpretacja Wyniku**
- 97–100: „wyjątkowa”
- 90–96.9: „bardzo dobra”
- 80–89.9: „dobra”
- 68–79.9: „umiarkowana”
- 55–67.9: „dostateczna”
- 42–54.9: „słaba”
- 28–41.9: „bardzo słaba”
- <28: „alarmowa”

**Testowanie Scenariuszy**
- Ręcznie (UI – opcja 1) przetestuj kilka zestawów (czyste vs zanieczyszczone powietrze, różny wiatr, różna wilgotność/temperatura).
- CSV (UI – opcja 2) – przefiltruj rekordy po strefie/sezonie/porze dnia i porównaj wyniki.

**Walidacja i Ograniczenia**
- Uniwersa wejść: PM2.5 0–200, Wiatr 0–18 m/s, Temperatura −20–40°C, Wilgotność 0–100%.
- Dla wartości skrajnych/niefizycznych wyniki mogą być mylące. Rekomendacja: nie podawaj danych spoza uniwersów (w razie potrzeby dodaj walidację/„clamping” w `simple_fuzzy.py`).
- Reguły są przykładowe – możesz je modyfikować i optymalizować do własnego przypadku.


**Licencja / Autorstwo**
- Projekt edukacyjny do przedmiotu „Podstawy AI”. Brak formalnej licencji – użycie na własną odpowiedzialność.
