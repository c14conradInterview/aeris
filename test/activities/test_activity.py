import pytest
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation
from aeris.activities.activity import DiscGolfActivity, BaseActivity
from aerisweather.responses.ObservationsData import ObservationsData
from aeris import keys
from mock import MagicMock

flag = '86001'
phx = '85086'
tuc = '85075'
sb = '93101'

@pytest.fixture
def aeris_weather():
    return AerisWeather(client_id=keys.client_id, client_secret=keys.client_secret)


@pytest.fixture
def location():
    return RequestLocation(postal_code='86001')




@pytest.fixture
def paramed_list_obs_data(request):
    # Make the mocked object have the same strucutre used to get data.
    mock_response = MagicMock()
    mock_response.ob = ObservationsData(request.param)
    return [mock_response]


@pytest.fixture
def disc_actitivty(aeris_weather, location):
    return DiscGolfActivity(aeris_weather, location)


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


@pytest.mark.parametrize('paramed_list_obs_data,answer',
                         [({'windMPH': 0,
                          'windSpeedMPH': 0,
                          'windGustMPH': 0}, 5),
                          ({'windMPH': 0,
                            'windSpeedMPH': 0,
                            'windGustMPH': None}, 5),
                          ({'windMPH': 30,
                            'windSpeedMPH': 30,
                            'windGustMPH': 30}, 0),
                          ({'windMPH': 11,
                            'windSpeedMPH': 7,
                            'windGustMPH': 5}, 4),
                          ],
                         indirect=["paramed_list_obs_data"])
def test__check_wind_score(paramed_list_obs_data, answer, disc_actitivty):
    wind_scores = disc_actitivty._check_wind_score(paramed_list_obs_data)
    assert wind_scores[0] == answer

@pytest.mark.parametrize('paramed_list_obs_data,answer',
                         [({'heatindexF': 70,
                          'windchillF': 70,
                          'feelslikeF': 70}, 5),
                          ({'heatindexF': 60,
                            'windchillF': 60,
                            'feelslikeF': 60}, 4),
                          ({'heatindexF': 82,
                            'windchillF': 82,
                            'feelslikeF': 82}, 3),
                          ({'heatindexF': 30,
                            'windchillF': 30,
                            'feelslikeF': 30}, 1),
                          ],
                         indirect=["paramed_list_obs_data"])
def test__check_temp_score(paramed_list_obs_data, answer, disc_actitivty):
    scores = disc_actitivty._check_temp_score(paramed_list_obs_data)
    assert scores[0] == answer


def test__check_precipitation_score():
    assert False


def test__check_alerts_score():
    assert False


def test__check_forecasts_score():
    assert False


def test__check_air_quality_score():
    assert False


def test__create_index_from_scores():
    assert False


if __name__ == "__main__":
    pytest.main([__file__])