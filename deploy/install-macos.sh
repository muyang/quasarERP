#!/bin/bash
set -e
# ============================================================================
# Quasar ERP — macOS Installer (EN / 中文)
# License-protected one-click deployment
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

INSTALL_DIR="$HOME/quasar-erp"
SITE_NAME="${SITE_NAME:-erp.local}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
MARIADB_PASSWORD="${MARIADB_PASSWORD:-erpdev}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LICENSE_FILE="${SCRIPT_DIR}/licenses.txt"
LANG="en"

# ============================
# Language Selection
# ============================
select_language() {
    echo ""
    echo -e "${CYAN}=========================================${NC}"
    echo -e "${CYAN}  Quasar ERP - Installer / 安装程序${NC}"
    echo -e "${CYAN}=========================================${NC}"
    echo ""
    echo -e "  ${BOLD}Please select language / 请选择语言:${NC}"
    echo -e "  ${GREEN}[1]${NC} English"
    echo -e "  ${GREEN}[2]${NC} 中文"
    echo ""
    read -p "  Enter choice (1-2) [1]: " lang_choice
    case "${lang_choice:-1}" in
        2) LANG="zh" ;;
        *) LANG="en" ;;
    esac
}

msg() {
    if [ "$LANG" = "zh" ]; then
        case "$1" in
            "welcome")       echo -e "${CYAN}Quasar ERP — 一键部署安装${NC}" ;;
            "license_title") echo -e "${YELLOW}=== 软件授权验证 ===${NC}" ;;
            "license_prompt") echo -e "请输入授权码: " ;;
            "license_valid")  echo -e "${GREEN}[✓] 授权验证通过${NC}" ;;
            "license_invalid") echo -e "${RED}[✗] 授权码无效！安装已终止。${NC}" ;;
            "license_contact") echo -e "请联系供应商获取有效授权码。" ;;
            "check_homebrew") echo -e "${YELLOW}[!] 检测 Homebrew...${NC}" ;;
            "install_homebrew") echo -e "${YELLOW}[!] 正在安装 Homebrew...${NC}" ;;
            "ok_homebrew")    echo -e "${GREEN}[✓] Homebrew 已就绪${NC}" ;;
            "install_python") echo -e "${YELLOW}[!] 安装 Python 3.12...${NC}" ;;
            "ok_python")      echo -e "${GREEN}[✓] Python${NC}" ;;
            "install_node")   echo -e "${YELLOW}[!] 安装 Node.js 18...${NC}" ;;
            "ok_node")        echo -e "${GREEN}[✓] Node${NC}" ;;
            "install_mariadb") echo -e "${YELLOW}[!] 安装 MariaDB...${NC}" ;;
            "config_mariadb") echo -e "${YELLOW}[!] 配置 MariaDB...${NC}" ;;
            "ok_mariadb")     echo -e "${GREEN}[✓] MariaDB 已启动${NC}" ;;
            "install_redis")  echo -e "${YELLOW}[!] 安装 Redis...${NC}" ;;
            "ok_redis")       echo -e "${GREEN}[✓] Redis 已启动${NC}" ;;
            "install_bench")  echo -e "${YELLOW}[!] 安装 frappe-bench...${NC}" ;;
            "ok_bench")       echo -e "${GREEN}[✓] bench CLI 已就绪${NC}" ;;
            "init_bench")     echo -e "${YELLOW}[!] 初始化 frappe-bench (约 5-10 分钟)...${NC}" ;;
            "ok_bench_init")  echo -e "${GREEN}[✓] bench 初始化完成${NC}" ;;
            "create_site")    echo -e "${YELLOW}[!] 创建站点...${NC}" ;;
            "install_apps")   echo -e "${YELLOW}[!] 安装应用...${NC}" ;;
            "build")          echo -e "${YELLOW}[!] 构建前端...${NC}" ;;
            "complete_title") echo -e "${GREEN}=========================================${NC}" ;;
            "complete_msg1")  echo -e "${GREEN}  安装完成！${NC}" ;;
            "complete_msg2")  echo -e "  访问: ${CYAN}http://localhost:8000${NC}" ;;
            "complete_msg3")  echo -e "  用户名: ${BOLD}Administrator${NC}" ;;
            "complete_msg4")  echo -e "  密码: ${BOLD}${ADMIN_PASSWORD}${NC}" ;;
            "start_cmd")      echo -e "  启动: ${BOLD}cd ${INSTALL_DIR} && bench start${NC}" ;;
            "dir_exists")     echo -e "${YELLOW}[!] frappe-bench 已存在: ${INSTALL_DIR}${NC}" ;;
        esac
    else
        case "$1" in
            "welcome")       echo -e "${CYAN}Quasar ERP — One-Click Deployment${NC}" ;;
            "license_title") echo -e "${YELLOW}=== Software License Verification ===${NC}" ;;
            "license_prompt") echo -e "Enter license key: " ;;
            "license_valid")  echo -e "${GREEN}[✓] License verified successfully${NC}" ;;
            "license_invalid") echo -e "${RED}[✗] Invalid license key! Installation aborted.${NC}" ;;
            "license_contact") echo -e "Please contact your vendor for a valid license key." ;;
            "check_homebrew") echo -e "${YELLOW}[!] Checking Homebrew...${NC}" ;;
            "install_homebrew") echo -e "${YELLOW}[!] Installing Homebrew...${NC}" ;;
            "ok_homebrew")    echo -e "${GREEN}[✓] Homebrew ready${NC}" ;;
            "install_python") echo -e "${YELLOW}[!] Installing Python 3.12...${NC}" ;;
            "ok_python")      echo -e "${GREEN}[✓] Python${NC}" ;;
            "install_node")   echo -e "${YELLOW}[!] Installing Node.js 18...${NC}" ;;
            "ok_node")        echo -e "${GREEN}[✓] Node${NC}" ;;
            "install_mariadb") echo -e "${YELLOW}[!] Installing MariaDB...${NC}" ;;
            "config_mariadb") echo -e "${YELLOW}[!] Configuring MariaDB...${NC}" ;;
            "ok_mariadb")     echo -e "${GREEN}[✓] MariaDB started${NC}" ;;
            "install_redis")  echo -e "${YELLOW}[!] Installing Redis...${NC}" ;;
            "ok_redis")       echo -e "${GREEN}[✓] Redis started${NC}" ;;
            "install_bench")  echo -e "${YELLOW}[!] Installing frappe-bench...${NC}" ;;
            "ok_bench")       echo -e "${GREEN}[✓] bench CLI ready${NC}" ;;
            "init_bench")     echo -e "${YELLOW}[!] Initializing frappe-bench (~5-10 min)...${NC}" ;;
            "ok_bench_init")  echo -e "${GREEN}[✓] bench initialized${NC}" ;;
            "create_site")    echo -e "${YELLOW}[!] Creating site...${NC}" ;;
            "install_apps")   echo -e "${YELLOW}[!] Installing apps...${NC}" ;;
            "build")          echo -e "${YELLOW}[!] Building frontend...${NC}" ;;
            "complete_title") echo -e "${GREEN}=========================================${NC}" ;;
            "complete_msg1")  echo -e "${GREEN}  Installation Complete!${NC}" ;;
            "complete_msg2")  echo -e "  Visit: ${CYAN}http://localhost:8000${NC}" ;;
            "complete_msg3")  echo -e "  Username: ${BOLD}Administrator${NC}" ;;
            "complete_msg4")  echo -e "  Password: ${BOLD}${ADMIN_PASSWORD}${NC}" ;;
            "start_cmd")      echo -e "  Start: ${BOLD}cd ${INSTALL_DIR} && bench start${NC}" ;;
            "dir_exists")     echo -e "${YELLOW}[!] frappe-bench exists: ${INSTALL_DIR}${NC}" ;;
        esac
    fi
}

# ============================
# License Validation
# ============================
verify_license() {
    echo ""
    msg "license_title"
    echo ""
    read -p "$(msg "license_prompt")" input_key

    VALIDATOR="${SCRIPT_DIR}/license_validator.py"
    if [ ! -f "$VALIDATOR" ]; then
        # Fallback: check against license file directly
        if grep -qFx "${input_key}" "$LICENSE_FILE"; then
            msg "license_valid"
            echo ""
            return
        fi
        msg "license_invalid"
        msg "license_contact"
        exit 1
    fi

    result=$(python3 "$VALIDATOR" "${input_key}" 2>&1)
    if echo "$result" | grep -q "VALID"; then
        msg "license_valid"
        echo ""
    else
        reason=$(echo "$result" | cut -d'|' -f2)
        if [ "$LANG" = "zh" ]; then
            echo -e "${RED}[✗] ${reason}${NC}"
        else
            echo -e "${RED}[✗] ${reason}${NC}"
        fi
        msg "license_contact"
        exit 1
    fi
}

# ============================
# Main Install
# ============================
select_language
verify_license

msg "welcome"
echo ""

# ---- Homebrew ----
msg "check_homebrew"
if ! command -v brew &>/dev/null; then
    msg "install_homebrew"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
msg "ok_homebrew"

# ---- Python 3.12 ----
if ! python3.12 --version &>/dev/null; then
    msg "install_python"
    brew install python@3.12
fi
msg "ok_python"; python3.12 --version

# ---- Node.js 18 ----
if ! node --version | grep -q "v18"; then
    msg "install_node"
    brew install node@18 && brew link node@18
fi
msg "ok_node"; node --version

# ---- MariaDB ----
if ! brew services list | grep -q mariadb; then
    msg "install_mariadb"
    brew install mariadb@10.11
    brew services start mariadb@10.11
fi
msg "ok_mariadb"

# Configure MariaDB root password
mysql -u root -p"${MARIADB_PASSWORD}" -e "SELECT 1" 2>/dev/null || {
    msg "config_mariadb"
    mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${MARIADB_PASSWORD}'; FLUSH PRIVILEGES;" 2>/dev/null || true
}

# ---- Redis ----
if ! brew services list | grep -q redis; then
    msg "install_redis"
    brew install redis && brew services start redis
fi
msg "ok_redis"

# ---- Yarn ----
command -v yarn &>/dev/null || npm install -g yarn

# ---- frappe-bench ----
if ! command -v bench &>/dev/null; then
    msg "install_bench"
    pip3.12 install frappe-bench
fi
msg "ok_bench"

# ---- Initialize bench ----
if [ ! -d "${INSTALL_DIR}" ]; then
    msg "init_bench"
    bench init "${INSTALL_DIR}" \
        --frappe-path https://github.com/frappe/frappe.git \
        --frappe-branch version-15 \
        --python python3.12

    cd "${INSTALL_DIR}"
    bench get-app --branch version-15 erpnext
    bench get-app --branch version-15 hrms

    # Copy Quasar app
    cp -r "${SCRIPT_DIR}/../apps/quasar" apps/quasar 2>/dev/null || cp -r "${SCRIPT_DIR}/../quasar" apps/quasar 2>/dev/null || true

    msg "create_site"
    bench new-site "${SITE_NAME}" \
        --admin-password "${ADMIN_PASSWORD}" \
        --mariadb-root-password "${MARIADB_PASSWORD}"

    msg "install_apps"
    bench --site "${SITE_NAME}" install-app erpnext
    bench --site "${SITE_NAME}" install-app hrms
    bench --site "${SITE_NAME}" install-app quasar

    msg "build"
    bench build
    msg "ok_bench_init"
else
    msg "dir_exists"
fi

# ---- Done ----
echo ""
msg "complete_title"
msg "complete_msg1"
msg "complete_title"
echo ""
msg "complete_msg2"
msg "complete_msg3"
msg "complete_msg4"
echo ""
msg "start_cmd"
echo ""
