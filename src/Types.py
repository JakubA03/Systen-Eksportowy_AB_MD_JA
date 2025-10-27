from __future__ import annotations

"""Typy pomocnicze – model rekordu środowiskowego i ewaluacja.

EnvironmentalSample to prosty kontener danych wejściowych dla silnika
rozmytego (PM2.5, wiatr, temperatura, wilgotność) wraz z metodami:
- from_csv_row: mapowanie wiersza CSV (polskie nagłówki) na obiekt,
- evaluate: wywołanie silnika i zwrócenie QualityAssessment.
"""

from dataclasses import dataclass
from typing import Dict
from simple_fuzzy import QualityAssessment, ocena_jakosci


@dataclass(frozen=True)
class EnvironmentalSample:
    """Pojedyncza próbka środowiskowa do oceny jakości.

    Pola strefa/sezon/pora_dnia są wykorzystywane głównie w UI do filtrowania
    i prezentacji; logika rozmyta korzysta z pól liczbowych.
    """
    strefa: str
    sezon: str
    pora_dnia: str
    temperatura: float
    wilgotnosc: float
    wiatr: float
    pm25: float

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> "EnvironmentalSample":
        """Tworzy próbkę na podstawie wiersza CSV o polskich nagłówkach."""
        return cls(
            strefa=row.get("Strefa", ""),
            sezon=row.get("Sezon", ""),
            pora_dnia=row.get("Pora_dnia", ""),
            temperatura=float(row.get("Temperatura_C", 0.0)),
            wilgotnosc=float(row.get("Wilgotnosc_rel_%", 0.0)),
            wiatr=float(row.get("Predkosc_wiatru_m_s", 0.0)),
            pm25=float(row.get("PM2_5_ug_m3", 0.0)),
        )

    def evaluate(self) -> QualityAssessment:
        """Uruchamia ocenę jakości środowiska dla tej próbki."""
        return ocena_jakosci(
            pm25=self.pm25,
            wiatr=self.wiatr,
            temperatura=self.temperatura,
            wilgotnosc=self.wilgotnosc,
        )
