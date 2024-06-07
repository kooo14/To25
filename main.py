import os
import sys
import time

from PyQt6.QtCore import QPoint, QSize, Qt, QUrl
from PyQt6.QtGui import QIcon, QPalette, QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaDevices, QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QStyle,
    QVBoxLayout,
    QWidget,
)

BUTTON_SIZE = 50


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Set window background color
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.gray)
        self.setPalette(p)

        # Initialize the user interface
        self.init_ui()

        # Display the window
        self.show()

    def image_button(self, icon_path, size=BUTTON_SIZE, noBackground=True):
        button = QPushButton()
        img = QPixmap(icon_path).scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        button.setIcon(QIcon(img))
        button.setIconSize(QSize(size, size))
        button.setFixedSize(QSize(size, size))

        if noBackground:
            button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        return button

    # Initialize the user interface components
    def init_ui(self):
        # 音量調整レイアウト
        volumeLayout = QHBoxLayout()
        # ミュートボタン
        muteBtn = self.image_button("images/volume.png", 25, noBackground=True)

        # 音量スライダー
        volumeSlider = QSlider(Qt.Orientation.Horizontal)
        volumeSlider.setRange(0, 100)
        volumeSlider.setValue(100)
        volumeSlider.setFixedWidth(100)

        volumeLayout.addWidget(muteBtn)
        volumeLayout.addWidget(volumeSlider)

        # 再生調整レイアウト
        playLayout = QHBoxLayout()
        # 10秒戻しボタン
        backBtn = self.image_button("images/back.png")

        # 再生ボタン
        self.playBtn = self.image_button("images/play.png")
        self.playBtn.setEnabled(False)

        # 10秒進むボタン
        forwardBtn = self.image_button("images/forward.png")

        playLayout.addWidget(backBtn)
        playLayout.addSpacing(20)
        playLayout.addWidget(self.playBtn)
        playLayout.addSpacing(20)
        playLayout.addWidget(forwardBtn)

        etcLayout = QHBoxLayout()
        etcLayout.setContentsMargins(0, 0, 0, 0)
        # リピートボタン
        repeatBtn = self.image_button("images/repeat.png")

        etcLayout.addSpacing(80)
        etcLayout.addWidget(repeatBtn)

        # 動画操作ボタンレイアウト
        videoControlLayout = QHBoxLayout()
        videoControlLayout.setContentsMargins(30, 0, 30, 0)

        videoControlLayout.addLayout(volumeLayout)
        videoControlLayout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        videoControlLayout.addLayout(playLayout)
        videoControlLayout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        videoControlLayout.addLayout(etcLayout)

        # 操作ボタン
        # 設定ボタン
        settingBtn = self.image_button("images/settings.png")
        # TODO: 設定画面を表示する

        # ファイルオープンボタン
        openBtn = self.image_button("images/open.png")

        # 保存ボタン
        saveBtn = self.image_button("images/save.png")

        # Create a QSlider for seeking within the video
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)

        # 動画表示ウィジェット
        self.mediaPlayer = CustomMediaPlayer(
            playBtn=self.playBtn,
            durationSlider=self.slider,
            volumeSlider=volumeSlider,
            muteBtn=muteBtn,
        )

        self.videowidget = QVideoWidget()
        self.videowidget.setFixedSize(1280, 720)
        self.mediaPlayer.setVideoOutput(self.videowidget)

        # ボタンクリックイベント
        volumeSlider.valueChanged.connect(self.mediaPlayer.set_volume)
        self.playBtn.clicked.connect(self.mediaPlayer.play_video)
        openBtn.clicked.connect(self.mediaPlayer.open_file)
        self.slider.sliderMoved.connect(self.mediaPlayer.set_position)
        muteBtn.clicked.connect(self.mediaPlayer.toggle_mute)
        backBtn.clicked.connect(self.mediaPlayer.skip_seconds_func(-10))
        forwardBtn.clicked.connect(self.mediaPlayer.skip_seconds_func(10))

        # Create a QVBoxLayout for arranging widgets vertically
        vboxLayout = QVBoxLayout()
        vboxLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        vboxLayout.setContentsMargins(0, 0, 0, 0)
        vboxLayout.addWidget(self.videowidget)
        vboxLayout.addLayout(videoControlLayout)
        vboxLayout.addWidget(self.slider)
        vboxLayout.addStretch()

        # Set the layout of the window
        self.setLayout(vboxLayout)

    # Method to handle errors in media playback
    def handle_errors(self):
        self.playBtn.setEnabled(False)
        print(self.mediaPlayer.errorString())


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Get the size of the display
        screen = QApplication.primaryScreen()
        self.screen_size = screen.size()

        width = int(self.screen_size.width() / 1.5)
        height = int(self.screen_size.height() / 1.2)

        self.move(
            int((self.screen_size.width() - width) / 2),
            int((self.screen_size.height() - height) / 2),
        )
        # Set window properties such as title, size, and icon
        self.setWindowTitle("To25")
        self.setFixedSize(width, height)
        self.setWindowIcon(QIcon("player.png"))

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

        self.show()


class CustomMediaPlayer(QMediaPlayer):
    def __init__(
        self,
        playBtn: QPushButton,
        durationSlider: QSlider,
        volumeSlider: QSlider,
        muteBtn: QPushButton,
        parent=None,
    ):
        super().__init__(parent=parent)

        self.durationSlider = durationSlider
        self.playBtn = playBtn
        self.volumeSlider = volumeSlider
        self.muteBtn = muteBtn
        self.isMute = False
        self.volume = 100

        # Create QAudioOutput instance and set it to the media player
        self.audio_output = QAudioOutput()
        self.setAudioOutput(self.audio_output)

        # Connect media player signals to their respective slots
        self.playbackStateChanged.connect(self.mediastate_changed)
        self.positionChanged.connect(self.position_changed)
        self.durationChanged.connect(self.duration_changed)

        # DEBUG

        self.setSource(QUrl.fromLocalFile("test/center.mp4"))
        self.playBtn.setEnabled(True)
        self.play_video()

    # Method to open a video file
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != "":
            self.setSource(QUrl.fromLocalFile(filename))
            self.playBtn.setEnabled(True)
            self.play_video()

    # Method to play or pause the video
    def play_video(self):
        if self.isPlaying():
            self.pause()
            self.playBtn.setIcon(QIcon(os.getcwd() + "/images/play.png"))
        else:
            self.play()
            self.playBtn.setIcon(QIcon(os.getcwd() + "/images/pause.png"))

    # Method to handle changes in media player state (playing or paused)
    def mediastate_changed(self, state):
        if self.PlaybackState.PlayingState == True:
            self.playBtn.setIcon(QIcon(os.getcwd() + "/images/pause.png"))
        else:
            self.playBtn.setIcon(QIcon(os.getcwd() + "/images/play.png"))

    # Method to handle changes in video position
    def position_changed(self, position):
        self.durationSlider.setValue(position)

    # Method to handle changes in video duration
    def duration_changed(self, duration):
        self.durationSlider.setRange(0, duration)

    # Method to set the video position
    def set_position(self, position):
        self.setPosition(position)

    def set_volume(self, volume):
        self.audioOutput().setVolume(volume / 100)
        self.volume = volume
        if volume == 0:
            self.set_mute(True)
        else:
            self.set_mute(False)

    def toggle_mute(self):
        self.set_mute(not self.isMute)

    def set_mute(self, isMute):
        self.isMute = isMute
        if isMute:
            self.audioOutput().setVolume(0)
            self.muteBtn.setIcon(QIcon(os.getcwd() + "/images/mute.png"))
        else:
            if self.volume == 0:
                self.volume = 100
            self.audioOutput().setVolume(self.volume / 100)
            self.volumeSlider.setValue(self.volume)
            self.muteBtn.setIcon(QIcon(os.getcwd() + "/images/volume.png"))

    def skip_seconds_func(self, seconds):
        def skip_seconds(self, seconds=seconds, mediaPlayer=self):
            mediaPlayer.setPosition(mediaPlayer.position() + seconds * 1000)

        return skip_seconds


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
