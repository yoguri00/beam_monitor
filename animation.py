from matplotlib.animation import FuncAnimation
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import cv2
from get_fps import FrameRate


class Animation:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.x, self.y = np.meshgrid(np.arange(0, 640, 1), np.arange(0, 480, 1))

        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if ret:
            self.im = self.ax.imshow(frame[:, :, 0], cmap=cm.hot)

        self.frame_rate = FrameRate()
        cv2.namedWindow('src', cv2.WINDOW_NORMAL)

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def update(self, index):
        ret, frame = self.cap.read()
        key = cv2.waitKey(1)

        if ret:
            self.im.set_data(frame[:, :, 0])
            cv2.putText(frame, str(self.frame_rate.get()), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('src', frame)

        if key == ord('q'):
            self.__del__()


if __name__ == '__main__':
    animation = Animation()
    ani = FuncAnimation(animation.fig, animation.update, interval=50, blit=False)
    plt.show()


