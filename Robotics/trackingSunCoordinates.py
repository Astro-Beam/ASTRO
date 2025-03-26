from datetime import datetime
from astropy.time import Time
from astropy.coordinates import get_sun, EarthLocation, AltAz
import astropy.units as u

def automatic_tracking_better_astropy():
    # Define telescope location (Thessaloniki, Greece)
    telescopeLongitude = 22.9638  # degrees
    telescopeLatitude = 40.6401   # degrees
    elevation = 0 * u.m           # optional, set to 0 if unknown

    location = EarthLocation(lat=telescopeLatitude * u.deg,
                             lon=telescopeLongitude * u.deg,
                             height=elevation)

    # Get current time in UTC
    time = Time(datetime.utcnow())

    # Get Sun's equatorial coordinates (RA/Dec)
    sun_coord = get_sun(time)

    # Transform to horizontal coordinates (Alt/Az)
    altaz_frame = AltAz(obstime=time, location=location)
    sun_altaz = sun_coord.transform_to(altaz_frame)

    # Print results
    print(f"Sun's Right Ascension: {sun_coord.ra.to_string(unit='hourangle', precision=2)} ({sun_coord.ra.deg:.6f}°)")
    print(f"Sun's Declination: {sun_coord.dec.deg:.6f}°")
    print(f"Height (Altitude): {sun_altaz.alt:.2f}")
    print(f"Azimuth: {sun_altaz.az:.2f}")


automatic_tracking_better_astropy()