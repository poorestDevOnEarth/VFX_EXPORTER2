from getResolve import get_resolve
from time import sleep
import logging


class Rinter:
    def _init_(self):
        self.project_manager = None
        self.project = None
        self.clip_index = None
        self.current_clip = None
        self.clips = None
        self.clipsV1 = None
        self.clipsV2 = None
        self.timeline = None
        self.resolve = None

    def start(self):
        successful = False
        while not successful:
            try:
                self.resolve = get_resolve()
                self.project_manager = self.resolve.GetProjectManager()
                self.project = self.project_manager.GetCurrentProject()
                self.timeline = self.project.GetCurrentTimeline()
                self.project.SetCurrentTimeline(self.timeline)
                self.clips = self.timeline.GetItemListInTrack("video", 1)
                self.current_clip = self.timeline.GetCurrentVideoItem()
                self.clip_index = self.index_of_clip()
                logging.info("successfully loaded resolve")
                successful = True
            except ImportError:
                logging.fatal("resolve api not found")
                print("resolve api not found")
                exit(-1)
            except AttributeError:
                logging.error("resolve not found. retrying in 5 seconds")
                sleep(5)

    def load_timeline_clips(self, id):
        self.clips = self.timeline.GetItemListInTrack("video", id)

    def reload(self) -> None:
        try:
            self.timeline = self.project.GetCurrentTimeline()
            self.clips = self.timeline.GetItemListInTrack("video", 1)
            self.current_clip = self.timeline.GetCurrentVideoItem()
            self.clip_index = self.index_of_clip()
            logging.debug(
                f"reloaded data from resolve. clips {len(self.clips)}, current: {self.clip_index}")
        except AttributeError and TypeError:
            logging.error(
                "error while reloading. setting script state to initial.")

    def apply_cdl(self, cdl, state) -> None:
        try:
            self.current_clip = self.timeline.GetCurrentVideoItem()
            if self.current_clip is not None:
                self.current_clip.SetCDL(cdl)
        except AttributeError and TypeError:
            state.error = True
            logging.error(
                "error while reloading. setting script state to initial.")

    def index_of_clip(self):
        for x in range(0, len(self.clips)):
            if f"{self.clips[x]}" == f"{self.current_clip}":
                return x + 1

        return -1