import io
import random
import sys
import time
from pathlib import Path
from typing import TextIO

from ssc_core import AMAX, OpCode, Word, ssc_read

# from ssc_emu import * 実行時の名前空間汚染を防止
__all__ = ["SSCEmulator", "to_signed"]


def to_signed(val: int) -> int:
    """8ビット符号なし整数を符号付き整数 (-128〜127) に変換"""
    val &= 0xFF
    return val - 256 if val >= 128 else val


class SSCEmulator:
    """Slow Scan Computer (SSC) エミュレータ"""

    def __init__(
        self,
        debug: bool = False,
        step: bool = False,
        wait_ms: int = 0,
        random_mem: bool = True,
    ):
        self.debug = debug
        self.step = step
        self.wait_ms = wait_ms
        self.memory = [
            Word(random.randint(0, 255) if random_mem else 0)
            for _ in range(AMAX)
        ]
        self.ac = random.randint(0, 255) if random_mem else 0
        self.pc = 0

    def dump_memory(self) -> None:
        """現在の全32ワードのメモリ状態を出力"""
        print("=== Memory Dump (32 Words) ===")
        for i, w in enumerate(self.memory):
            end_char = "\n" if i % 4 == 3 else "  "
            print(f"M[{i:02d}]: {w.to_bin()} ({w.v & 0xFF:3d})", end=end_char)
        print()

    def load_program(
        self, source: list[Word] | str | Path | TextIO
    ) -> None:
        """各種入力からプログラムを読み込み、メモリにセット"""
        if isinstance(source, list) and all(
            isinstance(w, Word) for w in source
        ):
            p = source[:AMAX]
            self.memory[: len(p)] = [Word(w.v) for w in p]
        else:
            if isinstance(source, str) and not Path(source).is_file():
                source = io.StringIO(source)

            if isinstance(source, (str, Path)):
                with open(source, "r", encoding="utf-8") as f:
                    ssc_read(f, memory=self.memory)
            else:
                ssc_read(source, memory=self.memory)

    def _interactive_prompt(self) -> None:
        """ステップ実行用のプロンプト"""
        print(
            " [Enter]: 次へ | d: ダンプ表示 | m <addr> <val>: メモリ変更 | ac <val>: AC変更 | pc <val>: PC変更"
        )
        while True:
            cmd = input("SSC-Debug> ").strip()
            if not cmd:
                break

            parts = cmd.split()
            op = parts[0].lower()

            try:
                if op in ("d", "dump"):
                    self.dump_memory()

                elif op == "m" and len(parts) == 3:
                    addr, val = int(parts[1]), int(parts[2], 0)
                    if 0 <= addr < AMAX:
                        self.memory[addr].v = val & 0xFF
                        print(
                            f"  -> Memory[{addr:02d}] を 0b{val & 0xFF:08b} ({val & 0xFF}) に変更しました。"
                        )
                    else:
                        print("  !! アドレス範囲外です (0〜31)")

                elif op == "ac" and len(parts) == 2:
                    val = int(parts[1], 0)
                    self.ac = val & 0xFF
                    print(
                        f"  -> AC を 0b{self.ac:08b} ({to_signed(self.ac)}) に変更しました。"
                    )

                elif op == "pc" and len(parts) == 2:
                    val = int(parts[1])
                    if 0 <= val < AMAX:
                        self.pc = val
                        print(f"  -> PC を {self.pc:02d} に変更しました。")
                    else:
                        print("  !! アドレス範囲外です (0〜31)")

                else:
                    print(
                        "  !! 不正なコマンドです。例: 'd', 'm 8 10', 'ac 5', 'pc 0'"
                    )
            except ValueError:
                print("  !! 数値の指定が不正です。")

    def run(self, input_fp: TextIO | None = None) -> None:
        """【第1回 課題1】エミュレータのメインルーチンを完成させよ

        PC(プログラムカウンタ)で指定されたメモリから命令をフェッチし、
        デコード（オペコードとアドレスの分離）を行って、各命令を実行すること。
        """
        self.pc = 0

        while True:
            curr = self.memory[self.pc]

            # -------------------------------------------------------------
            # TODO: 命令のフェッチとデコード
            #  1. curr.op (または上位3ビット) からオペコード (OpCode) を取得
            #  2. curr.addr (または下位5ビット) からアドレス値 (0-31) を取得
            # -------------------------------------------------------------
            op, addr = curr.op, curr.addr

            if self.debug:
                print(
                    f"[DEBUG] PC:{self.pc:02d} | Op:{op.name.lower():<5s} Addr:{addr:02d} | Raw:{curr.v:02x}"
                )

            if self.step:
                print(
                    f"\n--- PC: {self.pc:05b} ({self.pc:2d}) | Acc: {self.ac & 0xFF:08b} ({to_signed(self.ac):4d}) ---"
                )
                self._interactive_prompt()

            elif self.wait_ms > 0:
                time.sleep(self.wait_ms / 1000.0)

            # PCの更新 (32ワードでラップアラウンド)
            self.pc = (self.pc + 1) % AMAX

            # -------------------------------------------------------------
            # TODO: 命令の実行処理 (match-case または if-elif を使用)
            #
            # - OpCode.JUMP  : addr == 0 ならプログラム停止 (printメッセージを出力して return)。
            #                  self.ac が 0 以上なら self.pc を addr に更新。
            # - OpCode.ADD   : self.ac に memory[addr].v を加算 (& 0xFF)
            # - OpCode.SUB   : self.ac から memory[addr].v を減算 (& 0xFF)
            # - OpCode.LOAD  : memory[addr].v を self.ac にロード
            # - OpCode.STORE : self.ac の値を memory[addr].v に保存
            # - OpCode.READ  : 入力装置からの値を memory[addr].v に読み込み
            # - OpCode.WRITE : memory[addr].v の値を画面に出力
            # - OpCode.SHIFT : self.ac を addr ビット分だけ左シフト (& 0xFF)
            # -------------------------------------------------------------
            raise NotImplementedError("SSCEmulator.run() を実装してください。")


def main(
    args_list: list[str] | None = None,
    file: str | None = None,
    source_text: str | None = None,
    debug: bool | None = None,
    step: bool | None = None,
    wait_ms: int | None = None,
):
    """エミュレータのメイン関数

    CLIコマンド、パイプライン（標準入力）、PyCharm等からの直接呼び出しの
    全てに対応しています。
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="ssc_emu", description="Slow Scan Computer (SSC) Emulator"
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        default=None,
        help="Input binary file (.sso). If omitted, reads from stdin.",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug trace output"
    )
    parser.add_argument(
        "-s", "--step", action="store_true", help="Enable interactive step mode"
    )
    parser.add_argument(
        "-w",
        "--wait",
        type=int,
        default=0,
        help="Wait time between steps in milliseconds",
    )

    parsed_args = parser.parse_args(args_list)

    # パラメータの確定（関数の明示指定 > CLI引数）
    target_file = file if file is not None else parsed_args.file
    run_debug = debug if debug is not None else parsed_args.debug
    run_step = step if step is not None else parsed_args.step
    run_wait = wait_ms if wait_ms is not None else parsed_args.wait

    emu = SSCEmulator(debug=run_debug, step=run_step, wait_ms=run_wait)

    # 入力ソースの確定処理 (明示文字列 > 指定ファイル > 標準入力)
    if source_text is not None:
        emu.load_program(source_text)
    elif target_file:
        try:
            emu.load_program(target_file)
        except OSError as e:
            sys.stderr.write(f"ssc_emu: {e}\n")
            sys.exit(2)
    else:
        # 引数・指定なし：標準入力 (stdin) から読み込み
        emu.load_program(sys.stdin.read())

    try:
        emu.run()
    except NotImplementedError as e:
        print(f"\n[エラー] {e}")


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

    # --- パターン A [基本テスト]: 組込サンプルプログラムを渡して実行 ---
    main(source_text=SAMPLE_PROGRAM)

    # --- パターン B [ファイル指定]: 指定した .sso ファイルをロードして実行 ---
    # main(file="../samples/loop.sso")

    # --- パターン C [デバッグ]: トレースログを出力しながら実行 ---
    # main(file="../samples/loop.sso", debug=True)

    # --- パターン D [ステップ実行]: 1命令ごとにプロンプトを止めてレジスタ確認 ---
    # main(file="../samples/loop.sso", step=True)

    # --- パターン E [標準入力]: CLIのパイプラインや手動入力をテスト（引数なし） ---
    # main()
