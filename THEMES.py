import datetime
from kivy.utils import platform, get_hex_from_color

if platform == "android":
    from android.runnable import run_on_ui_thread
    from jnius import autoclass

    Color = autoclass("android.graphics.Color")
    WindowManager = autoclass('android.view.WindowManager$LayoutParams')
    activity = autoclass('org.kivy.android.PythonActivity').mActivity


# theme_kit = {
#     "background_image": '',
#     "background_blur_image": '',
#     "background_forest": '',
#     "gif": '',
#
#     "background_color": (1.0, 1.0, 1.0, 1.0),         # -фон
#     "base_color": (1.0, 1.0, 1.0, 1.0),               # -основной цвет в соответствие с темой
#     "base_color_opacity": (1.0, 1.0, 1.0, ю5),       # -основной цвет, но прозрачный
#
#     "palette": 'Red',                                    # -тема приложения
#
#     "hello_text_color": (1.0, 1.0, 1.0, 1.0),         # -цвет текста на экране приветствия
#
#     "login_background_color": (1.0, 1.0, 1.0, 1.0),   # -цвет фона на экране входа
#     "login_text_color": (1.0, 1.0, 1.0, 1.0),         # -цвет текста на экране входа
#     "login_btn_line_color": (1.0, 1.0, 1.0, 1.0),     # -цвет линии кнопки на экране входа
#
#     "settings_switch_color": (1.0, 1.0, 1.0, 1.0),            # -цвет переключателей на экране настроек
#     "settings_and_dialog_text_color": (1.0, 1.0, 1.0, 1.0),   # -цвет текста на экране настроек в диалогах
#     "settings_and_dialog_text_color": (1.0, 1.0, 1.0, .5),   # -цвет текста на экране настроек в диалогах, но прозрачный
#
#     "bottom_nav_color": (1.0, 1.0, 1.0, 1.0),            # Цвет навигационной панели
#     "bottom_nav_icon_color": (1.0, 1.0, 1.0, 1.0),       # Цвет иконок навигационной панели
#
#     "toolbar_text_color": (1.0, 1.0, 1.0, 1.0),               # Цвет текста тул-баров
#     "MD3CARD_text_color": (1.0, 1.0, 1.0, 1.0),               # Цвет дневных карточек
#
# }


class Theming:
    def __init__(self, settings_json):
        dt = datetime.datetime.now()
        self.themes_dictionary = {"Theme 1": 1, "Theme 2": 4, "Theme 3": 7, "Theme 4": 10,
                                  "Theme 5": 13, "Theme 6": 16, "Theme 7": 19, "Theme 8": 21,
                                  "Dynamic Theme": dt.hour}

        self.hour = self.themes_dictionary.get(settings_json["Theme"]["name"])
        self.theme_kit = dict()
        self.kivy_object_kit = dict()
        self.defining_theme(self.hour)

    # obj.property_name = Theming.get(obj, property_name, color|image)
    def get(self, obj, property_name, color_or_image):
        if not self.kivy_object_kit.get(color_or_image):
            self.kivy_object_kit[color_or_image] = [(obj, property_name)]
        else:
            self.kivy_object_kit[color_or_image].append((obj, property_name))

        return self.theme_kit[color_or_image]

    @staticmethod
    def android_navbar_color(navbar_color: str):
        @run_on_ui_thread
        def set_color():
            window = activity.getWindow()
            window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)
            window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
            # window.setStatusBarColor(Color.parseColor(statusbar_color))
            window.setNavigationBarColor(Color.parseColor(navbar_color))

        set_color()

    def change_android_navbar_color(self):
        if platform == "android":
            self.android_navbar_color(
                get_hex_from_color(self.theme_kit["bottom_nav_color"][:-1]),
            )

    def defining_theme(self, hour):
        self.theme_kit["gif"] = 'gif/black.gif'
        self.theme_kit["hello_text_color"] = (0, 0, 0, 1)
        self.theme_kit["slider_color"] = (1, 1, 1, 1)
        self.theme_kit["MD3CARD_text_color"] = (245 / 255, 238 / 255, 228 / 255, 1)
        self.theme_kit["MD3CARD_color"] = (245 / 255, 245 / 255, 245 / 255, 0.08)
        self.theme_kit["rounded_layout_color"] = (245 / 255, 245 / 255, 245 / 255, 0.15)

        if hour == 23 or 0 <= hour <= 2:
            self.theme_kit["background_blur_image"] = 'backgrounds_blur/23.jpg'
            self.theme_kit["background_image"] = 'backgrounds/23.jpg'
            self.theme_kit["background_forest"] = 'backgrounds_forest/23.png'
            self.theme_kit["gif"] = 'gif/grey-blue.gif'

            self.theme_kit["palette"] = 'BlueGray'

            self.theme_kit["background_color"] = (79 / 255, 76 / 255, 73 / 255, 1)
            self.theme_kit["base_color"] = (96 / 255, 121 / 255, 135 / 255, 1)

            self.theme_kit["hello_text_color"] = (58 / 255, 67 / 255, 71 / 255, 1)

            self.theme_kit["login_background_color"] = (58 / 255, 67 / 255, 71 / 255, 1)
            self.theme_kit["login_text_color"] = (0, 0, 0, 1)
            self.theme_kit["login_btn_line_color"] = (96 / 255, 121 / 255, 135 / 255, 1)

            self.theme_kit["settings_switch_color"] = (245 / 255, 238 / 255, 228 / 255, 1)
            self.theme_kit["settings_and_dialog_text_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["bottom_nav_color"] = (58 / 255, 67 / 255, 71 / 255, 1)
            self.theme_kit["bottom_nav_icon_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["toolbar_text_color"] = (79 / 255, 76 / 255, 73 / 255, 1)
            self.theme_kit["main_labels_color"] = (162 / 255, 162 / 255, 162 / 255, 1)

        elif 3 <= hour <= 5:
            self.theme_kit["background_blur_image"] = 'backgrounds_blur/3-5.jpg'
            self.theme_kit["background_image"] = 'backgrounds/3-5.jpg'
            self.theme_kit["background_forest"] = 'backgrounds_forest/3-5.png'

            self.theme_kit["palette"] = 'Green'

            self.theme_kit["background_color"] = (81 / 255, 100 / 255, 98 / 255, 1)
            self.theme_kit["base_color"] = (75 / 255, 168 / 255, 84 / 255, 1)

            self.theme_kit["login_background_color"] = (61 / 255, 92 / 255, 80 / 255, 1)
            self.theme_kit["login_text_color"] = (0, 0, 0, 1)
            self.theme_kit["login_btn_line_color"] = (75 / 255, 168 / 255, 84 / 255, 1)

            self.theme_kit["settings_switch_color"] = (245 / 255, 238 / 255, 228 / 255, 1)
            self.theme_kit["settings_and_dialog_text_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["bottom_nav_color"] = (61 / 255, 92 / 255, 80 / 255, 1)
            self.theme_kit["bottom_nav_icon_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["toolbar_text_color"] = (61 / 255, 61 / 255, 61 / 255, 1)
            self.theme_kit["main_labels_color"] = (162 / 255, 162 / 255, 162 / 255, 1)

        elif 6 <= hour <= 8:
            self.theme_kit["background_blur_image"] = 'backgrounds_blur/6-8.jpg'
            self.theme_kit["background_image"] = 'backgrounds/6-8.jpg'
            self.theme_kit["background_forest"] = 'backgrounds_forest/21-22.png'

            self.theme_kit["palette"] = 'Amber'

            self.theme_kit["background_color"] = (96 / 255, 115 / 255, 111 / 255, 1)
            self.theme_kit["base_color"] = (240 / 255, 184 / 255, 9 / 255, 1)

            self.theme_kit["login_background_color"] = (61 / 255, 92 / 255, 80 / 255, 1)
            self.theme_kit["login_text_color"] = (0, 0, 0, 1)
            self.theme_kit["login_btn_line_color"] = (240 / 255, 184 / 255, 9 / 255, 1)

            self.theme_kit["settings_switch_color"] = (245 / 255, 238 / 255, 228 / 255, 1)
            self.theme_kit["settings_and_dialog_text_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["bottom_nav_color"] = (61 / 255, 92 / 255, 80 / 255, 1)
            self.theme_kit["bottom_nav_icon_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["toolbar_text_color"] = (91 / 255, 91 / 255, 91 / 255, 1)
            self.theme_kit["main_labels_color"] = (199 / 255, 209 / 255, 206 / 255, 1)

        elif 9 <= hour <= 11:
            self.theme_kit["background_blur_image"] = 'backgrounds_blur/9-11.jpg'
            self.theme_kit["background_image"] = 'backgrounds/9-11.jpg'
            self.theme_kit["background_forest"] = 'backgrounds_forest/9-11.png'

            self.theme_kit["palette"] = 'Green'

            self.theme_kit["background_color"] = (1, 1, 1, 1)
            self.theme_kit["base_color"] = (76 / 255, 168 / 255, 84 / 255, 1)

            self.theme_kit["login_background_color"] = (76 / 255, 168 / 255, 84 / 255, 1)
            self.theme_kit["login_text_color"] = (0, 0, 0, 1)
            self.theme_kit["login_btn_line_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["settings_switch_color"] = (242 / 255, 242 / 255, 242 / 255, 1)
            self.theme_kit["settings_and_dialog_text_color"] = (61 / 255, 61 / 255, 61 / 255, 1)

            self.theme_kit["bottom_nav_color"] = (242 / 255, 242 / 255, 242 / 255, 1)
            self.theme_kit["bottom_nav_icon_color"] = (71 / 255, 71 / 255, 71 / 255, 1)

            self.theme_kit["toolbar_text_color"] = (61 / 255, 61 / 255, 61 / 255, 1)
            self.theme_kit["main_labels_color"] = (61 / 255, 61 / 255, 61 / 255, 1)

        elif 12 <= hour <= 14:
            self.theme_kit["background_blur_image"] = 'backgrounds_blur/12-14.jpg'
            self.theme_kit["background_image"] = 'backgrounds/12-14.jpg'
            self.theme_kit["background_forest"] = 'backgrounds_forest/12-14.png'

            self.theme_kit["palette"] = 'LightBlue'

            self.theme_kit["background_color"] = (1, 1, 1, 1)
            self.theme_kit["base_color"] = (11 / 255, 164 / 255, 231 / 255, 1)

            self.theme_kit["login_background_color"] = (1, 1, 1, 1)
            self.theme_kit["login_text_color"] = (0, 0, 0, 1)
            self.theme_kit["login_btn_line_color"] = (11 / 255, 164 / 255, 231 / 255, 1)

            self.theme_kit["settings_switch_color"] = (242 / 255, 242 / 255, 242 / 255, 1)
            self.theme_kit["settings_and_dialog_text_color"] = (61 / 255, 61 / 255, 61 / 255, 1)

            self.theme_kit["bottom_nav_color"] = (242 / 255, 242 / 255, 242 / 255, 1)
            self.theme_kit["bottom_nav_icon_color"] = (71 / 255, 71 / 255, 71 / 255, 1)

            self.theme_kit["toolbar_text_color"] = (61 / 255, 61 / 255, 61 / 255, 1)
            self.theme_kit["main_labels_color"] = (61 / 255, 61 / 255, 61 / 255, 1)

            self.theme_kit["MD3CARD_color"] = (61 / 255, 61 / 255, 61 / 255, 0.12)
            self.theme_kit["rounded_layout_color"] = (61 / 255, 61 / 255, 61 / 255, 0.24)
            self.theme_kit["slider_color"] = (0, 0, 0, 1)

        elif 15 <= hour <= 17:
            self.theme_kit["background_blur_image"] = 'backgrounds_blur/15-17.jpg'
            self.theme_kit["background_image"] = 'backgrounds/15-17.jpg'
            self.theme_kit["background_forest"] = 'backgrounds_forest/21-22.png'

            self.theme_kit["palette"] = 'Amber'

            self.theme_kit["background_color"] = (107 / 255, 107 / 255, 107 / 255, 1)
            self.theme_kit["base_color"] = (240 / 255, 184 / 255, 9 / 255, 1)

            self.theme_kit["login_background_color"] = (91 / 255, 91 / 255, 91 / 255, 1)
            self.theme_kit["login_text_color"] = (0, 0, 0, 1)
            self.theme_kit["login_btn_line_color"] = (240 / 255, 184 / 255, 9 / 255, 1)

            self.theme_kit["settings_switch_color"] = (245 / 255, 238 / 255, 228 / 255, 1)
            self.theme_kit["settings_and_dialog_text_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["bottom_nav_color"] = (91 / 255, 91 / 255, 91 / 255, 1)
            self.theme_kit["bottom_nav_icon_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["toolbar_text_color"] = (61 / 255, 61 / 255, 61 / 255, 1)
            self.theme_kit["main_labels_color"] = (61 / 255, 61 / 255, 61 / 255, 1)

            self.theme_kit["MD3CARD_color"] = (61 / 255, 61 / 255, 61 / 255, 0.12)
            self.theme_kit["rounded_layout_color"] = (61 / 255, 61 / 255, 61 / 255, 0.24)
            self.theme_kit["slider_color"] = (0, 0, 0, 1)

        elif 18 <= hour <= 20:
            self.theme_kit["background_blur_image"] = 'backgrounds_blur/18-20.jpg'
            self.theme_kit["background_image"] = 'backgrounds/18-20.jpg'
            self.theme_kit["background_forest"] = 'backgrounds_forest/18-20.png'

            self.theme_kit["palette"] = 'Orange'

            self.theme_kit["background_color"] = (79 / 255, 76 / 255, 73 / 255, 1)
            self.theme_kit["base_color"] = (232 / 255, 119 / 255, 32 / 255, 1)

            self.theme_kit["login_background_color"] = (69 / 255, 62 / 255, 58 / 255, 1)
            self.theme_kit["login_text_color"] = (0, 0, 0, 1)
            self.theme_kit["login_btn_line_color"] = (232 / 255, 119 / 255, 32 / 255, 1)

            self.theme_kit["settings_switch_color"] = (245 / 255, 238 / 255, 228 / 255, 1)
            self.theme_kit["settings_and_dialog_text_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["bottom_nav_color"] = (69 / 255, 62 / 255, 58 / 255, 1)
            self.theme_kit["bottom_nav_icon_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["toolbar_text_color"] = (61 / 255, 61 / 255, 61 / 255, 1)
            self.theme_kit["main_labels_color"] = (61 / 255, 61 / 255, 61 / 255, 1)

            self.theme_kit["MD3CARD_color"] = (61 / 255, 61 / 255, 61 / 255, 0.12)
            self.theme_kit["rounded_layout_color"] = (61 / 255, 61 / 255, 61 / 255, 0.24)
            self.theme_kit["slider_color"] = (0, 0, 0, 1)

        elif 21 <= hour <= 22:
            self.theme_kit["background_blur_image"] = 'backgrounds_blur/21-22.jpg'
            self.theme_kit["background_image"] = 'backgrounds/21-22.jpg'
            self.theme_kit["background_forest"] = 'backgrounds_forest/21-22.png'

            self.theme_kit["palette"] = 'Amber'

            self.theme_kit["background_color"] = (79 / 255, 76 / 255, 73 / 255, 1)
            self.theme_kit["base_color"] = (240 / 255, 184 / 255, 9 / 255, 1)

            self.theme_kit["login_background_color"] = (69 / 255, 62 / 255, 58 / 255, 1)
            self.theme_kit["login_text_color"] = (0, 0, 0, 1)
            self.theme_kit["login_btn_line_color"] = (240 / 255, 184 / 255, 9 / 255, 1)

            self.theme_kit["settings_switch_color"] = (245 / 255, 238 / 255, 228 / 255, 1)
            self.theme_kit["settings_and_dialog_text_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["bottom_nav_color"] = (69 / 255, 62 / 255, 58 / 255, 1)
            self.theme_kit["bottom_nav_icon_color"] = (245 / 255, 238 / 255, 228 / 255, 1)

            self.theme_kit["toolbar_text_color"] = (79 / 255, 76 / 255, 73 / 255, 1)
            self.theme_kit["main_labels_color"] = (162 / 255, 162 / 255, 162 / 255, 1)

        self.theme_kit["base_color_opacity"] = list(self.theme_kit["base_color"])[:-1] + [.5]
        self.theme_kit["settings_and_dialog_text_color_opacity"] = list(self.theme_kit["settings_and_dialog_text_color"])[:-1] + [.55]
        self.theme_kit["background_color_opacity"] = list(self.theme_kit["background_color"])[:-1] + [.6]

    def change_theme(self, hour):
        self.defining_theme(hour)
        self.change_android_navbar_color()

        for key in self.kivy_object_kit.keys():
            for obj in self.kivy_object_kit[key]:
                if obj[1] == "label_options":
                    setattr(obj[0], obj[1], {'color': self.theme_kit[key]})
                else:
                    setattr(obj[0], obj[1], self.theme_kit[key])

                if obj[1] == 'text_color_normal':
                    obj[0].on_resize()
