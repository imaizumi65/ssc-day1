import io
import sys
from pathlib import Path

from ssc_core import AMAX, Word, ssc_read

# from ssc_dis import * 実行時の名前空間汚染を防止
__all__ = ["SSCDisassembler", "Role", "SSC_OP_NAMES", "SSC_OP_CHARS"]

# オペレーション名テーブル
SSC_OP_NAMES = ["JUMP", "ADD", "SUB", "LOAD", "STORE", "READ", "WRITE", "SHIFT"]
SSC_OP_CHARS = ["J", "A", "B", "L", "T", "R", "W", "S"]


class SSCDisassembler:
    """【第1回 課題2】簡易ディスアセンブラ"""


    def disassemble(self, memory: list[Word], lflag: bool = False) -> str:
        """【第1回 課題2】メモリ配列を受け取り、簡易表記形式の文字列を返せ

        例: 各ワードからオペコードとアドレスを取り出し、"L/5" や "J/0"
        のような形式の行を作成して改行で結合して返す。
        """

        output_lines = []

        # -------------------------------------------------------------
        # TODO: メモリの内容(32ワード)を順に読み出し、簡易表記に変換せよ
        #  1. Word オブジェクトから op (0-7) と addr (0-31) を取得
        #  2. SSC_OP_CHARS[op] を用いて "J/0" や "L/5" などの文字列を作成
        #  3. output_lines リストに追加し、最後に "\n".join(output_lines) で返す
        # -------------------------------------------------------------
        raise NotImplementedError("SSCDisassembler.disassemble() を実装してください。")
        return "\n".join(output_lines)


def main(
    args_list: list[str] | None = None,
    file: str | None = None,
    source_text: str | None = None,
    lflag: bool | None = None,
):
    """ディスアセンブラのメイン関数

    CLIコマンド、パイプライン（標準入力）、PyCharm等からの直接呼び出しの
    全てに対応しています。
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="ssc_dis", description="SSC Disassembler (Reverse Translator)"
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        default=None,
        help="Input SSC binary (.sso) file (default: stdin)",
    )

    # 1. CLI引数のパース
    parsed_args = parser.parse_args(args_list)

    # 2. パラメータの確定（関数の明示指定 > CLI引数）
    target_file = file if file is not None else parsed_args.file

    # 3. 入力ソースの確定処理 (明示文字列 > 指定ファイル > 標準入力)
    if source_text is not None:
        fp = io.StringIO(source_text)
    elif target_file:
        try:
            fp = open(target_file, "r", encoding="utf-8", errors="ignore")
        except OSError as e:
            sys.stderr.write(f"ssc_dis: {e}\n")
            sys.exit(2)
    else:
        fp = sys.stdin

    try:
        memory = ssc_read(fp)
    except Exception as e:
        sys.stderr.write(f"ssc_dis: program format error ({e})\n")
        sys.exit(3)
    finally:
        if fp is not sys.stdin and not isinstance(fp, io.StringIO):
            fp.close()

    disassembler = SSCDisassembler()
    try:
        result = disassembler.disassemble(memory, lflag=use_lflag)
        if result:
            print(result)
    except NotImplementedError as e:
        sys.stderr.write(f"ssc_dis error: {e}\n")
        sys.exit(1)


# デフォルトのセルフテスト用サンプルプログラム
SAMPLE_PROGRAM = """
 0(00000): 01100101  ; L/5 (アドレス5の「3」をロード)
 1(00001): 00100110  ; A/6 (アドレス6の「5」を加算)
 2(00010): 10000111  ; T/7 (アドレス7に「8」を保存)
 3(00011): 11000111  ; W/7 (アドレス7の「8」を出力)
 4(00100): 00000000  ; J/0 (プログラム停止)
 5(00101): 00000011  ; データ: 3
 6(00110): 00000101  ; データ: 5
 7(00111): 11111111  ; データ: ダミー初期値 (書き換え確認用)
"""


if __name__ == "__main__":
    # =========================================================================
    # 【PyCharm / IDE デバッグ時の使い方ガイド】
    #
    # IDE（PyCharm等）からこのファイルを直接「Run / Debug」する場合、
    # カレントディレクトリは src/ になるため、samples/ へのパスには `../` を付けます。
    # =========================================================================

    # --- パターン A [基本テスト]: 組込サンプルプログラムを渡して逆アセンブル ---
    main(source_text=SAMPLE_PROGRAM)

    # --- パターン B [ファイル指定]: 指定した .sso ファイルを逆アセンブル ---
    # main(file="../samples/loop.sso")

    # --- パターン C [標準入力]: CLIのパイプラインや手動入力をテスト（引数なし） ---
    # main()

