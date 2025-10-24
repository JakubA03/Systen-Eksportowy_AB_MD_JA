"""Silnik logiki rozmytej do oceny jakosci srodowiska."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


@dataclass(frozen=True)
class QualityAssessment:
    label: str
    index: float


def ocena_jakosci(
    pm25: float,
    wiatr: float,
    temperatura: float,
    wilgotnosc: float,
) -> QualityAssessment:
    """Zwraca rozmyta ocene jakosci srodowiska."""
    if pm25 < 0 or wiatr < 0 or wilgotnosc < 0:
        raise ValueError("Wartosci PM2.5, wiatru i wilgotnosci musza byc nieujemne.")

    system = _build_control_system()
    simulation = ctrl.ControlSystemSimulation(system)
    simulation.input["pm25"] = pm25
    simulation.input["wind"] = wiatr
    simulation.input["temperature"] = temperatura
    simulation.input["humidity"] = wilgotnosc
    simulation.compute()

    score = float(simulation.output["quality"])
    label = _label_for_score(score)
    return QualityAssessment(label=label, index=round(score, 1))


@lru_cache(maxsize=1)
def _build_control_system() -> ctrl.ControlSystem:
    """Tworzy system sterowania logika rozmyta."""
    pm25 = ctrl.Antecedent(np.linspace(0, 200, 201), "pm25")
    pm25["very_low"] = fuzz.trapmf(pm25.universe, [0, 0, 5, 12])
    pm25["low"] = fuzz.gaussmf(pm25.universe, 20, 6)
    pm25["moderate"] = fuzz.gaussmf(pm25.universe, 35, 8)
    pm25["high"] = fuzz.gaussmf(pm25.universe, 60, 12)
    pm25["very_high"] = fuzz.trapmf(pm25.universe, [80, 100, 200, 200])

    wind = ctrl.Antecedent(np.linspace(0, 18, 181), "wind")
    wind["calm"] = fuzz.trapmf(wind.universe, [0, 0, 0.6, 1.2])
    wind["breeze"] = fuzz.gaussmf(wind.universe, 2.0, 0.8)
    wind["windy"] = fuzz.gaussmf(wind.universe, 4.0, 1.2)
    wind["gusty"] = fuzz.trapmf(wind.universe, [5.0, 6.5, 18.0, 18.0])

    temperature = ctrl.Antecedent(np.linspace(-20, 40, 241), "temperature")
    temperature["freezing"] = fuzz.trapmf(temperature.universe, [-20, -20, -5, 2])
    temperature["cold"] = fuzz.gaussmf(temperature.universe, 5.0, 4.0)
    temperature["mild"] = fuzz.gaussmf(temperature.universe, 18.0, 5.0)
    temperature["warm"] = fuzz.gaussmf(temperature.universe, 24.0, 4.0)
    temperature["hot"] = fuzz.trapmf(temperature.universe, [28, 32, 40, 40])

    humidity = ctrl.Antecedent(np.linspace(0, 100, 201), "humidity")
    humidity["very_dry"] = fuzz.trapmf(humidity.universe, [0, 0, 20, 35])
    humidity["dry"] = fuzz.gaussmf(humidity.universe, 40.0, 10.0)
    humidity["comfortable"] = fuzz.gaussmf(humidity.universe, 50.0, 8.0)
    humidity["humid"] = fuzz.gaussmf(humidity.universe, 70.0, 8.0)
    humidity["saturated"] = fuzz.trapmf(humidity.universe, [80, 90, 100, 100])

    quality = ctrl.Consequent(np.linspace(0, 100, 201), "quality")
    quality["alarmowa"] = fuzz.trapmf(quality.universe, [0, 0, 8, 14])
    quality["bardzo_slaba"] = fuzz.trapmf(quality.universe, [12, 18, 24, 30])
    quality["slaba"] = fuzz.trapmf(quality.universe, [26, 32, 40, 48])
    quality["dostateczna"] = fuzz.trapmf(quality.universe, [44, 50, 56, 62])
    quality["umiarkowana"] = fuzz.trapmf(quality.universe, [58, 64, 70, 76])
    quality["dobra"] = fuzz.trapmf(quality.universe, [72, 78, 84, 90])
    quality["bardzo_dobra"] = fuzz.trapmf(quality.universe, [88, 92, 96, 99])
    quality["wyjatkowa"] = fuzz.trapmf(quality.universe, [97, 99, 100, 100])

    rules = [
        ctrl.Rule(pm25["very_high"], quality["alarmowa"]),
        ctrl.Rule(pm25["high"] & humidity["saturated"], quality["bardzo_slaba"]),
        ctrl.Rule(pm25["high"] & wind["gusty"], quality["slaba"]),
        ctrl.Rule(pm25["moderate"] & wind["calm"], quality["slaba"]),
        ctrl.Rule(pm25["moderate"] & wind["windy"], quality["umiarkowana"]),
        ctrl.Rule(pm25["moderate"] & humidity["humid"], quality["dostateczna"]),
        ctrl.Rule(pm25["low"] & wind["windy"], quality["dobra"]),
        ctrl.Rule(pm25["low"] & humidity["comfortable"] & temperature["mild"], quality["bardzo_dobra"]),
        ctrl.Rule(pm25["very_low"] & wind["breeze"] & humidity["comfortable"], quality["wyjatkowa"]),
        ctrl.Rule(pm25["very_low"] & temperature["freezing"], quality["dobra"]),
        ctrl.Rule(humidity["very_dry"] & temperature["hot"], quality["slaba"]),
        ctrl.Rule(humidity["humid"] & temperature["warm"], quality["umiarkowana"]),
        ctrl.Rule(humidity["dry"] & temperature["mild"] & pm25["moderate"], quality["dostateczna"]),
        ctrl.Rule(pm25["low"] & temperature["warm"], quality["dobra"]),
        ctrl.Rule(pm25["very_low"] & wind["gusty"], quality["bardzo_dobra"]),
    ]

    return ctrl.ControlSystem(rules)


def _label_for_score(score: float) -> str:
    if score >= 97:
        return "wyjatkowa"
    if score >= 90:
        return "bardzo dobra"
    if score >= 80:
        return "dobra"
    if score >= 68:
        return "umiarkowana"
    if score >= 55:
        return "dostateczna"
    if score >= 42:
        return "slaba"
    if score >= 28:
        return "bardzo slaba"
    return "alarmowa"
