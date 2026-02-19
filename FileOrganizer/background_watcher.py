import time
from ai_sorter import sort_folder


class BackgroundWatcher:
    def __init__(self, folder):
        self.folder = folder

    def start_watching(self, callback):
        while True:
            actions = sort_folder(self.folder)

            for action in actions:
                callback(action)

            time.sleep(5)
