from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView


markers = {
    'Пинск': (52.1229, 26.0951),
    'Ласицк': (51.929840, 26.291353),
    'Вишевичи': (52.133496, 26.142502),
    'Молотковичи': (52.118612, 25.922504),
    'Валище': (52.397116, 25.940830),
    'Морозовичи': (52.037912, 26.278516),
    'Большие Диковичи': (51.9975, 26.0967),
    'Дубой': (52.030566, 26.862825),
    'Ольшанка': (52.304464, 25.878361),
    'Сернички': (52.058727,  26.253273),
    'Пинковичи': (52.142683, 26.164771),
    'Почапово': (52.151310, 26.202384),
    'Мерчицы': (52.261865,  25.940839),
    'Хойно': (51.963332, 26.042591),
    'Лопатино': (52.019965, 26.330277),
    'Ковнятин': (52.331972, 26.035252),
    'Местковичи': (52.024914, 26.087444),
    'Паре': (51.898108, 26.135926),
    'Житковичи': (52.216941, 27.854853),
    'Охово': (52.191420,  25.915444),
    'Доброславка': (52.402375, 26.241281),
    'Логишин': (52.334388, 25.991001),
    'Площево': (52.115349, 26.415931),
    'Каллауровичи': (52.084673, 26.501720),
    'Берёзовичи': (52.158073, 25.866710),
    'Камень': (52.325153, 26.375327),
    'Сошно': (52.240016, 26.353022)
}

info_texts = {
    'Пинск': 'Пинск — искомый город',
    'Ласицк': 'Ласицк — деревеня.',
    # остальной текст...
}


class ImageButton(ButtonBehavior, Image):
    pass


class ColoredBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class RoundedButton(Button):
    def __init__(self, radius=15, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius])
        self.bind(pos=self._update_rect, size=self._update_rect, background_color=self._update_color)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_color(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*value)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius])


class LabeledMapMarker(MapMarkerPopup):
    def __init__(self, lat, lon, text, **kwargs):
        super().__init__(lat=lat, lon=lon, **kwargs)
        self.source = "marker_icon.PNG"
        self.popup_size = (150, 50)
        label = Label(
            text=text,
            halign='center',
            valign='middle',
            text_size=self.popup_size,
            color=(0, 0, 0, 1),
            markup=True,
        )
        self.add_widget(label)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        bg = Image(source='menu_icon.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(bg)

        label_text = 'Добро пожаловать в приложение'
        label = Label(
            text=label_text,
            font_size='20sp',
            color=(0, 0, 0, 1),
            size_hint=(0.9, None),
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5, 'top': 0.95})
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size) or setattr(inst, 'height', inst.texture_size[1]))
        layout.add_widget(label)

        label2_text = '"Назвы валошак у гаворках Піншчыны"'
        label2 = Label(
            text=label2_text,
            font_size='20sp',
            color=(0, 0, 0, 1),
            size_hint=(0.9, None),
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5, 'top': 0.9})
        label2.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size) or setattr(inst, 'height', inst.texture_size[1]))
        layout.add_widget(label2)

        enter_button = Button(
            text="Вход на карту",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            pos_hint={'x': 0, 'y': 0})
        enter_button.bind(on_press=self.go_to_map)
        layout.add_widget(enter_button)

        self.add_widget(layout)

    def go_to_map(self, instance):
        self.manager.current = 'map'


class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        self.black_bar = Widget(size_hint=(None, 1), width=30, pos=(0, 0))
        with self.black_bar.canvas:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(pos=self.black_bar.pos, size=self.black_bar.size)
        self.black_bar.bind(pos=self._update_rect, size=self._update_rect)
        self.layout.add_widget(self.black_bar)

        self.mapview = MapView(zoom=10, lat=markers['Пинск'][0], lon=markers['Пинск'][1], size_hint=(None, 1))
        self.mapview.size = (self.width - 30, self.height)
        self.mapview.pos = (30, 0)
        self.mapview.center_on(markers['Пинск'][0], markers['Пинск'][1])
        self.layout.add_widget(self.mapview)
        self.bind(size=self._update_map_size)

        for name, (lat, lon) in markers.items():
            marker = LabeledMapMarker(lat=lat, lon=lon, text=name)
            self.mapview.add_marker(marker)

        self.side_menu = ColoredBoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=250,
            pos=(-250, 0),
            padding=10,
            spacing=10
        )
        with self.side_menu.canvas.before:
            Color(0, 0, 0, 1)
            self.side_menu_bg = Rectangle(size=self.side_menu.size, pos=self.side_menu.pos)
        self.side_menu.bind(size=self._update_side_menu_bg, pos=self._update_side_menu_bg)

        # ScrollView для прокрутки списка в боковом меню
        scrollview = ScrollView(size_hint=(1, 1))
        menu_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=0, spacing=10)
        menu_layout.bind(minimum_height=menu_layout.setter('height'))

        # Добавляем кнопки с единым стилем RoundedButton
        for name in markers.keys():
            btn = RoundedButton(
                text=name,
                size_hint_y=None,
                height=50,
                background_color=(0.2, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                radius=10
            )
            btn.bind(on_release=self.go_to_info)
            menu_layout.add_widget(btn)

        scrollview.add_widget(menu_layout)
        self.side_menu.add_widget(scrollview)

        exit_btn = RoundedButton(
            text='Выход',
            size_hint_y=None,
            height=50,
            background_color=(0, 0, 0.3, 1),
            color=(1, 1, 1, 1),
            radius=10
        )
        exit_btn.bind(on_release=App.get_running_app().stop)
        self.side_menu.add_widget(exit_btn)

        self.layout.add_widget(self.side_menu)

        self.menu_button = ImageButton(
            source='hamburger.jpg',
            size_hint=(None, None),
            size=(30, 30),
            pos=(0, self.height - 30)
        )
        self.menu_button.bind(on_release=self.toggle_side_menu)
        self.layout.add_widget(self.menu_button)
        self.bind(size=self.update_menu_button_pos)

        self.add_widget(self.layout)
        self.menu_open = False

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_map_size(self, instance, value):
        self.mapview.size = (self.width - 30, self.height)
        self.mapview.pos = (30, 0)

    def _update_side_menu_bg(self, instance, value):
        self.side_menu_bg.pos = instance.pos
        self.side_menu_bg.size = instance.size

    def update_menu_button_pos(self, *args):
        self.menu_button.pos = (0, self.height - 30)

    def toggle_side_menu(self, *args):
        if self.menu_open:
            anim = Animation(x=-self.side_menu.width, d=0.3)
            anim.start(self.side_menu)
            self.menu_open = False
        else:
            anim = Animation(x=0, d=0.3)
            anim.start(self.side_menu)
            self.menu_open = True

    def go_to_info(self, instance):
        info_screen = self.manager.get_screen('info')
        info_screen.set_info(instance.text)
        self.manager.current = 'info'


class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.label = Label(text='', halign='center', valign='middle', font_size='18sp')
        self.label.bind(size=lambda instance, value: setattr(instance, 'text_size', instance.size))
        self.layout.add_widget(self.label)

        back_btn = Button(text='Назад', size_hint=(1, 0.1), background_color=(0.2,0.6,0.9,1), color=(1,1,1,1))
        back_btn.bind(on_release=self.go_back)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def set_info(self, place_name):
        self.label.text = info_texts.get(place_name, 'Информация отсутствует')

    def go_back(self, instance):
        self.manager.current = 'map'


class MapApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(MapScreen(name='map'))
        sm.add_widget(InfoScreen(name='info'))
        return sm


if __name__ == '__main__':
    MapApp().run()
