import time
import numpy as np
from pylsl import StreamInfo, StreamOutlet, cf_float32

def create_mock_eeg_stream(
    stream_name='MockEEG',
    stream_type='EEG',
    num_channels=8,
    sample_rate=250,
    source_id='myuniquesourceid12345'
):
    """
    疑似的なEEGデータをLSLストリームとして送信する関数。

    Args:
        stream_name (str): LSLストリームの名前。
        stream_type (str): LSLストリームのタイプ。
        num_channels (int): EEGチャンネル数。
        sample_rate (float): サンプリング周波数 (Hz)。
        source_id (str): ストリームのユニークID。
    """
    print(f"Creating LSL stream: {stream_name} ({stream_type})")
    print(f"  Channels: {num_channels}, Sample Rate: {sample_rate} Hz")

    # 1. ストリーム情報を定義
    # name, type, channel_count, nominal_srate, channel_format, source_id
    info = StreamInfo(
        name=stream_name,
        type=stream_type,
        channel_count=num_channels,
        nominal_srate=sample_rate,
        channel_format=cf_float32, # データ型をfloat32に指定
        source_id=source_id
    )

    # (オプション) チャンネル情報を追加することも可能
    channels = info.desc().append_child("channels")
    for i in range(num_channels):
        ch = channels.append_child("channel")
        ch.append_child_value("label", f"Ch{i+1}")
        ch.append_child_value("unit", "microvolts")
        ch.append_child_value("type", "EEG")

    # 2. ストリームアウトレットを作成
    outlet = StreamOutlet(info)
    print(f"Stream '{stream_name}' is now broadcasting.")
    print("Press Ctrl+C to stop.")

    try:
        sequence_id = 0
        while True:
            # 3. 送信する疑似EEGデータを生成 (num_channels x 1 のNumpy配列)
            # この例では、-50から50の範囲のランダムな値を生成
            mysample = (np.random.rand(num_channels) - 0.5) * 100
            
            # (オプション) 周期的なデータ（例：サイン波）を生成することも可能
            # t = time.time()
            # for i in range(num_channels):
            #     frequency = 10 + i # チャンネルごとに異なる周波数
            #     mysample[i] = 50 * np.sin(2 * np.pi * frequency * t)

            # 4. LSLタイムスタンプと共にデータを送信
            # push_sample() は自動的にLSLのタイムスタンプを付与します。
            # 明示的にタイムスタンプを指定したい場合は、
            # outlet.push_sample(mysample, pylsl.local_clock()) のようにします。
            outlet.push_sample(mysample)
            
            # print(f"Sent sample {sequence_id}: {mysample[:3]}...") # デバッグ用に一部表示
            sequence_id += 1

            # 5. サンプリングレートに合わせて待機
            time.sleep(1.0 / sample_rate)

    except KeyboardInterrupt:
        print("Stopping stream...")
    finally:
        # アウトレットを閉じる（実際にはStreamOutletオブジェクトが破棄される際に自動で行われることが多い）
        # outlet.close() # pylslには明示的なcloseメソッドはない
        print("Stream stopped.")

if __name__ == '__main__':
    # モックEEGストリームを開始
    # 例: 8チャンネル、250Hz のEEGデータ
    create_mock_eeg_stream(num_channels=8, sample_rate=250)

    # 例: 1チャンネル、10Hz のマーカーのようなデータ (タイプを'Markers'などに変更)
    # create_mock_eeg_stream(
    #     stream_name='MockMarkers',
    #     stream_type='Markers',
    #     num_channels=1,
    #     sample_rate=10
    # )