from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QStyle, QSizePolicy, QFileDialog
import sys
import os
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette, QPixmap
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5 import QtSvg

from pyqt_svg_button import SvgButton


BUTTON_SIZE = 50


class Window(QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties such as title, size, and icon
        self.setWindowTitle("To25")
        self.setGeometry(100, 100, 1280, 1000)
        self.setWindowIcon(QIcon('player.png'))

        # Set window background color
        p = self.palette()
        p.setColor(QPalette.Window, Qt.gray)
        self.setPalette(p)

        # Initialize the user interface
        self.init_ui()

        # Display the window
        self.show()

    # Initialize the user interface components
    def init_ui(self):
        # Create a QMediaPlayer object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Create a QVideoWidget object to display video
        videowidget = QVideoWidget()
        videowidget.setFixedSize(1280, 720)

        # 操作ボタン
        # 設定ボタン
        settingBtn = SvgButton()
        settingBtn.setIcon("images/settings.svg")
        settingBtn.setFixedSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
        # TODO: 設定画面を表示する

        # ファイルオープンボタン
        openBtn = SvgButton()
        openBtn.setIcon("images/open.svg")
        openBtn.setFixedSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
        openBtn.clicked.connect(self.open_file)

        # 10秒戻しボタン
        backBtn = SvgButton()
        backBtn.setIcon("images/back.svg")
        backBtn.setFixedSize(QSize(BUTTON_SIZE, BUTTON_SIZE))

        # 再生ボタン
        self.playBtn = SvgButton()
        self.playBtn.setIcon("images/play.svg")
        self.playBtn.setFixedSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
        self.playBtn.setEnabled(False)
        self.playBtn.clicked.connect(self.play_video)

        # 10秒進むボタン
        forwardBtn = SvgButton()
        forwardBtn.setIcon("images/forward.svg")
        forwardBtn.setFixedSize(QSize(BUTTON_SIZE, BUTTON_SIZE))

        # リピートボタン
        repeatBtn = SvgButton()
        repeatBtn.setIcon("images/repeat.svg")
        repeatBtn.setFixedSize(QSize(BUTTON_SIZE, BUTTON_SIZE))

        # 保存ボタン
        saveBtn = SvgButton()
        saveBtn.setIcon("images/save.svg")
        saveBtn.setFixedSize(QSize(BUTTON_SIZE, BUTTON_SIZE))

        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Create a QSlider for seeking within the video
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Create a QHBoxLayout for arranging widgets horizontally
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        # Add widgets to the QHBoxLayout
        hboxLayout.addWidget(settingBtn)
        hboxLayout.addWidget(openBtn)
        hboxLayout.addSpacing(300)
        hboxLayout.addWidget(backBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(forwardBtn)
        hboxLayout.addSpacing(300)
        hboxLayout.addWidget(repeatBtn)
        hboxLayout.addWidget(saveBtn)

        # Create a QVBoxLayout for arranging widgets vertically
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.label)
        vboxLayout.addWidget(self.slider)

        # Set the layout of the window
        self.setLayout(vboxLayout)

        # Set the video output for the media player
        self.mediaPlayer.setVideoOutput(videowidget)

        # Connect media player signals to their respective slots
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    # Method to open a video file

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)

    # Method to play or pause the video
    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    # Method to handle changes in media player state (playing or paused)
    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                os.getcwd() + "/images/pause.svg"
            )
        else:
            self.playBtn.setIcon(
                os.getcwd() + "/images/play.svg"
            )

    # Method to handle changes in video position
    def position_changed(self, position):
        self.slider.setValue(position)

    # Method to handle changes in video duration
    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    # Method to set the video position
    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    # Method to handle errors in media playback
    def handle_errors(self):
        self.playBtn.setEnabled(False)
        self.label.setText("Error: " + self.mediaPlayer.errorString())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
