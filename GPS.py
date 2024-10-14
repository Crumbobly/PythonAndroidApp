import time

from kivy.clock import mainthread
from kivy.properties import StringProperty
from kivy.utils import platform
from kivymd.app import MDApp
from WEATHER import in_new_thread

if platform == "android":
    from plyer import gps
else:
    print("No module GPS")


class Gps(MDApp):
    gps_location_string = StringProperty('Not used')
    gps_location_list = []
    is_active = False

    def build(self):
        try:
            gps.configure(on_location=self.on_location)
        except NameError:
            pass

        if platform == "android":
            self.request_android_permissions()

    @in_new_thread
    def wait_gps(self, func, callback):
        if not callback:
            return

        print("wait gps")
        stop = 0

        while not self.gps_location_list:
            time.sleep(0.1)
            stop += 1
            if stop > 50:
                break

        func(self.gps_location_list, callback)

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location_string = 'lat = {lat} \n lon = {lon}'.format(**kwargs)
        self.gps_location_list = [kwargs["lat"], kwargs["lon"]]

    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission

        def callback(permissions, results):
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                self.gps_location_string = "Permissions not granted"
                print("callback. Some permissions refused.")

        request_permissions([Permission.ACCESS_COARSE_LOCATION, Permission.ACCESS_FINE_LOCATION], callback)

    def start(self):
        try:
            self.gps_location_string = "Loading..."
            gps.start(10000, 10)
            self.gps_location_string = "Loading..."
            self.is_active = True
        except NameError:
            self.gps_location_string = "Gps not implemented on your device"

    def stop(self):
        try:
            self.gps_location_string = "GPS not used"
            self.gps_location_list = []
            gps.stop()
            self.is_active = False
        except NameError:
            pass
