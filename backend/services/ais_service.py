from math import radians, sin, cos, sqrt, atan2


EARTH_RADIUS_KM = 6371.0088


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two geographic points in KM.
    """

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def reconstruct_vessels(
    ais_rows,
    source_lat: float,
    source_lon: float,
    source_radius_km: float,
    source_start,
    source_end
):
    """
    Reconstruct historical AIS traffic around the
    estimated spill source region and source time window.
    """

    vessels = {}

    for row in ais_rows:

        vessel_name = (
            row.get("vessel_name")
            or row.get("name")
            or "UNKNOWN VESSEL"
        )

        mmsi = (
            row.get("mmsi")
            or row.get("MMSI")
            or "UNKNOWN"
        )

        latitude = (
            row.get("latitude")
            or row.get("lat")
        )

        longitude = (
            row.get("longitude")
            or row.get("lon")
        )

        timestamp = (
            row.get("timestamp")
            or row.get("time")
            or row.get("observation_time")
        )

        if latitude is None or longitude is None:
            continue

        latitude = float(latitude)
        longitude = float(longitude)

        distance_km = haversine_distance(
            source_lat,
            source_lon,
            latitude,
            longitude
        )

        inside_source_region = (
            distance_km <= source_radius_km
        )

        inside_time_window = True

        if timestamp is not None:

            if source_start and timestamp < source_start:
                inside_time_window = False

            if source_end and timestamp > source_end:
                inside_time_window = False

        sog = (
            row.get("sog")
            or row.get("speed_over_ground")
            or row.get("speed")
            or 0
        )

        cog = (
            row.get("cog")
            or row.get("course_over_ground")
            or row.get("course")
            or 0
        )

        key = str(mmsi)

        if key not in vessels:

            vessels[key] = {
                "vessel_name": vessel_name,
                "mmsi": mmsi,

                "positions": [],

                "closest_approach_km": distance_km,

                "source_region_overlap": False,

                "time_window_match": False,

                "sog": float(sog),
                "cog": float(cog)
            }

        vessel = vessels[key]

        vessel["positions"].append({
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": str(timestamp)
                if timestamp is not None
                else None,
            "distance_km": round(
                distance_km,
                3
            )
        })

        vessel["closest_approach_km"] = min(
            vessel["closest_approach_km"],
            distance_km
        )

        if inside_source_region:
            vessel["source_region_overlap"] = True

        if inside_time_window:
            vessel["time_window_match"] = True

    # =====================================================
    # FINAL CLASSIFICATION
    # =====================================================

    result = []

    for vessel in vessels.values():

        relevant = (
            vessel["source_region_overlap"]
            and vessel["time_window_match"]
        )

        assessment = (
            "RELEVANT"
            if relevant
            else "EXCLUDED"
        )

        result.append({

            "vessel_name": vessel["vessel_name"],

            "mmsi": vessel["mmsi"],

            "sog": vessel["sog"],

            "cog": vessel["cog"],

            "closest_approach_km": round(
                vessel["closest_approach_km"],
                3
            ),

            "source_region_overlap":
                vessel["source_region_overlap"],

            "time_window_match":
                vessel["time_window_match"],

            "assessment": assessment,

            "position_count":
                len(vessel["positions"]),

            "positions":
                vessel["positions"]
        })

    # Relevant vessels first
    result.sort(
        key=lambda x: (
            x["assessment"] != "RELEVANT",
            x["closest_approach_km"]
        )
    )

    return result
