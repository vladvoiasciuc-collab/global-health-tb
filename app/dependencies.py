from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.observation_repository import ObservationRepository
from app.services.observation_service import ObservationService


def get_observation_service(
    session: Annotated[Session, Depends(get_db)],
) -> ObservationService:
    return ObservationService(ObservationRepository(session))
