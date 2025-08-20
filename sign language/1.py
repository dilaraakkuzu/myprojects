import cv2
import mediapipe as mp
import csv
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class HandTrackingApp(App):
    def build(self):
        self.img1 = Image()
        self.capture = cv2.VideoCapture(0)

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        Clock.schedule_interval(self.update, 1.0/30.0)
        return self.img1

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Orijinal frame (ML / MediaPipe için)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # MediaPipe ile el tespiti
            results = self.hands.process(frame_rgb)

            # Tespit edilen elleri çiz
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame_rgb, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    # Landmark verilerini CSV'ye kaydet
                    self.save_landmarks_to_csv(hand_landmarks, label='hand')

            # Ekranda göstermek için X eksenine göre aynala
            frame_display = cv2.flip(frame_rgb, 1)

            # Kivy Texture oluştur
            buf = frame_display.tobytes()
            texture = Texture.create(size=(frame_display.shape[1], frame_display.shape[0]), colorfmt='rgb')
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

            # Texture dikey olarak çevir (baş aşağı olmasın)
            texture.flip_vertical()

            self.img1.texture = texture

    def on_stop(self):
        self.capture.release()

    # CSV'ye landmark verilerini kaydetmek için fonksiyon
    def save_landmarks_to_csv(self, landmarks, label, filename='landmarks.csv'):
        with open(filename, mode='a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Her kayıt için label ve landmark koordinatları (x, y, z) yazılıyor
            row = [label] + [val for point in landmarks.landmark for val in (point.x, point.y, point.z)]
            csv_writer.writerow(row)

if __name__ == '__main__':
    HandTrackingApp().run()
# This code implements a simple hand tracking application using Kivy and MediaPipe.
# It captures video from the webcam, processes it to detect hands, and displays the results in a Kivy Image widget.
# The application uses MediaPipe's hand detection capabilities to draw landmarks on detected hands.
# The video feed is updated at approximately 30 frames per second.
# The application can handle up to two hands and uses a minimum detection confidence of 0.7.
# The captured video is flipped horizontally to create a mirror effect.
# The application releases the video capture resource when it stops.
# Note: Ensure you have the required libraries installed:
# pip install kivy mediapipe opencv-python
# Make sure to run this script in an environment where a webcam is available.




