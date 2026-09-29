import sys
from ssc_core import AMAX, Word, ssc_read

# 命令名・文字テーブル
SSC_OP_CHARS = ["J", "A", "B", "L", "T", "R", "W", "S"]
SSC_OP_NAMES = ["JUMP", "ADD", "SUB", "LOAD", "STORE", "READ", "WRITE", "SHIFT"]


class SSCDisassembler:
    """【第1回 課題2】簡易ディスアセンブラ"""

    def disassemble(self, memory: list[Word]) -> str:
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


def main(
    args_list: list[str] | None = None,
    file: str | None = None,
):
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="ssc_dis", description="SSC Disassembler (1-to-1 Disassembler)"
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        default=None,
        help="Input .sso file (default: stdin)",
    )

    parsed_args = parser.parse_args(args_list)
    target_file = file if file is not None else parsed_args.file

    if target_file:
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
        if fp is not sys.stdin:
            fp.close()

    disassembler = SSCDisassembler()
    try:
        result = disassembler.disassemble(memory)
        if result:
            print(result)
    except NotImplementedError as e:
        sys.stderr.write(f"ssc_dis error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
