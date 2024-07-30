import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def extract_segments(data):
    """データからメインとサブのセグメントを抽出する"""
    non_zero_indices = [i for i, x in enumerate(data) if x != 0]
    if not non_zero_indices:
        return [], []
    
    start_idx = non_zero_indices[0]
    end_idx = non_zero_indices[-1] + 1
    data = data[start_idx:end_idx]

    main = []
    subs = []
    current_segment = []
    in_main = False
    
    for i, value in enumerate(data):
        if value > 0:
            current_segment.append(value)
            if value == max(data):
                in_main = True
        else:
            if current_segment:
                # Add a zero before the segment if it's the start of the array or the previous value was non-zero
                if i == 0 or data[i-1] != 0:
                    current_segment.insert(0, 0)
                # Add a zero after the segment if it's the end of the array or the next value is non-zero
                if i == len(data) - 1 or data[i+1] != 0:
                    current_segment.append(0)
                if in_main:
                    main.append(current_segment)
                    in_main = False
                else:
                    subs.append(current_segment)
                current_segment = []
    
    if current_segment:
        # Add a zero after the last segment
        current_segment.append(0)
        if in_main:
            main.append(current_segment)
        else:
            subs.append(current_segment)
    
    return main, subs

def plot_histogram_data(csv_file: str, column: str, start_row: int, end_row: int):
    # CSVからデータを読み込む
    df = pd.read_csv(csv_file)
    
    all_main = []
    all_subs = []
    
    for row in range(start_row, end_row + 1):
        # 指定された列と行のデータを抽出し、空白で区切られた文字列を配列に変換
        data_str = df[column].iloc[row]
        data = list(map(int, data_str.split()))
        
        # メインとサブのセグメントを抽出
        main, subs = extract_segments(data)
        
        # メインとサブのデータを集める
        all_main.extend(main)
        all_subs.extend(subs)
    
    # メインのプロット
    plt.figure()
    for segment in all_main:
        plt.plot(range(len(segment)), segment, label='Main Segment', alpha=0.7)
    plt.title('Main Segments from Selected Rows')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.legend()
    plt.show()
    
    # サブのプロット
    plt.figure()
    for segment in all_subs:
        plt.plot(range(len(segment)), segment, label='Sub Segment', alpha=0.7)
    plt.title('Sub Segments from Selected Rows')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.legend()
    plt.show()

# 使用例
csv_file = 'data.csv'  # CSVファイルのパス
column = 'HistData'         # 抽出したい列の名前
start_row = 3150               # 開始行（0始まりのインデックス）
end_row = 3160                 # 終了行（0始まりのインデックス）
plot_histogram_data(csv_file, column, start_row, end_row)
