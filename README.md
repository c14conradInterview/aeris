#Aeris Disc Golf Index

## Install
Requires python3 and using the provided api aerisweather.\
From the library root execute \
`python setup.py`

### Assumptions and Notes

I'm assuming that this does not need a sophisticated user interface and 
calling an entry point from the command line is sufficient. i.e. python create_activity_index.py <location_argument>
would yield a std_out print with the 1-5 value.

The activity index should be for that day.

I should use which ever weather data I find relevant to the activity to determine the index.

I'm not necessarily extending the api, just using it to acquire data to create an answer. 
Though if this were a task at the company it would get added into the api.



