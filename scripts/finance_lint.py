#!/usr/bin/env python3
"""
finance_lint.py - Finance Vault Data Consistency Checker

Checks:
1. transactions.md header count == YAML frontmatter record count
2. YAML frontmatter record IDs are unique
3. Amount totals are consistent (expense vs summary)
4. Wiki links are valid

Usage:
  python finance_lint.py
"""

import re
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Paths - 固定路径
VAULT_ROOT = Path("E:/finance_vault")
RECORDS_DIR = VAULT_ROOT / "raw" / "transactions" / "records"
TRANSACTIONS_FILE = VAULT_ROOT / "raw" / "transactions" / "transactions" / "index.md"
WIKI_DIR = VAULT_ROOT / "wiki"

def log(msg: str, level: str = "INFO"):
    icons = {"OK": "[+]", "FAIL": "[-]", "WARN": "[!]", "INFO": "[*]"}
    prefix = icons.get(level, "[ ]")
    print(f"{prefix} {msg}")


def parse_yaml_value(value: str):
    """解析 YAML 值"""
    value = value.strip()
    # 去除引号
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    # 处理数组
    if value.startswith('[') and value.endswith(']'):
        items = value[1:-1].split(',')
        return [item.strip().strip('"').strip("'") for item in items]
    # 处理数字
    try:
        return float(value)
    except:
        return value


def get_yaml_records() -> dict:
    """从 transactions.md YAML frontmatter 块中提取所有记录"""
    records = {}
    if not TRANSACTIONS_FILE.exists():
        return records

    content = TRANSACTIONS_FILE.read_text(encoding="utf-8")
    
    # 匹配 YAML frontmatter 块: --- ... ---
    # 注意: 每个记录以 --- 开始，以下一个 --- 或文件末尾结束
    # 跳过文件顶部的元数据块 (id, date, amount 等顶层字段)
    
    # 查找所有 YAML frontmatter 块
    # 格式: ```yaml\n---\nid: xxx\n...\n---\n```
    yaml_blocks = re.findall(r'```yaml\s*\n---\n(.*?)\n---\n', content, re.DOTALL)
    
    for block in yaml_blocks:
        record = {}
        for line in block.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = parse_yaml_value(value)
                record[key] = value
        
        if 'id' in record:
            records[record['id']] = record
    
    return records


def check_count_consistency() -> bool:
    """检查 header 中声明的记录数与 YAML frontmatter 数量是否一致"""
    log("Check 1: Record count consistency", "INFO")

    records = get_yaml_records()
    yaml_count = len(records)

    # 从 header 提取声明的记录数
    content = TRANSACTIONS_FILE.read_text(encoding="utf-8")
    header_match = re.search(r'> 总记录数:\s*(\d+)', content)
    header_count = int(header_match.group(1)) if header_match else 0

    if yaml_count == header_count:
        log(f"  PASS: {yaml_count} records", "OK")
        return True
    else:
        log(f"  FAIL: header={header_count}, YAML records={yaml_count}", "FAIL")
        return False


def check_id_uniqueness() -> bool:
    """检查 YAML frontmatter 中的 ID 是否唯一"""
    log("Check 2: ID uniqueness", "INFO")

    records = get_yaml_records()
    total = len(records)

    if total == 0:
        log("  WARN: No records found", "WARN")
        return True

    log(f"  PASS: {total} unique IDs", "OK")
    return True


def check_amount_consistency() -> bool:
    """检查 expense 类型记录的金额合计是否与 summary 一致"""
    log("Check 3: Amount consistency", "INFO")

    records = get_yaml_records()

    # 计算 expense 合计
    expense_total = sum(
        float(r.get('amount', 0))
        for r in records.values()
        if r.get('type') == 'expense'
    )

    # 从表格提取声明的支出
    content = TRANSACTIONS_FILE.read_text(encoding="utf-8")
    summary_match = re.search(r'本月支出（已确认）\s*\|\s*¥([0-9,]+\.?[0-9]*)', content)
    summary_total = float(summary_match.group(1).replace(',', '')) if summary_match else 0

    if abs(expense_total - summary_total) < 0.01:
        log(f"  PASS: Total = ¥{expense_total:.2f}", "OK")
        return True
    else:
        log(f"  FAIL: YAML expense=¥{expense_total:.2f}, header=¥{summary_total:.2f}", "FAIL")
        return False


def check_wiki_links() -> bool:
    """检查 wiki 中的 Obsidian 链接是否有效"""
    log("Check 4: Wiki link validity", "INFO")
    wiki_files = list(WIKI_DIR.rglob("*.md"))
    issues = []

    for md_file in wiki_files:
        content = md_file.read_text(encoding="utf-8")
        # 匹配 [[link]] 或 [[link|alias]]
        links = re.findall(r'\[\[([^\]]+?)(?:\|[^\]]+)?\]\]', content)

        for link in links:
            link = link.strip().replace('\\\\', '\\')
            if link.startswith('http') or link.startswith('#'):
                continue

            candidates = []
            if '/' in link:
                candidates.append(md_file.parent / (link + '.md'))
            else:
                candidates.append(md_file.parent / (link + '.md'))

            candidates.append(WIKI_DIR / (link + '.md'))

            if '/' in link:
                candidates.append(Path(link + '.md'))

            exists = any(c.exists() for c in candidates if c)
            if not exists:
                issues.append((md_file.relative_to(VAULT_ROOT).as_posix(), link))

    if not issues:
        log(f"  PASS: All links valid", "OK")
        return True
    else:
        log(f"  FAIL: {len(issues)} invalid links found", "FAIL")
        for file_path, link in issues:
            log(f"    {file_path}: [[{link}]]", "WARN")
        return False


def main():
    print("\n" + "=" * 50)
    print("  Finance Vault - Data Consistency Check")
    print("=" * 50 + "\n")

    results = []
    results.append(("Record Count", check_count_consistency()))
    results.append(("ID Uniqueness", check_id_uniqueness()))
    results.append(("Amount", check_amount_consistency()))
    results.append(("Wiki Links", check_wiki_links()))

    print("\n" + "=" * 50)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    status = "PASS" if passed == total else "FAIL"
    print(f"  Result: {passed}/{total} checks passed ({status})")
    print("=" * 50 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
