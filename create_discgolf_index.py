import argparse

from aeris import keys
from aeris.activities.activity import DiscGolfActivity
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.Endpoint import EndpointType, Endpoint
from aerisweather.requests.RequestLocation import RequestLocation


def determine_activity_index(zipcode, golf=False):
    aeris = AerisWeather(client_id=keys.client_id, client_secret=keys.client_secret, app_id=keys.app_id)
    loc = RequestLocation(postal_code=zipcode)
    disc_activity = DiscGolfActivity(aeris_weather=aeris, location=loc)
    index = disc_activity.determine_activity_index()

    print(f'The index for today is {index}. Go bang some chains!!!')
    if golf:
        EndpointType.custom = 'indices/golf'
        golf_index = aeris.request(endpoint=Endpoint(endpoint_type=EndpointType.CUSTOM, location=loc))
        print(f'Existing golf index shows {golf_index[0].indice.current.index}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='City/State location for activity')
    parser.add_argument("zipcode", help="String of the zipcode where the activity is being held ", type=str)
    parser.add_argument('-g', '--golf', required=False, help="Compare to already existing ball golf index", action='store_true')
    args = parser.parse_args()
    determine_activity_index(args.zipcode, args.golf)
