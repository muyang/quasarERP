#!/usr/bin/env python3
"""
Quasar ERP — 授权注册机 (命令行版)
- CLI: keygen.py --generate-5000  (初始化 5000 个授权码)
- CLI: keygen.py --check <key>    (验证授权码)
- 交互式: python3 keygen.py       (输入 1-10 从可用池中随机抽取)
"""

import random
import os
import sys
from datetime import datetime

CHARS = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
SEGMENTS = 4
SEG_LEN = 4
LICENSE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(LICENSE_DIR, "licenses.txt")
BATCH_SIZE = 5000


def generate_raw_key():
    parts = ["".join(random.choices(CHARS, k=SEG_LEN)) for _ in range(SEGMENTS)]
    return "QUASAR-" + "-".join(parts)


def get_pool():
    available, used = [], []
    if not os.path.exists(LICENSE_FILE):
        return available, used
    with open(LICENSE_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) >= 2 and parts[1] == "available":
                available.append(parts[0])
            else:
                used.append(line)
    return available, used


def save_pool(available, used):
    with open(LICENSE_FILE, "w") as f:
        for k in available:
            f.write(f"{k},available\n")
        for entry in used:
            f.write(f"{entry}\n")


def generate_5000():
    print(f"Generating {BATCH_SIZE} license keys...")
    keys = set()
    while len(keys) < BATCH_SIZE:
        keys.add(generate_raw_key())
    with open(LICENSE_FILE, "w") as f:
        for k in sorted(keys):
            f.write(f"{k},available\n")
    print(f"Done: {BATCH_SIZE} keys → {LICENSE_FILE}")


def draw_from_pool(n):
    """从可用池中随机抽取 n 个，标记为 assigned"""
    available, used = get_pool()
    if n > len(available):
        return None, len(available)

    chosen = random.sample(available, n)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    remain = [k for k in available if k not in chosen]
    for key in chosen:
        used.append(f"{key},assigned,{timestamp},cli-keygen")
    save_pool(remain, used)
    return chosen, len(remain)


def interactive():
    available, used = get_pool()
    print("=" * 50)
    print("  Quasar ERP 授权注册机 (CLI)")
    print("=" * 50)
    print(f"  可用授权: {len(available):,}  |  已用: {len(used):,}")
    print("  输入 1-10 从可用池中抽取，输入 q 退出")
    print("=" * 50)

    while True:
        try:
            cmd = input("\nEnter count (1-10): ").strip()
            if cmd.lower() == "q":
                break
            n = int(cmd)
            if n < 1 or n > 10:
                print("Enter a number between 1 and 10.")
                continue

            keys, remaining = draw_from_pool(n)
            if keys is None:
                print(f"Only {remaining} available — cannot generate {n}.")
                continue

            print(f"\nGenerated {n} key(s):")
            for i, k in enumerate(keys, 1):
                print(f"  [{i:02d}]  {k}")
            print(f"\nRemaining: {remaining:,}")

        except ValueError:
            print("Invalid input.")
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--generate-5000":
            generate_5000()
        elif sys.argv[1] == "--check" and len(sys.argv) > 2:
            from license_validator import check_key
            status = check_key(sys.argv[2])
            print(status.upper())
            sys.exit(0 if status == "available" else 1)
        elif sys.argv[1] == "--gui":
            from keygen_gui import main
            main()
        else:
            print("Usage: keygen.py [--generate-5000 | --check <key> | --gui]")
    else:
        interactive()
