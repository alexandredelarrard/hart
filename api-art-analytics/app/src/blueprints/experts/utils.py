from sqlalchemy.ext.hybrid import hybrid_method
import math

from math import pi, sqrt, radians, cos
Earth_radius_km = 6371.009
km_per_deg_lat = 2 * pi * Earth_radius_km / 360.0

@hybrid_method
def great_circle_distance(self, other):
    """
    Tries to calculate the great circle distance between the two locations

    If it succeeds, it will return the great-circle distance
    multiplied by 3959, which calculates the distance in miles.

    If it cannot, it will return None.

    """
    return math.acos(  self.cos_rad_lat 
                     * other.cos_rad_lat 
                     * math.cos(self.rad_lng - other.rad_lng)
                     + self.sin_rad_lat
                     * other.sin_rad_lat
                     ) * 3959

def approx_dist_2(lat1, lon1, lat2, lon2):
    # calculate km_per_deg_lon for your central station in Python and 
    # embed it in your query
    km_per_deg_lon = km_per_deg_lat * cos(radians(lat1))
    return sqrt((km_per_deg_lat *(lat1 - lat2)) ** 2 + (km_per_deg_lon * (lon1 - lon2)) ** 2)