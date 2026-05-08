---
month: 2026-05
---

# 📊 财务图表中心

> 数据来源：`raw/transactions/transactions/index.md`
> 🔧 切换月份：修改上方 **frontmatter** 中的 `month:` 值即可（如留空则显示全部）

```dataviewjs
// 从当前页面的 frontmatter 读取月份配置（兼容写法）
var _fm = null;
try { _fm = dv.current().file.frontmatter; } catch(e) {}
var month = (_fm && _fm.month) ? String(_fm.month) : "2026-04";

(async () => {
  const container = this.container;
  const sourcePath = "raw/transactions/transactions/index.md";

  try {
    const file = app.vault.getAbstractFileByPath(sourcePath);
    if (!file) {
      container.innerHTML = '<p style="color:#888;">⚠️ 找不到数据文件</p>';
      return;
    }

    const text = await app.vault.read(file);
    const blocks = text.match(/```yaml\n([\s\S]*?)```/g) || [];

    // 解析所有记录
    const records = [];
    blocks.forEach(block => {
      const yaml = block.replace(/```yaml\n?/, '').replace(/```\n?/g, '');
      const record = {};
      yaml.split('\n').forEach(line => {
        const colonIdx = line.indexOf(':');
        if (colonIdx > 0) {
          const key = line.substring(0, colonIdx).trim();
          let val = line.substring(colonIdx + 1).trim();
          if (val === 'null' || val === '') val = null;
          else if (!isNaN(val) && val !== '') val = parseFloat(val);
          else if (val === 'true') val = true;
          else if (val === 'false') val = false;
          record[key] = val;
        }
      });
      if (record.id) records.push(record);
    });

    // 筛选月份
    const filtered = records.filter(r => r.date && (!month || r.date.startsWith(month)));

    // ── 统计数据 ──
    let totalIncome = 0, totalExpense = 0;
    const byCategory = {};
    const byAccount = {};
    const byDay = {};

    filtered.forEach(r => {
      const amt = Math.abs(r.amount || 0);
      if (r.type === 'income') totalIncome += amt;
      else if (r.type === 'expense') {
        totalExpense += amt;
        byCategory[r.category] = (byCategory[r.category] || 0) + amt;
      }
      if (r.account) byAccount[r.account] = (byAccount[r.account] || 0) + amt;
      if (r.date && r.date.length >= 10 && r.type === 'expense') {
        byDay[r.date.substring(8,10)] = (byDay[r.date.substring(8,10)] || 0) + amt;
      }
    });

    const netSavings = totalIncome - totalExpense;
    const totalExp = Object.values(byCategory).reduce((a,b)=>a+b,0);

    // 颜色方案
    const catColors = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e91e63','#00bcd4'];
    const accColors = ['#3498db','#e74c3c','#2ecc71','#f39c12','#9b59b6'];

    let html = '';

    // 当前月份标签
    html += `<div style="background:#1565c0;color:white;padding:10px 20px;border-radius:8px;display:inline-block;margin-bottom:16px;font-size:15px;">📅 ${month ? month + '月' : '全部'} 数据</div>`;

    // ═══ 收支概览卡片 ═══
    html += '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px;">';
    html += `<div style="background:linear-gradient(135deg,#e8f5e9,#c8e6c9);padding:20px;border-radius:12px;text-align:center;box-shadow:0 2px 8px rgba(46,125,50,0.15);">
      <div style="font-size:13px;color:#2e7d32;font-weight:600;">💰 收入</div>
      <div style="font-size:28px;font-weight:bold;color:#1b5e20;margin-top:8px;">¥${totalIncome.toFixed(2)}</div>
    </div>`;
    html += `<div style="background:linear-gradient(135deg,#ffebee,#ffcdd2);padding:20px;border-radius:12px;text-align:center;box-shadow:0 2px 8px rgba(198,40,40,0.15);">
      <div style="font-size:13px;color:#c62828;font-weight:600;">💸 支出</div>
      <div style="font-size:28px;font-weight:bold;color:#b71c1c;margin-top:8px;">¥${totalExpense.toFixed(2)}</div>
    </div>`;
    html += `<div style="background:linear-gradient(135deg,#e3f2fd,#bbdefb);padding:20px;border-radius:12px;text-align:center;box-shadow:0 2px 8px rgba(21,101,192,0.15);">
      <div style="font-size:13px;color:#1565c0;font-weight:600;">📊 结余</div>
      <div style="font-size:28px;font-weight:bold;color:#0d47a1;margin-top:8px;">${netSavings>=0?'':'-'}¥${Math.abs(netSavings).toFixed(2)}</div>
    </div>`;
    html += '</div>';

    // ═══ 支出分类占比（堆叠条 + 表格）═══
    if (Object.keys(byCategory).length > 0) {
      html += '<details open><summary style="cursor:pointer;font-size:18px;font-weight:bold;color:#333;padding:8px 0;">📈 支出分类占比</summary>';

      // 堆叠横条
      html += '<div style="display:flex;height:32px;border-radius:16px;overflow:hidden;background:#eee;margin:12px 0 16px;">';
      Object.entries(byCategory).sort((a,b)=>b[1]-a[1]).forEach(([cat, amt], i) => {
        const pct = totalExp > 0 ? (amt/totalExp*100) : 0;
        const color = catColors[i % catColors.length];
        if (pct > 1.5) {
          html += `<div style="width:${pct}%;height:100%;background:${color};display:flex;align-items:center;justify-content:center;font-size:11px;color:white;font-weight:bold;overflow:hidden;" title="${cat}: ¥${amt.toFixed(2)}">${pct > 5 ? cat : ''}</div>`;
        }
      });
      html += '</div>';

      // 分类表格
      html += '<table style="width:100%;border-collapse:collapse;font-size:14px;"><thead><tr style="background:#f8f8f8;">';
      html += '<th style="padding:10px 12px;border:1px solid #e0e0e0;text-align:left;">分类</th><th style="padding:10px;border:1px solid #e0e0e0;text-align:right;width:120px;">金额</th><th style="padding:10px;border:1px solid #e0e0e0;text-align:right;width:70px;">占比</th><th style="padding:10px;border:1px solid #e0e0e0;">分布</th></tr></thead><tbody>';
      Object.entries(byCategory).sort((a,b)=>b[1]-a[1]).forEach(([cat, amt], i) => {
        const pct = totalExp > 0 ? (amt/totalExp*100).toFixed(1) : '0.0';
        const color = catColors[i % catColors.length];
        const barLen = Math.round(parseFloat(pct)/5);
        const bar = '█'.repeat(Math.max(barLen,1)) + '░'.repeat(Math.max(20-barLen,0));
        html += `<tr><td style="padding:8px 12px;border:1px solid #e0e0e0;"><span style="display:inline-block;width:14px;height:14px;background:${color};border-radius:4px;margin-right:8px;vertical-align:-2px;"></span>${cat}</td><td style="padding:8px 12px;border:1px solid #e0e0e0;text-align:right;font-weight:bold;">¥${amt.toFixed(2)}</td><td style="padding:8px 12px;border:1px solid #e0e0e0;text-align:right;color:#666;">${pct}%</td><td style="padding:8px 12px;border:1px solid #e0e0e0;font-family:monospace;letter-spacing:-1px;color:${color};">${bar}</td></tr>`;
      });
      html += `<tr style="background:#fafafa;font-weight:bold;"><td colspan="2" style="padding:10px 12px;border:1px solid #e0e0e0;">合计支出</td><td style="padding:10px 12px;border:1px solid #e0e0e0;text-align:right;color:#c62828;">¥${totalExp.toFixed(2)}</td><td style="padding:10px 12px;border:1px solid #e0e0e0;">100%</td></tr>`;
      html += '</tbody></table></details>';
    } else {
      html += '<p style="color:#888;padding:12px 0;">📈 本月暂无支出记录</p>';
    }

    // ═══ 每日支出趋势 ═══
    html += '<details open><summary style="cursor:pointer;font-size:18px;font-weight:bold;color:#333;padding:8px 0;margin-top:16px;">📉 每日支出趋势</summary>';

    const daysInMonth = month ? new Date(parseInt(month.split('-')[0]), parseInt(month.split('-')[1]), 0).getDate() : 31;
    const dayList = Array.from({length:daysInMonth},(_,i)=>String(i+1).padStart(2,'0'));
    const maxDayAmt = Math.max(...Object.values(byDay), 1);

    html += '<div style="margin-top:12px;display:flex;align-items:flex-end;gap:3px;height:140px;padding:4px 0;">';
    dayList.forEach(d => {
      const amt = byDay[d] || 0;
      const h = amt > 0 ? Math.max(4, (amt/maxDayAmt)*130) : 2;
      const color = amt > 0 ? '#e74c3c' : '#f0f0f0';
      html += `<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;">
        <div style="width:100%;max-width:28px;height:${h}px;background:${color};border-radius:3px 3px 0 0;" title="${d}号: ¥${amt.toFixed(2)}"></div>
        <span style="font-size:10px;color:#999;">${d}</span>
      </div>`;
    });
    html += '</div></details>';

    // ═══ 收支对比条 ═══
    html += '<details open><summary style="cursor:pointer;font-size:18px;font-weight:bold;color:#333;padding:8px 0;margin-top:16px;">💵 收支对比</summary>';
    html += '<div style="margin-top:12px;">';

    const maxVal = Math.max(totalIncome, totalExpense);
    const incomeW = maxVal > 0 ? (totalIncome/maxVal*100) : 0;
    const expenseW = maxVal > 0 ? (totalExpense/maxVal*100) : 0;

    html += `<div style="margin-bottom:14px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-weight:bold;color:#2e7d32;font-size:15px;">✅ 收入</span>
        <span style="font-weight:bold;color:#2e7d32;font-size:15px;">¥${totalIncome.toFixed(2)}</span>
      </div>
      <div style="height:26px;background:#e8f5e9;border-radius:13px;overflow:hidden;">
        <div style="height:100%;width:${Math.max(incomeW,2)}%;background:linear-gradient(90deg,#43a047,#2e7d32);border-radius:13px;"></div>
      </div>
    </div>`;
    html += `<div>
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-weight:bold;color:#c62828;font-size:15px;">❌ 支出</span>
        <span style="font-weight:bold;color:#c62828;font-size:15px;">¥${totalExpense.toFixed(2)}</span>
      </div>
      <div style="height:26px;background:#ffebee;border-radius:13px;overflow:hidden;">
        <div style="height:100%;width:${Math.max(expenseW,2)}%;background:linear-gradient(90deg,#e53935,#c62828);border-radius:13px;"></div>
      </div>
    </div>`;
    html += '</div></details>';

    // ═══ 账户分布 ═══
    if (Object.keys(byAccount).length > 0) {
      html += '<details open><summary style="cursor:pointer;font-size:18px;font-weight:bold;color:#333;padding:8px 0;margin-top:16px;">🏦 账户分布</summary>';
      html += '<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:12px;">';
      const accTotal = Object.values(byAccount).reduce((a,b)=>a+b,0);
      Object.entries(byAccount).sort(function(a,b){return b[1]-a[1];}).forEach(function(pair, i) {
        const acc = pair[0];
        const amt = pair[1];
        const pct = accTotal > 0 ? (amt/accTotal*100).toFixed(1) : '0.0';
        const color = accColors[i % accColors.length];
        html += `<div style="flex:1;min-width:110px;background:white;border-left:5px solid ${color};padding:14px 16px;border-radius:0 10px 10px 0;box-shadow:0 2px 6px rgba(0,0,0,0.08);">
          <div style="font-size:12px;color:#888;">${acc}</div>
          <div style="font-size:22px;font-weight:bold;color:#333;margin-top:4px;">¥${amt.toFixed(0)}</div>
          <div style="font-size:12px;color:#999;margin-top:2px;">占比 ${pct}%</div>
        </div>`;
      });
      html += '</div></details>';
    }

    container.innerHTML = html;

  } catch (err) {
    container.innerHTML = `<p style="color:red;padding:12px;background:#fff3f3;border-radius:8px;">❌ 错误: ${err.message}</p>`;
  }
})();
```
