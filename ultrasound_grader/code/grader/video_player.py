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
        self.media_player.mediaStatusChanged.connect(self._handle_media_status)

    def set_slider(self, slider):
        self.slider = slider
        self.slider.setValue(0)
        self.slider.sliderMoved.connect(self._slider_moved)

    def update_slider_range(self, duration):
        if self.slider:
            self.slider.setRange(0, duration)

    def load_video(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video not found: {path}")
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.media_player.stop()

    def play(self):
        # If we're at (or extremely close to) the end, restart
        if self.media_player.position() >= self.media_player.duration() - 5:
            self.media_player.setPosition(0)
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def stop(self):
        self.media_player.stop()

    # ---------------- Slot for slider ----------------
    def update_slider(self, position):
        if self.slider and not self.slider.isSliderDown():
            self.slider.setValue(position)

    def _slider_moved(self, position):
        self.media_player.setPosition(position)

    def _handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.pause()
            self.media_player.setPosition(self.media_player.duration())

    # ---------------- Frame grab for annotation ----------------
    def grab_frame(self):
        return self.video_widget.grab()