from aerisweather.responses.ObservationsData import ObservationsData
from aerisweather.responses.ObservationsResponse import ObservationsResponse
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation
from aerisweather.requests.Endpoint import EndpointType, Endpoint
from aerisweather.requests.ParameterType import ParameterType
from aeris.enums import AirQualityMinEnum, WindSpeedEnum, TemperatureEnum, ScoreEnum

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


# TODO create a factory so the activity object has everything it needs already
class DiscGolfActivity(BaseActivity):

    def __init__(self, aeris_weather, location):
        super().__init__(aeris_weather=aeris_weather, location=location)

    def determine_activity_index(self):
        """
        Gather weather data for things that would affect the ability to play disc golf.
        Apply a rule to create index on how good a day it would be to play at the self.location
        :return: int index value of 1-5 for how nice a day it is to play. 1 being very poor, 5 being best.
        """
        ### Gather the data ###
        # Only grab one to make methods consistant
        obs_data = self.aeris_weather.observations(location=self.location)
        #obs_data = self.aeris_weather.observations(location=self.location)[0].ob
        alerts = self.aeris_weather.alerts(location=self.location)[0]
        forecasts = self.aeris_weather.forecasts(location=self.location, params={ParameterType.FORECASTS.TO: '+5hours',
                                                                                 ParameterType.FORECASTS.FROM: 'today'})
        # aerisweather object doesn't have an explicit method of airquality, so we use the custom endpoint option
        EndpointType.custom = 'airquality'
        air_qualities = self.aeris_weather.request(endpoint=Endpoint(
            endpoint_type=EndpointType.CUSTOM, location=self.location))

        # For each of the weather types, create a score for how good/bad it is
        wind_score = self._check_wind_score(obs_data)
        temp_score = self._check_temp_score(obs_data)
        precipitation_score = self._check_precipitation_score(obs_data)
        # TODO come back to this and handle alert codes, there is probably an enum to handle them
        #alerts_score = self._check_alerts_score(alerts)
        # TODO come back after making the score method generic
        #forecasts_score = self._check_forecasts_score(forecasts)
        air_quality_score = self._check_air_quality_score(air_qualities)

        # Using all the individual weather scores, apply rule to determine overall answer
        index = self._create_index_from_scores(wind_score, temp_score, precipitation_score,
                                               air_quality_score)

        return index

    # TODO could refactor to a single generic method that takes keys to get, and some scoring algorithm with that data?
    def _check_wind_score(self, obs: list):
        """
        Given a list of ObservationsData grab the wind data and compare those to some wind scores
        :param obs: list of ObservationsData holding data from a aerisweather.observations api endpoint
        :return: list of int scores for each observation passed.
        """
        scores = list()
        for idx, obs_response in enumerate(obs):
            ignored_values = 0
            score = 0

            wind = obs_response.ob.windMPH

            if wind is None:
                ignored_values += ScoreEnum.BEST
            elif wind <= WindSpeedEnum.GOOD:
                score += ScoreEnum.BEST
            elif wind <= WindSpeedEnum.MODERATE:
                score += ScoreEnum.MODERATE
            elif wind <= WindSpeedEnum.POOR:
                score += ScoreEnum.NEUTRAL
            elif wind <= WindSpeedEnum.TERRIBLE:
                score += ScoreEnum.POOR
            else:
                score += ScoreEnum.TERRIBLE

            # Not sure what the difference between windMPH and windSpeedMPH
            wind_speed = obs_response.ob.windSpeedMPH
            if wind_speed is None:
                ignored_values += 1
            elif wind <= WindSpeedEnum.GOOD:
                score += 5
            elif wind <= WindSpeedEnum.MODERATE:
                score += 4
            elif wind <= WindSpeedEnum.POOR:
                score += 3
            elif wind <= WindSpeedEnum.TERRIBLE:
                score += 2
            else:
                score += 1

            wind_gust = obs_response.ob.windGustMPH
            if wind_gust is None or wind_gust <= 4:
                score += 5
            elif wind_gust <= WindSpeedEnum.GOOD:
                score += 5
            elif wind_gust <= WindSpeedEnum.MODERATE:
                score += 4
            elif wind_gust <= WindSpeedEnum.POOR:
                score += 3
            elif wind_gust <= WindSpeedEnum.TERRIBLE:
                score += 2
            else:
                ignored_values += 1

            # Take the average, though some weighted score could be used.
            if ignored_values == 3:

                scores.append(None)
            else:
                # don't have values that were none count to the average
                scores.append(round(score / (3 - ignored_values)))
        return scores

    def _check_temp_score(self, obs: list):
        """
        Given a list of ObservationsData grab the wind data and compare those to some temperature scores
        :param obs: list of ObservationsData holding data from a aerisweather.observations api endpoint
        :return: list of int scores for each observation passed.
        """
        scores = list()
        for obs_response in obs:
            score = 0
            heat_index = obs_response.ob.heatindexF
            wind_chill = obs_response.ob.windchillF
            feels_like = obs_response.ob.feelslikeF
            for value in [heat_index, wind_chill, feels_like]:
                if TemperatureEnum.GOOD_MIN <= value <= TemperatureEnum.GOOD_MAX:
                    score += 5
                elif TemperatureEnum.MODERATE_MIN <= value <= TemperatureEnum.MODERATE_MAX:
                    score += 4
                elif TemperatureEnum.POOR_MIN <= value <= TemperatureEnum.POOR_MAX:
                    score += 3
                elif TemperatureEnum.TERRIBLE_MIN <= value <= TemperatureEnum.TERRIBLE_MAX:
                    score += 2
                else:
                    score += 1

            scores.append(round(score / 3))

        return scores

    def _check_precipitation_score(self, obs: list):
        """
        Given a list of ObservationsData grab the wind data and compare those to some precipitation scores
        :param obs: list of ObservationsData holding data from a aerisweather.observations api endpoint
        :return: list of int scores for each observation passed.
        """
        scores = list()
        for obs_response in obs:
            precep_inches = obs_response.ob.precipIN
            score = 0
            # Not sure if these values are reasonable since where the rain is
            # happening could determine how much if affects the conditions
            if precep_inches is None or precep_inches <= 0.2:
                score += 5
            elif precep_inches <= .5:
                score += 4
            elif precep_inches <= .9:
                score += 3
            elif precep_inches <= 1.3:
                score += 2
            else:
                score += 1

            scores.append(score)
        return scores


    def _check_alerts_score(self, alerts):
        pass

    def _check_forecasts_score(self, forecasts):

        for forecast in forecasts:
            obs = ObservationsData(forecast.data)
            res = ObservationsResponse(forecast.data)
            wind_scores = self._check_wind_score(obs)
            temp_scores = self._check_temp_score(forecast)
            precip_scores = self._check_precipitation_score(forecast)

            wat = 'wat'

    def _check_air_quality_score(self, air_quality):
        """
        Given a list of ObservationsData grab the wind data and compare those to some air quality scores
        :param obs: list of ObservationsData holding data from a aerisweather.observations api endpoint
        :return: list of int scores for each observation passed.
        """
        scores = list()
        for obs_response in air_quality:
            for period in obs_response.periods:
                score = 0
                aqi = period.aqi
                # compare against the lowest value for AQI starting at the highest
                if aqi is None:
                    score = None
                elif aqi > AirQualityMinEnum.HAZARDOUS:
                    score += 0
                elif aqi > AirQualityMinEnum.VERY_UNHEALTHY:
                    score += 1
                elif aqi > AirQualityMinEnum.UNHEALTHY:
                    score += 2
                elif aqi > AirQualityMinEnum.USG:
                    score += 3
                elif aqi > AirQualityMinEnum.MODERATE:
                    score += 4
                else:
                    score += 5
                scores.append(score)

        return scores



    def _create_index_from_scores(self, wind_score, temp_score, precipitation_score,
                                  air_quality_score):
        """
        Given lists of scores for each weather data type, average them out and determine a all-around score
        :param wind_score: list of ints from the score determined for wind data
        :param temp_score: list of ints from the score determined for the temperature data
        :param precipitation_score: list of ints from the score determined for the precipitation data
        :param air_quality_score: list of ints from the score determined for the air quality data
        :return: int: Overall score for the data of playing some disc
        """
        # any of the values might be none and should not contribute to score

        # Each score could have multiple entries that need to be averaged out
        total = 0
        for score_type in [wind_score, temp_score, precipitation_score, air_quality_score]:
            type_total = 0
            for score in score_type:
                type_total += score
            # This assumes each entry holds the same weight to contribute
            type_avg = type_total / len(score_type)

            total += type_avg

        # Using 4 different score types.
        # this assumes each type contributes the same amount to the index!
        unrounded = total / 4
        total_avg = round(unrounded)

        return total_avg