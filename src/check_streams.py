#!/usr/bin/env python
# filepath: /home/neuron/Documents/lsl-rt-analyzer/src/check_streams.py
import time
from pylsl import resolve_streams

def print_all_lsl_streams():
    """利用可能なすべてのLSLストリームを表示する"""
    print("利用可能なLSLストリームを検索しています...")
    
    # すべてのストリームを検索（引数なしで検索）
    all_streams = resolve_streams()
    
    if not all_streams:
        print("LSLストリームが見つかりませんでした。")
        return
    
    print(f"{len(all_streams)}個のLSLストリームが見つかりました:")
    for i, stream in enumerate(all_streams):
        print(f"\nストリーム {i+1}:")
        print(f"  名前: {stream.name()}")
        print(f"  タイプ: {stream.type()}")
        print(f"  チャンネル数: {stream.channel_count()}")
        print(f"  サンプリングレート: {stream.nominal_srate()} Hz")
        print(f"  ソースID: {stream.source_id()}")
        print(f"  ホスト: {stream.hostname()}")

if __name__ == "__main__":
    # ストリーム情報を表示
    print_all_lsl_streams()
    
    # 5秒待って再度検索（ストリームが遅れて現れる場合に対応）
    print("\n5秒後に再度検索します...")
    time.sleep(5)
    print_all_lsl_streams()
