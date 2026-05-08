#!/usr/bin/env python3
import re
from pathlib import Path

VAULT_ROOT = Path("E:/finance_vault")
RECORDS_DIR = VAULT_ROOT / "raw" / "transactions" / "records"
TRANSACTIONS_FILE = VAULT_ROOT / "raw" / "transactions" / "transactions.md"
WIKI_DIR = VAULT_ROOT / "wiki"

print("=" * 50)
print("  Finance Vault - Data Consistency Check")
print("=" * 50)
print()

# Check 1: File count
records_files = list(RECORDS_DIR.glob("*.md"))
print(f"[1] File count consistency")
print(f"    records/ = {len(records_files)} files")

content = TRANSACTIONS_FILE.read_text(encoding="utf-8")
json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
print(f"    transactions.md = {len(json_blocks)} records")

if len(records_files) == len(json_blocks):
    print(f"    [OK] PASS")
else:
    print(f"    [FAIL] MISMATCH")

print()

# Check 2: ID match
records_dir = {}
for f in records_files:
    content = f.read_text(encoding="utf-8")
    frontmatter = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter:
        for line in frontmatter.group(1).split('\n'):
            if line.startswith('id:'):
                record_id = line.split(':', 1)[1].strip()
                records_dir[record_id] = f.name
                break

records_txn = {}
for block in json_blocks:
    block = block.strip()
    block = re.sub(r"'([^']+)':", r'"\1":', block)
    try:
        record = eval(block)
        if 'id' in record:
            records_txn[record['id']] = record
    except:
        pass

print(f"[2] ID list consistency")
print(f"    records/ IDs: {len(records_dir)}")
print(f"    transactions.md IDs: {len(records_txn)}")

if set(records_dir.keys()) == set(records_txn.keys()):
    print(f"    [OK] PASS")
else:
    missing_in_txn = set(records_dir.keys()) - set(records_txn.keys())
    missing_in_dir = set(records_txn.keys()) - set(records_dir.keys())
    if missing_in_txn:
        print(f"    [WARN] Missing in transactions.md: {missing_in_txn}")
    if missing_in_dir:
        print(f"    [WARN] Missing in records/: {missing_in_dir}")
    print(f"    [FAIL] MISMATCH")

print()

# Check 3: Amount consistency
dir_total = sum(float(r.get('amount', 0)) for r in records_dir.values() if hasattr(r, 'get'))
records_dir_amounts = {}
for f in records_files:
    content = f.read_text(encoding="utf-8")
    frontmatter = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter:
        record = {}
        for line in frontmatter.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                record[key.strip()] = value.strip()
        if record.get('type') == 'expense':
            records_dir_amounts[record.get('id', '')] = float(record.get('amount', 0))

records_txn_amounts = {}
for block in json_blocks:
    block = block.strip()
    block = re.sub(r"'([^']+)':", r'"\1":', block)
    try:
        record = eval(block)
        if record.get('type') == 'expense':
            records_txn_amounts[record.get('id', '')] = float(record.get('amount', 0))
    except:
        pass

dir_total = sum(records_dir_amounts.values())
txn_total = sum(records_txn_amounts.values())

print(f"[3] Amount consistency")
print(f"    records/ total: {dir_total:.2f}")
print(f"    transactions.md total: {txn_total:.2f}")

if abs(dir_total - txn_total) < 0.01:
    print(f"    [OK] PASS")
else:
    print(f"    [FAIL] MISMATCH")

print()
print("=" * 50)
