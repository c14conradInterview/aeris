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
        try:
            self.verify_valid_location(location)
        # TODO use aeris weather exception for invalid location
        except Exception:
            raise ValueError('Location data invalid')
        self.location = location

    def verify_valid_location(self, location):
        """
        Verify that the location used for the activity will get weather data
        :param location:
        :return:
        """
        # TODO Ju Lee, do the thing
        pass

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
        """
        Gather weather data for things that would affect the ability to play disc golf.
        :return:
        """
        # Gather the data
        obs = self.aeris_weather.observations(location=self.location)
        alerts = self.aeris_weather.alerts(location=self.location)
        forecasts = self.aeris_weather.forecasts(location=self.location, params={ParameterType.FORECASTS.TO: '+2hours'})
        # aerisweather object doesn't have an explicit method of airquality, so we use the custom endpoint option
        EndpointType.custom = 'airquality'
        air_qualities = self.aeris_weather.request(endpoint=Endpoint(
            endpoint_type=EndpointType.CUSTOM, location=self.location))

        # For each of the weather types, create a score for how good/bad it is
        wind_score = self._check_wind_score(obs)
        temp_score = self._check_temp_score(obs)
        precipitation_score = self._check_precipitation_score(obs)
        alerts_score = self._check_alerts_score(alerts)
        forecasts_score = self._check_forecasts_score(forecasts)
        air_quality_score = self._check_air_quality_score(air_qualities)

        # Using all the individual weather scores, apply rule to determine overall answer
        index = self._create_index_from_scores(wind_score, temp_score, precipitation_score,
                                               alerts_score, forecasts_score,air_quality_score)

        return index

    def _check_wind_score(self, obs: list):
        scores = list()
        for idx, obs_response in enumerate(obs):
            ignored_values = 0
            score = 0
            wind = obs_response.ob.windMPH

            if wind is None:
                raise ValueError('Invalid wind data')
            elif wind <= 4:
                score += 5
            elif wind <= 8:
                score += 4
            elif wind <= 12:
                score += 3
            elif wind <= 15:
                score += 2
            elif wind <= 18:
                score += 1
            else:
                pass

            # Not sure what the difference between windMPH and windSpeedMPH
            wind_speed = obs_response.ob.windSpeedMPH
            if wind_speed is None:
                raise ValueError('Invalid wind data')
            elif wind_speed <= 4:
                score += 5
            elif wind_speed <= 8:
                score += 4
            elif wind_speed <= 12:
                score += 3
            elif wind_speed <= 15:
                score += 2
            elif wind_speed <= 18:
                score += 1
            else:
                pass

            wind_gust = obs_response.ob.windGustMPH
            if wind_gust is None or wind_gust <= 4:
                score += 5
            elif wind_gust <= 8:
                score += 4
            elif wind_gust <= 12:
                score += 3
            elif wind_gust <= 15:
                score += 2
            elif wind_gust <= 18:
                score += 1
            else:
                ignored_values += 1

            # Take the average, though some weighted score could be used.
            # TODO this seems confusing
            scores.append(round(score / (3 - ignored_values)))
        return scores

    def _check_temp_score(self, obs):
        scores = list()
        for obs_response in obs:
            score = 0
            heat_index = obs_response.ob.heatindexF
            wind_chill = obs_response.ob.windchillF
            feels_like = obs_response.ob.feelslikeF
            # TODO check if they are None
            for value in [heat_index, wind_chill, feels_like]:
                if value >= 65 and value <= 75:
                    score += 5
                elif value >= 60 and value <= 80:
                    score += 4
                elif value >= 55 and value <= 85:
                    score += 3
                elif value >= 50 and value <= 90:
                    score += 2
                elif value >= 45 and value <= 95:
                    score += 1
                else:
                    pass
            scores.append(round(score / 3))

        return scores

    def _check_precipitation_score(self, obs):
        for obs_response in obs:
            precep_inches = obs.ob.precipIN

    def _check_alerts_score(self, alerts):
        pass

    def _check_forecasts_score(self, forecasts):
        pass

    def _check_air_quality_score(self, air_quality):
        pass

    def _create_index_from_scores(self, wind_score, temp_score, precipitation_score,
                                  alerts_score, forecasts_score,air_quality_score):
        return 1