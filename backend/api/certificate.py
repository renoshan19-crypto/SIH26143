from fastapi import APIRouter
from sqlalchemy import text

from database.connection import engine
from api.casc import get_casc


router = APIRouter(
    prefix="/certificates",
    tags=["Stability Certificates"]
)


@router.get("/{incident_id}")
def get_certificate(incident_id: int):

    # Get latest actual CASC calculation
    casc_data = get_casc(incident_id)

    casc_runs = casc_data.get(
        "casc_runs",
        []
    )

    if not casc_runs:
        return {
            "incident_id": incident_id,
            "count": 0,
            "certificates": []
        }

    casc = casc_runs[0]

    # --------------------------------------------------
    # Certificate information
    # --------------------------------------------------

    certificate = {
        "certificate_id":
            f"CASC-CERT-{incident_id:04d}",

        "incident_id":
            incident_id,

        "leading_vessel":
            casc.get(
                "vessel_name",
                "UNKNOWN"
            ),

        "initial_correlation":
            None,

        "casc_stability":
            round(
                float(
                    casc.get(
                        "winner_probability",
                        0.0
                    )
                ) * 100,
                2
            ),

        "closest_alternate":
            casc.get(
                "closest_alternate"
            ),

        "winner_flip_minutes":
            casc.get(
                "winner_flip_minutes"
            ),

        "normalized_perturbation":
            casc.get(
                "normalized_perturbation"
            ),

        "status":
            casc.get(
                "stability_status",
                "ABSTAIN"
            ),

        "decision_summary": (
            "Leading vessel is a source hypothesis "
            "based on satellite, drift and AIS evidence. "
            "This certificate does not establish "
            "definitive responsibility."
        ),

        "uncertainty_summary":
            casc.get(
                "uncertainty_summary"
            )
    }

    return {
        "incident_id": incident_id,
        "count": 1,
        "mode": "CERTIFICATE_GENERATED",
        "certificates": [
            certificate
        ]
    }