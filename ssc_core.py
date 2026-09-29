from dataclasses import dataclass
from enum import IntEnum
from typing import TextIO

AMAX = 32


class OpCode(IntEnum):
    JUMP = 0
    ADD = 1
    SUB = 2
    LOAD = 3
    STORE = 4
    READ = 5
    WRITE = 6
    SHIFT = 7


OPCODES: dict[str, int] = {op.name.lower(): op.value for op in OpCode}


@dataclass
class Word:
    v: int = 0

    def __post_init__(self):
        self.v &= 0xFF

    def copy(self) -> "Word":
        """自身のディープコピー（独立した別インスタンス）を生成して返す"""
        return Word(self.v)

    @property
    def op(self) -> OpCode:
        return OpCode((self.v >> 5) & 0x07)

    @op.setter
    def op(self, code: OpCode | int) -> None:
        self.v = ((int(code) & 0x07) << 5) | (self.v & 0x1F)

    @property
    def addr(self) -> int:
        return self.v & 0x1F

    @addr.setter
    def addr(self, address: int) -> None:
        self.v = (self.v & 0xE0) | (address & 0x1F)

    def to_bin(self) -> str:
        """8ビットの2進数文字列を返す"""
        return f"{self.v:08b}"


def dtob(n: int) -> str:
    """整数値を8桁の2進数文字列（負数はワイルドカード）に変換"""
    return "********" if n < 0 else f"{n & 0xFF:08b}"


def ssc_read(fp: TextIO, memory: list[Word] | None = None) -> list[Word]:
    """ファイルオブジェクトからプログラムを読み込んでメモリを更新・生成"""
    if memory is None:
        memory = [Word() for _ in range(AMAX)]

    first_line = fp.readline()

    if not first_line:
        return memory

    if first_line.startswith("SSC"):
        raw_bytes = fp.buffer.read() if hasattr(fp, "buffer") else b""
        for i, b in enumerate(raw_bytes[:AMAX]):
            memory[i] = Word(b)
        return memory

    lines = [first_line] + fp.readlines()
    for line in lines:
        clean_line = line.split(";")[0].strip()
        if not clean_line or ":" not in clean_line:
            continue

        addr_part, code_part = clean_line.split(":", 1)
        try:
            addr_str = addr_part.split("(")[0].strip()
            addr = int(addr_str)
            code_str = code_part.replace(" ", "").strip()

            if 0 <= addr < AMAX and code_str:
                memory[addr] = Word(int(code_str, 2))
        except (ValueError, IndexError):
            continue

    return memory


def ssc_write(memory: list[Word], fp: TextIO) -> None:
    """32ワードのメモリ内容をSSC標準テキスト形式 (.sso) でファイルオブジェクトに出力"""
    for i in range(AMAX):
        if i < len(memory):
            w = memory[i]
            val = w.v if isinstance(w, Word) else int(w)
        else:
            val = 0
        fp.write(f"{i:2d}({i:05b}): {val & 0xFF:08b}\n")
