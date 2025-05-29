import asyncio
import time
from pylsl import StreamInlet, resolve_streams
import numpy as np

# EEGデータ受信部からデータ処理部へのキュー
raw_eeg_queue = asyncio.Queue()

# データ処理部からデータ送信部へのキュー
processed_data_queue = asyncio.Queue()

# --- EEGデータ受信部 (LSL Client) ---
async def lsl_receiver_task():
    print("LSLストリームを検索中...")
    # 十分なタイムアウトを設定（10秒）して全ストリームを検索
    streams = resolve_streams()
    
    if not streams:
        print("LSLストリームが見つかりませんでした。")
        print("モックEEGストリームを起動するか、別のEEGデバイスを接続してください。")
        return
    
    # 見つかったストリームの情報を表示（デバッグ用）
    print(f"{len(streams)}個のLSLストリームが見つかりました:")
    for i, stream in enumerate(streams):
        print(f"ストリーム {i+1}: 名前={stream.name()}, タイプ={stream.type()}, チャンネル数={stream.channel_count()}")
    
    # EEGタイプのストリームをフィルタリング
    eeg_streams = [stream for stream in streams if stream.type() == 'EEG']
    
    if not eeg_streams:
        print("EEGタイプのストリームが見つかりませんでした。")
        print("モックEEGストリームを起動するか、別のEEGデバイスを接続してください。")
        return
    
    # 最初のEEGストリームを使用
    inlet = StreamInlet(eeg_streams[0])
    print(f"EEGストリーム '{eeg_streams[0].name()}' に接続しました")
    print(f"チャンネル数: {inlet.info().channel_count()}")
    print(f"サンプリングレート: {inlet.info().nominal_srate()} Hz")
    
    while True:
        # タイムアウトを少し長めに設定（1秒）
        sample, timestamp = inlet.pull_sample(timeout=1.0)
        if sample:
            await raw_eeg_queue.put((timestamp, sample))
            # デバッグ用に最初のサンプルを表示
            print(f"受信: time={timestamp:.3f}, data={sample[:3]}...")
        await asyncio.sleep(0.001)  # 他のタスクに実行を譲る

# --- データ処理部 (Processing Engine) ---
async def processing_task():
    while True:
        timestamp, sample = await raw_eeg_queue.get()
        # シンプルな処理として、各チャンネルの値、平均値、標準偏差を計算
        sample_array = np.array(sample)
        mean_value = np.mean(sample_array)
        std_value = np.std(sample_array)
        
        # 処理結果を作成
        processed_result = {
            "timestamp": timestamp,
            "raw_data": sample,
            "mean": mean_value,
            "std": std_value
        }
        
        # 処理結果をキューに入れる
        await processed_data_queue.put(processed_result)
        raw_eeg_queue.task_done()  # キューのタスク完了を通知

# --- データ出力部 (Console Output) ---
async def console_output_task():
    print("データ出力を開始します...")
    while True:
        processed_data = await processed_data_queue.get()
        # 標準出力にデータを表示
        print(f"時刻: {processed_data['timestamp']:.3f}s")
        print(f"平均値: {processed_data['mean']:.3f}")
        print(f"標準偏差: {processed_data['std']:.3f}")
        print("-" * 50)
        processed_data_queue.task_done()

# メインの非同期処理の実行
async def main():
    # 各タスクを起動
    receiver_task = asyncio.create_task(lsl_receiver_task())
    processor_task = asyncio.create_task(processing_task())
    output_task = asyncio.create_task(console_output_task())
    
    try:
        # メインループ - 終了するまで待機
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nプログラムを終了します...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        # タスクをクリーンアップ
        for task in [receiver_task, processor_task, output_task]:
            if not task.done():
                task.cancel()
        
        # タスクが完了するまで待機
        await asyncio.gather(*[receiver_task, processor_task, output_task], 
                             return_exceptions=True)
        print("すべてのタスクが終了しました。")

if __name__ == "__main__":
    asyncio.run(main())