

import csv
from typing import List, Optional

from simple_fuzzy import QualityAssessment
from src.Types import EnvironmentalSample


def wczytaj_baze(sciezka: str = "data/data.csv") -> List[dict[str, str]]:
    """Load CSV into a list of dicts (expects UTF-8)."""
    dane: List[dict[str, str]] = []
    try:
        with open(sciezka, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dane.append(row)
    except FileNotFoundError:
        print("Nie znaleziono pliku z baza:", sciezka)
    return dane


def filtruj_baze(dane: List[dict[str, str]], kryteria: dict[str, str]) -> List[dict[str, str]]:
    """Return records matching all equality criteria (case-insensitive)."""
    wyniki: List[dict[str, str]] = []
    for rekord in dane:
        dopasowanie = True
        for klucz, wartosc in kryteria.items():
            if rekord.get(klucz, "").strip().lower() != wartosc.strip().lower():
                dopasowanie = False
                break
        if dopasowanie:
            wyniki.append(rekord)
    return wyniki


def ui() -> None:
    """Main UI menu and flow dispatcher."""
    print("=== SYSTEM EKSPERTOWY: JAKOSC SRODOWISKA ===")
    print("1) Podaj wlasne parametry pogodowe")
    print("2) Uzyj danych z bazy (CSV)")
    wybor = input("\nWybierz opcje (1 lub 2): ").strip()

    if wybor == "1":
        _obsluga_trybu_recznego()
        return

    if wybor == "2":
        _obsluga_trybu_bazy()
        return

    print("Nieprawidlowy wybor.")


def _obsluga_trybu_recznego() -> None:
    """Read values from stdin, evaluate and print result."""
    try:
        pm25 = float(input("PM2.5 (ug/m3): "))
        wiatr = float(input("Predkosc wiatru (m/s): "))
        temperatura = float(input("Temperatura (stopnie Celsjusza): "))
        wilgotnosc = float(input("Wilgotnosc wzgledna (%): "))
    except ValueError:
        print("Niepoprawne dane liczbowe.")
        return

    sample = EnvironmentalSample(
        strefa="manual",
        sezon="manual",
        pora_dnia="manual",
        temperatura=temperatura,
        wilgotnosc=wilgotnosc,
        wiatr=wiatr,
        pm25=pm25,
    )
    wynik = sample.evaluate()
    _pokaz_wynik(wynik)


def _obsluga_trybu_bazy() -> None:
    """Load CSV, let user filter and evaluate matching records."""
    dane = wczytaj_baze()
    if not dane:
        return

    print("\nChcesz filtrowac dane po:")
    print("1) Strefa")
    print("2) Sezon")
    print("3) Pora_dnia")
    print("4) Strefa + Sezon")
    print("5) Sezon + Pora_dnia")
    print("6) Strefa + Pora_dnia")
    print("7) Wszystkie trzy")

    f = input("Wybierz numer opcji: ").strip()
    kryteria: dict[str, str] = {}

    strefy = _unikalne_wartosci(dane, "Strefa")
    sezony = _unikalne_wartosci(dane, "Sezon")
    pory = _unikalne_wartosci(dane, "Pora_dnia")

    if f == "1":
        wybor = _wybierz_z_listy("Wybierz strefe", strefy)
        if wybor is None:
            print("Anulowano.")
            return
        kryteria["Strefa"] = wybor
    elif f == "2":
        wybor = _wybierz_z_listy("Wybierz sezon", sezony)
        if wybor is None:
            print("Anulowano.")
            return
        kryteria["Sezon"] = wybor
    elif f == "3":
        wybor = _wybierz_z_listy("Wybierz pore dnia", pory)
        if wybor is None:
            print("Anulowano.")
            return
        kryteria["Pora_dnia"] = wybor
    elif f == "4":
        w1 = _wybierz_z_listy("Wybierz strefe", strefy)
        w2 = _wybierz_z_listy("Wybierz sezon", sezony)
        if w1 is None or w2 is None:
            print("Anulowano.")
            return
        kryteria["Strefa"] = w1
        kryteria["Sezon"] = w2
    elif f == "5":
        w1 = _wybierz_z_listy("Wybierz sezon", sezony)
        w2 = _wybierz_z_listy("Wybierz pore dnia", pory)
        if w1 is None or w2 is None:
            print("Anulowano.")
            return
        kryteria["Sezon"] = w1
        kryteria["Pora_dnia"] = w2
    elif f == "6":
        w1 = _wybierz_z_listy("Wybierz strefe", strefy)
        w2 = _wybierz_z_listy("Wybierz pore dnia", pory)
        if w1 is None or w2 is None:
            print("Anulowano.")
            return
        kryteria["Strefa"] = w1
        kryteria["Pora_dnia"] = w2
    elif f == "7":
        w1 = _wybierz_z_listy("Wybierz strefe", strefy)
        w2 = _wybierz_z_listy("Wybierz sezon", sezony)
        w3 = _wybierz_z_listy("Wybierz pore dnia", pory)
        if w1 is None or w2 is None or w3 is None:
            print("Anulowano.")
            return
        kryteria["Strefa"] = w1
        kryteria["Sezon"] = w2
        kryteria["Pora_dnia"] = w3

    wyniki = filtruj_baze(dane, kryteria)

    if not wyniki:
        print("\nNie znaleziono zadnych rekordow spelniajacych warunki.")
        return

    print(f"\nZnaleziono {len(wyniki)} rekordow.\n")

    for rekord in wyniki:
        sample = EnvironmentalSample.from_csv_row(rekord)
        wynik = sample.evaluate()
        _pokaz_rekord(rekord, wynik)


def _unikalne_wartosci(dane: List[dict[str, str]], kolumna: str) -> List[str]:
    """Return sorted unique values of column (case-insensitive)."""
    wartosci = {
        (rekord.get(kolumna, "") or "").strip()
        for rekord in dane
        if (rekord.get(kolumna, "") or "").strip()
    }
    return sorted(wartosci, key=lambda s: s.lower())


def _wybierz_z_listy(tresc: str, opcje: List[str]) -> Optional[str]:
    """Show numbered options and return chosen value; ENTER cancels."""
    if not opcje:
        print("Brak dostepnych opcji.")
        return None
    print(f"\n{tresc}:")
    for i, val in enumerate(opcje, 1):
        print(f"{i}) {val}")
    while True:
        wybor = input("Wybierz numer (ENTER aby anulowac): ").strip()
        if wybor == "":
            return None
        if wybor.isdigit():
            idx = int(wybor)
            if 1 <= idx <= len(opcje):
                return opcje[idx - 1]
        print("Nieprawidlowy wybor, sprobuj ponownie.")


def _pokaz_wynik(wynik: QualityAssessment) -> None:
    """Print label and index for a single evaluation result."""
    print(f"\nWynik oceny srodowiska: {wynik.label} (indeks {wynik.index})")


def _pokaz_rekord(rekord: dict[str, str], wynik: QualityAssessment) -> None:
    """Print CSV record summary and fuzzy evaluation result."""
    print(
        f"Strefa: {rekord['Strefa']}, Sezon: {rekord['Sezon']}, "
        f"Pora_dnia: {rekord['Pora_dnia']}"
    )
    print(
        f"  Temperatura={rekord['Temperatura_C']} st.C, "
        f"Wilgotnosc={rekord['Wilgotnosc_rel_%']} %, "
        f"PM2.5={rekord['PM2_5_ug_m3']} ug/m3, "
        f"Wiatr={rekord['Predkosc_wiatru_m_s']} m/s"
    )
    print(f"  Ocena: {wynik.label} (indeks {wynik.index})\n")
