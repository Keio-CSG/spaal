import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_histogram_data(csv_file: str, column: str, start_row: int, end_row: int):
    # CSVからデータを読み込む
    df = pd.read_csv(csv_file)
    
    # 指定された範囲の各行のデータを順番にプロット
    for row in range(start_row, end_row + 1):
        # 指定された列と行のデータを抽出し、空白で区切られた文字列を配列に変換
        data_str = df[column].iloc[row]
        data = list(map(int, data_str.split()))
        
        # 縦軸にプロットするデータ
        y_data = np.array(data)
        
        # 横軸のインデックスを生成
        x_data = np.arange(len(y_data))
        
        # グラフをプロット
        plt.plot(x_data, y_data, marker='o', label=f'Row {row}')
    
    plt.title('Histogram Data Plot')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.legend()
    plt.show()

# 使用例
csv_file = 'data.csv'  # CSVファイルのパス
column = 'HistData'         # 抽出したい列の名前
start_row = 3155            # 開始行（0始まりのインデックス）
end_row = 3157              # 終了行（0始まりのインデックス）
plot_histogram_data(csv_file, column, start_row, end_row)
