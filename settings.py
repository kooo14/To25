import json
import os
from pathlib import Path

settingFolderPath = Path(os.getenv("APPDATA")) / "To25"
settingFolderPath.mkdir(parents=True, exist_ok=True)
settingFilePath = settingFolderPath / "settings.json"


class Settings:
    def __init__(self):
        self.settings = {}

    def reset(self):
        default = {
            "defaultOptions": {
                "frameRate": 30,
                "resolution": "1280x720",
                "size": 25,
                "noAudio": False,
            },
            "clipPath": os.path.expanduser("~/Videos").replace("\\", "/"),
            "outputPath": os.path.expanduser("~/Desktop").replace("\\", "/"),
            "autoPlayClip": True,
            "openFolderAfterExport": True,
        }

        self.settings = default
        self.save()

    def load(self):
        try:
            with open(settingFilePath, "r") as f:
                self.settings = json.load(f)
                self.check()
            return True
        except:
            self.reset()
            return False

    def save(self):
        with open(settingFilePath, "w") as f:
            json.dump(self.settings, f)

    def check(self):
        try:
            if (
                self.settings["defaultOptions"]["resolution"]
                not in exportSettings["resolution"]
            ):
                self.settings["defaultOptions"]["resolution"] = exportSettings[
                    "resolution"
                ][1]
            if (
                self.settings["defaultOptions"]["frameRate"]
                not in exportSettings["frameRate"]
            ):
                self.settings["defaultOptions"]["frameRate"] = exportSettings[
                    "frameRate"
                ][1]

        except Exception as e:
            print(e)
            print("Settings file is corrupted. Resetting to default.")
            self.reset()


exportSettings = {
    "resolution": ["1920x1080", "1280x720", "640x360"],
    "frameRate": [60, 30, 15],
    "size": [500, 50, 25, "カスタム"],
}
