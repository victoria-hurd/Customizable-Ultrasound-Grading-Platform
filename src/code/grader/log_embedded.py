import time


class EmbeddedDataLogger:

    def __init__(self):
        self.reset()

    def reset(self):
        self.replay_enabled = None
        self.autoplay_enabled = None

        self.play_start_time = None
        self.last_play_start = None
        self.review_duration = 0
        self.total_watch_time = 0

        self.times_replayed = 0
        self.pause_count = 0
        self.play_count = 0
        self.scrub_count = 0

    def start_review(self,):
        self.reset()
        self.play_start_time = time.time()

    def end_review(self,replay_status,autoplay_status):
        if self.play_start_time:
            self.review_duration = time.time() - self.play_start_time

        if self.last_play_start:
            self.total_watch_time += time.time() - self.last_play_start

        self.replay_enabled = replay_status
        self.autoplay_enabled = autoplay_status

    def log_pause(self):
        print("Logging pause event")
        self.pause_count += 1
        if self.last_play_start:
            self.total_watch_time += time.time() - self.last_play_start
            self.last_play_start = None

    def log_play(self):
        print("Logging play event")
        self.play_count += 1
        self.last_play_start = time.time()

    def log_scrub(self):
        self.scrub_count += 1

    def log_replay(self):
        self.times_replayed += 1

    def to_dict(self):
        return {
            "replay_enabled": self.replay_enabled,
            "autoplay_enabled": self.autoplay_enabled,
            "review_duration_sec": round(self.review_duration,3),
            "total_watch_time_sec": round(self.total_watch_time,3),
            "pause_count": self.pause_count,
            "play_count": self.play_count,
            "scrub_count": self.scrub_count,
            "times_replayed": self.times_replayed
        }