import os
import sys
import time

videoExtensions = ["mp4", "avi", "mov", "wmv", "flv", "mkv"]


# clipPath内のすべてのファイルを再帰的に取得
def getVideoFiles(path: str, maxDepth=5):
    files = []
    for root, dirs, fs in os.walk(path):
        depth = root[len(path) - 1 :].count(os.sep)
        if depth > maxDepth:
            continue
        for file in fs:
            files.append(os.path.join(root, file))
    return files


def getNewestFile(path: str):
    files = getVideoFiles(path)
    if not files:
        return None
    return max(files, key=os.path.getctime)


def getRecentClip(clipPath: str):
    clip = getNewestFile(clipPath)
    # 6時間以内に作成されたファイルのみを対象とする
    if clip and os.path.getctime(clip) > time.time() - 6 * 60 * 60:
        return clip

    return None
