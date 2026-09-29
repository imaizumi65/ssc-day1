import io
import random
import time
from pathlib import Path
from typing import TextIO

from ssc_core import AMAX, OpCode, Word, ssc_read


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


if __name__ == "__main__":
    # セルフテスト用サンプルプログラム (J/12, L/13 ... 相当のバイナリ)
    SAMPLE_PROGRAM = """
 0(00000): 10101100
 1(00001): 01101111
 2(00010): 10001101
 3(00011): 01101100
 4(00100): 11100001
 5(00101): 10001100
 6(00110): 11001100
 7(00111): 01101101
 8(01000): 01001110
 9(01001): 10001101
10(01010): 00000011
11(01011): 00000000
12(01100): 00000000
13(01101): 00000000
14(01110): 00000001
15(01111): 00001000
"""
    print("=== [SSC Emulator Self-Test] ===")
    emu = SSCEmulator(debug=False, step=False, wait_ms=100)
    emu.load_program(SAMPLE_PROGRAM)

    print("\n--- 実行前メモリダンプ ---")
    emu.dump_memory()

    try:
        emu.run()
    except NotImplementedError as e:
        print(f"\n[エラー] {e}")

    print("\n--- 実行後最終メモリダンプ ---")
    emu.dump_memory()
