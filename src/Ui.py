import csv
from typing import List

from simple_fuzzy import QualityAssessment
from src.Types import EnvironmentalSample


def wczytaj_baze(sciezka: str = "data/data.csv") -> List[dict[str, str]]:
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

    if f == "1":
        kryteria["Strefa"] = input("Podaj strefe (miejska/podmiejska/wiejska/przemyslowa): ")
    elif f == "2":
        kryteria["Sezon"] = input("Podaj sezon (wiosna/lato/jesien/zima): ")
    elif f == "3":
        kryteria["Pora_dnia"] = input("Podaj pore dnia (rano/poludnie/popoludnie/noc): ")
    elif f == "4":
        kryteria["Strefa"] = input("Strefa: ")
        kryteria["Sezon"] = input("Sezon: ")
    elif f == "5":
        kryteria["Sezon"] = input("Sezon: ")
        kryteria["Pora_dnia"] = input("Pora dnia: ")
    elif f == "6":
        kryteria["Strefa"] = input("Strefa: ")
        kryteria["Pora_dnia"] = input("Pora dnia: ")
    elif f == "7":
        kryteria["Strefa"] = input("Strefa: ")
        kryteria["Sezon"] = input("Sezon: ")
        kryteria["Pora_dnia"] = input("Pora dnia: ")

    wyniki = filtruj_baze(dane, kryteria)

    if not wyniki:
        print("\nNie znaleziono zadnych rekordow spelniajacych warunki.")
        return

    print(f"\nZnaleziono {len(wyniki)} rekordow.\n")

    for rekord in wyniki:
        sample = EnvironmentalSample.from_csv_row(rekord)
        wynik = sample.evaluate()
        _pokaz_rekord(rekord, wynik)


def _pokaz_wynik(wynik: QualityAssessment) -> None:
    print(f"\nWynik oceny srodowiska: {wynik.label} (indeks {wynik.index})")


def _pokaz_rekord(rekord: dict[str, str], wynik: QualityAssessment) -> None:
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
