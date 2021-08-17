from aeris.enums import AirQualityMinEnum, WindSpeedEnum, TemperatureEnum, ScoreEnum
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.Endpoint import EndpointType, Endpoint
from aerisweather.requests.RequestLocation import RequestLocation
from aerisweather.responses.ForecastPeriod import ForecastPeriod
from aerisweather.responses.ObservationsData import ObservationsData


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
        # Only grab one to make methods consistent.
        # Note, the ObservationsData generates a new instance of itself and returns that.
        # Might be a memory leak if we don't lose reference to them
        obs_responses = self.aeris_weather.observations(location=self.location)

        # aerisweather object doesn't have an explicit method of airquality, so we use the custom endpoint option
        EndpointType.custom = 'airquality'
        air_qualities = self.aeris_weather.request(endpoint=Endpoint(
            endpoint_type=EndpointType.CUSTOM, location=self.location))
        wind_scores = list()
        temp_scores = list()
        precipitation_scores = list()
        forecast_scores = list()
        # For each of the weather types, create a score for how good/bad it is
        for obs_data in obs_responses:
            wind_scores.append(self._check_wind_score(obs_data.ob))
            temp_scores.append(self._check_temp_score(obs_data.ob))
            precipitation_scores.append(self._check_precipitation_score(obs_data.ob))


        # TODO come back to this and handle alert codes, there is probably an enum to handle them
        #alerts = self.aeris_weather.alerts(location=self.location)[0]
        #alerts_score = self._check_alerts_score(alerts)
        # TODO come back after making the score method generic
        #forecasts = self.aeris_weather.forecasts(location=self.location, params={ParameterType.FORECASTS.TO: '+5hours',
        #                                                                         ParameterType.FORECASTS.FROM: 'today'})
        #for period in forecasts[0].periods:
        #    forecast_scores.append(self._check_forecasts_score(period))


        air_quality_scores = self._check_air_quality_score(air_qualities)

        # Using all the individual weather scores, apply rule to determine overall answer
        # This method could probably be made generalized if each of the scores were objects and
        index = self._create_index_from_scores(wind_scores, temp_scores, precipitation_scores,
                                               air_quality_scores)

        return index

    # TODO could refactor to a single generic method that takes keys to get, and some scoring algorithm with that data
    def _check_wind_score(self, obs: ObservationsData):
        """
        Given a list of ObservationsData grab the wind data and compare those to some wind scores
        :param obs: list of ObservationsData holding data from a aerisweather.observations api endpoint
        :return: list of int scores for each observation passed.
        """

        ignored_values = 0
        score = 0
        wind_types = [obs.windMPH, obs.windSpeedMPH, obs.windGustMPH]
        # Not sure what the difference between windMPH and windSpeedMPH
        for wind_type in wind_types:
            if wind_type is None:
                ignored_values += 1
            elif wind_type <= WindSpeedEnum.BEST:
                score += ScoreEnum.BEST
            elif wind_type <= WindSpeedEnum.BEST:
                score += ScoreEnum.MODERATE
            elif wind_type <= WindSpeedEnum.NEUTRAL:
                score += ScoreEnum.NEUTRAL
            elif wind_type <= WindSpeedEnum.POOR:
                score += ScoreEnum.POOR
            elif wind_type <= WindSpeedEnum.TERRIBLE:
                score += ScoreEnum.TERRIBLE
            else:
                score += ScoreEnum.TERRIBLE

        # Take the average, though some weighted score could be used.
        if ignored_values == 3:

            avg = None
        else:
            # don't have values that were none count to the average
            avg = round(score / (3 - ignored_values))
        return avg

    def _check_temp_score(self, obs: ObservationsData):
        """
        Given a list of ObservationsData grab the temperature data and compare those to some temperature scores
        :param obs: ObservationsData holding data from a aerisweather.observations api endpoint
        :return: list of int scores for each observation passed.
        """
        score = 0
        temp_types = [obs.heatindexF, obs.windchillF, obs.feelslikeF]
        for value in temp_types:
            if TemperatureEnum.BEST_MIN <= value <= TemperatureEnum.BEST_MAX:
                score += ScoreEnum.BEST
            elif TemperatureEnum.MODERATE_MIN <= value <= TemperatureEnum.MODERATE_MAX:
                score += ScoreEnum.MODERATE
            elif TemperatureEnum.NEUTRAL_MIN <= value <= TemperatureEnum.NEUTRAL_MAX:
                score += ScoreEnum.NEUTRAL
            elif TemperatureEnum.POOR_MIN <= value <= TemperatureEnum.POOR_MAX:
                score += ScoreEnum.POOR
            elif TemperatureEnum.TERRIBLE_MIN <= value <= TemperatureEnum.TERRIBLE_MAX:
                score += ScoreEnum.TERRIBLE
            else:
                score += ScoreEnum.TERRIBLE

        avg = round(score / 3)

        return avg

    def _check_precipitation_score(self, obs: ObservationsData):
        """
        Given an ObservationsData grab the percipitation data and compare those to some precipitation scores
        :param obs: ObservationsData holding data from a aerisweather.observations api endpoint
        :return: int scores for how much downfall there is
        """

        precep_inches = obs.precipIN
        score = 0
        # Not sure if these values are reasonable since where the rain is
        # happening could determine how much if affects the conditions
        # TODO handle boundaries as floats
        if precep_inches is None or precep_inches <= 0.2:
            score += ScoreEnum.BEST
        elif precep_inches <= .5:
            score += ScoreEnum.MODERATE
        elif precep_inches <= .9:
            score += ScoreEnum.NEUTRAL
        elif precep_inches <= 1.3:
            score += ScoreEnum.POOR
        else:
            score += ScoreEnum.TERRIBLE

        return score


    def _check_alerts_score(self, alerts):
        pass

    def _check_forecasts_score(self, forecast: ForecastPeriod):
        """
        From the forecast given, create an index score for all the weather types.
        :param forecast: ForecastPeriod for a future time which the activity will still be happening
        :return: int: score for that period of time
        """
        # TODO forecastPeriod and ObservationsData don't have the same keys, so we would need a generic method that takes
        # arguments for which attribute and which enum
        wind = self._check_wind_score(forecast)
        temp = self._check_temp_score(forecast)
        precipitation_score = self._check_precipitation_score(forecast)


    def _check_air_quality_score(self, air_quality):
        """
        Given an ObservationsData grab the air quality data and compare those to some air quality scores
        :param obs: list of ObservationsData holding data from a aerisweather.observations api endpoint
        :return: int score
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
                    score += ScoreEnum.TERRIBLE
                elif aqi > AirQualityMinEnum.VERY_UNHEALTHY:
                    score += ScoreEnum.TERRIBLE
                elif aqi > AirQualityMinEnum.UNHEALTHY:
                    score += ScoreEnum.POOR
                elif aqi > AirQualityMinEnum.USG:
                    score += ScoreEnum.NEUTRAL
                elif aqi > AirQualityMinEnum.MODERATE:
                    score += ScoreEnum.MODERATE
                else:
                    score += ScoreEnum.BEST
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