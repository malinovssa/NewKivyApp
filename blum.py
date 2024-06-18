import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

import cv2
import numpy as np
from jnius import autoclass

PythonActivity = autoclass('org.kivy.android.PythonActivity')
MotionEvent = autoclass('android.view.MotionEvent')

class GreenDetectorApp(App):
    def build(self):
        self.is_running = False
        layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text='Нажмите "Старт" для начала работы')
        start_button = Button(text='Старт', on_press=self.start_detection)
        stop_button = Button(text='Стоп', on_press=self.stop_detection)

        layout.add_widget(self.status_label)
        layout.add_widget(start_button)
        layout.add_widget(stop_button)
        
        return layout

    def start_detection(self, instance):
        self.is_running = True
        self.status_label.text = 'Работа началась'
        Clock.schedule_interval(self.detect_green_shapes, 1.0 / 30.0)

    def stop_detection(self, instance):
        self.is_running = False
        self.status_label.text = 'Работа остановлена'
        Clock.unschedule(self.detect_green_shapes)

    def detect_green_shapes(self, dt):
        if not self.is_running:
            return

        # Получаем изображение экрана
        screenshot = self.get_screenshot()
        if screenshot is None:
            return

        # Обрабатываем изображение
        green_shapes = self.find_green_shapes(screenshot)
        if green_shapes:
            for shape in green_shapes:
                self.tap_on_shape(shape)

    def get_screenshot(self):
        try:
            activity = PythonActivity.mActivity
            view = activity.getWindow().getDecorView().getRootView()
            view.setDrawingCacheEnabled(True)
            bitmap = view.getDrawingCache()
            width, height = bitmap.getWidth(), bitmap.getHeight()
            pixels = np.zeros((height, width, 4), dtype=np.uint8)
            bitmap.getPixels(pixels, 0, width, 0, 0, width, height)
            view.setDrawingCacheEnabled(False)
            return cv2.cvtColor(pixels, cv2.COLOR_RGBA2RGB)
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None

    def find_green_shapes(self, img):
        # Конвертируем изображение в HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Находим контуры зеленых фигур
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        shapes = []
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Фильтрация по размеру
                x, y, w, h = cv2.boundingRect(contour)
                shapes.append((x + w // 2, y + h // 2))
        return shapes

    def tap_on_shape(self, shape):
        x, y = shape
        activity = PythonActivity.mActivity
        view = activity.getWindow().getDecorView().getRootView()

        # Создаем событие касания
        down_time = System.currentTimeMillis()
        event = MotionEvent.obtain(
            down_time,
            down_time,
            MotionEvent.ACTION_DOWN,
            x,
            y,
            0
        )
        view.dispatchTouchEvent(event)
        event.recycle()

        event = MotionEvent.obtain(
            down_time,
            down_time,
            MotionEvent.ACTION_UP,
            x,
            y,
            0
        )
        view.dispatchTouchEvent(event)
        event.recycle()

if name == 'main':
    GreenDetectorApp().run()