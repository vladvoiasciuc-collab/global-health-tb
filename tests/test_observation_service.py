import pytest
from unittest.mock import MagicMock

from app.domain import ObservationCriteria, Sex
from app.services.observation_service import ObservationService, ObservationPage


def test_get_page_returns_observation_page():
    repo = MagicMock()
    repo.find.return_value = []
    repo.count.return_value = 0

    service = ObservationService(repo, page_size=10)
    page = service.get_page(ObservationCriteria(), number=1)

    assert isinstance(page, ObservationPage)
    assert page.number == 1
    assert page.total_items == 0
    repo.find.assert_called_once()
    repo.count.assert_called_once()


def test_page_size_must_be_positive():
    with pytest.raises(ValueError):
        ObservationService(MagicMock(), page_size=0)
