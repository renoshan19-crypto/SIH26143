from fastapi import APIRouter
from database.connection import engine
from sqlalchemy import text


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


@router.get("/")
def get_incidents():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT *
                FROM incidents
                ORDER BY incident_id DESC
            """)
        )

        incidents = [
            dict(row._mapping)
            for row in result
        ]

    return {
        "count": len(incidents),
        "incidents": incidents
    }