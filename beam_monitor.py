import numpy as np
import matplotlib.pyplot as plt
import cv2
import json

from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm

from get_fps import FrameRate
from ssh import control_ssh


def nothing(x):
    """
    nothing function
    """

    pass


def beam_profile_3d():
    """
    ストリーミングサーバーからフレームを取得、加工、表示する
    """

    # jsonファイルから各種パラメータを抽出
    with open('config.json', 'r') as f:
        obj = json.load(f)
        # ストリーミングサーバのURL
        stream_url = "http://" + obj["monitor"]["ip"] + ":" + str(obj["monitor"]["port"]) + "/" + obj["monitor"]["query"]
        # プロット領域の初期位置(x座標)
        default_x = obj["monitor"]["default_x"]
        # プロット領域の初期位置(y座標)
        default_y = obj["monitor"]["default_y"]
        # fpsの設定値
        fps = obj["monitor"]["fps"]

    # ストリーミングサーバからcaptureオブジェクトを作成
    cap = cv2.VideoCapture(stream_url)

    # ウィンドウの作成
    # フレーム表示用
    cv2.namedWindow('src', cv2.WINDOW_AUTOSIZE)
    # トラックバー用
    cv2.namedWindow('palette')

    # 1フレーム読み込み
    ret, frame = cap.read()
    width = 0
    height = 0
    if ret:
        width = frame.shape[1]
        height = frame.shape[0]

    # トラックバーを作成
    # プロット領域の位置(x座標)
    cv2.createTrackbar('pos_x', 'palette', default_x, width, nothing)
    # プロット領域の位置(y座標)
    cv2.createTrackbar('pos_y', 'palette', default_y, height, nothing)
    # プロット領域のスケール
    cv2.createTrackbar('scale', 'palette', 7, 20, nothing)
    # プロット点の列間隔
    cv2.createTrackbar('col stride', 'palette', 5, 50, nothing)
    # プロット点の行間隔
    cv2.createTrackbar('row stride', 'palette', 5, 50, nothing)

    # 3Dグラフを表示する範囲の設定
    rec_x1 = 200
    rec_x2 = 400
    len_x = rec_x2 - rec_x1
    rec_y1 = 200
    rec_y2 = 400
    len_y = rec_y2 - rec_y1
    pixel_y = np.arange(0, width, 1)
    pixel_x = np.arange(0, height, 1)
    pixel_x, pixel_y = np.meshgrid(pixel_x, pixel_y)

    # 初期プロット
    fig = plt.figure()
    # axesオブジェクト
    ax = fig.add_subplot(111, projection='3d')
    # 3D-wireframeプロット
    wf = ax.plot_wireframe(pixel_x[rec_x1:rec_x2, rec_y1:rec_y2],
                           pixel_y[rec_x1:rec_x2, rec_y1:rec_y2],
                           np.zeros((rec_x2 - rec_x1, rec_y2 - rec_y1)))

    # FrameRateクラスのオブジェクトを生成
    frame_rate = FrameRate()
    while True:
        ret, frame = cap.read()
        # キーボードからの入力を受け付け
        key = cv2.waitKey(1)
        # fpsの取得
        read_fps = frame_rate.get()

        if ret:
            # 3Dプロット領域を表示
            cv2.rectangle(frame, (rec_x1, rec_y1), (rec_x2, rec_y2), (0, 0, 255), 5)

            # cv2.line(frame, (rec_x1, int((rec_y1+rec_y2)/2)), (rec_x2, int((rec_y1+rec_y2)/2)), (0, 0, 255), 2)
            # cv2.line(frame, (int((rec_x1+rec_x2)/2), rec_y1), (int((rec_x1+rec_x2)/2), rec_y2), (0, 0, 255), 2)

            # フレームの左上にfpsを表示
            cv2.putText(frame, str(read_fps), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

            # トラックバーからの値を読み出し
            pos_x = cv2.getTrackbarPos('pos_x', 'palette')
            pos_y = cv2.getTrackbarPos('pos_y', 'palette')
            pos_s = cv2.getTrackbarPos('scale', 'palette')
            c_stride = cv2.getTrackbarPos('col stride', 'palette')
            r_stride = cv2.getTrackbarPos('row stride', 'palette')

            rec_x1 = pos_x + (len_x - int(len_x*pos_s/10))
            rec_x2 = pos_x + len_x - (len_x - int(len_x*pos_s/10))

            rec_y1 = pos_y + (len_y - int(len_y*pos_s/10))
            rec_y2 = pos_y + len_y - (len_y - int(len_y*pos_s/10))
            
            # ウィンドウ"src"にフレームを表示
            cv2.imshow('src', frame)
            old_wf = wf

            # 軸の上限の設定
            # y軸
            ax.set_ylim(rec_y1, rec_y2)
            # x軸
            ax.set_xlim(rec_x1, rec_x2)
            # z軸
            ax.set_zlim(0, 255)

            # ビューの視点変更
            # ax.view_init(45, 90)

            if rec_x1 > 0 and rec_x2 < width and rec_y1 > 0 and rec_y2 < height:
                # 3D-wireframeプロット(設定された領域のみ表示)
                wf = ax.plot_wireframe(pixel_y[rec_x1:rec_x2, rec_y1:rec_y2],
                                       pixel_x[rec_x1:rec_x2, rec_y1:rec_y2],
                                       frame[rec_y1:rec_y2, rec_x1:rec_x2, 0],
                                       cstride=c_stride, rstride=r_stride)
            
                # 古いwireframeオブジェクトを削除
                ax.collections.remove(old_wf)
            
            # 次の読み出しまで 1/fps[s]待つ
            plt.pause(1/fps)

        # print((rec_x1, rec_x2), (rec_y1, rec_y2))

        # キーボード"q"が押されたときにループを抜ける
        if key == ord('q'):
            break

    # captureをリリース
    cap.release()

    # すべてのウィンドウを消去
    cv2.destroyAllWindows()


def beam_profile_3d_ssh():
    """
    """
    with open('config.json', 'r') as f:
        obj = json.load(f)

    # command_start 実行
    control_ssh(obj["ssh"]["command_start"])
    # フレーム表示 & 3D-wireframeプロット
    beam_profile_3d()
    # command_end 実行
    control_ssh(obj["ssh"]["command_end"])


if __name__ == '__main__':
    # beam_profile_3d()
    beam_profile_3d_ssh()
