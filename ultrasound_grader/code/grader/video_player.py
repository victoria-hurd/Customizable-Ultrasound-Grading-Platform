from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider
import os

class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Media Player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Video Widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

        # Slider
        self.slider = None
        self.media_player.positionChanged.connect(self._update_slider)
        self.media_player.durationChanged.connect(self._update_slider_range)
        self.media_player.mediaStatusChanged.connect(self._handle_media_status)

    # ---------------- Video Controls ----------------
    def load_video(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video not found: {path}")
        from PyQt6.QtCore import QUrl
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.media_player.stop()

    def play(self): 
        if self.media_player.position() >= self.media_player.duration() - 5:
            self.media_player.setPosition(0)
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def stop(self):
        self.media_player.stop()

    # ---------------- Slider ----------------
    def set_slider(self, slider: QSlider):
        self.slider = slider
        self.slider.setValue(0)
        self.slider.sliderMoved.connect(self._slider_moved)

    def _update_slider_range(self, duration):
        if self.slider:
            self.slider.setRange(0, duration)

    def _update_slider(self, position):
        if self.slider and not self.slider.isSliderDown():
            self.slider.setValue(position)

    def _slider_moved(self, position):
        self.media_player.setPosition(position)

    def _handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            #self.pause()
            self.stop()
            self.media_player.setPosition(self.media_player.duration())

