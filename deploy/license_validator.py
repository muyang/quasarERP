#!/usr/bin/env python3
"""
Quasar ERP — 授权验证器
- 验证授权码是否在授权池中且未被使用
- 验证通过后将授权码标记为已使用（一码一机）
- 记录使用时间、设备标识
"""

import os
import sys
import platform
import socket
import hashlib
from datetime import datetime

LICENSE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(LICENSE_DIR, "licenses.txt")


def get_device_id():
    """生成设备唯一标识"""
    info = f"{platform.node()}-{socket.gethostname()}-{platform.machine()}"
    return hashlib.sha256(info.encode()).hexdigest()[:16]


def validate_and_consume(key):
    """
    验证授权码并标记为已使用。
    返回 (valid: bool, message: str)
    """
    key = key.strip().upper()

    if not os.path.exists(LICENSE_FILE):
        return False, "License file not found. Please contact support."

    lines = []
    found = False
    already_used = False

    with open(LICENSE_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if parts[0] == key:
                found = True
                if parts[1] != "available":
                    already_used = True
                    # Keep existing used status
                    lines.append(line)
                else:
                    # Mark as used
                    device = get_device_id()
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    lines.append(f"{key},used,{timestamp},{device}")
            else:
                lines.append(line)

    if not found:
        return False, "Invalid license key."

    if already_used:
        return False, "This license key has already been used on another device."

    # Write back
    with open(LICENSE_FILE, "w") as f:
        for l in lines:
            f.write(l + "\n")

    return True, "License validated successfully."


def check_key(key):
    """仅检查授权码状态，不消耗"""
    key = key.strip().upper()
    if not os.path.exists(LICENSE_FILE):
        return "not_found"

    with open(LICENSE_FILE) as f:
        for line in f:
            parts = line.strip().split(",")
            if parts[0] == key:
                return parts[1] if len(parts) > 1 else "available"
    return "not_found"


def available_count():
    """返回可用授权码数量"""
    if not os.path.exists(LICENSE_FILE):
        return 0
    count = 0
    with open(LICENSE_FILE) as f:
        for line in f:
            if ",available" in line:
                count += 1
    return count


def used_count():
    """返回已使用授权码数量"""
    if not os.path.exists(LICENSE_FILE):
        return 0
    count = 0
    with open(LICENSE_FILE) as f:
        for line in f:
            if ",used" in line:
                count += 1
    return count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: license_validator.py <license_key>")
        sys.exit(1)

    valid, msg = validate_and_consume(sys.argv[1])
    if valid:
        print(f"VALID|{msg}")
        sys.exit(0)
    else:
        print(f"INVALID|{msg}")
        sys.exit(1)
