import json
import os


class Settings:
    def __init__(self):
        self.settings = {}
        self.load()
        self.check()

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
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
        except:
            self.reset()

    def save(self):
        with open("settings.json", "w") as f:
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

        except:
            self.reset()


exportSettings = {
    "resolution": ["1920x1080", "1280x720", "640x360"],
    "frameRate": [60, 30, 15],
    "size": [200, 25, "入力"],
}
