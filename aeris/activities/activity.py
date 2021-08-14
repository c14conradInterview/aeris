from aerisweather.responses.ObservationsData import ObservationsData
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation
from aerisweather.requests.Endpoint import EndpointType, Endpoint
from aerisweather.requests.ParameterType import ParameterType


class BaseActivity:
    """
    Base class for activities.
    """

    def __init__(self, aeris_weather: AerisWeather, location: RequestLocation):
        self.aeris_weather = aeris_weather
        self.location = location

    def determine_activity_index(self) -> int:
        """
        Abstract method that all child classes must implement to determine the index for the activity it represents.
        :return:
        """
        raise NotImplementedError('Child class did not implement method')


class DiscGolfActivity(BaseActivity):

    def __init__(self, aeris_weather, location):
        super().__init__(aeris_weather=aeris_weather, location=location)

    def determine_activity_index(self):
        obs = self.aeris_weather.observations(location=self.location)
        alerts = self.aeris_weather.alerts(location=self.location)
        forecasts = self.aeris_weather.forecasts(location=self.location, params={ParameterType.FORECASTS.TO: '+2hours'})
        # aerisweather object doesn't have an explicit method of air_quality, so we use the custom endpoint option
        EndpointType.custom = 'airquality'
        air_qualities = self.aeris_weather.request(endpoint=Endpoint(
            endpoint_type=EndpointType.CUSTOM, location=self.location))


        wind_score = self.check_wind_score(obs)
        temp_score = self.check_temp_score(obs)
        precipitation_score = self.check_precipitation_score(obs)
        alerts_score = self.check_alerts_score(alerts)
        forecasts_score = self.check_forecasts_score(forecasts)

        air_quality_score = self.check_air_quality_score(air_qualities)

        index = self.create_index_from_scores(wind_score, temp_score, precipitation_score,
                                              alerts_score, forecasts_score, threats_score,
                                              air_quality_score)

        return index

    def check_wind_score(self, obs):
        pass

    def check_temp_score(self, obs):
        pass

    def check_precipitation_score(self, obs):
        pass

    def check_alerts_score(self, alerts):
        pass

    def check_forecasts_score(self, forecasts):
        pass

    def check_air_quality_score(self, air_quality):
        pass

    def create_index_from_scores(self, wind_score, temp_score, precipitation_score, alerts_score, forecasts_score,
                                 threats_score, air_quality_score):
        return 1