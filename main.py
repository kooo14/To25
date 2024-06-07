import os
import sys
import time

from PyQt6.QtCore import QPoint, QSize, Qt, QUrl, QRectF
from PyQt6.QtGui import QIcon, QMouseEvent, QPalette, QPixmap, QPainter, QBrush
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

BUTTON_SIZE = 40
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 900


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

        etcLayout.addSpacing(130 - BUTTON_SIZE)
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

        # 動画表示ウィジェット
        self.mediaPlayer = CustomMediaPlayer(
            playBtn=self.playBtn,
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
        muteBtn.clicked.connect(self.mediaPlayer.toggle_mute)
        backBtn.clicked.connect(self.mediaPlayer.skip_seconds_func(-10))
        forwardBtn.clicked.connect(self.mediaPlayer.skip_seconds_func(10))

        # Create a QVBoxLayout for arranging widgets vertically
        controlLayout = QVBoxLayout()
        controlLayout.setContentsMargins(10, 10, 10, 10)
        controlLayout.addWidget(self.mediaPlayer.seekbar)
        controlLayout.addLayout(videoControlLayout)

        vboxLayout = QVBoxLayout()
        vboxLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        vboxLayout.setContentsMargins(0, 0, 0, 0)
        vboxLayout.addWidget(self.videowidget)
        vboxLayout.addLayout(controlLayout)
        vboxLayout.addStretch()

        # Set the layout of the window
        self.setLayout(vboxLayout)

    # Method to handle errors in media playback
    def handle_errors(self):
        self.playBtn.setEnabled(False)
        print(self.mediaPlayer.errorString())


class Window(QMainWindow):
    def __init__(self):
        global WINDOW_WIDTH, WINDOW_HEIGHT

        super().__init__()
        # Get the size of the display
        screen = QApplication.primaryScreen()
        self.screen_size = screen.size()

        WINDOW_WIDTH = int(self.screen_size.width() / 1.5)
        WINDOW_HEIGHT = int(self.screen_size.height() / 1.3)

        # self.move(
        #     int((self.screen_size.width() - WINDOW_WIDTH) / 2),
        #     int((self.screen_size.height() - WINDOW_WIDTH) / 2),
        # )

        self.setWindowTitle("To25")
        # self.setFixedSize(WINDOW_WIDTH, WINDOW_WIDTH)
        self.setFixedWidth(WINDOW_WIDTH)
        self.setWindowIcon(QIcon("player.png"))

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

        self.show()
        self.move(0, 0)


class CustomMediaPlayer(QMediaPlayer):
    def __init__(
        self,
        playBtn: QPushButton,
        volumeSlider: QSlider,
        muteBtn: QPushButton,
        parent=None,
    ):
        super().__init__(parent=parent)

        self.seekbar = SeekBar(self)

        self.playBtn = playBtn
        self.volumeSlider = volumeSlider
        self.muteBtn = muteBtn
        self.isMute = False
        self.isSeeking = False
        self.pausedBySeeking = False
        self.volume = 100

        # Create QAudioOutput instance and set it to the media player
        self.audio_output = QAudioOutput()
        self.setAudioOutput(self.audio_output)

        # Connect media player signals to their respective slots
        self.playbackStateChanged.connect(self.mediastate_changed)
        self.durationChanged.connect(self.seekbar.durationChanged)
        self.positionChanged.connect(self.seekbar.positionChanged)

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
        if self.isSeeking is False:
            if self.isPlaying() == True:
                self.playBtn.setIcon(QIcon(os.getcwd() + "/images/pause.png"))
            else:
                self.playBtn.setIcon(QIcon(os.getcwd() + "/images/play.png"))

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

    def set_is_seeking(self, isSeeking):
        self.isSeeking = isSeeking
        if self.isPlaying() or self.pausedBySeeking:
            if isSeeking:
                self.pause()
                self.pausedBySeeking = True
            elif self.pausedBySeeking:
                self.play()
                self.pausedBySeeking = False

    def skip_seconds_func(self, seconds):
        def skip_seconds(self, seconds=seconds, mediaPlayer=self):
            mediaPlayer.setPosition(mediaPlayer.position() + seconds * 1000)

        return skip_seconds


class SeekBar(QWidget):
    def __init__(self, mediaPlayer: CustomMediaPlayer):
        super().__init__()

        self.duration = 0
        self.position = 0
        self.mediaPlayer = mediaPlayer

        # self.setFixedSize(WINDOW_WIDTH, 30)
        self.setFixedHeight(30)
        self.setMouseTracking(True)

    def durationChanged(self, duration):
        self.duration = duration

    def positionChanged(self, position):
        self.position = position
        self.update()

    def paintEvent(self, event):
        if self.duration == 0:
            return
        p = QPainter(self)
        if p.isActive() == False:
            p.begin(self)

        p.setPen(Qt.GlobalColor.red)
        p.setBrush(Qt.GlobalColor.red)
        center = int(self.width() * self.position / self.duration)
        p.drawRect(center - 1, 0, 1, self.height())

        p.setPen(Qt.GlobalColor.black)
        p.setBrush(Qt.BrushStyle.NoBrush)
        rectangle = QRectF(0, 0, self.width(), self.height())
        p.drawRoundedRect(rectangle, 5, 5)
        p.end()

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:

        if a0.buttons() == Qt.MouseButton.LeftButton and self.duration != 0:
            self.seek(a0.pos().x())
        return super().mouseMoveEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if self.duration != 0:
            self.seek(a0.pos().x())
            self.mediaPlayer.set_is_seeking(True)
        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if self.duration != 0:
            self.mediaPlayer.set_is_seeking(False)

    def seek(self, mousePos: int):
        position = int(mousePos / self.width() * self.duration)
        self.mediaPlayer.setPosition(position)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
