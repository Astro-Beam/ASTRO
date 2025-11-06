import math
from datetime import datetime, timedelta
from typing import Tuple
from astral import sun
from astral.location import LocationInfo

# this function takes (azimouth, elevation) and returns a vector n = (x, y, z) where |n|=1
def convert_az_el_to_enu_coordinates(azimouth, elevation):
    # shift 0 from North(standard) to East(+x)
    az_east_ccw = math.radians(90.0-azimouth)
    el = math.radians(elevation)

    x = math.cos(el) * math.cos(az_east_ccw)  # East
    y = math.cos(el) * math.sin(az_east_ccw)  # North
    z = math.sin(el)                           # Up 

    return (x, y, z)

def sun_vector(t_seconds, lat_deg, lon_deg, start_dt_utc, altitude_m=0.0):

    # safety check and prevention of accidental errors like using local time or naive datetime instead of UTC time
    if start_dt_utc.tzinfo is None or start_dt_utc.utcoffset() is None:
        raise ValueError("start_dt_utc must be timezone-aware (UTC).")

    # calculate current UTC time
    now_utc = start_dt_utc + timedelta(seconds=float(t_seconds))

    # build Astral location => get position of the sun on this specific time
    loc = LocationInfo(latitude=lat_deg, longitude=lon_deg, timezone="UTC")

    # get sun's azimuth (deg from North, clockwise) and elevation (deg above horizon)
    az_deg = sun.azimuth(loc.observer, now_utc)
    el_deg = sun.elevation(loc.observer, now_utc)

    return convert_az_el_to_enu_coordinates(az_deg, el_deg)






