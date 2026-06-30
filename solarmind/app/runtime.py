from dataclasses import dataclass, field


@dataclass
class SunData:
    azimuth: float = 0.0
    elevation: float = 0.0


@dataclass
class PVData:
    installed_power_wc: int = 6060
    panel_azimuth: float = 145.0
    panel_tilt: float = 45.0
    theoretical_power: float = 0.0
    panel_exposure: float = 0.0
    incidence_factor: float = 0.0


@dataclass
class SystemData:
    health: int = 100
    errors: list[str] = field(default_factory=list)


@dataclass
class Runtime:
    sun: SunData = field(default_factory=SunData)
    system: SystemData = field(default_factory=SystemData)
    pv: PVData = field(default_factory=PVData)


