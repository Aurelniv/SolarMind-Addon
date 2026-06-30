from dataclasses import dataclass, field


@dataclass
class SunData:
    azimuth: float = 0.0
    elevation: float = 0.0


@dataclass
class SystemData:
    health: int = 100
    errors: list[str] = field(default_factory=list)


@dataclass
class Runtime:
    sun: SunData = field(default_factory=SunData)
    system: SystemData = field(default_factory=SystemData)