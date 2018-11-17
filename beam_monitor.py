import numpy as np
import matplotlib.pyplot as plt
import cv2
import json

from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm

from get_fps import FrameRate
from ssh import control_ssh


def nothing(x):
    pass


def beam_profile_3d():
    with open('config.json', 'r') as f:
        obj = json.load(f)
        stream_url = "http://" + obj["monitor"]["ip"] + ":" + str(obj["monitor"]["port"]) + "/" + obj["monitor"]["query"]
        default_x = obj["monitor"]["default_x"]
        default_y = obj["monitor"]["default_y"]
        fps = obj["monitor"]["fps"]

    cap = cv2.VideoCapture(stream_url)
    cv2.namedWindow('src', cv2.WINDOW_NORMAL)

    # initial cap
    ret, frame = cap.read()
    width = 0
    height = 0
    if ret:
        width = frame.shape[1]
        height = frame.shape[0]

    # trackbar
    cv2.createTrackbar('pos_x', 'src', default_x, width, nothing)
    cv2.createTrackbar('pos_y', 'src', default_y, height, nothing)
    cv2.createTrackbar('scale', 'src', 7, 20, nothing)
    cv2.createTrackbar('col stride', 'src', 5, 50, nothing)
    cv2.createTrackbar('row stride', 'src', 5, 50, nothing)

    # area of 3d plot
    rec_x1 = 200
    rec_x2 = 400
    len_x = rec_x2 - rec_x1
    rec_y1 = 200
    rec_y2 = 400
    len_y = rec_y2 - rec_y1
    pixel_y = np.arange(0, width, 1)
    pixel_x = np.arange(0, height, 1)
    pixel_x, pixel_y = np.meshgrid(pixel_x, pixel_y)

    # initial plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    wf = ax.plot_wireframe(pixel_x[rec_x1:rec_x2, rec_y1:rec_y2],
                           pixel_y[rec_x1:rec_x2, rec_y1:rec_y2],
                           np.zeros((rec_x2 - rec_x1, rec_y2 - rec_y1)))

    # for fps
    frame_rate = FrameRate()
    while True:
        ret, frame = cap.read()
        key = cv2.waitKey(1)
        read_fps = frame_rate.get()

        if ret:
            cv2.rectangle(frame, (rec_x1, rec_y1), (rec_x2, rec_y2), (0, 0, 255), 5)
            # cv2.line(frame, (rec_x1, int((rec_y1+rec_y2)/2)), (rec_x2, int((rec_y1+rec_y2)/2)), (0, 0, 255), 2)
            # cv2.line(frame, (int((rec_x1+rec_x2)/2), rec_y1), (int((rec_x1+rec_x2)/2), rec_y2), (0, 0, 255), 2)
            cv2.putText(frame, str(read_fps), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
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
            plt.pause(1/fps)

        # print((rec_x1, rec_x2), (rec_y1, rec_y2))

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def beam_profile_3d_ssh():
    with open('config.json', 'r') as f:
        obj = json.load(f)

    control_ssh(obj["ssh"]["command_start"])
    beam_profile_3d()
    control_ssh(obj["ssh"]["command_end"])


if __name__ == '__main__':
    # beam_profile_3d()
    beam_profile_3d_ssh()
