from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout

import os

class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

        # Track slider externally
        self.slider = None

        # Connect media_player signals
        self.media_player.positionChanged.connect(self.update_slider)
        self.media_player.durationChanged.connect(self.update_slider_range)

    def set_slider(self, slider):
        """Assign the slider to control this video"""
        self.slider = slider
        self.slider.setValue(0)
        self.slider.sliderReleased.connect(self.slider_released)

    def load_video(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video not found: {path}")
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.media_player.stop()

    def play(self):
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def stop(self):
        self.media_player.stop()

    def seek(self, percent):
        """Seek to a percentage of the video (0.0 - 1.0)"""
        duration = self.media_player.duration()
        if duration > 0:
            self.media_player.setPosition(int(duration * percent))

    # ---------------- Slot for slider ----------------
    def update_slider(self, position):
        """Update slider position as video plays"""
        if self.slider and self.media_player.duration() > 0:
            value = int((position / self.media_player.duration()) * 100)
            self.slider.blockSignals(True)  # prevent recursion
            self.slider.setValue(value)
            self.slider.blockSignals(False)

    def update_slider_range(self, duration):
        """Ensure slider is reset when video loads"""
        if self.slider:
            self.slider.setMinimum(0)
            self.slider.setMaximum(100)

    def slider_released(self):
        """When user drags slider, update video position"""
        if self.slider:
            percent = self.slider.value() / 100
            self.seek(percent)