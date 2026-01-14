from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_widget)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.play_btn)
        layout.addLayout(btn_layout)

    def load_video(self, path):
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.pause()
        self.play_btn.setText("Play")

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("Play")
        else:
            self.player.play()
            self.play_btn.setText("Pause")
