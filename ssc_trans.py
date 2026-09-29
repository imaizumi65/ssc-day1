import sys
from ssc_core import AMAX, OpCode, Word


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
    """CLIおよびPyCharm等の直接呼び出しに対応したメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="ssc_trans", description="SSC Translator (1-Pass Translator)"
    )
    parser.add_argument(
        "file", nargs="?", type=str, default=None, help="Input .sss file"
    )

    parsed_args = parser.parse_args(args_list)
    target_file = file if file is not None else parsed_args.file

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

    for i, w in enumerate(translated_mem):
        print(f"{i:02d}: {w.to_bin()}")


if __name__ == "__main__":
    main()
