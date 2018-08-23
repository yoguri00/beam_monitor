import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm
from get_fps import FrameRate
import cv2

STREAM_URL = 'http://172.20.4.25:8080/?action=stream'
DEFAULT_X = 139
DEFAULT_Y = 15
FPS = 15


def nothing(x):
    pass


def beam_monitor():
    cap = cv2.VideoCapture(STREAM_URL)
    cv2.namedWindow('src', cv2.WINDOW_NORMAL)

    center_x = 200
    center_y = 200
    radius = 100
    tick = 10

    while True:
        ret, frame = cap.read()
        cv2.circle(frame, (center_x, center_y), radius, (0, 0, 255), 10)
        key = cv2.waitKey(1)

        if ret:
            cv2.imshow('src', frame)

        if key == ord('w'):
            center_y -= tick

        if key == ord('s'):
            center_y += tick

        if key == ord('a'):
            center_x -= tick

        if key == ord('d'):
            center_x += tick

        if key == ord('o'):
            radius += tick

        if key == ord('i'):
            radius -= tick

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def beam_profile_3d():
    cap = cv2.VideoCapture(STREAM_URL)
    cv2.namedWindow('src', cv2.WINDOW_NORMAL)

    ret, frame = cap.read()
    width = 0
    height = 0
    if ret:
        width = frame.shape[1]
        height = frame.shape[0]
        print(width)
        print(height)

    cv2.createTrackbar('pos_x', 'src', DEFAULT_X, width, nothing)
    cv2.createTrackbar('pos_y', 'src', DEFAULT_Y, height, nothing)
    cv2.createTrackbar('scale', 'src', 7, 20, nothing)
    cv2.createTrackbar('col stride', 'src', 5, 50, nothing)
    cv2.createTrackbar('row stride', 'src', 5, 50, nothing)

    frame_rate = FrameRate()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    rec_x1 = 200
    rec_x2 = 400
    len_x = rec_x2 - rec_x1
    rec_y1 = 200
    rec_y2 = 400
    len_y = rec_y2 - rec_y1

    pixel_y = np.arange(0, width, 1)
    pixel_x = np.arange(0, height, 1)
    pixel_x, pixel_y = np.meshgrid(pixel_x, pixel_y)

    wf = ax.plot_wireframe(pixel_x[rec_x1:rec_x2, rec_y1:rec_y2],
                           pixel_y[rec_x1:rec_x2, rec_y1:rec_y2],
                           np.zeros((rec_x2 - rec_x1, rec_y2 - rec_y1)))

    while True:
        ret, frame = cap.read()
        key = cv2.waitKey(1)
        fps = frame_rate.get()

        if ret:
            cv2.rectangle(frame, (rec_x1, rec_y1), (rec_x2, rec_y2), (0, 0, 255), 5)
            # cv2.line(frame, (rec_x1, int((rec_y1+rec_y2)/2)), (rec_x2, int((rec_y1+rec_y2)/2)), (0, 0, 255), 2)
            # cv2.line(frame, (int((rec_x1+rec_x2)/2), rec_y1), (int((rec_x1+rec_x2)/2), rec_y2), (0, 0, 255), 2)
            cv2.putText(frame, str(fps), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
            pos_x = cv2.getTrackbarPos('pos_x', 'src')
            pos_y = cv2.getTrackbarPos('pos_y', 'src')
            pos_s = cv2.getTrackbarPos('scale', 'src')
            c_stride = cv2.getTrackbarPos('col stride', 'src')
            r_stride = cv2.getTrackbarPos('row stride', 'src')

            rec_x1 = pos_x + (len_x - int(len_x*pos_s/10))
            rec_x2 = pos_x + len_x - (len_x - int(len_x*pos_s/10))

            rec_y1 = pos_y + (len_y - int(len_y*pos_s/10))
            rec_y2 = pos_y + len_y - (len_y - int(len_y*pos_s/10))

            cv2.imshow('src', frame)
            old_wf = wf
            ax.set_ylim(rec_y1, rec_y2)
            ax.set_xlim(rec_x1, rec_x2)
            ax.set_zlim(0, 255)
            # ax.view_init(45, 90)

            if rec_x1 > 0 and rec_x2 < width and rec_y1 > 0 and rec_y2 < height:
                wf = ax.plot_wireframe(pixel_y[rec_x1:rec_x2, rec_y1:rec_y2],
                                       pixel_x[rec_x1:rec_x2, rec_y1:rec_y2],
                                       frame[rec_y1:rec_y2, rec_x1:rec_x2, 0],
                                       cstride=c_stride, rstride=r_stride)
                ax.collections.remove(old_wf)
            plt.pause(1/FPS)

        # print((rec_x1, rec_x2), (rec_y1, rec_y2))

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # beam_monitor()
    beam_profile_3d()

