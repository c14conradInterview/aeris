import pytest
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation
from aeris.activities.activity import DiscGolfActivity, BaseActivity
from aerisweather.responses.ObservationsData import ObservationsData
from aerisweather.responses.AlertsResponse import AlertsResponse
from aeris import keys
from mock import MagicMock

flag = '86001'
phx = '85086'
tuc = '85075'
sb = '93101'
sd = '92101'


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
def paramed_list_air_quality(request):
    mock_response = MagicMock()
    mock_response.periods = []
    period = MagicMock()
    period.aqi = request.param
    mock_response.periods.append(period)
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


@pytest.mark.parametrize('paramed_list_obs_data,answer',
                         [({'windMPH': 0,
                          'windSpeedMPH': 0,
                          'windGustMPH': 0}, 5),
                          ({'windMPH': 0,
                            'windSpeedMPH': 0,
                            'windGustMPH': None}, 5),
                          ({'windMPH': 30,
                            'windSpeedMPH': 30,
                            'windGustMPH': 30}, 1),
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

@pytest.mark.parametrize('paramed_list_obs_data,answer',
                         [({'precipIN': 0}, 5),
                          ({'precipIN': .4}, 4),
                          ({'precipIN': 1}, 2),
                          ({'precipIN': 2}, 1),
                          ],
                         indirect=["paramed_list_obs_data"])
def test__check_precipitation_score(paramed_list_obs_data, answer, disc_actitivty):
    scores = disc_actitivty._check_precipitation_score(paramed_list_obs_data)
    assert scores[0] == answer


def test__check_alerts_score():
    assert False


def test__check_forecasts_score():
    assert False


@pytest.mark.parametrize('paramed_list_air_quality,answer',
                         [(0, 5),
                          (55, 4),
                          (101, 3),
                          (204, 1),
                          ],
                         indirect=["paramed_list_air_quality"])
def test__check_air_quality_score(paramed_list_air_quality, answer, disc_actitivty):
    score = disc_actitivty._check_air_quality_score(paramed_list_air_quality)
    assert score[0] == answer


@pytest.mark.parametrize('scores, answer',
                         [(([1], [1], [1], [1]), 1),
                          (([1], [3], [3], [4]), 3),
                          (([4, 2], [3, 3], [3, 1], [4, 2]), 3)])
def test__create_index_from_scores(scores, answer, disc_actitivty):
    index = disc_actitivty._create_index_from_scores(*scores)
    assert index == answer


if __name__ == "__main__":
    pytest.main([__file__])
