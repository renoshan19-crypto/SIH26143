from fastapi import APIRouter
from sqlalchemy import text

from database.connection import engine


router = APIRouter(
    prefix="/detection",
    tags=["Detection"]
)


@router.get("/{incident_id}")
def get_detection(incident_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT *
                FROM spill_detections
                WHERE incident_id = :incident_id
                ORDER BY detection_time DESC
            """),
            {"incident_id": incident_id}
        )

        detections = [
            dict(row._mapping)
            for row in result
        ]

    return {
        "incident_id": incident_id,
        "count": len(detections),
        "detections": detections
    }