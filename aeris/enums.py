from enum import IntEnum


class AirQualityMinEnum(IntEnum):

    GOOD = 0
    MODERATE = 50
    USG = 100
    UNHEALTHY = 150
    VERY_UNHEALTHY = 200
    HAZARDOUS = 300


class WindSpeedEnum(IntEnum):
    BEST = 4
    MODERATE = 8
    NEUTRAL = 12
    POOR = 15
    TERRIBLE = 18


# These are very arbitrary as temperature ranges based on location. i.e. 90 in Phoenix isn't too terrible
class TemperatureEnum(IntEnum):
    BEST_MIN = 65
    BEST_MAX = 75
    MODERATE_MIN = 60
    MODERATE_MAX = 80
    NEUTRAL_MIN = 55
    NEUTRAL_MAX = 85
    POOR_MIN = 50
    POOR_MAX = 90
    TERRIBLE_MIN = 30
    TERRIBLE_MAX = 100


class ScoreEnum(IntEnum):
    BEST = 5
    MODERATE = 4
    NEUTRAL = 3
    POOR = 2
    TERRIBLE = 1
