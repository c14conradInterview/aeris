from aeris import keys
import argparse
from aerisweather.aerisweather import AerisWeather
from aerisweather.requests.RequestLocation import RequestLocation
from aerisweather.requests.Endpoint import EndpointType, Endpoint




one = 1



def determine_activity_index(zipcode):
  aeris = AerisWeather(client_id=keys.client_id, client_secret=keys.client_secret, app_id=keys.app_id)

  loc = RequestLocation(postal_code=zipcode)

  obs = aeris.observations(location=loc)
  EndpointType.custom = 'indices/golf'
  f_list = aeris.request(endpoint=Endpoint(endpoint_type=EndpointType.CUSTOM, location=loc))

  one = 1

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='City/State location for activity')
  parser.add_argument("zipcode", help="String of the zipcode where the activity is being held ", type=str)
  args = parser.parse_args()
  determine_activity_index(zipcode=args.zipcode)
