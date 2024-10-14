import os

os.environ['KIVY_IMAGE'] = 'pil,sdl2'

from graph import Graph, LinePlot
from kivytransitions.transitions import Wind

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem, TwoLineRightIconListItem, IRightBodyTouch, OneLineRightIconListItem, OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.carousel import MDCarousel
from kivymd.uix.label import MDIcon

from kivy.metrics import dp
from kivy.lang import Builder
from kivy.loader import Loader
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock, mainthread
from kivy.modules import inspector
from kivy.core.window import Window
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.utils import platform

from typing import Callable
from functools import partial
import datetime
import math
import glob

from WEATHER import Weather, in_new_thread
from THEMES import Theming
from GPS import Gps


class RightSwitch(IRightBodyTouch, MDSwitch):
    def __init__(self, **kwargs):
        super(RightSwitch, self).__init__(**kwargs)
        self.theme_thumb_color = 'Custom'
        self.thumb_color = theming.get(self, 'thumb_color', 'settings_switch_color')
        self.thumb_color_down = theming.get(self, 'thumb_color_down', 'base_color')


class RightIcon(IRightBodyTouch, MDIconButton):
    def __init__(self, **kwargs):
        super(RightIcon, self).__init__(**kwargs)
        self.theme_text_color = "Custom"
        self.text_color = theming.get(self, 'text_color', 'base_color')
        self.icon = "pine-tree-box"


class ListItemWithSwitch(BaseListItem):
    def __init__(self, **kwargs):
        super(ListItemWithSwitch, self).__init__(**kwargs)
        self.divider = None
        self._no_ripple_effect = True


class OneLineListItemWithSwitch(ListItemWithSwitch, OneLineRightIconListItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_text_color = 'Custom'
        self.text_color = theming.get(self, "text_color", 'settings_and_dialog_text_color')
        self.height = "48dp"


class TwoLineListItemWithSwitch(ListItemWithSwitch, TwoLineRightIconListItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_text_color = 'Custom'
        self.secondary_theme_text_color = 'Custom'
        self.text_color = theming.get(self, "text_color", 'settings_and_dialog_text_color')
        self.secondary_text_color = theming.get(self, "secondary_text_color", 'settings_and_dialog_text_color_opacity')
        self.height = "64dp"


class MyNoneTouchCarousel(MDCarousel):
    def on_touch_down(self, touch):
        self.children[0].on_touch_down(touch)


class MyCarousel(MDCarousel):
    cord_x = []

    def change_slide(self):

        if self.cord_x[0] - self.cord_x[-1] > self.width / 4 and self.next_slide:
            self.load_next()
            MyApp.anim_change_opacity(screens[0].ids.first_slide, .2, duration=.2)
            MyApp.anim_change_opacity(screens[0].ids.second_slide, 1, duration=.2)

        elif self.cord_x[0] - self.cord_x[-1] < -self.width / 4 and self.previous_slide:
            self.load_previous()
            MyApp.anim_change_opacity(screens[0].ids.second_slide, .2, duration=.2)
            MyApp.anim_change_opacity(screens[0].ids.first_slide, 1, duration=.2)

        self.cord_x.clear()

    def on_touch_down(self, touch):
        if self.check_touch(touch.x, touch.y):
            self.cord_x.append(touch.x)

    def on_touch_up(self, touch):
        if self.check_touch(touch.x, touch.y):
            self.cord_x.append(touch.x)
            self.change_slide()

    def check_touch(self, x, y):
        return self.center_x + self.width / 2 > x > self.center_x - self.width / 2 and self.center_y + self.height / 2 > y > self.center_y - self.height / 2


class MD3Card(MDCard):
    text = StringProperty()
    icon = StringProperty()
    max = StringProperty()
    min = StringProperty()


class DialogContent(MDBoxLayout):
    def __draw_shadow__(self, origin, end, context=None):
        pass

    information_text = StringProperty()
    license_text = StringProperty()

    def __init__(self, close_function: Callable, **kwargs):
        super(DialogContent, self).__init__(**kwargs)
        self.close_dialog = close_function
        self.information_text = license_json["information"]["text"]
        self.license_text = license_json["license"]["text"]

    def scroll_dialog(self, y: float):
        if y != 1 and not license_json["agreement"]["taken"]:
            self.ids.btn1.disabled = False
            self.ids.btn2.disabled = False


class MyDialog(MDDialog):
    def __init__(self, **kwargs):
        super(MyDialog, self).__init__(**kwargs)
        self.children[0].remove_widget(self.children[0].children[0])
        self.children[0].remove_widget(self.children[0].children[0])
        self.children[0].size_hint = [1, 1]
        self.children[0].children[0].size_hint = [1, 1]
        self.md_bg_color = theming.get(self, "md_bg_color", "background_color")

        title = self.children[0].children[-1]
        title.color = theming.get(title, "color", "settings_and_dialog_text_color")


class ItemConfirm(OneLineAvatarIconListItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.divider = None
        self.ripple_alpha = 0

        text = self.children[2].children[2]
        text.color = theming.get(text, "color", "settings_and_dialog_text_color")

    @staticmethod
    def set_icon(instance_check, parent_item):
        if settings_json["Theme"]["name"] != parent_item.text:
            theming.change_theme(theming.themes_dictionary[parent_item.text])
            settings_json.put("Theme", name=parent_item.text)

        instance_check.active = True
        instance_check.color = theming.theme_kit["base_color"]
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False
            if check.font_size != 24:
                check.font_size = dp(24)


class Settings(Screen):
    dialog = None
    theme_change_dialog = None

    # Переход на основной экран
    def go_to_main(self):
        if self.call_change_settings():
            screens[0].set_NA()
            weather.reset_labels()

            if settings_json["Gps"]["status"] == "Used":
                gps.start()
                gps.wait_gps(weather.call_weather, screens[0].update_all)
            else:
                weather.call_weather(gps.gps_location_list, screens[0].update_all)

        self.parent.switch_to(screens[0])

    def call_change_settings(self):
        old_file = [settings_json["App launch"]["login"],
                    settings_json["APPID"]["text"],
                    settings_json["City"]["text"],
                    settings_json["Country tag"]["text"],
                    settings_json["Timezone"]["offset"],
                    settings_json["Gps"]["status"]
                    ]

        self.change_settings(
            self.ids.appid_switch1.active,
            self.ids.gps_switch1.active,
            self.ids.gps_switch3.active,
            self.ids.timezone_switch1.active,
            self.ids.field_appid_settings.text,
            self.ids.field_gps1_settings.text,
            self.ids.field_gps2_settings.text,
            self.ids.field_gps3_settings.text,
            self.ids.field_gps4_settings.text
        )

        new_file = [settings_json["App launch"]["login"],
                    settings_json["APPID"]["text"],
                    settings_json["City"]["text"],
                    settings_json["Country tag"]["text"],
                    settings_json["Timezone"]["offset"],
                    settings_json["Gps"]["status"]
                    ]

        return old_file != new_file

    # Изменение файла настроек
    def change_settings(self, sw1: bool, sw2: bool, sw3: bool, sw4: bool, *text):

        if sw1 and text[0] != '':
            settings_json.put('APPID', text=text[0])
        else:
            settings_json.put('APPID', text='61d93d0e4c9b99f0973fdc5237b1872f')
            self.ids.appid_switch2.active = True

        if sw2 and text[1] != '' and text[2] != '':
            settings_json.put('City', text=text[1])
            settings_json.put('Country tag', text=text[2])
            settings_json.put('Gps', status='Not Used', lat=text[3], lon=text[4])

        elif sw3 and text[3] != '' and text[4] != '':
            settings_json.put("Gps", status='My', lat=text[3], lon=text[4])

        else:
            settings_json.put('Gps', status='Used', lat=text[3], lon=text[4])
            self.ids.gps_switch2.active = True

        if sw4:
            settings_json.put('Timezone', offset=weather.get_timezone())
            self.ids.timezone_switch1.active = True
        else:
            settings_json.put('Timezone', offset="auto")

    # Создание и вызов диалогового окна
    #     def create_dialog(self, stop_func):
    def create_dialog(self):
        # Создание диалогового окна
        if not self.dialog:
            self.dialog = MDDialog(
                title="Reset all application settings?",
                text="Reset all settings and remove all files associated with this application",
                radius=(15, 15, 15, 15),

                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        theme_text_color="Custom",
                        on_release=self.close_dialog
                    ),
                    MDRectangleFlatButton(
                        text="Yes, Reset",
                        on_press=self.execute_dialog,
                        # on_release=stop_func,
                    ),
                ]
            )
            btn1 = self.dialog.buttons[0]
            btn1.text_color = theming.get(btn1, "text_color", "settings_and_dialog_text_color")
            btn2 = self.dialog.buttons[1]
            btn2.text_color = theming.get(btn2, "text_color", "settings_and_dialog_text_color")
            btn2.line_color = theming.get(btn2, "line_color", "base_color")

            title = self.dialog.children[0].children[3]
            title.color = theming.get(title, "color", "settings_and_dialog_text_color_opacity")

            text = self.dialog.children[0].children[5]
            text.color = theming.get(text, "color", "settings_and_dialog_text_color")

            self.dialog.md_bg_color = theming.get(self.dialog, "md_bg_color", "background_color")
        self.dialog.open()

    def create_theme_change_dialog(self):
        if not self.theme_change_dialog:
            self.theme_change_dialog = MyDialog(
                title="Application themes",
                radius=(15, 15, 15, 15),
                size_hint=[.9, .6],
                type="confirmation",
                items=[
                    ItemConfirm(text="Dynamic Theme"),
                    ItemConfirm(text="Theme 1"),
                    ItemConfirm(text="Theme 2"),
                    ItemConfirm(text="Theme 3"),
                    ItemConfirm(text="Theme 4"),
                    ItemConfirm(text="Theme 5"),
                    ItemConfirm(text="Theme 6"),
                    ItemConfirm(text="Theme 7"),
                    ItemConfirm(text="Theme 8"),
                ],
            )

            for item in self.theme_change_dialog.items:
                if item.text == settings_json["Theme"]["name"]:
                    ItemConfirm.set_icon(item.children[1].children[0], item)
                    break

        self.theme_change_dialog.open()

    # Закрытие диалогового окна
    def close_dialog(self, *obj):
        self.dialog.dismiss()

    # Исполнение диалогового окна
    def execute_dialog(self, *obj):
        self.dialog.dismiss()
        self.parent.switch_to(screens[1])
        screens[0].set_NA()
        settings_json.put("App launch", login=False)
        gps.stop()

    @staticmethod
    def switch_touch(*pressed_switch_fields):
        for field in pressed_switch_fields:
            if field.text == '':
                field.text = ' '

            if field.text == ' ':
                field.text = ''


class Application(Screen):
    toolbar_title = StringProperty()
    day = -1
    weather_dict = dict()

    def go_to_settings(self):
        self.manager.transition = Wind(duration=.6, direction="rl")
        self.parent.switch_to(screens[2])
        self.manager.transition = Wind(duration=.6, direction="lr")

    def update_title(self):
        if weather.status in ("Used", "Not Used", "My") and len(weather.place) == 3:
            self.toolbar_title = weather.place[0] + ", " + weather.place[2].upper()
        else:
            self.toolbar_title = "Not defined"

    def update_all(self, new_dict: dict):
        self.day = -1
        self.weather_dict = new_dict
        print(self.weather_dict, self.weather_dict.get("timezone"))
        self.update_main_info()
        self.daily_card_update()
        self.map_update()
        self.set_day(0)

    def map_update(self):
        if gps.is_active:
            lat = gps.gps_location_list[0]
            lon = gps.gps_location_list[1]

        else:
            new_lat = self.weather_dict.get("latitude", 0)
            new_lon = self.weather_dict.get("longitude", 0)
            lat = new_lat if new_lat else 0
            lon = new_lon if new_lon else 0

        screens[0].ids.map.lat = lat
        screens[0].ids.map.lon = lon
        screens[0].ids.map.zoom = 12
        screens[0].ids.map.center_on(lat, lon)

    def daily_card_update(self):
        for i in range(len(screens[0].ids.days.children)):
            if self.weather_dict.get("days"):
                day = datetime.datetime.strptime(self.weather_dict.get("days")[i], "%Y-%m-%d")
                day_num = datetime.datetime.strftime(day, "%d")
                day_str = datetime.datetime.strftime(day, "%A")[:3].upper()
            else:
                day_num = "N/A"
                day_str = "N/A"

            screens[0].ids.days.children[6 - i].text = f"{day_str} [b]{day_num}[/b]"
            screens[0].ids.days.children[6 - i].max = self.weather_dict['temperature_max'][i]
            screens[0].ids.days.children[6 - i].min = self.weather_dict['temperature_min'][i]
            screens[0].ids.days.children[6 - i].icon = self.weather_dict["weathercode_daily"][i]

    def delete_graph(self):
        plots = self.ids.rain.children[0].plots
        for i in plots:
            self.ids.rain.children[0].remove_plot(i)

    def set_NA(self):
        self.delete_graph()

        self.ids.nowrealtemp.text = "N/A"
        self.ids.nowfeeltemp.text = "Feels like N/A"

        self.ids.maxtemp.text = "N/A°C\n"
        self.ids.mintemp.text = "N/A°C\n"
        self.ids.sunrise.text = "N/A\n"
        self.ids.sunset.text = "N/A\n"
        self.ids.avgwindspeed.text = "N/A"
        self.ids.maxwindspeed.text = "N/A"
        self.ids.maxwindgust.text = "N/A"
        self.ids.winddirrection.text = "N/A"
        self.ids.precsum.text = "N/A"

        for i in range(24):
            screens[0].ids.hours.children[95 - i].text = f"{i}:00"
            screens[0].ids.hours.children[71 - i].icon = "icons/NA.png"
            screens[0].ids.hours.children[47 - i].text = "N/A"
            screens[0].ids.hours.children[23 - i].text = "N/A"

        for i in range(7):
            screens[0].ids.days.children[i].text = "N/A [b]N/A[/b]"
            screens[0].ids.days.children[i].max = "N/A"
            screens[0].ids.days.children[i].min = "N/A"
            screens[0].ids.days.children[i].icon = "icons/NA.png"

    def set_day(self, day, *args):
        if self.day == day:
            return

        def daily_label_update():
            max_temp = self.weather_dict.get("temperature_max")[day]
            min_temp = self.weather_dict.get("temperature_min")[day]
            sunrise = self.weather_dict.get("sunrise")[day]
            sunset = self.weather_dict.get("sunset")[day]
            average_windspeed = self.weather_dict.get("average_windspeed")[day]
            max_windspeed = self.weather_dict.get("windspeed_max")[day]
            max_windgusts = self.weather_dict.get("windgusts_max")[day]
            winddirection = self.weather_dict.get("winddirection_dominant")[day]
            precipitation_sum = self.weather_dict.get("precipitation_sum")[day]

            self.ids.maxtemp.text = f"{max_temp}°C\n"
            self.ids.mintemp.text = f"{min_temp}°C\n"
            self.ids.sunrise.text = f"{sunrise}\n"
            self.ids.sunset.text = f"{sunset}\n"
            self.ids.avgwindspeed.text = f"{average_windspeed}"
            self.ids.maxwindspeed.text = f"{max_windspeed}"
            self.ids.maxwindgust.text = f"{max_windgusts}"
            self.ids.winddirrection.text = f"{winddirection}"
            self.ids.precsum.text = f"{precipitation_sum}"

        @in_new_thread
        def hourly_info_update():
            for i in range(24):
                screens[0].ids.hours.children[95 - i].text = f"{i}:00"
                screens[0].ids.hours.children[71 - i].icon = self.weather_dict.get("weathercode_hourly")[i + 23 * day]
                screens[0].ids.hours.children[47 - i].text = self.weather_dict.get("relativehumidity")[i + 23 * day]
                screens[0].ids.hours.children[23 - i].text = self.weather_dict.get("temperature")[i + 23 * day]

        @mainthread
        def graph_update():
            plot_rain = LinePlot(line_width=2, color=(245 / 255, 238 / 255, 228 / 255, 1))
            max_roundup_value = 1

            if self.weather_dict.get("precipitation"):
                float_perc = [float(i) for i in self.weather_dict.get("precipitation")][day * 24:(day + 1) * 24]
                max_value = max(float_perc)
                max_roundup_value = math.ceil(max_value) if math.ceil(max_value) != 0 else 1
                plot_rain.points = [(i, float_perc[i]) for i in range(24)]

            self.delete_graph()
            screens[0].ids.rain.children[0].ymax = max_roundup_value
            screens[0].ids.rain.children[0].y_ticks_major = max_roundup_value
            screens[0].ids.rain.children[0].add_plot(plot_rain)

        daily_label_update()
        hourly_info_update()
        graph_update()
        self.day = day

    def update_main_info(self):

        def lastupdate_update():
            date = datetime.datetime.now()
            h = date.hour
            m = date.minute

            if h < 10:
                h = "0" + str(h)
            if m < 10:
                m = "0" + str(m)

            self.ids.lastupdate.text = f" last update {h}:{m}\n"

        def main_label_update():
            if self.weather_dict.get("current_time").year != 1000:
                date = self.weather_dict.get("current_time")
                self.ids.nowdate.text = f"Today is {date.day}.{date.month}"
                hour = date.hour
            else:
                hour = 0
                self.ids.nowdate.text = "Today is N/A"

            real_temp = self.weather_dict.get("temperature")[hour]
            feel_temp = self.weather_dict.get("apparent_temperature")[hour]
            self.ids.nowrealtemp.text = f"{real_temp}"
            self.ids.nowfeeltemp.text = f"Feels like {feel_temp}"

        lastupdate_update()
        main_label_update()


class LogInScreen(Screen):
    dialog = None

    # Переход на основной экран
    def go_to_main(self):
        self.parent.switch_to(screens[0])

        if self.ids.latlon.active:
            gps.start()
            gps.wait_gps(weather.call_weather, screens[0].update_all)
        else:
            weather.call_weather(gps.gps_location_list, screens[0].update_all)

    # Когда трогаем чекбокс.
    def checkbox_touch(self, name: str, is_active: bool):
        if name == 'appid':
            self.ids.field_appid.disabled = is_active
        if name == 'latlon':
            self.ids.field_ctag.disabled = is_active
            self.ids.field_city.disabled = is_active

    def first_open(self) -> bool:
        # Запись с текстовых полей первого экрана в файл настроек.
        settings_json.put('APPID', text='61d93d0e4c9b99f0973fdc5237b1872f' if self.ids.appid.active else self.ids.field_appid.text)
        settings_json.put('City', text='' if self.ids.latlon.active else self.ids.field_ctag.text)
        settings_json.put('Country tag', text='' if self.ids.latlon.active else self.ids.field_city.text)
        settings_json.put('Gps', status='Used' if self.ids.latlon.active else "Not Used", lat="", lon="")

        login_correct = (settings_json['APPID']['text'] != '' and
                         ((settings_json['City']['text'] != '' and settings_json['Country tag']['text'] != '') or settings_json['Gps']['status'] == 'Used'))

        settings_json.put('App launch', login=login_correct)
        return login_correct

    # создание диалогового окна соглашения
    def create_agreement(self):
        if not self.dialog:
            self.dialog = MyDialog(
                size_hint=[.9, .9],
                type="custom",
                content_cls=DialogContent(self.close_agreement),
                auto_dismiss=False,
            )
            self.dialog.md_bg_color = theming.get(self, "md_bg_color", "background_color")

            if license_json["agreement"]["taken"]:
                self.close_agreement()

        self.dialog.open()

    # закрытие диалогового окна соглашения
    def close_agreement(self):
        self.dialog.children[0].children[0].children[0].remove_widget(self.dialog.children[0].children[0].children[0].children[0])
        self.dialog.children[0].children[0].children[0].ids.agree_lbl.text = ''

        self.dialog.children[0].add_widget(
            MDRectangleFlatButton(
                pos_hint={'center_x': .5},
                text='Close',
            )
        )
        btn = self.dialog.children[0].children[0]
        btn.text_color = theming.get(btn, "text_color", "settings_and_dialog_text_color")
        btn.line_color = theming.get(btn, "line_color", "base_color")
        btn.bind(on_press=self.dialog.dismiss)

        license_json.put("agreement", taken=True)
        self.dialog.auto_dismiss = True
        self.dialog.dismiss()


class HelloScreen(Screen):
    cord_x = []

    # Проверка наличия свапа по экрану и переход к логин-экрану
    def go_to_login(self):
        if self.cord_x[0] - self.cord_x[-1] > self.width / 3:
            self.parent.switch_to(screens[3])
            if not license_json["agreement"]["taken"]:
                screens[3].create_agreement()

        self.cord_x.clear()

    # Обработка касания (когда только касаемся экрана)
    def on_touch_down(self, touch: MouseMotionEvent):
        self.cord_x.append(touch.x)

    # Обработка касания (когда отпускаем экран)
    def on_touch_up(self, touch: MouseMotionEvent):
        self.cord_x.append(touch.x)
        self.go_to_login()


class MyApp(MDApp):
    checks = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.theming = theming
        self.weather = weather
        self.gps = gps

        self.graph_rain = Graph(
            draw_border=False,
            xmin=0,
            xmax=23,
            x_ticks_major=6, x_ticks_minor=6,
            y_grid_label=True, x_grid_label=True,
            x_grid=True, y_grid=True,
            padding=5,
        )
        self.graph_rain.tick_color = theming.get(self.graph_rain, "tick_color", "base_color")
        self.graph_rain.label_options = {'color': theming.get(self.graph_rain, "label_options", "MD3CARD_text_color")}

        Builder.load_file("1_2.kv")

    def build(self) -> ScreenManager:
        global screens
        self.title = "MYWeather"
        self.theme_cls.primary_palette = theming.get(self.theme_cls, "primary_palette", "palette")
        self.sm.transition = Wind(duration=.6, direction="lr")

        screens = [Application(name="main"), HelloScreen(name="HelloScreen"), Settings(name="Settings"), LogInScreen(name="LogInScreen")]
        gps.build()
        inspector.create_inspector(Window, screens[1])

        if settings_json["App launch"]["login"]:
            Loader.loading_image = theme_kit['background_image']
            self.start_dynamic_update()
            self.sm.switch_to(screens[0])

        else:
            Loader.loading_image = theme_kit['background_blur_image']
            self.sm.switch_to(screens[1])

        return self.sm

    def map_load_weather(self):
        screens[2].ids.gps_switch3.active = True
        screens[2].ids.field_gps3_settings.text = str(screens[0].ids.map.lat)
        screens[2].ids.field_gps4_settings.text = str(screens[0].ids.map.lon)
        screens[2].call_change_settings()

        self.load_weather()

    @staticmethod
    def add_days_cards():
        for i in range(7):
            locals()[f'day{i}'] = MD3Card(
                text=f"N/A [b]N/A[/b]",
                max="N/A°C",
                min="N/A°C",
                icon="icons/NA.png",
                radius='20sp',
                elevation=0,
                ripple_behavior=True,
            )

            card = locals()[f'day{i}']
            card.md_bg_color = theming.get(card, "md_bg_color", "MD3CARD_color")
            card.bind(on_press=partial(
                screens[0].set_day, i)
            )

            screens[0].ids.days.add_widget(locals()[f'day{i}'])

    @staticmethod
    def add_hourly_cards():
        for i in range(24):
            screens[0].ids.hours.add_widget(Label(text=f"{i}:00", halign="center", color=(1, 1, 1, 1)))

        for _ in range(24):
            screens[0].ids.hours.add_widget(MDIcon(icon="icons/NA.png", size_hint=(None, None), height=dp(60), width=dp(60), halign='center'))

        for _ in range(24):
            screens[0].ids.hours.add_widget(Label(text="N/A", halign="center", color=(1, 1, 1, 1)))

        for _ in range(24):
            screens[0].ids.hours.add_widget(Label(text="N/A", halign="center", color=(1, 1, 1, 1)))

    @staticmethod
    def load_weather():
        if settings_json["Gps"]["status"] == "Used":
            gps.start()
            gps.wait_gps(weather.call_weather, screens[0].update_all)
        else:
            weather.call_weather(gps.gps_location_list, screens[0].update_all)

    @staticmethod
    def reload_weather():
        weather.call_weather(gps.gps_location_list, screens[0].update_all)

    def on_start(self):
        self.add_days_cards()
        self.add_hourly_cards()
        screens[0].ids.rain.add_widget(self.graph_rain)
        theming.change_android_navbar_color()
        self.load_weather()

    def on_stop(self):
        gps.stop()

        for img in glob.iglob(os.path.join('./cache', '*.png')):
            os.remove(img)

        if self.sm.current == 'Settings':
            print('App closing, save settings')
            print(screens[2].ids.gps_switch1.active, screens[2].ids.gps_switch3.active)
            Settings().change_settings(
                screens[2].ids.appid_switch1.active,
                screens[2].ids.gps_switch1.active,
                screens[2].ids.gps_switch3.active,
                screens[2].ids.timezone_switch1.active,
                screens[2].ids.field_appid_settings.text,
                screens[2].ids.field_gps1_settings.text,
                screens[2].ids.field_gps2_settings.text,
                screens[2].ids.field_gps3_settings.text,
                screens[2].ids.field_gps4_settings.text,
            )

    def on_pause(self):
        self.on_stop()
        return True

    def on_resume(self):
        if settings_json["Gps"]["status"] == "Used":
            gps.start()

    @staticmethod
    def anim_change_opacity(widget, new_opacity, duration=.4):
        anim = Animation(opacity=new_opacity, duration=duration)
        anim.start(widget)

    def start_dynamic_update(self):
        print('dynamic update start')
        Clock.schedule_once(self.first_update)
        # self.dynamic_func = [
        #     Clock.schedule_interval(self.check_labels_update, 5),
        #     Clock.schedule_interval(self.check_weather_update, 5)]

    # Запуск функций обновления (один раз)
    def first_update(self, *args):
        # self.check_labels_update()
        # self.check_weather_update()
        self.settings_update()
        screens[0].update_title()

    # Синхронизация switch на экране settings
    def settings_update(self):
        print('settings update')
        app_id = settings_json["APPID"]["text"]
        city = settings_json["City"]["text"]
        c_tag = settings_json["Country tag"]["text"]
        status = settings_json["Gps"]["status"]
        lat = settings_json["Gps"]["lat"]
        lon = settings_json["Gps"]["lon"]
        timezone = settings_json["Timezone"]["offset"]

        if app_id != '' and app_id != "61d93d0e4c9b99f0973fdc5237b1872f":
            screens[2].ids.field_appid_settings.text = app_id
            screens[2].ids.appid_switch1.active = True

        if city != '' and c_tag != '' and status == 'Not Used':
            screens[2].ids.gps_switch1.active = True

        if status == 'Used':
            screens[2].ids.gps_switch2.active = True

        if lat != '' and lon != '' and status == 'My':
            screens[2].ids.gps_switch3.active = True

        if timezone != "auto":
            screens[2].ids.timezone_switch1.active = True

        screens[2].ids.field_gps1_settings.text = city
        screens[2].ids.field_gps2_settings.text = c_tag

        screens[2].ids.field_gps3_settings.text = lat
        screens[2].ids.field_gps4_settings.text = lon


if __name__ == '__main__':
    settings_json = JsonStore('settings.json')
    license_json = JsonStore('license.json')
    screens = list()

    theming = Theming(settings_json)
    theme_kit = theming.theme_kit
    weather = Weather(settings_json)
    gps = Gps()

    MyApp().run()
