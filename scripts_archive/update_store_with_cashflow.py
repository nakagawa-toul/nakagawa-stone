with open('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. STORAGE_KEY 更新
text = text.replace("const STORAGE_KEY = 'nakagawa_stone_app_data_v10';", "const STORAGE_KEY = 'nakagawa_stone_app_data_v11'; // v11: Googleスプレッドシート（洋外注費・外注費・商品仕入・事業主消費・返済・税金）連動版")

# 2. INITIAL_DATA にプロパティ追加
target_init = "currentUser: 'wife',"
replacement_init = """currentUser: 'wife',
  cashflowDailySchedule: (typeof window !== 'undefined' && window.NAKAGAWA_INITIAL_CASHFLOW_DAILY) ? window.NAKAGAWA_INITIAL_CASHFLOW_DAILY : [],
  spreadsheetConfig: {
    spreadsheetId: '11bCt4mXclylQYrMAydtdVdgybNewbp5N-t0qpbTzNjU',
    viewUrl: 'https://docs.google.com/spreadsheets/d/11bCt4mXclylQYrMAydtdVdgybNewbp5N-t0qpbTzNjU/edit',
    csvUrl: 'https://docs.google.com/spreadsheets/d/11bCt4mXclylQYrMAydtdVdgybNewbp5N-t0qpbTzNjU/export?format=csv&gid=0',
    lastSyncedAt: '2026/11/25 14:00'
  },"""
text = text.replace(target_init, replacement_init, 1)

# 3. StoneAppStore クラスにメソッド群を追加
new_methods = """
  // ==============================================================
  // Googleスプレッドシート連動 日別資金繰り管理
  // ==============================================================
  getCashflowDailySchedule() {
    if (!this.data.cashflowDailySchedule || this.data.cashflowDailySchedule.length === 0) {
      if (typeof window !== 'undefined' && window.NAKAGAWA_INITIAL_CASHFLOW_DAILY) {
        this.data.cashflowDailySchedule = window.NAKAGAWA_INITIAL_CASHFLOW_DAILY;
        this.saveData();
      }
    }
    return this.data.cashflowDailySchedule || [];
  }

  getSpreadsheetConfig() {
    return this.data.spreadsheetConfig || {
      spreadsheetId: '11bCt4mXclylQYrMAydtdVdgybNewbp5N-t0qpbTzNjU',
      viewUrl: 'https://docs.google.com/spreadsheets/d/11bCt4mXclylQYrMAydtdVdgybNewbp5N-t0qpbTzNjU/edit',
      csvUrl: 'https://docs.google.com/spreadsheets/d/11bCt4mXclylQYrMAydtdVdgybNewbp5N-t0qpbTzNjU/export?format=csv&gid=0',
      lastSyncedAt: null
    };
  }

  getCashflowSummary(targetDateStr) {
    const list = this.getCashflowDailySchedule();
    if (!list || list.length === 0) return null;

    const todayStr = targetDateStr || new Date().toISOString().slice(0, 10);
    const curMonthPrefix = todayStr.slice(0, 7);

    let todayItem = list.find(d => d.date === todayStr);
    if (!todayItem) {
      const pastOrToday = list.filter(d => d.date <= todayStr);
      todayItem = pastOrToday.length > 0 ? pastOrToday[pastOrToday.length - 1] : list[0];
    }

    let monthIncome = 0;
    let monthExpense = 0;
    let monthYoSubcontract = 0;
    let monthSubcontract = 0;
    let monthCogs = 0;
    let monthLoanRepay = 0;
    let monthOwnerExpense = 0;
    let monthTax = 0;

    list.forEach(d => {
      if (d.date && d.date.startsWith(curMonthPrefix)) {
        monthIncome += (d.incomeTotal || 0);
        monthExpense += (d.expenseTotal || 0);
        monthYoSubcontract += (d.yoSubcontract || 0);
        monthSubcontract += (d.subcontract || 0);
        monthCogs += (d.cogs || 0);
        monthLoanRepay += (d.loanRepay || 0);
        monthOwnerExpense += (d.ownerExpense || 0);
        monthTax += ((d.withholdingTax || 0) + (d.consumptionTax || 0));
      }
    });

    const threshold = 1500000;
    const warningDays = list.filter(d => d.date >= todayStr && d.balance < threshold);

    return {
      todayDate: todayItem ? todayItem.date : todayStr,
      todayBalance: todayItem ? todayItem.balance : 0,
      todayRemarks: todayItem ? todayItem.remarks : '',
      monthIncome,
      monthExpense,
      monthYoSubcontract,
      monthSubcontract,
      monthCogs,
      monthLoanRepay,
      monthOwnerExpense,
      monthTax,
      warningDays
    };
  }

  importCashflowCsv(csvText) {
    if (!csvText || !csvText.trim()) return false;
    const lines = csvText.trim().split(/\\r?\\n/);
    if (lines.length < 5) return false;

    // ヘッダー行判定（4行目または見出しが含まれる行を探す）
    let startRow = 4; // 0-indexed で5行目
    const newList = [];

    for (let i = startRow; i < lines.length; i++) {
      const parts = lines[i].split(',').map(s => s.replace(/^\"|\"$/g, '').trim());
      if (parts.length < 5) continue;
      
      const rawDate = parts[1]; // B列: 日付
      if (!rawDate || !rawDate.match(/\\d{4}/)) continue;
      
      const dateStr = rawDate.replace(/\\//g, '-').slice(0, 10);
      const weekday = parts[2] || '';
      const remarks = parts[3] || '';
      const balance = parseInt(parts[4] ? parts[4].replace(/,/g, '') : '0', 10) || 0;
      const incomeTotal = parseInt(parts[7] ? parts[7].replace(/,/g, '') : '0', 10) || 0;
      const salesIncome = parseInt(parts[8] ? parts[8].replace(/,/g, '') : '0', 10) || 0;
      const expenseTotal = parseInt(parts[10] ? parts[10].replace(/,/g, '') : '0', 10) || 0;
      const yoSubcontract = parseInt(parts[11] ? parts[11].replace(/,/g, '') : '0', 10) || 0;
      const subcontract = parseInt(parts[12] ? parts[12].replace(/,/g, '') : '0', 10) || 0;
      const cogs = parseInt(parts[13] ? parts[13].replace(/,/g, '') : '0', 10) || 0;
      const genExpense = parseInt(parts[14] ? parts[14].replace(/,/g, '') : '0', 10) || 0;
      const loanRepay = parseInt(parts[15] ? parts[15].replace(/,/g, '') : '0', 10) || 0;
      const ownerExpense = parseInt(parts[16] ? parts[16].replace(/,/g, '') : '0', 10) || 0;
      const withholdingTax = parseInt(parts[17] ? parts[17].replace(/,/g, '') : '0', 10) || 0;
      const consumptionTax = parseInt(parts[18] ? parts[18].replace(/,/g, '') : '0', 10) || 0;
      const otherExpense = parseInt(parts[19] ? parts[19].replace(/,/g, '') : '0', 10) || 0;

      newList.append ? null : newList.push({
        date: dateStr,
        weekday,
        remarks,
        balance,
        incomeTotal,
        salesIncome,
        loanIncome: 0,
        expenseTotal,
        yoSubcontract,
        subcontract,
        cogs,
        genExpense,
        loanRepay,
        ownerExpense,
        withholdingTax,
        consumptionTax,
        otherExpense
      });
    }

    if (newList.length > 0) {
      this.data.cashflowDailySchedule = newList;
      if (!this.data.spreadsheetConfig) this.data.spreadsheetConfig = {};
      const now = new Date();
      this.data.spreadsheetConfig.lastSyncedAt = now.toLocaleString('ja-JP');
      this.saveData();
      return true;
    }
    return false;
  }
"""

# StoneAppStore の末尾（最後の波括弧の前）に挿入
last_brace_idx = text.rfind('}')
if last_brace_idx != -1:
    text = text[:last_brace_idx] + new_methods + "\n}\n"

with open('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated store.js successfully!')
