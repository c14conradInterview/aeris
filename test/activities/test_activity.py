import pytest
from aeris import keys
from aeris.activities.activity import DiscGolfActivity, BaseActivity
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation
from aerisweather.responses.ObservationsData import ObservationsData
from mock import MagicMock


@pytest.fixture
def aeris_weather():
    return AerisWeather(client_id=keys.client_id, client_secret=keys.client_secret)


@pytest.fixture
def location(request):
    if hasattr(request, 'param'):
        return RequestLocation(postal_code=request.param)
    else:
        return RequestLocation(postal_code='86001')


@pytest.fixture
def paramed_obs_data(request):
    return ObservationsData(request.param)


@pytest.fixture
def paramed_list_air_quality(request):
    # Make the same structure as the response will get.
    mock_response = MagicMock()
    mock_response.periods = []
    period = MagicMock()
    period.aqi = request.param
    mock_response.periods.append(period)
    return [mock_response]


@pytest.fixture
def disc_actitivty(aeris_weather, location):
    return DiscGolfActivity(aeris_weather, location)


def test_determine_activity_index_base(aeris_weather, location):
    with pytest.raises(NotImplementedError):
        activity = BaseActivity(aeris_weather, location)
        activity.determine_activity_index()


@pytest.mark.parametrize('location',
                         [('86001'),
                          ('85086'),
                          ('85075'),
                          ('93101'),
                          ('92101')],
                         indirect=True)
def test_determine_activity_index(aeris_weather, location):
    activity = DiscGolfActivity(aeris_weather, location)

    index = activity.determine_activity_index()
    assert index in [1, 2, 3, 4, 5]


@pytest.mark.parametrize('paramed_obs_data,answer',
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
                            'windGustMPH': 5}, 3),
                          ],
                         indirect=["paramed_obs_data"])
def test__check_wind_score(paramed_obs_data, answer, disc_actitivty):
    wind_score = disc_actitivty._check_wind_score(paramed_obs_data)
    assert wind_score == answer

@pytest.mark.parametrize('paramed_obs_data,answer',
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
                         indirect=["paramed_obs_data"])
def test__check_temp_score(paramed_obs_data, answer, disc_actitivty):
    score = disc_actitivty._check_temp_score(paramed_obs_data)
    assert score == answer

@pytest.mark.parametrize('paramed_obs_data,answer',
                         [({'precipIN': 0}, 5),
                          ({'precipIN': .4}, 4),
                          ({'precipIN': 1}, 2),
                          ({'precipIN': 2}, 1),
                          ],
                         indirect=["paramed_obs_data"])
def test__check_precipitation_score(paramed_obs_data, answer, disc_actitivty):
    score = disc_actitivty._check_precipitation_score(paramed_obs_data)
    assert score == answer


def test__check_alerts_score():
    pass


def test__check_forecasts_score():
    pass


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
