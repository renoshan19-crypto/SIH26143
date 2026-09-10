from fastapi import APIRouter
from sqlalchemy import text

from database.connection import engine


router = APIRouter(
    prefix="/spill",
    tags=["Spill Characterization"]
)


@router.get("/{incident_id}")
def get_spill_characterization(incident_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT *
                FROM spill_characteristics
                WHERE incident_id = :incident_id
            """),
            {"incident_id": incident_id}
        )

        characteristics = [
            dict(row._mapping)
            for row in result
        ]

    return {
        "incident_id": incident_id,
        "count": len(characteristics),
        "characteristics": characteristics
    }