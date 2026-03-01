#!/usr/bin/env python3
"""
텍타일 센서 히트맵 시각화 (Thumb, Index, Middle 각 7셀).
ROS2로 /glove/tactile 구독만 하며, 별도 프로세스로 실행 시 로봇 제어에 영향 없음.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import threading

NUM_TACTILE = 21
TACTILE_PER_FINGER = 7
CELL_GRID = [(0, 1), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]


def make_tactile_cmap():
    c = ['#0000ff', '#008000', '#ff0000']
    cmap = LinearSegmentedColormap.from_list('tactile', c, N=256)
    cmap.set_bad(color='#333333', alpha=0.5)
    return cmap


def tactiles_to_grid(tactiles: list, start: int) -> np.ma.MaskedArray:
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
        self.latest = None

        self.declare_parameter('topic', '/glove/tactile')
        topic = self.get_parameter('topic').get_parameter_value().string_value
        self.sub = self.create_subscription(Float32MultiArray, topic, self.cb, 1)

        self.cmap = make_tactile_cmap()
        self.vmin, self.vmax = -100000.0, 100000.0
        self.fig, self.axes = plt.subplots(1, 3, figsize=(9, 3))
        self.fig.suptitle('Tactile Sensors (read-only)')
        titles = ['Thumb', 'Index', 'Middle']
        self.imgs = []
        for ax, title in zip(self.axes, titles):
            ax.set_title(title)
            ax.set_xticks([])
            ax.set_yticks([])
            g = np.full((3, 3), np.nan)
            im = ax.imshow(g, cmap=self.cmap, vmin=self.vmin, vmax=self.vmax, aspect='equal')
            self.imgs.append(im)
        plt.colorbar(self.imgs[0], ax=self.axes, label='kPa', shrink=0.8)
        plt.ion()
        plt.show(block=False)
        self.timer = self.create_timer(0.1, self.update_plot)

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
            for idx, im in enumerate(self.imgs):
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
