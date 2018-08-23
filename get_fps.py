import cv2


class FrameRate:
    def __init__(self):
        self._count = 0
        self._fps = 0
        self._freq = 1000 / cv2.getTickFrequency()
        self._tm_start = cv2.getTickCount()
        self._tm_now = cv2.getTickCount()

    def get(self):
        self._count += 1
        self._tm_now = cv2.getTickCount()
        tm_diff = (self._tm_now - self._tm_start) * self._freq
        if tm_diff >= 1000:
            self._tm_start = self._tm_now
            self._fps = self._count
            self._count = 0
        return self._fps

