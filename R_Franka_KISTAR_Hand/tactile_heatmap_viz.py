#!/usr/bin/env python3
"""
텍타일 센서 히트맵 시각화 (Thumb, Index, Middle 각 7셀).

셀 배열 형태:
  [0]
[1][2][3]
[4][5][6]

색상: -100000=파랑, 0=초록, +100000=빨강
별도 프로세스로 실행 → target joint 발행 속도에 영향 없음.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import numpy as np
import matplotlib
matplotlib.use('QtAgg')  # GUI, 블로킹 없음
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import threading

NUM_TACTILE = 21
TACTILE_PER_FINGER = 7
# 7셀 배치: (0,1), (1,0),(1,1),(1,2), (2,0),(2,1),(2,2)
CELL_GRID = [(0, 1), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]


def make_tactile_cmap():
    """-100000 파랑, 0 초록, +100000 빨강"""
    c = ['#0000ff', '#008000', '#ff0000']  # blue, green, red
    cmap = LinearSegmentedColormap.from_list('tactile', c, N=256)
    cmap.set_bad(color='#333333', alpha=0.5)  # 빈 셀
    return cmap


def tactiles_to_grid(tactiles: list, start: int) -> np.ma.MaskedArray:
    """7개 셀 → 3x3 그리드 (빈 칸은 masked)"""
    g = np.zeros((3, 3))
    mask = np.ones((3, 3), dtype=bool)
    for i in range(TACTILE_PER_FINGER):
        r, c = CELL_GRID[i]
        g[r, c] = tactiles[start + i]
        mask[r, c] = False
    return np.ma.masked_where(mask, g)


class TactileHeatmapViz(Node):
    def __init__(self):
        super().__init__('tactile_heatmap_viz')
        self.lock = threading.Lock()
        self.latest = None  # [21] or None

        self.declare_parameter('topic', '/glove/tactile')
        topic = self.get_parameter('topic').get_parameter_value().string_value
        self.sub = self.create_subscription(Float32MultiArray, topic, self.cb, 10)

        # matplotlib 초기화
        self.cmap = make_tactile_cmap()
        self.vmin, self.vmax = -100000.0, 100000.0
        self.fig, self.axes = plt.subplots(1, 3, figsize=(9, 3))
        self.fig.suptitle('Tactile Sensors')
        titles = ['Thumb', 'Index', 'Middle']
        self.imgs = []
        for ax, title in zip(self.axes, titles):
            ax.set_title(title)
            ax.set_xticks([])
            ax.set_yticks([])
            g = np.zeros((3, 3))
            g[:] = np.nan
            im = ax.imshow(g, cmap=self.cmap, vmin=self.vmin, vmax=self.vmax, aspect='equal')
            self.imgs.append(im)
        plt.colorbar(self.imgs[0], ax=self.axes, label='kPa', shrink=0.8)
        plt.ion()
        plt.show(block=False)

        self.timer = self.create_timer(0.033, self.update_plot)  # ~30Hz 그리기

    def cb(self, msg):
        with self.lock:
            if len(msg.data) >= NUM_TACTILE:
                self.latest = list(msg.data)[:NUM_TACTILE]

    def update_plot(self):
        with self.lock:
            data = self.latest
        if data is None:
            return
        try:
            for idx, (ax, im) in enumerate(zip(self.axes, self.imgs)):
                start = idx * TACTILE_PER_FINGER
                g = tactiles_to_grid(data, start)
                im.set_data(g)
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except Exception:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = TactileHeatmapViz()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        plt.close('all')


if __name__ == '__main__':
    main()
