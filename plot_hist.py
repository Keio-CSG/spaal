from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from matplotlib.widgets import TextBox, Button
import numpy as np

class PlotHist2:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(bottom=0.2)
        self.fig.tight_layout()
        self.signals = []
        mplstyle.use('fast')

    def record(self, signal, legitimate_signal, echoes, title):
        self.signals.append((signal, legitimate_signal, echoes, title))

    def show(self):
        # 1つのデータのみを表示する。デフォルトは最初のデータ
        # 次へボタンを押すと次のデータを表示する
        # 前へボタンを押すと前のデータを表示する
        # テキストボックスに数字を入力して移動することもできる
        # 0から前へボタンを押すと最後のデータを表示する
        # 最後から次へボタンを押すと最初のデータを表示する
        # プロット下部に、[戻る] [テキストボックス] [進む] の順に配置する
        # テキストボックスに入力された数字が無効な場合は無視する

        self.current_index = 0
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        axprev = self.fig.add_axes(rect=(0.4, 0.05, 0.2, 0.075))
        axnext = self.fig.add_axes(rect=(0.6, 0.05, 0.2, 0.075))
        axindex = self.fig.add_axes(rect=(0.1, 0.05, 0.2, 0.075))
        bnext = Button(axnext, 'Next')
        bnext.on_clicked(self.next)
        bprev = Button(axprev, 'Previous')
        bprev.on_clicked(self.prev)
        self.text_box = TextBox(axindex, 'Index', initial='0')
        self.text_box.on_submit(self.submit)
        self.plot()
        plt.show()
    
    def next(self, event):
        self.current_index += 1
        if self.current_index == len(self.signals):
            self.current_index = 0
        self.plot()

    def prev(self, event):
        self.current_index -= 1
        if self.current_index == -1:
            self.current_index = len(self.signals) - 1
        self.plot()

    def submit(self, text):
        try:
            index = int(text)
            if 0 <= index < len(self.signals):
                self.current_index = index
                self.plot()
        except:
            pass

    def plot(self):
        signal, legitimate_signal, echoes, title = self.signals[self.current_index]
        self.ax.clear()
        self.fig.subplots_adjust(bottom=0.2)
        self.ax.plot(signal, color='blue')
        self.ax.plot(legitimate_signal, color='green')
        self.ax.scatter([x[0].peak_position for x in echoes], [x[0].peak_height for x in echoes], color='red')
        self.ax.set_title(title)
        for i, x in enumerate(echoes):
            self.ax.axvline(x=x[0].peak_position - x[0].width/2, color='green', linestyle='--')
            self.ax.axvline(x=x[0].peak_position + x[0].width/2, color='green', linestyle='--')
            self.ax.text(x[0].peak_position, x[0].peak_height, f'{i}', color='red', size=30)
            if len(x) == 4:
                for e in x:
                    self.ax.text(e.peak_position, e.peak_height, f'{i}', color='blue', size=10)

    def on_key(self, event):
        if event.key == 'enter':
            try:
                index = int(event.inaxes.get_children()[0].get_text().split(': ')[1])
                if 0 <= index < len(self.signals):
                    self.current_index = index
                    self.plot()
                    plt.draw()
            except:
                pass

        elif event.key == 'right':
            self.current_index += 1
            if self.current_index == len(self.signals):
                self.current_index = 0
            self.plot()
            plt.draw()

        elif event.key == 'left':
            self.current_index -= 1
            if self.current_index == -1:
                self.current_index = len(self.signals) - 1
            self.plot()
            plt.draw()

        elif event.key == 'up':
            self.current_index = 0
            self.plot()
            plt.draw()

        elif event.key == 'down':
            self.current_index = len(self.signals) - 1
            self.plot()
            plt.draw()

        elif event.key == 'escape':
            plt.close()

        plt.draw()

class PlotHist:
    def __init__(self, shape: Tuple[int, int]):
        self.shape = shape
        self.fig, self.ax = plt.subplots(shape[0], shape[1], figsize=(shape[0] * 5, shape[1] * 5))
        self.fig.tight_layout()
        self.current_index = 0

    def plot(self, signal, legitimate_signal, echoes, title):
        ax = self.ax[self.current_index // self.shape[1], self.current_index % self.shape[1]]
        ax.bar(np.arange(len(signal)), signal, width=1.0)
        ax.bar(np.arange(len(legitimate_signal)), legitimate_signal, width=1.0, color='green')
        ax.scatter([x[0].peak_position for x in echoes], [x[0].peak_height for x in echoes], color='red')
        ax.set_title(title)
        for i, x in enumerate(echoes):
            ax.axvline(x=x[0].peak_position - x[0].width/2, color='green', linestyle='--')
            ax.axvline(x=x[0].peak_position + x[0].width/2, color='green', linestyle='--')
            ax.text(x[0].peak_position, x[0].peak_height, f'{i}', color='red', size=30)
            if len(x) == 4:
                for e in x:
                    ax.text(e.peak_position, e.peak_height, f'{i}', color='blue', size=10)
        self.current_index += 1

        if self.current_index == self.shape[0] * self.shape[1]:
            plt.show()
            self.fig, self.ax = plt.subplots(self.shape[0], self.shape[1], figsize=(self.shape[0] * 5, self.shape[1] * 5))
            self.current_index = 0