# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import sys
import cv2

# 適宜変更
STREAM_URL = 'http://192.168.0.27:8080/?action=stream'


class GraphWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(GraphWindow, self).__init__(parent)
        # カメラデバイスをオープン
        self.cap = cv2.VideoCapture(0)
        # self.cap = cv2.VideoCapture(STREAM_URL)
        _, frame = self.cap.read()
        # frame[y, x]であることに注意
        self.width = frame.shape[1]
        self.height = frame.shape[0]

        # 3次元プロットのためのウィジェット
        self.w = gl.GLViewWidget()
        self.w.setWindowTitle('3D animation plot')
        # ウィンドウ出現場所、ウィンドウサイズ
        self.w.setGeometry(110, 110, 1200, 800)
        # 3次元プロットを観測するカメラの場所
        self.w.setCameraPosition(distance=np.sqrt(self.width**2 + self.height)*1.5)
        self.w.show()

        # x平面
        gx = gl.GLGridItem()
        # 回転
        gx.rotate(90, 0, 1, 0)
        # 移動
        gx.translate(-self.height/2, 0, 0)
        # スケール
        gx.scale(self.height/20, self.width/20, 1)
        self.w.addItem(gx)

        # y平面
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -self.width/2, 0)
        gy.scale(self.height/20, self.height/20, 1)
        self.w.addItem(gy)

        # z平面
        gz = gl.GLGridItem()
        gz.translate(0, 0, -self.height/2)
        gz.scale(self.height/20, self.width/20, 1)
        self.w.addItem(gz)

        # 画素値をいくつ読みとばすか（大きいほど処理が軽いが、精度に欠ける）
        self.step = 8
        self.x = np.arange(0, self.width, 1)
        self.y = np.arange(0, self.height, 1)
        # データの用意
        self.p = gl.GLSurfacePlotItem(x=self.y[0:self.height:self.step], y=self.x[0:self.width:self.step],
                                      z=np.zeros((int(self.height/self.step), int(self.width/self.step))),
                                      shader='normalColor')
        self.p.translate(-self.height/2, -self.width/2, 0)
        # データのフレームを設定
        self.w.addItem(self.p)
        # タイマーの用意
        self.timer = QtCore.QTimer()

    def __del__(self):
        # カメラのリリース
        self.cap.release()

    def update(self):
        # 一枚読み込む
        frame = self.capture()
        if frame is not None:
            # frame[, , x]  x=0->B x=1->G x=2->R
            # データをセットする(処理を軽くするためにstepごとに読み飛ばしてからセットする)
            self.p.setData(z=frame[0:self.height:self.step, 0:self.width:self.step, 2])

    def capture(self):
        # ret->読み込みに成功したかどうか
        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            return None

    def start(self):
        # タイマーでupdate関数を50ms秒ごとに呼び出すよう設定
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def stop(self):
        # タイマーを解除
        self.timer.disconnect()


if __name__ == '__main__':
    # アプリケーションを作成
    app = QtGui.QApplication([])
    # インスタンス呼び出し
    graphWindow = GraphWindow()
    # タイマースタート
    graphWindow.start()
    # ループ開始
    sys.exit(app.exec_())

