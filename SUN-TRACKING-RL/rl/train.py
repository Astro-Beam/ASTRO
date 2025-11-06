import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from astro_tracker.sky_objects.sun_model import sun_vector

def main():
    lat, lon = 40.64, 22.94  # Thessaloniki

    # use current local time and convert to UTC
    local_now = datetime.now(ZoneInfo("Europe/Athens"))
    start = local_now.astimezone(timezone.utc)

    for t in [0, 1800, 3600]:  # now, +30m, +1h
        x, y, z = sun_vector(t, lat, lon, start)
        print(f"t={t:4d}s -> ({x:.6f}, {y:.6f}, {z:.6f})  | |v|={math.sqrt(x*x+y*y+z*z):.6f}")

if __name__ == "__main__":
    main()

