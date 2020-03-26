from django.db import models
from django.urls import reverse

__author__ = 'brleinad'

import re
import json 
import requests
import ipinfo

from . import defaults


"""

    # TODO: Give the output in JSON
    # TODO: Error handling: MP API not working, no routes near location, etc
    # TODO: add weather forecast info
    # TODO: Write all doc strings
    # TODO: Write doc tests
    # TODO: Write a few tests
    # TODO: Consider number of votes when getting best routes
"""

class ProjFinder(models.Model):
    """
    """

    def __init__(self):
        self.nearby_route =[]

    def get_best_routes(self, routes, top = 10):
        """
        Returns a list of the best routes (based on the stars) given a list of routes)
        """
        # TODO: split the list to give just the first 5
        best_routes = sorted(routes, reverse=True)
        return best_routes[0:top]

    def print_routes(self, routes):
        """
        Nicely print a list of routes.
        """

        for route in routes:
            #route.print_route_name() 
            print(route) 


    def get_user_input(self):
        """
        Asks for User input and save to self.
         
        # TODO: Make sure the grade is an acceptable grade
        # TODO: Take other grade formats and convert
        """

        print('What grade is your hardest onsight?')
        self.min_grade = 5.9 #input()

        #valid_grade_regex = re.compile(r'5\.\d{1,2}[a-d]+')
        if not re.match(r'5\.\d{1,2}[a-d]?', str(self.min_grade)):
            raise UserInputError('Grade given is not a valid climbing grade in the YDS.')

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def main(self, request, min_grade=defaults.MIN_GRADE, max_grade=defaults.MAX_GRADE, max_distance=defaults.MAX_DISTANCE):

        # TODO: optionally get the email/key from the user.
        email    = 'daniel.rodas.bautista@gmail.com'
        key      = '200222284-dae8be573771fdff71e7b535b47b600d'

        nearby_routes = []
        best_routes   = []
        MP            = MountainProjectAPI(email, key)
        self.location      = Location()

        ## User gives max red point grade (sport by default).
        ## Optionally the user can choose max distance, style, pitches, etc.
        #self.get_user_input()

        ## Getting the location based on the IP address.
        ip_address = self.get_client_ip(request)
        if ip_address == '127.0.0.1':
            #If on Dev mode just use local IP
            ip_address = None 
        self.location.get_location(ip_address)
        print('Your location is set to:')
        self.location.print_location()

        print()
        ## Based on that location ask MP for all the routes nearby (max default 50).
        print('Getting nearby routes.')
        nearby_routes = MP.get_nearby_routes(self.location, min_diff=min_grade, max_diff=max_grade, max_distance=max_distance)

        ## Get list of best routes (top 5 by default).
        # TODO: allow user to say how many top routes to get
        print('Getting the best routes.')
        best_routes = self.get_best_routes(nearby_routes)

        ## Show in a pretty way these routes with route name, grade, location, link.
        self.print_routes(best_routes)
        return best_routes

class UserInputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class MountainProjectAPI(object):
    """
    A class to interact with the Mountain Project API https://www.mountainproject.com/data
    """

    def __init__(self, email, key):

        self.parameters = {
                'email' : email,
                'key'   : key,
                'format': 'json',
                }

    def jprint(self, obj):
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text)

    def get_user(self, user):
        """
        Given a user ID or corresponding email it will retrieve the user's information from MP.
        """

        response = requests.get(self.MP_URL+'get-user', params = self.parameters)
        self.jprint(response.json())
        return response

    def get_nearby_routes(self, location, max_distance = 30, max_results = 100, min_diff = 5.6, max_diff = 5.13):
        """
        Given a location in the form of a tuple it will look for all the routes near that location and return them in a list of routes.
        """
        #Required Arguments:
        #key - Your private key
        #lat - Latitude for a given area
        #lon - Longitude for a given area
        #Optional Arguments:
        #maxDistance - Max distance, in miles, from lat, lon. Default: 30. Max: 200.
        #maxResults - Max number of routes to return. Default: 50. Max: 500.
        #minDiff - Min difficulty of routes to return, e.g. 5.6 or V0.
        #maxDiff - Max difficulty of routes to return, e.g. 5.10a or V2.

        params = self.parameters

        params['lat']         = location.latitude
        params['lon']         = location.longitude
        params['maxDistance'] = max_distance
        params['maxResults']  = max_results
        params['minDiff']     = min_diff
        params['maxDiff']     = max_diff

        #response = requests.get(self.MP_URL+'get-routes-for-lat-lon', params = self.parameters)
        response = self.get_response_from_api('get-routes-for-lat-lon', params)
        #self.jprint(response.json())
        nearby_routes = self.json2routes(response.json())
        return nearby_routes

    def get_response_from_api(self, api_method, parameters):
        """
        """
        MP_URL   = 'https://www.mountainproject.com/data/'
        #try:
        response = requests.get(''.join((MP_URL, api_method)), params = parameters)
        #response = requests.get(MP_URL+api_method, params = parameters)
        #except ConnectionError:
            #print('ERROR: Could not connect to Mountain Project')
        return response

    def json2routes(self, json_routes):
        """
        Returns a list of route objects given a json containing routes.
        """

        routes = []

        for json_route in json_routes['routes']:
            # TODO: What to do if one of the fields is empty
            loc = Location()
            loc.latitude  = json_route['latitude'],
            loc.longitude = json_route['longitude'],
            loc.place     = json_route['location'],

            route  = Route(
                name     = json_route['name'], 
                style    = json_route['type'],
                grade    = json_route['rating'],
                stars    = json_route['stars'],
                pitches  = json_route['pitches'],
                url      = json_route['url'],
                location = loc
                )

            routes.append(route)

        return routes


class Location(object):
    """
    # TODO:  Do I really need this class?  (I could get IP on main class and have a named touple)
    # TODO:  What to do if IP doesn't reflect to actual location?
    """
    longitude = ''
    latitude = ''
    place     = []

    def __init__(self):
        pass

    def __str__(self):
        location_str = f'{self.latitude},  {self.longitude}) \
                            Latitude  :   {self.latitude}    \
                            Longitude :   {self.longitude}    \
                            city      :   {self.city}    \
                            country   :   {self.country}'    
        return location_str

    def get_location(self, ip_address = None):
        """
        Returns a touple with lattitute and longitude according to the IP address. It uses the ipinfo library.
        """

        access_token   = 'eba1bfd8659873'
        handler        = ipinfo.getHandler(access_token)
        details        = handler.getDetails(ip_address)
        self.city      = details.city
        self.country   = details.country
        self.longitude = details.longitude
        self.latitude  = details.latitude
        return (self.latitude, self.longitude,)

    def print_location(self):
        """
        Detailed printing of location.
        """
        print(self.latitude + ', ' + self.longitude)
        print('Latitude  : ' + self.latitude)
        print('Longitude : ' + self.longitude)
        print('city      : ' + self.city)
        print('country   : ' + self.country)


class Route(models.Model):
    """
    A class to encapsulate all the information of a route along with some helpful methods.
    """

    def __init__(self, name, style, grade, stars, pitches, url, location):
        self.name     = name
        self.style    = style
        self.grade    = grade
        self.stars    = stars
        self.pitches  = pitches
        self.location = location
        self.url      = url

    def __str__(self):
        # TODO: don't show pitches when it's bouldering
        pad = 20
        route_str  = ' '.join((
            'Name'.ljust(pad), 
            'Grade'.ljust(pad), 
            'Style'.ljust(pad), 
            'Stars'.ljust(pad), 
            'Pitches'.ljust(pad), 
            'MP Link'.ljust(pad),
            '\n'))
        route_str += ' '.join((
            self.name.ljust(pad), 
            self.style.ljust(pad), 
            str(self.grade).ljust(pad), 
            str(self.stars).ljust(pad), 
            str(self.pitches).ljust(pad), 
            self.url.ljust(pad)
            ))
        return route_str

    def is_single_pitch(self):
        return self.pitches == 1

    def is_multi_pitch(self):
        return self.pitches > 1

    def is_five_stars(self):
        return self.stars == 5

    def is_good_route(self):
        return self.stars > 4

    def is_sport(self):
        return self.style == 'sport'

    def print_route_name(self):
        #print((self.name, self.grade))
        print(self)

   # Allow sorting by stars
    def __ge__(self, other):
        return self.stars >= other.stars

    def __le__(self, other):
        return self.stars <= other.stars

    def __gt__(self, other):
        return self.stars > other.stars

    def __lt__(self, other):
        return self.stars < other.stars

    def __eq__(self, other):
        return self.stars == other.stars

    def __ne__(self, other):
        return self.stars != other.stars


if __name__ == '__main__':
    proj_finder = ProjFinder()
    try:
        proj_finder.main()
    except (UserInputError):
        print('Please provide a valid input')
    except (ConnectionError):
        print('Could not connect to Mountain Project API')
