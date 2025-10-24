from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from simple_fuzzy import QualityAssessment, ocena_jakosci


@dataclass(frozen=True)
class EnvironmentalSample:
    strefa: str
    sezon: str
    pora_dnia: str
    temperatura: float
    wilgotnosc: float
    wiatr: float
    pm25: float

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> "EnvironmentalSample":
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
        return ocena_jakosci(
            pm25=self.pm25,
            wiatr=self.wiatr,
            temperatura=self.temperatura,
            wilgotnosc=self.wilgotnosc,
        )
