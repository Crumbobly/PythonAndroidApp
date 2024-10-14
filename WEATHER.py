from datetime import datetime
from suntimes import SunTimes

import threading
import time
import requests
from kivy.properties import ListProperty
from kivymd.app import MDApp


def check_internet(func):
    def wrapper(*args, checks=None):
        if checks is None:
            checks = [None, None]

        try:
            ret = func(*args, checks=checks)
            checks[0] = "Internet access granted"
            return ret

        except requests.exceptions.ConnectionError:
            checks[0] = "No Internet access or sites is not available"
            return []

    return wrapper


def in_new_thread(func):
    def wrapper(*args):
        thread = threading.Thread(target=func, daemon=True, args=args)
        if threading.current_thread().__class__.__name__ == '_MainThread':
            thread.start()
        else:
            thread.run()

    return wrapper


class Geocode:

    def direct_geocode(self, app_id, city, country_tag, checks):
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},,{country_tag}&appid={app_id}"
        res = self.geocode_request(url, country_tag, checks=checks)
        return res[:2]

    def reverse_geocode(self, app_id, lat, lon, checks):
        url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=5&appid={app_id}"
        res = self.geocode_request(url, checks=checks)
        return res[2:]

    @staticmethod
    @check_internet
    def geocode_request(url, required_country_tag=None, checks=None):
        res = requests.get(url)
        json = res.json()

        if not checks:
            checks = [None, None]

        if isinstance(json, dict) and json.get("message") and "Invalid API key" in json.get("message"):
            checks[1] = "Not Defined (Wrong API key)"
            return []

        try:
            lat = json[0].get("lat")
            lon = json[0].get("lon")
            city = json[0].get("name")
            country_tag = json[0].get("country")
            state = json[0].get("state")

            if required_country_tag and country_tag.upper() != required_country_tag.upper():
                raise IndexError
            return [lat, lon, city, state, country_tag]

        except IndexError:
            return []


class ParseWeather:
    def __init__(self, weather_dict: dict):
        self.old_weather_dict = weather_dict
        self.weather_dict = dict()
        self.icons = {0: "icons/0", 1: "icons/1-2", 2: "icons/1-2", 3: "icons/3", 45: "icons/45-48", 48: "icons/45-48", 51: "icons/51-53-55",
                      53: "icons/51-53-55", 55: "icons/51-53-55", 56: "icons/56-57", 57: "icons/56-57", 61: "icons/61-66", 66: "icons/61-66", 63: "icons/63-80",
                      80: "icons/63-80", 65: "icons/65-67-81", 67: "icons/65-67-81", 81: "icons/65-67-81", 71: "icons/71-85", 85: "icons/71-85", 73: "icons/73",
                      75: "icons/75-86", 86: "icons/75-86", 77: "icons/77", 82: "icons/82", 95: "icons/95", 96: "icons/96-99", 99: "icons/96-99",
                      "N/A": "icons/NA"
                      }

        self.parse()

    def parse(self):

        def add_extent(arg: list, extend, err_len=0):
            if arg:
                return [str(i) + str(extend) for i in arg]
            else:
                return ['N/A' for i in range(err_len)]

        def replace_wrong_date(dates: list, lon, lat):
            new_dates = list()

            if not dates:
                return ['N/A' for i in range(7)]

            for i in range(len(dates)):
                try:
                    date = datetime.strptime(dates[i], '%Y-%m-%dT%H:%M')
                    new_dates.append(datetime.strftime(date, "%H:%M"))
                except ValueError:

                    if lon is None or lat is None:
                        polar = SunTimes(0, 0)
                    else:
                        polar = SunTimes(lon, lat)

                    if polar.riseutc(datetime.utcnow()) == "PD":
                        new_dates.append("PD")
                    elif polar.riseutc(datetime.utcnow()) == "PN":
                        new_dates.append("PN")
                    else:
                        new_dates.append("N/A")

            return new_dates

        print(self.old_weather_dict)

        degree = self.old_weather_dict.get("hourly_units", dict()).get("temperature_2m")
        speed = " " + str(self.old_weather_dict.get("hourly_units", dict()).get("windspeed_10m"))
        precipitation = " " + str(self.old_weather_dict.get("hourly_units", dict()).get("precipitation"))

        self.weather_dict["timezone"] = self.old_weather_dict.get("timezone")
        self.weather_dict["current_time"] = datetime.strptime(self.old_weather_dict.get("current_weather", dict()).get("time", "1000-01-01T00:00"), '%Y-%m-%dT%H:%M')
        self.weather_dict["days"] = add_extent(self.old_weather_dict.get("daily", dict()).get("time"), "", err_len=7)

        # polar
        self.weather_dict["latitude"] = self.old_weather_dict.get("latitude")
        self.weather_dict["longitude"] = self.old_weather_dict.get("longitude")

        # hourly list
        self.weather_dict["temperature"] = add_extent(self.old_weather_dict.get("hourly", dict()).get("temperature_2m"), degree, err_len=24)
        self.weather_dict["relativehumidity"] = add_extent(self.old_weather_dict.get("hourly", dict()).get("relativehumidity_2m"), "%", err_len=24)
        self.weather_dict["apparent_temperature"] = add_extent(self.old_weather_dict.get("hourly", dict()).get("apparent_temperature"), degree, err_len=24)
        self.weather_dict["precipitation"] = self.old_weather_dict.get("hourly", dict()).get("precipitation")
        self.weather_dict["windspeed"] = add_extent(self.old_weather_dict.get("hourly", dict()).get("windspeed_10m"), speed, err_len=24)

        # daily list
        self.weather_dict["days"] = self.old_weather_dict.get("daily", dict()).get("time")
        self.weather_dict["temperature_max"] = add_extent(self.old_weather_dict.get("daily", dict()).get("temperature_2m_max"), "", err_len=7)
        self.weather_dict["temperature_min"] = add_extent(self.old_weather_dict.get("daily", dict()).get("temperature_2m_min"), "", err_len=7)

        self.weather_dict["sunrise"] = replace_wrong_date(
            self.old_weather_dict.get("daily", dict()).get("sunrise", list()),
            self.weather_dict["longitude"],
            self.weather_dict["latitude"]
        )
        self.weather_dict["sunset"] = replace_wrong_date(
            self.old_weather_dict.get("daily", dict()).get("sunset", list()),
            self.weather_dict["longitude"],
            self.weather_dict["latitude"]
        )

        self.weather_dict["precipitation_sum"] = add_extent(self.old_weather_dict.get("daily", dict()).get("precipitation_sum"), precipitation, err_len=7)
        self.weather_dict["windspeed_max"] = add_extent(self.old_weather_dict.get("daily", dict()).get("windspeed_10m_max"), speed, err_len=7)
        self.weather_dict["windgusts_max"] = add_extent(self.old_weather_dict.get("daily", dict()).get("windgusts_10m_max"), speed, err_len=7)

        # hourly list
        self.weather_dict["weathercode_hourly"] = self.calculate_icon_hourly(
            self.old_weather_dict.get("hourly", dict()).get("weathercode", list()),
            self.weather_dict["sunrise"],
            self.weather_dict["sunset"]
        )

        self.weather_dict["average_windspeed"] = add_extent(
            self.calculate_avg_windspeed(self.old_weather_dict.get("hourly", dict()).get("windspeed_10m")), speed, err_len=24
        )

        # daily list
        daily = self.old_weather_dict.get("daily", dict()).get("weathercode", ["N/A" for _ in range(7)])
        self.weather_dict["weathercode_daily"] = add_extent([self.icons.get(daily[i]) for i in range(len(daily))], ".png", err_len=7)

        self.weather_dict["winddirection_dominant"] = add_extent(
            self.calculate_string_winddirection(self.old_weather_dict.get("daily", dict()).get("winddirection_10m_dominant", list())), "°", err_len=7
        )

    def get_day_info(self, day: int):
        # day 1..7
        day_dict = dict()
        for k, v in self.weather_dict.items():
            if len(v) == 7:
                day_dict[str(k)] = v[day]
            elif len(v) == 7 * 24:
                day_dict[str(k)] = v[(day - 1) * 24:day * 24]
            else:
                day_dict[str(k)] = v

        return day_dict

    def calculate_icon_hourly(self, weathercode: list, sunrise: list, sunset: list):
        if self.weather_dict["longitude"] is None or self.weather_dict["latitude"] is None:
            polar = SunTimes(0, 0)
        else:
            polar = SunTimes(self.weather_dict["longitude"], self.weather_dict["latitude"])
        new_weathercode = list()

        def is_day(sunrise_str, sunset_str, now):
            # don't forget about polar day and polar night
            if polar.riseutc(datetime.utcnow()) == "PD":
                return True
            elif polar.riseutc(datetime.utcnow()) == "PN":
                return False

            sunrise_hour = datetime.strptime(sunrise_str, '%H:%M').hour
            sunset_hour = datetime.strptime(sunset_str, '%H:%M').hour

            # 23:00 6:00    3:00   23-24<x<6
            # 1:00 8:00     5:00   1<x<8
            # 19:00 2:00    23:00  19<x<2+24

            return not (now >= sunset_hour or now <= sunrise_hour)

        now_hour = 0
        for i in range(len(weathercode)):
            if now_hour == 24:
                now_hour = 0

            if weathercode[i] == 0 or weathercode[i] == 1 or weathercode[i] == 2:
                if not is_day(sunrise[i//24], sunset[i//24], now_hour):
                    new_weathercode.append(self.icons.get(weathercode[i]) + "n.png")
                    now_hour += 1
                    continue

            new_weathercode.append(self.icons.get(weathercode[i]) + ".png")
            now_hour += 1

        return new_weathercode if new_weathercode else ["icons/NA.png" for _ in range(24)]

    @staticmethod
    def calculate_avg_windspeed(wind: list):
        if not wind:
            return None

        # len(wind) = 24*7 (by 7 days)
        new_wind = list()

        for i in range(1, 8):
            arr = wind[(i - 1) * 24:i * 24]
            new_wind.append("{0:.1f}".format(sum(arr) / len(arr)))

        # len(new_wind) = 7
        return new_wind

    @staticmethod
    def calculate_string_winddirection(dominant_winddirection: list) -> list:
        new_directions = list()
        string_directions = {0: "N", 22.5: "NEE", 45: "NE", 67.5: "ENE",
                             90: "E", 112.5: "ESE", 135: "SE", 157.5: "SSE",
                             180: "S", 202.5: "SSW", 225: "SW", 247.5: "WSW",
                             270: "W", 292.5: "WNW", 315: "NW", 337.5: "NNW",
                             360: "N"
                             }

        for i in range(len(dominant_winddirection)):
            for k, v in string_directions.items():
                if k - 11.25 < dominant_winddirection[i] < k + 11.25:
                    new_directions.append(v + " " + str(dominant_winddirection[i]))

        return new_directions


class Weather(MDApp, Geocode):
    # internet, place
    checks = ListProperty(["Not used", "Loading..."])

    def __init__(self, settings_json, **kwargs):
        super().__init__(**kwargs)
        self.settings_json = settings_json

        self.city = settings_json["City"]["text"]
        self.c_tag = settings_json["Country tag"]["text"]
        self.app_id = settings_json["APPID"]["text"]
        self.status = settings_json["Gps"]["status"]
        self.timezone = settings_json["Timezone"]["offset"]

        self.latlon = []
        self.place = []

        self.offset_m = None
        self.offset_h = None
        self.offset_update()

    def reset_labels(self):
        self.checks = ["Not Used", "Loading..."]

    def get_timezone(self):
        timezones = {0: "GMT",
                     1: "CET", -1: "Atlantic/Azores",
                     2: "CAT", -2: "Atlantic/South_Georgia",
                     3: "EAT", -3: "Atlantic/Stanley",
                     4: "Asia/Dubai", -4: "Brazil/West",
                     5: "Asia/Ashgabat", -5: "America/Panama",
                     6: "Asia/Urumqi", -6: "America/Costa_Rica",
                     7: "Asia/Bangkok", -7: "America/Creston",
                     8: "Asia/Shanghai", -8: "America/Ensenada",
                     9: "JST", -9: "America/Anchorage",
                     10: "Pacific/Port_Moresby", -10: "America/Adak",
                     11: "Australia/Sydney", -11: "Pacific/Midway",
                     12: "Pacific/Kwajalein",
                     13: "Pacific/Auckland",
                     14: "Pacific/Kiritimati",
                     }

        return timezones.get(self.offset_h)

    def offset_update(self):
        offset_h = -time.timezone / 3600
        self.offset_h = round(offset_h - 0.01)
        self.offset_m = int((offset_h - self.offset_h) * 60)

    def latlon_update(self, gps_latlon=()):
        if self.status == "My":
            self.latlon = [self.settings_json["Gps"]["lat"], self.settings_json["Gps"]["lon"]]

        elif self.status == "Not Used":
            self.latlon = self.direct_geocode(self.app_id, self.city, self.c_tag, self.checks)

        else:
            self.latlon = gps_latlon

    def place_update(self):
        if self.latlon:
            self.place = self.reverse_geocode(self.app_id, self.latlon[0], self.latlon[1], self.checks)
            place = ", ".join(str(i) for i in self.place if i is not None)
            if place:
                self.checks[1] = place
                return

        if self.checks[1] != "Not Defined (Wrong API key)":
            self.checks[1] = "Not Defined "

    @staticmethod
    def create_url(latlon, timezone):
        return "https://api.open-meteo.com/v1/forecast?" \
               f"latitude={latlon[0]}&longitude={latlon[1]}" \
               "&" \
               "hourly=temperature_2m," \
               "relativehumidity_2m," \
               "apparent_temperature," \
               "precipitation," \
               "weathercode," \
               "windspeed_10m" \
               "&" \
               "daily=weathercode," \
               "temperature_2m_max," \
               "temperature_2m_min," \
               "sunrise," \
               "sunset," \
               "precipitation_sum," \
               "windspeed_10m_max," \
               "windgusts_10m_max," \
               "winddirection_10m_dominant" \
               "&" \
               "current_weather=true"\
               "&" \
               "windspeed_unit=ms" \
               "&" \
               f"timezone={timezone}"

    @in_new_thread
    def call_weather(self, gps_latlon, callback):
        self.status = self.settings_json["Gps"]["status"]
        self.app_id = self.settings_json["APPID"]["text"]
        self.city = self.settings_json["City"]["text"]
        self.c_tag = self.settings_json["Country tag"]["text"]
        self.timezone = self.settings_json["Timezone"]["offset"]
        self.latlon_update(gps_latlon)
        self.place_update()
        self.offset_update()

        if self.latlon:
            callback(ParseWeather(self.get_weather()).weather_dict)

        else:
            callback(ParseWeather(dict()).weather_dict)

    def get_weather(self, checks=None) -> dict:
        if self.latlon:
            try:
                url = self.create_url(self.latlon, self.timezone)
                res = requests.get(url)
                json = res.json()

                print(url)
                print(self.place, json.get("latitude"), json.get("longitude"), "timezone: ", json.get("timezone"))
                return json

            except requests.exceptions.ConnectionError:
                pass

        return {}


if __name__ == "__main__":
    from kivy.storage.jsonstore import JsonStore

    weather = Weather(JsonStore('settings.json'))
    weather.get_weather((40, 50))
