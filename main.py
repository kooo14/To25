import os
import subprocess
import sys
import threading
import time
import webbrowser

from PyQt6.QtCore import (
    QCoreApplication,
    QEvent,
    QPoint,
    QRectF,
    QSize,
    QStandardPaths,
    Qt,
    QUrl,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QMouseEvent,
    QPainter,
    QPalette,
    QPen,
    QPixmap,
    QKeyEvent,
)
from PyQt6.QtMultimedia import QAudioOutput, QMediaDevices, QMediaFormat, QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QSpinBox,
    QStyle,
    QVBoxLayout,
    QWidget,
)

import autoload
import expoter
import settings

BUTTON_SIZE = 40
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 900

VERSION = "1.0.0"


class PlayButton(QPushButton):
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            event.ignore()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            event.ignore()
        else:
            super().keyReleaseEvent(event)


class MainWidget(QWidget):
    def __init__(self, setting: settings.Settings):
        super().__init__()

        self.settings = setting

        # UIの初期化
        self.setUpUI()
        self.setAcceptDrops(True)
        # ウィンドウの表示
        self.show()

    def createImageButton(
        self, iconFilePath: str, size=BUTTON_SIZE, iconPadding=10, ignoreSpace=False
    ):
        if ignoreSpace:
            button = PlayButton()
        else:
            button = QPushButton()

        img = QPixmap(iconFilePath).scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # ボタンのアイコンとサイズを設定
        button.setIcon(QIcon(img))
        button.setIconSize(QSize(size - iconPadding, size - iconPadding))
        button.setFixedSize(QSize(size, size))

        button.setStyleSheet(
            "QPushButton {background-color: rgba(5,5,5,0); \
                        height: 200px; \
                        color: yellow; \
                        font: 30px; \
                        border-radius: 5px;} \
                        QPushButton:hover {background: rgba(20,20,20,50)} \
                        QPushButton:pressed {background: rgba(20,20,20,100)}\
"
        )

        return button

    # Initialize the user interface components
    def setUpUI(self):
        # 音量調整レイアウト
        volumeLayout = QHBoxLayout()
        # ミュートボタン
        muteBtn = self.createImageButton("images/volume.png", 25, 5)
        muteBtn.setShortcut("m")

        # 音量スライダー
        volumeSlider = QSlider(Qt.Orientation.Horizontal)
        volumeSlider.setStyleSheet(
            "\
        QSlider::groove:horizontal {\
            border: 1px solid #999999;\
            height: 10px; \
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);\
            margin: 2px 0;\
            }\
        QSlider::handle:horizontal {\
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b3b3b3, stop:1 #8f8f8f);\
            border: 1px solid #5c5c5c;\
            width: 18px; \
            margin: -2px 0; \
            border-radius: 3px;\
        }\
        Qslider::handle:horizontal:hover {\
            background: #ffffff;\
        }\
        "
        )
        volumeSlider.setRange(0, 100)
        volumeSlider.setValue(100)
        volumeSlider.setFixedWidth(100)

        volumeLayout.addWidget(muteBtn)
        volumeLayout.addWidget(volumeSlider)

        # 再生調整レイアウト
        playLayout = QHBoxLayout()

        # トリミング開始地点ボタン
        trimStartBtn = self.createImageButton("images/start.png")
        trimStartBtn.setShortcut("s")
        trimStartBtn.setToolTip("トリミング開始地点を設定します")

        # 10秒戻しボタン
        backBtn = self.createImageButton("images/back.png", iconPadding=5)
        backBtn.setShortcut(Qt.Key.Key_Left)

        # 再生ボタン
        self.playBtn = self.createImageButton(
            "images/play.png", iconPadding=5, ignoreSpace=True
        )
        self.playBtn.setEnabled(False)
        self.playBtn.setShortcut(Qt.Key.Key_Space)

        # 10秒進むボタン
        forwardBtn = self.createImageButton("images/forward.png", iconPadding=5)
        forwardBtn.setShortcut(Qt.Key.Key_Right)

        # トリミング終了地点ボタン
        trimEndBtn = self.createImageButton("images/end.png")
        trimEndBtn.setShortcut("e")
        trimEndBtn.setToolTip("トリミング終了地点を設定します")

        playLayout.addWidget(trimStartBtn)
        playLayout.addSpacing(20)
        playLayout.addWidget(backBtn)
        playLayout.addSpacing(20)
        playLayout.addWidget(self.playBtn)
        playLayout.addSpacing(20)
        playLayout.addWidget(forwardBtn)
        playLayout.addSpacing(20)
        playLayout.addWidget(trimEndBtn)

        etcLayout = QHBoxLayout()
        etcLayout.setContentsMargins(0, 0, 0, 0)

        # 保存
        self.saveBtn = self.createImageButton("images/save.png", iconPadding=5)
        self.saveBtn.setShortcut("Ctrl+s")
        self.saveBtn.setToolTip("動画を保存します")
        self.saveBtn.setEnabled(False)
        self.saveBtn.clicked.connect(self.openExportWindow)

        etcLayout.addSpacing(130 - BUTTON_SIZE)
        etcLayout.addWidget(self.saveBtn)

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

        # 動画表示ウィジェット
        self.mediaPlayer = CustomMediaPlayer(
            playBtn=self.playBtn,
            saveBtn=self.saveBtn,
            volumeSlider=volumeSlider,
            muteBtn=muteBtn,
        )

        self.videowidget = CustomVideoWidget(mediaPlayer=self.mediaPlayer)
        self.videowidget.setFixedSize(1280, 720)
        self.mediaPlayer.setVideoOutput(self.videowidget)

        # ボタンクリックイベント
        volumeSlider.valueChanged.connect(self.mediaPlayer.changeVolume)
        self.playBtn.clicked.connect(self.mediaPlayer.togglePlayback)
        muteBtn.clicked.connect(self.mediaPlayer.switchMute)
        backBtn.clicked.connect(self.mediaPlayer.skipSeconds(-10))
        forwardBtn.clicked.connect(self.mediaPlayer.skipSeconds(10))
        trimStartBtn.clicked.connect(self.mediaPlayer.setStartTrimPosition)
        trimEndBtn.clicked.connect(self.mediaPlayer.setTrimEndPos)

        # 操作パネルレイアウト
        controlLayout = QVBoxLayout()
        controlLayout.setContentsMargins(10, 10, 10, 10)
        controlLayout.addWidget(self.mediaPlayer.seekbar)
        controlLayout.addLayout(videoControlLayout)

        # メインレイアウト
        vboxLayout = QVBoxLayout()
        vboxLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        vboxLayout.setContentsMargins(0, 0, 0, 0)
        vboxLayout.addWidget(self.videowidget)
        vboxLayout.addLayout(controlLayout)
        vboxLayout.addStretch()

        # レイアウトをセット
        self.setLayout(vboxLayout)

    # エラー処理
    def handle_errors(self):
        self.playBtn.setEnabled(False)
        print(self.mediaPlayer.errorString())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            self.mediaPlayer.startPlay(url)

    def openExportWindow(self):
        self.stopEditing()
        exportWindow = ExportWindow(
            self.settings,
            self.mediaPlayer.source().toString().replace("file:///", ""),
            self.mediaPlayer.trimStartPositon,
            self.mediaPlayer.trimEndPositon,
        )
        exportWindow.exec()

    def stopEditing(self):
        if self.mediaPlayer.isPlaying():
            self.mediaPlayer.togglePlayback()


class SettingWindow(QDialog):
    def __init__(self, settings: settings.Settings):
        super().__init__()

        self.settings = settings

        self.setWindowTitle("設定")
        self.setWindowIcon(QIcon("images/icon.png"))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setUpUI()

    def setUpUI(self):
        # 出力設定
        outputLabel = QLabel("デフォルトの出力設定")
        outputLabel.setStyleSheet("font-size: 15px; font-weight: bold;")

        self.outputSettingLayout = OutputSetting(self.settings)

        # フォルダ設定
        clipPathLabel = QLabel("動画フォルダ")
        clipPathLabel.setToolTip(
            "クリップが保存されるフォルダを指定します。クリップ自動再生に使用されます。"
        )
        self.clipPathEdit = QLineEdit()
        self.clipPathEdit.setMinimumWidth(200)
        self.clipPathEdit.setText(self.settings.settings["clipPath"])
        clipPathButton = QPushButton("参照")
        clipPathButton.clicked.connect(self.selectInstantReplayFolder)

        # フォルダ設定レイアウト
        pathLayout = QGridLayout()
        pathLayout.addWidget(clipPathLabel, 0, 0)
        pathLayout.addWidget(self.clipPathEdit, 0, 1)
        pathLayout.addWidget(clipPathButton, 0, 2)

        # 基本設定
        baseSettings = QLabel("設定")
        baseSettings.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.autoClipPlay = QCheckBox("クリップ自動再生")
        self.autoClipPlay.setChecked(self.settings.settings["autoPlayClip"])
        self.autoClipPlay.setToolTip(
            "ソフト起動時に動画フォルダ内の最近録画されたクリップを自動再生します"
        )

        self.openFolderAfterExport = QCheckBox("保存後にフォルダを開く")
        self.openFolderAfterExport.setChecked(
            self.settings.settings["openFolderAfterExport"]
        )
        self.openFolderAfterExport.setToolTip(
            "ソフト起動時に動画フォルダ内の最近録画されたクリップを自動再生します"
        )

        baseSettingsLayout = QVBoxLayout()
        baseSettingsLayout.addWidget(self.autoClipPlay)
        baseSettingsLayout.addWidget(self.openFolderAfterExport)

        # 設定保存ボタン
        saveButton = QPushButton("保存")
        saveButton.clicked.connect(self.saveSettings)

        # バージョン表示
        versionLabel = QLabel("Version: " + VERSION)
        versionLabel.setAlignment(Qt.AlignmentFlag.AlignRight)

        # レイアウトをセット
        self.layout.addWidget(baseSettings)
        self.layout.addLayout(baseSettingsLayout)
        self.layout.addLayout(pathLayout)
        self.layout.addSpacing(20)
        self.layout.addWidget(outputLabel)
        self.layout.addLayout(self.outputSettingLayout)
        self.layout.addWidget(versionLabel)
        self.layout.addWidget(saveButton)

    def selectInstantReplayFolder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "インスタントリプレイのフォルダを選択"
        )
        if folder:
            self.clipPathEdit.setText(folder)

    def saveSettings(self):
        output = self.outputSettingLayout.getOutputSetting()

        self.settings.settings["defaultOptions"]["resolution"] = output["resolution"]
        self.settings.settings["defaultOptions"]["frameRate"] = output["frameRate"]
        self.settings.settings["defaultOptions"]["size"] = output["size"]
        self.settings.settings["defaultOptions"]["noAudio"] = output["noAudio"]

        self.settings.settings["autoPlayClip"] = self.autoClipPlay.isChecked()
        self.settings.settings["openFolderAfterExport"] = (
            self.openFolderAfterExport.isChecked()
        )
        self.settings.settings["clipPath"] = self.clipPathEdit.text()
        self.settings.settings["outputPath"] = (
            self.outputSettingLayout.outputPathEdit.text()
        )

        self.settings.save()
        self.settings.check()
        self.close()


class Window(QMainWindow):
    def __init__(self):
        global WINDOW_WIDTH, WINDOW_HEIGHT

        super().__init__()
        self.settings = settings.Settings()
        exitSettings = self.settings.load()
        # ディスプレイのサイズを取得
        screen = QApplication.primaryScreen()
        self.screenSize = screen.size()

        WINDOW_WIDTH = int(self.screenSize.width() / 1.5)
        WINDOW_HEIGHT = int(self.screenSize.height() / 1.3)

        # ウィンドウの背景色を設定
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        self.setPalette(p)

        self.setWindowTitle("To25")
        self.setFixedWidth(WINDOW_WIDTH)
        self.setWindowIcon(QIcon("images/icon.png"))

        self.mainWidget = MainWidget(self.settings)
        self.setCentralWidget(self.mainWidget)

        # メニューバーの設定
        self.setupMenuBar()

        self.show()
        # 画面中央にウィンドウを移動
        self.move(
            int((self.screenSize.width() - self.width()) / 2),
            int((self.screenSize.height() - self.height()) / 2 - 50),
        )

        if exitSettings is False:
            welcomeWindow = WelcomeWindow()
            welcomeWindow.exec()
            self.showSettings()

        self.autoLoadClip()

    # メニューバーの設定
    def setupMenuBar(self):
        menubar = self.menuBar()

        # ファイルメニュー
        fileMenu = menubar.addMenu("ファイル")

        # ファイルを開く
        openFileAction = fileMenu.addAction("開く")
        openFileAction.triggered.connect(self.open)
        openFileAction.setShortcut("o")

        # ファイルを保存
        saveFileAction = fileMenu.addAction("保存")
        saveFileAction.triggered.connect(self.mainWidget.openExportWindow)

        # 終了
        fileMenu.addSeparator()
        exitAction = fileMenu.addAction("終了")
        exitAction.triggered.connect(self.close)

        editMenu = menubar.addMenu("編集")

        toggleRepeatWithinTrimming = editMenu.addAction("トリミング範囲内でリピート")
        toggleRepeatWithinTrimming.triggered.connect(
            self.mainWidget.mediaPlayer.toggleRepeat
        )
        toggleRepeatWithinTrimming.setShortcut("r")

        # 設定
        editMenu.addSeparator()
        openSettingsAction = editMenu.addAction("設定")
        openSettingsAction.triggered.connect(self.showSettings)

        # ヘルプメニュー
        helpMenu = menubar.addMenu("ヘルプ")
        helpAction = helpMenu.addAction("ヘルプを開く")
        helpAction.triggered.connect(self.openHelp)

    def open(self):
        self.mainWidget.stopEditing()

        fileDialog = QFileDialog(self)
        fileDialog.setWindowTitle("ファイルを開く")
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        fileDialog.setNameFilter("動画ファイル (*.mp4 *.avi *.mov *.wmv *.flv *.mkv)")

        fileDialog.setDirectory(self.settings.settings["clipPath"])
        if fileDialog.exec() == QDialog.DialogCode.Accepted:
            try:
                url = fileDialog.selectedUrls()[0]
                self.mainWidget.mediaPlayer.startPlay(url)
            except Exception as e:
                dialog = QDialog()
                dialog.setWindowTitle("Error")
                dialog.setFixedSize(300, 100)
                dialog.setWindowIcon(QIcon("images/icon.png"))
                dialog.setModal(True)
                dialog.setLayout(QVBoxLayout())
                dialog.layout().addWidget(QLabel("Error: " + str(e)))
                dialog.exec()

    def showSettings(self):
        self.mainWidget.stopEditing()
        settingWindow = SettingWindow(self.settings)
        settingWindow.exec()

    def openHelp(self):
        self.mainWidget.stopEditing()
        webbrowser.open("https://github.com/kooo14/To25")

    def autoLoadClip(self):
        if self.settings.settings["autoPlayClip"]:
            clip = autoload.getRecentClip(self.settings.settings["clipPath"])
            if clip:
                self.mainWidget.mediaPlayer.startPlay(QUrl.fromLocalFile(clip))
                self.statusBar().showMessage(
                    "最新のクリップを自動再生しました - " + clip, 5000
                )
            else:
                self.statusBar().showMessage(
                    "最新のクリップが見つかりませんでした。手動で選択してください。",
                    5000,
                )
                self.open()
        else:
            self.statusBar().showMessage("クリップ自動再生が無効です。", 5000)
            self.open()


class CustomMediaPlayer(QMediaPlayer):
    def __init__(
        self,
        playBtn: QPushButton,
        saveBtn: QPushButton,
        volumeSlider: QSlider,
        muteBtn: QPushButton,
        parent=None,
    ):
        super().__init__(parent=parent)

        self.seekbar = SeekBar(self)

        self.playBtn = playBtn
        self.saveBtn = saveBtn
        self.volumeSlider = volumeSlider
        self.muteBtn = muteBtn
        self.isMute = False
        self.isRepeat = False
        self.isSeeking = False
        self.pausedBySeeking = False
        self.volume = 100

        self.trimStartPositon = 0
        self.trimEndPositon = 0

        # オーディオ出力を設定
        self.audioOutput = QAudioOutput()
        self.setAudioOutput(self.audioOutput)

        # メディアプレイヤーのシグナルを設定
        self.playbackStateChanged.connect(self.handleMediaStateChanged)
        self.durationChanged.connect(self.seekbar.handleDurationChange)
        self.positionChanged.connect(self.seekbar.handlePositionChange)
        self.positionChanged.connect(self.repeatPlaybackIfInRange)

    def startPlay(self, url: QUrl):
        self.stop()
        QCoreApplication.processEvents()
        self.setSource(url)
        self.togglePlayback()
        self.playBtn.setEnabled(True)
        self.saveBtn.setEnabled(True)

    # 再生と一時停止を切り替える
    def togglePlayback(self):
        if self.isPlaying():
            self.pause()
            self.playBtn.setIcon(QIcon(os.getcwd() + "/images/play.png"))
        else:
            self.play()
            self.playBtn.setIcon(QIcon(os.getcwd() + "/images/pause.png"))

    # 再生状況が変更されたときの処理
    def handleMediaStateChanged(self, state):
        if self.isSeeking is False:
            if self.isPlaying() == True:
                self.playBtn.setIcon(QIcon(os.getcwd() + "/images/pause.png"))
            else:
                self.playBtn.setIcon(QIcon(os.getcwd() + "/images/play.png"))

    # 音量を設定
    def changeVolume(self, volume: int):
        self.audioOutput.setVolume(volume / 100)
        self.volume = volume
        if volume == 0:
            self.setMute(True)
        else:
            self.setMute(False)

    # ミュートを切り替える
    def switchMute(self):
        self.setMute(not self.isMute)

    # ミュートを設定
    def setMute(self, isMute):
        self.isMute = isMute
        if isMute:
            self.audioOutput.setVolume(0)
            self.muteBtn.setIcon(QIcon(os.getcwd() + "/images/mute.png"))
        else:
            if self.volume == 0:
                self.volume = 100
            self.audioOutput.setVolume(self.volume / 100)
            self.volumeSlider.setValue(self.volume)
            self.muteBtn.setIcon(QIcon(os.getcwd() + "/images/volume.png"))

    def toggleRepeat(self):
        self.isRepeat = not self.isRepeat

    def repeatPlaybackIfInRange(self):
        # トリミング範囲内で再生を繰り返す
        if self.isRepeat:
            if self.position() >= self.trimEndPositon:
                self.setPosition(self.trimStartPositon)
            if self.position() < self.trimStartPositon:
                self.setPosition(self.trimStartPositon)

    # シーク中かどうかを設定
    def setIsSeeking(self, isSeeking):
        self.isSeeking = isSeeking
        if self.isPlaying() or self.pausedBySeeking:
            if isSeeking:
                self.pause()
                self.pausedBySeeking = True
            elif self.pausedBySeeking:
                self.play()
                self.pausedBySeeking = False

    # 指定秒数進める関数を返す
    def skipSeconds(self, seconds):
        def func(self, seconds=seconds, mediaPlayer=self):
            mediaPlayer.setPosition(mediaPlayer.position() + seconds * 1000)

        return func

    # トリミング開始位置を設定
    def setStartTrimPosition(self):
        if self.position() < self.trimEndPositon:
            self.trimStartPositon = self.position()
            self.seekbar.update()

    # トリミング終了位置を設定
    def setTrimEndPos(self):
        if self.position() > self.trimStartPositon:
            self.trimEndPositon = self.position()
            self.seekbar.update()


class CustomVideoWidget(QVideoWidget):
    def __init__(self, mediaPlayer: CustomMediaPlayer):
        super().__init__()
        self.setAcceptDrops(True)
        self.windowChild.installEventFilter(self)
        self.mediaPlayer = mediaPlayer

    @property
    def windowChild(self):
        child = self.findChild(QWidget)
        if child.metaObject().className() == "QWindowContainer":
            return child

    def eventFilter(self, obj, event):
        if obj is self.windowChild:
            if event.type() == QEvent.Type.DragEnter:
                if event.mimeData().hasUrls():
                    event.accept()
            elif event.type() == QEvent.Type.Drop:
                if event.mimeData().hasUrls():
                    url = event.mimeData().urls()[0]
                    self.mediaPlayer.startPlay(url)

        return super().eventFilter(obj, event)


class SeekBar(QWidget):
    def __init__(self, mediaPlayer: CustomMediaPlayer):
        super().__init__()

        self.duration = 0
        self.position = 0
        self.mediaPlayer = mediaPlayer
        self.setFixedHeight(30)
        self.setMouseTracking(True)
        self.nowTrimStartPositon = 0
        self.nowTrimEndPositon = 0

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.positionLabel = QLabel("0:00:00")
        self.positionLabel.setFixedWidth(60)
        self.positionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.positionLabel)

        self.remainSecondsLabel = QLabel("0:00:00")
        self.remainSecondsLabel.setFixedWidth(60)
        self.remainSecondsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addStretch()
        self.layout.addWidget(self.remainSecondsLabel)

    # 動画の長さが変更されたときの処理
    def handleDurationChange(self, duration):
        self.duration = duration
        self.mediaPlayer.trimStartPositon = 0
        self.mediaPlayer.trimEndPositon = duration

    # 再生位置が変更されたときの処理
    def handlePositionChange(self, position):
        self.position = position
        self.positionLabel.setText(
            time.strftime("%H:%M:%S", time.gmtime(position / 1000))
        )
        self.remainSecondsLabel.setText(
            time.strftime("%H:%M:%S", time.gmtime((self.duration - position) / 1000))
        )
        self.update()

    # 描画処理
    def paintEvent(self, event):
        if self.duration == 0:
            return
        p = QPainter(self)

        if p.isActive() == False:
            p.begin(self)

        self.paint(p)
        p.end()

    # シークバーを描画
    def paint(self, p: QPainter):
        center = int(self.width() * self.position / self.duration)
        trimStart = int(
            self.width() * self.mediaPlayer.trimStartPositon / self.duration
        )
        trimEnd = int(self.width() * self.mediaPlayer.trimEndPositon / self.duration)

        p.setPen(Qt.GlobalColor.red)
        p.setBrush(Qt.GlobalColor.red)
        p.drawRect(center - 1, 0, 1, self.height())

        pen = QPen()
        pen.setColor(Qt.GlobalColor.black)
        pen.setWidth(2)
        p.setPen(pen)

        p.setBrush(Qt.BrushStyle.SolidPattern)
        p.setBrush(QColor(81, 93, 232, 100))
        rectangle = QRectF(trimStart, 0, trimEnd - trimStart, self.height())
        p.drawRoundedRect(rectangle, 5, 5)

        p.setBrush(Qt.BrushStyle.NoBrush)
        rectangle = QRectF(0, 0, self.width(), self.height())
        p.drawRoundedRect(rectangle, 5, 5)

    # マウスが動いたときの処理
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if a0.buttons() == Qt.MouseButton.LeftButton and self.duration != 0:
            self.seek(a0.pos().x())
        return super().mouseMoveEvent(a0)

    # マウスがクリックされたときの処理
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if self.duration != 0 and a0.button() == Qt.MouseButton.LeftButton:
            self.seek(a0.pos().x())
            self.mediaPlayer.setIsSeeking(True)
        return super().mousePressEvent(a0)

    # マウスが離されたときの処理
    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if self.duration != 0 and a0.button() == Qt.MouseButton.LeftButton:
            self.mediaPlayer.setIsSeeking(False)
        return super().mouseReleaseEvent(a0)

    # ホイールスクロールを検知して1秒スキップする
    def wheelEvent(self, event):
        if event.buttons() == Qt.MouseButton.NoButton:
            moveSeconds = 1
        else:
            moveSeconds = 5

        if event.angleDelta().y() > 0:
            self.mediaPlayer.setPosition(
                self.mediaPlayer.position() - moveSeconds * 1000
            )
        else:
            self.mediaPlayer.setPosition(
                self.mediaPlayer.position() + moveSeconds * 1000
            )

    # シークバーをクリックした位置に移動
    def seek(self, mousePos: int):
        position = int(mousePos / self.width() * self.duration)
        self.mediaPlayer.setPosition(position)


class OutputSetting(QGridLayout):
    def __init__(self, setting: settings.Settings):
        super().__init__()

        self.settings = setting

        # 解像度設定
        resolutionBox = QGroupBox("解像度")
        resolutionBox.setToolTip(
            "大きな解像度ほど画質が向上します。ただし容量も大きくなります。"
        )
        resolutionLayout = QVBoxLayout()
        self.resolutionRadioGroup = QButtonGroup()
        for resolution in settings.exportSettings["resolution"]:
            resolutionRadioButton = QRadioButton(resolution)
            self.resolutionRadioGroup.addButton(resolutionRadioButton)
            if resolution == self.settings.settings["defaultOptions"]["resolution"]:
                resolutionRadioButton.setChecked(True)
            resolutionLayout.addWidget(resolutionRadioButton)
        resolutionBox.setLayout(resolutionLayout)
        self.addWidget(resolutionBox, 0, 0)

        # フレームレート設定
        frameRateBox = QGroupBox("フレームレート")
        frameRateBox.setToolTip(
            "大きなフレームレートほど動きが滑らかになります。ただし容量も大きくなります。"
        )
        frameRateLayout = QVBoxLayout()
        self.frameRateRadioGroup = QButtonGroup()
        for frameRate in settings.exportSettings["frameRate"]:
            frameRateRadioButton = QRadioButton(str(frameRate))
            self.frameRateRadioGroup.addButton(frameRateRadioButton)
            if frameRate == self.settings.settings["defaultOptions"]["frameRate"]:
                frameRateRadioButton.setChecked(True)
            frameRateLayout.addWidget(frameRateRadioButton)

        frameRateBox.setLayout(frameRateLayout)
        self.addWidget(frameRateBox, 0, 1)

        # 容量設定
        sizeBox = QGroupBox("容量（MB）")
        sizeBox.setToolTip(
            "出力される動画の容量を指定します。ただし、多少の誤差が生じることがあります。"
        )
        sizeLayout = QVBoxLayout()
        self.sizeSpinBox = QSpinBox()
        self.sizeRadioGroup = QButtonGroup()

        sizePolicy = QSizePolicy()
        sizePolicy.setRetainSizeWhenHidden(True)
        self.sizeSpinBox.setSizePolicy(sizePolicy)

        for size in settings.exportSettings["size"]:
            sizeRadioButton = QRadioButton(str(size))
            self.sizeRadioGroup.addButton(sizeRadioButton)
            sizeRadioButton.toggled.connect(self.handleSizeRadioButtonToggle)
            if size == self.settings.settings["defaultOptions"]["size"]:
                sizeRadioButton.setChecked(True)
            sizeLayout.addWidget(sizeRadioButton)

        self.sizeSpinBox.setRange(1, 1000)
        self.sizeSpinBox.setValue(50)

        if (
            self.settings.settings["defaultOptions"]["size"]
            not in settings.exportSettings["size"]
        ):
            self.sizeRadioGroup.buttons()[2].setChecked(True)
            self.sizeSpinBox.setValue(self.settings.settings["defaultOptions"]["size"])
        else:
            self.sizeSpinBox.setVisible(False)

        sizeLayout.addWidget(self.sizeSpinBox)

        sizeBox.setLayout(sizeLayout)
        self.addWidget(sizeBox, 1, 0)

        # その他の設定
        otherBox = QGroupBox("その他")
        otherLayout = QVBoxLayout()

        self.noAudioCheckBox = QCheckBox("音声を含めない")
        self.noAudioCheckBox.setChecked(
            self.settings.settings["defaultOptions"]["noAudio"]
        )

        otherLayout.addWidget(self.noAudioCheckBox)
        otherLayout.addStretch()
        otherBox.setLayout(otherLayout)

        self.addWidget(otherBox, 1, 1)

        # 出力フォルダ設定
        outputPathLabel = QLabel("出力フォルダ")
        outputPathLabel.setMinimumWidth(60)
        outputPathLabel.setToolTip("動画が出力されるフォルダを指定します。")
        self.outputPathEdit = QLineEdit()
        self.outputPathEdit.setMinimumWidth(200)
        self.outputPathEdit.setText(self.settings.settings["outputPath"])
        outputPathButton = QPushButton("参照")
        outputPathButton.clicked.connect(self.openOutputPathDialog)

        pathLayout = QGridLayout()
        pathLayout.addWidget(outputPathLabel, 1, 0)
        pathLayout.addWidget(self.outputPathEdit, 1, 1)
        pathLayout.addWidget(outputPathButton, 1, 2)

        self.addLayout(pathLayout, 2, 0, 1, 2)

    def openOutputPathDialog(self):
        folder = QFileDialog.getExistingDirectory(
            None, "保存先を選択", self.settings.settings["outputPath"]
        )
        if folder:
            self.outputPathEdit.setText(folder)

    # スロット関数の定義
    def handleSizeRadioButtonToggle(self, checked):
        # "カスタム"というラジオボタンが選択された場合のみsizeSpinBoxを表示
        if checked and self.sender().text() == "カスタム":
            self.sizeSpinBox.setVisible(True)
        else:
            self.sizeSpinBox.setVisible(False)

    def getOutputSetting(self):
        output = {}
        output["resolution"] = self.resolutionRadioGroup.checkedButton().text()
        output["frameRate"] = int(self.frameRateRadioGroup.checkedButton().text())
        output["noAudio"] = self.noAudioCheckBox.isChecked()

        if self.sizeRadioGroup.checkedButton().text() == "カスタム":
            output["size"] = self.sizeSpinBox.value()
        else:
            output["size"] = int(self.sizeRadioGroup.checkedButton().text())

        return output


class ExportWindow(QDialog):
    def __init__(
        self,
        settings: settings.Settings,
        inputPath: str,
        trimStartPositon: int,
        trimEndPositon: int,
    ):
        super().__init__()

        self.settings = settings
        self.inputPath = inputPath
        self.trimStartPositon = trimStartPositon
        self.trimEndPositon = trimEndPositon

        self.setMinimumWidth(300)

        self.setWindowTitle("出力")
        self.setWindowIcon(QIcon("images/icon.png"))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setUpUI()

    def setUpUI(self):
        self.outputSettingLayout = OutputSetting(self.settings)

        # 保存とキャンセルボタン
        self.saveButton = QPushButton("保存")
        self.saveButton.clicked.connect(self.startExportProcess)

        self.cancelButton = QPushButton("キャンセル")
        self.cancelButton.clicked.connect(self.close)

        outputFileNameLabel = QLabel("ファイル名")
        outputFileNameLabel.setMinimumWidth(60)
        outputFileNameLabel.setToolTip(
            "動画のファイル名を指定します。拡張子は不要です。"
        )
        self.outputFileNameEdit = QLineEdit()
        self.outputFileNameEdit.setMinimumWidth(200)
        self.outputFileNameEdit.setText(
            ".".join(self.inputPath.split("/")[-1].split(".")[:-1]) + "_comp"
        )

        fileNameLayout = QGridLayout()
        fileNameLayout.addWidget(outputFileNameLabel, 1, 0)
        fileNameLayout.addWidget(self.outputFileNameEdit, 1, 1)

        # レイアウトをセット
        confirmLayout = QHBoxLayout()
        confirmLayout.addWidget(self.cancelButton)
        confirmLayout.addWidget(self.saveButton)
        self.layout.addLayout(self.outputSettingLayout)
        self.layout.addLayout(fileNameLayout)
        self.layout.addLayout(confirmLayout)

    def startExportProcess(self):
        output = self.outputSettingLayout.getOutputSetting()

        if os.path.exists(self.outputSettingLayout.outputPathEdit.text()) is False:
            QMessageBox.warning(self, "保存失敗", "出力フォルダが存在しません。")
            return

        fileName = self.outputFileNameEdit.text()
        outputPath = "{}/{}.mp4".format(
            self.outputSettingLayout.outputPathEdit.text(), fileName
        )

        args = (
            self.inputPath,
            outputPath,
            self.trimStartPositon,
            self.trimEndPositon,
            output["resolution"],
            output["frameRate"],
            output["size"],
            output["noAudio"],
        )

        self.saveButton.setVisible(False)
        self.cancelButton.setVisible(False)

        self.thread = threading.Thread(target=expoter.exportVideo, args=args)
        self.thread.start()

        progress = QProgressBar()
        progress.setValue(1)
        progress.setRange(
            0,
            int(output["size"]) * 1024,
        )

        progress.setFormat("出力中...")
        self.layout.addWidget(progress)

        while self.thread.is_alive():
            QApplication.processEvents()
            processingSize = getFileSizeKB(outputPath)
            if processingSize > int(output["size"]) * 1024 * 0.9:
                processingSize = int(int(output["size"]) * 1024 * 0.9)
            progress.setValue(processingSize)

        progress.setValue(int(output["size"]) * 1024)

        if getFileSizeKB(outputPath) != 0:
            self.exportDone(
                self.outputSettingLayout.outputPathEdit.text(),
                int(output["size"]) * 1024,
                getFileSizeKB(outputPath),
            )
        else:
            self.exportFailed()

    def exportDone(self, outputFolderPath: str, targetSizeKB: int, outputSizeKB: int):
        outputSizeMB = round(outputSizeKB / 1024, 2)

        if outputSizeKB > targetSizeKB:
            QMessageBox.warning(
                self,
                "保存成功（容量超過）",
                f"保存に成功しましたが、指定した容量を超えています。\n容量: {outputSizeMB}MB\n動画の長さを短くするか、出力設定を変更してください。",
            )
        else:
            QMessageBox.information(
                self,
                "保存完了",
                "保存が完了しました。\n容量: " + str(outputSizeMB) + "MB",
            )

        if self.settings.settings["openFolderAfterExport"]:
            outputFolderPath = outputFolderPath.replace("/", "\\")
            commands = ["explorer", outputFolderPath]
            subprocess.run(commands)

        self.close()

    def exportFailed(self):
        QMessageBox.warning(self, "保存失敗", "保存に失敗しました。")

        self.close()


class WelcomeWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("To25")
        self.setWindowIcon(QIcon("images/icon.png"))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setUpUI()

    def setUpUI(self):
        # メッセージ
        messageLabel = QLabel(
            "To25へようこそ！\n\n"
            + "To25は、簡単にクリップを編集し容量を圧縮できるソフトウェアです。\n\n"
            + "使い方は簡単です。起動時に最新の動画の再生、またはファイル選択画面が表示されます。\n"
            + "動画を再生すると、トリミング開始地点とトリミング終了地点を設定することができます。\n"
            + "設定が完了したら、保存ボタンを押して動画を保存してください。\n\n"
            + "設定を変更する場合は、メニューの「編集」→「設定」を押してください。\n\n"
            + "To25をお楽しみください！"
        )
        messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        attentionLabel = QLabel("注意")
        attentionLabel.setStyleSheet("font-size: 15px; font-weight: bold;")

        attentionMessage = QLabel(
            "注意：初回起動のため、設定画面が表示されます。\n"
            "インスタントリプレイが保存されるフォルダを指定してください。\n"
            "正しく指定しないと、起動時の自動再生ができません。"
        )

        # 閉じるボタン
        closeButton = QPushButton("閉じる")
        closeButton.clicked.connect(self.close)

        self.layout.addWidget(messageLabel)
        self.layout.addWidget(attentionLabel)
        self.layout.addWidget(attentionMessage)
        self.layout.addWidget(closeButton)


def getFileSizeKB(filePath):
    try:
        size = os.path.getsize(filePath)
        return int(size / 1024)
    except FileNotFoundError:
        return 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
