import pytest
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation
from aeris.activities.activity import DiscGolfActivity, BaseActivity
from mock import MagicMock
from aeris import keys


@pytest.fixture
def aeris_weather():
    return AerisWeather(client_id=keys.client_id, client_secret=keys.client_secret)


@pytest.fixture
def location():
    return RequestLocation(postal_code='93101')


@pytest.fixture
def mock_aerisweather():
    mock_obj = MagicMock()
    mock_obj.observations.return_value = {}
    mock_obj.alerts.return_value = {}
    mock_obj.forecasts.return_value = {}
    return mock_obj


@pytest.fixture
def mock_location():
    return MagicMock()



def test_determine_activity_index_base(aeris_weather, location):
    with pytest.raises(NotImplementedError):
        activity = BaseActivity(aeris_weather, location)
        activity.determine_activity_index()

# TODO parameterize on different locations?
def test_determine_activity_index(aeris_weather, location):
    activity = DiscGolfActivity(aeris_weather, location)

    index = activity.determine_activity_index()
    assert index in [1, 2, 3, 4, 5]


# TODO put is pytest.parameterize for different answers
def test_determine_activity_index_mock(mock_aerisweather, location):
    pass

