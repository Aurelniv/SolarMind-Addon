import math


def calculate_physics(runtime):
    sun_azimuth = math.radians(runtime.sun.azimuth)
    sun_elevation = math.radians(runtime.sun.elevation)
    panel_azimuth = math.radians(runtime.pv.panel_azimuth)
    panel_tilt = math.radians(runtime.pv.panel_tilt)

    if runtime.sun.elevation <= 0:
        runtime.pv.incidence_factor = 0.0
        runtime.pv.panel_exposure = 0.0
        runtime.pv.theoretical_power = 0.0
        return runtime

    incidence = (
        math.sin(sun_elevation) * math.cos(panel_tilt)
        + math.cos(sun_elevation)
        * math.sin(panel_tilt)
        * math.cos(sun_azimuth - panel_azimuth)
    )

    incidence = max(0.0, incidence)

    runtime.pv.incidence_factor = round(incidence, 3)
    runtime.pv.panel_exposure = round(incidence * 100, 1)
    runtime.pv.theoretical_power = round(
        runtime.pv.installed_power_wc * incidence * max(0.0, math.sin(sun_elevation)),
        0,
    )

    return runtime