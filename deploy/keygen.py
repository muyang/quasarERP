#!/usr/bin/env python3
"""
Quasar ERP — 授权注册机
生成格式: QUASAR-XXXX-XXXX-XXXX-XXXX
每次输入 1-10，生成对应数量的授权码
"""

import random
import os
import hashlib

# 字符集: 排除易混淆字符 (0/O, 1/I/L)
CHARS = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
SEGMENTS = 4
SEG_LEN = 4
LICENSE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(LICENSE_DIR, "licenses.txt")
BATCH_SIZE = 5000


def generate_key():
    """生成单个授权码"""
    parts = []
    for _ in range(SEGMENTS):
        parts.append("".join(random.choices(CHARS, k=SEG_LEN)))
    return "QUASAR-" + "-".join(parts)


def generate_batch(n):
    """生成 n 个不重复的授权码"""
    keys = set()
    while len(keys) < n:
        keys.add(generate_key())
    return sorted(keys)


def generate_5000():
    """一次性生成 5000 个授权码，写回 licenses.txt 文件"""
    print(f"正在生成 {BATCH_SIZE} 个授权码...")
    keys = generate_batch(BATCH_SIZE)
    with open(LICENSE_FILE, "w") as f:
        for k in keys:
            f.write(k + "\n")
    print(f"已完成: {BATCH_SIZE} 个授权码 → {LICENSE_FILE}")


def interactive():
    """交互式注册机: 输入 1-10 生成对应数量的授权码"""
    print("=" * 50)
    print("  Quasar ERP 授权注册机")
    print("=" * 50)
    print(f"  已有授权码: {_count_existing()} 个")
    print("  输入 1-10 生成新授权码，输入 q 退出")
    print("=" * 50)

    while True:
        try:
            cmd = input("\n请输入生成数量 (1-10): ").strip()
            if cmd.lower() == "q":
                print("退出注册机。")
                break
            n = int(cmd)
            if n < 1 or n > 10:
                print("请输入 1 到 10 之间的数字。")
                continue

            keys = generate_batch(n)
            with open(LICENSE_FILE, "a") as f:
                for k in keys:
                    f.write(k + "\n")

            print(f"\n已生成 {n} 个授权码:")
            for k in keys:
                print(f"  {k}")
            print(f"\n总计: {_count_existing()} 个授权码")

        except ValueError:
            print("输入无效，请输入数字 1-10 或 q 退出。")
        except KeyboardInterrupt:
            print("\n退出注册机。")
            break


def _count_existing():
    if not os.path.exists(LICENSE_FILE):
        return 0
    with open(LICENSE_FILE) as f:
        return sum(1 for _ in f)


def validate_key(key):
    """验证授权码是否在授权列表中"""
    if not os.path.exists(LICENSE_FILE):
        return False
    key = key.strip().upper()
    with open(LICENSE_FILE) as f:
        for line in f:
            if line.strip() == key:
                return True
    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--generate-5000":
        generate_5000()
    elif len(sys.argv) > 1 and sys.argv[1] == "--check":
        if len(sys.argv) > 2:
            valid = validate_key(sys.argv[2])
            print("VALID" if valid else "INVALID")
            sys.exit(0 if valid else 1)
        else:
            print("Usage: keygen.py --check <license_key>")
            sys.exit(1)
    else:
        # Auto-generate 5000 if no license file exists
        if not os.path.exists(LICENSE_FILE) or _count_existing() < 5000:
            print("首次运行，自动生成 5000 个授权码...")
            generate_5000()
        interactive()
