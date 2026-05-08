#!/usr/bin/env python3
"""更新 wiki 文件中的 Dataview 数据源"""
from pathlib import Path

files = [
    'E:/finance_vault/wiki/yearly/2026.md',
    'E:/finance_vault/wiki/monthly/2026-04.md',
    'E:/finance_vault/wiki/charts.md'
]

for f in files:
    p = Path(f)
    content = p.read_text(encoding='utf-8')
    content = content.replace('"raw/transactions/records"', '"raw/transactions/transactions"')
    content = content.replace('`raw/transactions/records/`', '`raw/transactions/transactions.md`')
    p.write_text(content, encoding='utf-8')
    print(f'Updated: {f}')
