from collections import OrderedDict
import math

MAX_IDENTIFIERS = 5
EARTH_RADIUS_M = 6_371_000


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


class FleetStore:
    def __init__(self) -> None:
        self._data: OrderedDict[str, dict[str, dict]] = OrderedDict()
        self._last: dict[str, tuple[float, float, float, float | None]] = {}

    def store_gps(self, identifier: str, lat: float, lng: float, timestamp: float) -> None:
        if identifier not in self._data:
            if len(self._data) >= MAX_IDENTIFIERS:
                oldest = next(iter(self._data))
                del self._data[oldest]
                self._last.pop(oldest, None)
            self._data[identifier] = {}

        speed: float | None = None
        acceleration: float | None = None

        if identifier in self._last:
            prev_lat, prev_lng, prev_time, prev_speed = self._last[identifier]
            dt = timestamp - prev_time
            if dt > 0:
                speed = _haversine_m(prev_lat, prev_lng, lat, lng) / dt
                if prev_speed is not None:
                    acceleration = (speed - prev_speed) / dt

        time_key = str(timestamp)
        self._data[identifier][time_key] = {
            "GPS": {"lat": lat, "lng": lng},
            "속도": speed,
            "가속도": acceleration,
        }
        self._last[identifier] = (lat, lng, timestamp, speed)

    def get_gps(self, identifier: str) -> dict | None:
        if identifier not in self._data:
            return None
        return {
            identifier: {
                t: {"GPS": entry["GPS"]} for t, entry in self._data[identifier].items()
            }
        }

    def get_speed(self, identifier: str) -> dict | None:
        if identifier not in self._data:
            return None
        return {
            identifier: {
                t: {"속도": entry["속도"]} for t, entry in self._data[identifier].items()
            }
        }

    def get_acceleration(self, identifier: str) -> dict | None:
        if identifier not in self._data:
            return None
        return {
            identifier: {
                t: {"가속도": entry["가속도"]} for t, entry in self._data[identifier].items()
            }
        }

    def get_all(self) -> dict:
        return dict(self._data)

    def get_telemetry(self, identifier: str) -> dict | None:
        if identifier not in self._data:
            return None
        return {identifier: dict(self._data[identifier])}

    def reset(self) -> None:
        self._data.clear()
        self._last.clear()
