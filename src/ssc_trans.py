import io
import sys
from pathlib import Path

from ssc_core import AMAX, OpCode, Word, ssc_write

# from ssc_trans import * 実行時の名前空間汚染を防止
__all__ = ["SSCTranslator"]


class SSCTranslator:
    """簡易記法 (J/0, L/5, D/3 等) を機械語 (Wordのリスト) に変換する1パス・トランスレータ"""

    OP_CHAR_MAP = {
        "J": OpCode.JUMP,
        "A": OpCode.ADD,
        "B": OpCode.SUB,
        "L": OpCode.LOAD,
        "T": OpCode.STORE,
        "R": OpCode.READ,
        "W": OpCode.WRITE,
        "S": OpCode.SHIFT,
    }

    def translate(
        self, source_text: str, memory: list[Word] | None = None
    ) -> list[Word]:
        """ソース文字列をパースし、指定されたメモリ配列に結果を上書きして返す"""
        if memory is None:
            memory = []

        target_mem = (
            [w.copy() for w in memory] + [Word(0) for _ in range(AMAX)]
        )[:AMAX]

        lines = source_text.splitlines()
        pc = 0

        for line_num, raw_line in enumerate(lines, 1):
            line = raw_line.split(";")[0].strip()
            if not line:
                continue

            if pc >= AMAX:
                raise SyntaxError(
                    f"Line {line_num}: Program size exceeds maximum memory size ({AMAX} words)"
                )

            parts = [p.strip() for p in line.split("/")]

            if len(parts) == 2:
                op_char, addr_str = parts[0].upper(), parts[1]
            else:
                space_parts = line.split()
                if len(parts) == 1 and len(space_parts) == 2:
                    op_char, addr_str = (
                        space_parts[0].upper(),
                        space_parts[1],
                    )
                    sys.stderr.write(
                        f"Warning (Line {line_num}): Missing '/' in '{line}'. "
                        f"Interpreted as '{op_char}/{addr_str}'.\n"
                    )
                else:
                    raise SyntaxError(
                        f"Line {line_num}: Invalid line format '{line}'"
                    )

            # D/数値 の場合は指定された数値をそのまま8ビットデータとして埋め込む
            if op_char == "D":
                try:
                    val = int(addr_str, 0)
                except ValueError:
                    raise SyntaxError(
                        f"Line {line_num}: Invalid data value '{addr_str}'"
                    )
                target_mem[pc] = Word(val & 0xFF)
            else:
                # 通常命令 (J, A, B, L, T, R, W, S) の処理
                try:
                    op = self.OP_CHAR_MAP[op_char]
                    addr = int(addr_str, 0)
                except KeyError:
                    raise SyntaxError(
                        f"Line {line_num}: Unknown opcode '{op_char}'"
                    )
                except ValueError:
                    raise SyntaxError(
                        f"Line {line_num}: Invalid address '{addr_str}'"
                    )

                w = Word()
                w.op = op
                w.addr = addr & 0x1F
                target_mem[pc] = w

            pc += 1

        return target_mem


def main(
    args_list: list[str] | None = None,
    file: str | None = None,
    source_text: str | None = None,
):
    """トランスレータのメイン関数

    CLIコマンド、パイプライン（標準入力）、PyCharm等からの直接呼び出しの
    全てに対応しています。
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="ssc_trans", description="SSC Translator (1-Pass Translator)"
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        default=None,
        help="Input .sss file (default: stdin)",
    )

    parsed_args = parser.parse_args(args_list)
    target_file = file if file is not None else parsed_args.file

    # 入力ソースの確定処理 (明示文字列 > 指定ファイル > 標準入力)
    if source_text is None:
        if target_file:
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    source_text = f.read()
            except OSError as e:
                sys.stderr.write(f"ssc_trans: {e}\n")
                sys.exit(2)
        else:
            source_text = sys.stdin.read()

    translator = SSCTranslator()
    try:
        translated_mem = translator.translate(source_text)
    except SyntaxError as e:
        sys.stderr.write(f"ssc_trans error: {e}\n")
        sys.exit(1)

    ssc_write(translated_mem, sys.stdout)


# デフォルトのセルフテスト用サンプルプログラム
SAMPLE_PROGRAM = """L/5
A/6
T/7
W/7
J/0
D/3
D/5
D/255
"""


if __name__ == "__main__":
    # =========================================================================
    # 【PyCharm / IDE デバッグ時の使い方ガイド】
    #
    # IDE（PyCharm等）からこのファイルを直接「Run / Debug」する場合、
    # カレントディレクトリは src/ になるため、samples/ へのパスには `../` を付けます。
    # =========================================================================

    # --- パターン A [基本テスト]: 組込サンプルプログラムを渡して変換 ---
    main(source_text=SAMPLE_PROGRAM)

    # --- パターン B [ファイル指定]: 指定した .sss ファイルをロードして変換 ---
    # main(file="../samples/add.sss")

    # --- パターン C [標準入力]: CLIのパイプラインや手動入力をテスト（引数なし） ---
    # main()
