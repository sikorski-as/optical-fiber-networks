import time


class Clock:

    def __init__(self):
        self._start_time = None
        self._end_time = None

    def start(self):
        self._start_time = time.process_time()

    def stop(self):
        self._end_time = time.process_time()

    def time_elapsed(self):
        if self._start_time is None or self._end_time is None:
            raise ValueError("Both start and end time needs to be set.")
        return self._end_time - self._start_time
