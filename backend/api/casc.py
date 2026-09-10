from fastapi import APIRouter
from sqlalchemy import text

from database.connection import engine
from services.casc_service import calculate_casc
from api.candidates import get_candidates


router = APIRouter(
    prefix="/casc",
    tags=["CASC Analysis"]
)


@router.get("/{incident_id}")
def get_casc(incident_id: int):

    # --------------------------------------------------
    # Get latest candidate ranking
    # --------------------------------------------------

    candidate_data = get_candidates(incident_id)

    candidates = candidate_data.get(
        "candidates",
        []
    )

    if not candidates:
        return {
            "incident_id": incident_id,
            "mode": "CASC",
            "status": "ABSTAIN",
            "message": "No candidate vessels available",
            "casc_runs": []
        }

    # --------------------------------------------------
    # Run actual CASC calculation
    # --------------------------------------------------

    casc_result = calculate_casc(
        candidates=candidates,
        scenarios=5000,
        seed=143
    )

    # --------------------------------------------------
    # Save latest CASC result to database
    # --------------------------------------------------

    leading_vessel = casc_result.get(
        "leading_vessel"
    )

    candidate_id = None

    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT id
                FROM candidate_vessels
                WHERE incident_id = :incident_id
                  AND vessel_name = :vessel_name
                ORDER BY id DESC
                LIMIT 1
            """),
            {
                "incident_id": incident_id,
                "vessel_name": leading_vessel
            }
        )

        row = result.mappings().first()

        if row:
            candidate_id = row["id"]

    # --------------------------------------------------
    # Return CASC result
    # --------------------------------------------------

    casc_run = {
        "incident_id": incident_id,

        "candidate_id": candidate_id,

        "vessel_name": leading_vessel,

        "total_scenarios":
            casc_result.get(
                "total_scenarios",
                5000
            ),

        "winner_probability":
            casc_result.get(
                "winner_probability",
                0.0
            ),

        "closest_alternate":
            casc_result.get(
                "closest_alternate"
            ),

        "winner_flip_minutes":
            casc_result.get(
                "winner_flip_minutes"
            ),

        "normalized_perturbation":
            casc_result.get(
                "normalized_perturbation",
                0.0
            ),

        "stability_status":
            casc_result.get(
                "stability_status",
                "ABSTAIN"
            ),

        "winner_distribution":
            casc_result.get(
                "winner_distribution",
                {}
            ),

        "uncertainty_summary": (
            "Plausible uncertainty applied to "
            "Time, Space, Drift and AIS evidence."
        )
    }

    return {
        "incident_id": incident_id,

        "mode": "CASC_CALCULATED",

        "count": 1,

        "casc_runs": [
            casc_run
        ]
    }