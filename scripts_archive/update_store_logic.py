import re

store_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js'

with open(store_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update loadData method
old_loadData = """  loadData() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        return {
          ...INITIAL_DATA,
          ...parsed,
          bankAccount: { ...INITIAL_DATA.bankAccount, ...(parsed.bankAccount || {}) }
        };
      }
    } catch (e) {
      console.warn('Failed to load data from localStorage:', e);
    }
    return JSON.parse(JSON.stringify(INITIAL_DATA));
  }"""

new_loadData = """  loadData() {
    try {
      let saved = localStorage.getItem(STORAGE_KEY);
      if (!saved) {
        // v3 からの自動移行
        saved = localStorage.getItem('nakagawa_stone_app_data_v3');
      }
      if (saved) {
        const parsed = JSON.parse(saved);
        const mergedAccounts = (parsed.accounts && parsed.accounts.length > 0)
          ? parsed.accounts
          : JSON.parse(JSON.stringify(DEFAULT_ACCOUNTS));
        
        // 取引データの口座補完
        const mergedTransactions = (parsed.transactions || INITIAL_DATA.transactions).map(tx => {
          if (!tx.accountId && tx.type !== 'transfer') {
            if (tx.category === '給与手当' || tx.category === '借入返済' || tx.category === '車両・燃料') {
              tx.accountId = 'bank-2'; // 十六銀行
            } else if (tx.category === '消耗品・工具') {
              tx.accountId = 'cash'; // 手許現金
            } else if (tx.category === '通信・光熱費') {
              tx.accountId = 'bank-4'; // 大垣共立
            } else if (tx.category === '戒名彫刻・納骨') {
              tx.accountId = 'bank-3'; // ゆうちょ
            } else {
              tx.accountId = 'bank-1'; // 中京銀行
            }
          }
          return tx;
        });

        return {
          ...INITIAL_DATA,
          ...parsed,
          accounts: mergedAccounts,
          transactions: mergedTransactions,
          bankAccount: { ...INITIAL_DATA.bankAccount, ...(parsed.bankAccount || {}) }
        };
      }
    } catch (e) {
      console.warn('Failed to load data from localStorage:', e);
    }
    return JSON.parse(JSON.stringify(INITIAL_DATA));
  }"""

code = code.replace(old_loadData, new_loadData)

# 2. Add Account and Transfer Helper methods in StoneAppStore
helper_methods = """
  // ==============================================================
  // 口座マスター管理（5銀行口座 + 手許現金）
  // ==============================================================
  getAccounts() {
    if (!this.data.accounts || this.data.accounts.length === 0) {
      this.data.accounts = JSON.parse(JSON.stringify(DEFAULT_ACCOUNTS));
      this.saveData();
    }
    return this.data.accounts;
  }

  getAccount(accountId) {
    const accounts = this.getAccounts();
    return accounts.find(a => a.id === accountId) || null;
  }

  updateAccount(accountId, updates) {
    const accounts = this.getAccounts();
    const idx = accounts.findIndex(a => a.id === accountId);
    if (idx !== -1) {
      accounts[idx] = { ...accounts[idx], ...updates, lastUpdated: new Date().toISOString() };
      this.saveData();
      return accounts[idx];
    }
    return null;
  }

  // 口座間振替の新規登録
  transferFunds({ date, fromAccountId, toAccountId, amount, note = '', isActual = false }) {
    if (!fromAccountId || !toAccountId || fromAccountId === toAccountId) {
      throw new Error('振替元と振替先には異なる口座を指定してください。');
    }
    const fromAcc = this.getAccount(fromAccountId);
    const toAcc = this.getAccount(toAccountId);
    const tx = {
      id: 'tx-tr-' + Date.now(),
      date: date || new Date().toISOString().slice(0, 10),
      type: 'transfer',
      fromAccountId,
      toAccountId,
      partner: `${fromAcc ? fromAcc.shortName : fromAccountId} ➔ ${toAcc ? toAcc.shortName : toAccountId}`,
      category: '口座間振替',
      amount: Number(amount) || 0,
      projectId: null,
      isActual: Boolean(isActual),
      note: note || '口座間資金移動'
    };
    this.addTransaction(tx);
    return tx;
  }

  // 取引の支払口座設定（未定からの決定・変更）
  setTransactionAccount(txId, accountId) {
    return this.updateTransaction(txId, { accountId: accountId || 'unassigned' });
  }

  // 取引の期日変更・入金遅延反映
  delayTransaction(txId, newDate, reason = '') {
    const tx = this.data.transactions.find(t => t.id === txId);
    if (!tx) return null;
    const originalDate = tx.originalDueDate || tx.date;
    const note = tx.note ? `${tx.note} (遅延: ${originalDate}➔${newDate} ${reason})` : `(期日変更: ${originalDate}➔${newDate})`;
    return this.updateTransaction(txId, {
      date: newDate,
      originalDueDate: originalDate,
      isDelayed: true,
      note
    });
  }
"""

if "getAccounts()" not in code:
    code = code.replace("  // ユーザー・権限制御\n  getCurrentUser() {", helper_methods + "\n  // ユーザー・権限制御\n  getCurrentUser() {")

# 3. Update calculateDailyCashFlowSchedule with multi-account support, shortage alert, and unassigned warning
old_daily_func = """  calculateDailyCashFlowSchedule() {
    const bank = this.data.bankAccount;
    const baseDate = bank.baseDate || '2026-10-31';
    let runningBalance = Number(bank.baseBalance) || 0;

    const futureTxs = this.data.transactions
      .filter(tx => tx.date >= baseDate)
      .sort((a, b) => a.date.localeCompare(b.date));

    const dateMap = {};
    futureTxs.forEach(tx => {
      if (!dateMap[tx.date]) {
        dateMap[tx.date] = {
          date: tx.date,
          income: 0,
          expense: 0,
          items: []
        };
      }
      dateMap[tx.date].items.push(tx);
      if (tx.type === 'income') dateMap[tx.date].income += tx.amount;
      else dateMap[tx.date].expense += tx.amount;
    });

    const list = Object.keys(dateMap).sort().map(d => {
      const dayData = dateMap[d];
      const net = dayData.income - dayData.expense;
      runningBalance += net;

      // 支払集中日フラグ（25日給料日、27日公庫、月末振込日、10万円以上の支払い）
      const dayNum = parseInt(d.slice(8), 10);
      const isPayday = dayNum === 25;
      const isLoanDay = dayNum === 27;
      const isMonthEnd = dayNum >= 28;
      const isHighOutflow = dayData.expense >= 200000;

      return {
        date: d,
        income: dayData.income,
        expense: dayData.expense,
        net,
        balance: runningBalance,
        items: dayData.items,
        isPayday,
        isLoanDay,
        isMonthEnd,
        isHighOutflow
      };
    });

    return list;
  }"""

new_daily_func = """  // ==============================================================
  // 5口座＋手許現金 日別資金繰り・残高予測シミュレーション
  // 二重計上防止・口座別不足警告・未配分支払管理
  // ==============================================================
  calculateDailyCashFlowSchedule(options = {}) {
    const accounts = this.getAccounts();
    const baseDate = options.baseDate || accounts[0]?.baseDate || '2026-10-31';
    
    // 各口座の初期残高マップ
    const runningBalances = {};
    let totalRunningBalance = 0;
    accounts.forEach(acc => {
      const bal = Number(acc.baseBalance) || 0;
      runningBalances[acc.id] = bal;
      totalRunningBalance += bal;
    });

    const futureTxs = this.data.transactions
      .filter(tx => tx.date >= baseDate)
      .sort((a, b) => a.date.localeCompare(b.date));

    // 日別マップの初期化
    const dateMap = {};
    futureTxs.forEach(tx => {
      const d = tx.date;
      if (!dateMap[d]) {
        dateMap[d] = {
          date: d,
          totalIncome: 0,
          totalExpense: 0,
          unassignedExpense: 0, // 口座未定の支払額
          items: [],
          accountDeltas: {} // 口座ごとの当日の出入り
        };
        accounts.forEach(a => {
          dateMap[d].accountDeltas[a.id] = { income: 0, expense: 0, transferIn: 0, transferOut: 0 };
        });
      }

      dateMap[d].items.push(tx);

      if (tx.type === 'income') {
        dateMap[d].totalIncome += Number(tx.amount) || 0;
        const targetAcc = tx.accountId || 'bank-1';
        if (dateMap[d].accountDeltas[targetAcc]) {
          dateMap[d].accountDeltas[targetAcc].income += Number(tx.amount) || 0;
        }
      } else if (tx.type === 'expense') {
        const amt = Number(tx.amount) || 0;
        dateMap[d].totalExpense += amt;
        const targetAcc = tx.accountId;
        if (!targetAcc || targetAcc === 'unassigned') {
          // 支払口座未定：全社合計からは引くが、個別口座は未定（未配分）
          dateMap[d].unassignedExpense += amt;
        } else if (dateMap[d].accountDeltas[targetAcc]) {
          dateMap[d].accountDeltas[targetAcc].expense += amt;
        }
      } else if (tx.type === 'transfer') {
        // 口座間振替：全口座合計の収支はゼロ（二重計上なし）
        const amt = Number(tx.amount) || 0;
        const fromId = tx.fromAccountId;
        const toId = tx.toAccountId;
        if (dateMap[d].accountDeltas[fromId]) {
          dateMap[d].accountDeltas[fromId].transferOut += amt;
        }
        if (dateMap[d].accountDeltas[toId]) {
          dateMap[d].accountDeltas[toId].transferIn += amt;
        }
      }
    });

    const shortageAlerts = []; // 残高不足警告リスト
    const unassignedAlerts = []; // 未配分支払警告リスト

    const sortedDates = Object.keys(dateMap).sort();
    const list = sortedDates.map(d => {
      const dayData = dateMap[d];
      
      // 全社合計の収支
      const dayTotalNet = dayData.totalIncome - dayData.totalExpense;
      totalRunningBalance += dayTotalNet;

      // 各口座ごとの残高計算
      const accountSnapshots = {};
      accounts.forEach(acc => {
        const delta = dayData.accountDeltas[acc.id] || { income: 0, expense: 0, transferIn: 0, transferOut: 0 };
        const accNet = (delta.income + delta.transferIn) - (delta.expense + delta.transferOut);
        runningBalances[acc.id] += accNet;
        
        const isShortage = runningBalances[acc.id] < 0;
        if (isShortage) {
          shortageAlerts.push({
            date: d,
            accountId: acc.id,
            accountName: acc.name,
            shortName: acc.shortName,
            balance: runningBalances[acc.id],
            shortageAmount: Math.abs(runningBalances[acc.id])
          });
        }

        accountSnapshots[acc.id] = {
          name: acc.name,
          shortName: acc.shortName,
          color: acc.color,
          income: delta.income,
          expense: delta.expense,
          transferIn: delta.transferIn,
          transferOut: delta.transferOut,
          net: accNet,
          balance: runningBalances[acc.id],
          isShortage
        };
      });

      // 未配分支払のチェック
      if (dayData.unassignedExpense > 0) {
        unassignedAlerts.push({
          date: d,
          amount: dayData.unassignedExpense,
          items: dayData.items.filter(t => t.type === 'expense' && (!t.accountId || t.accountId === 'unassigned'))
        });
      }

      const dayNum = parseInt(d.slice(8), 10);
      return {
        date: d,
        totalIncome: dayData.totalIncome,
        totalExpense: dayData.totalExpense,
        totalNet: dayTotalNet,
        totalBalance: totalRunningBalance,
        unassignedExpense: dayData.unassignedExpense,
        accountSnapshots,
        items: dayData.items,
        isPayday: dayNum === 25,
        isLoanDay: dayNum === 27,
        isMonthEnd: dayNum >= 28,
        isHighOutflow: dayData.totalExpense >= 200000,
        hasShortage: Object.values(accountSnapshots).some(a => a.isShortage)
      };
    });

    return {
      dailyList: list,
      shortageAlerts,
      unassignedAlerts,
      finalTotalBalance: totalRunningBalance,
      finalAccountBalances: { ...runningBalances }
    };
  }

  // トップ画面用 KPI・状況サマリー
  getDashboardKPIs() {
    const accounts = this.getAccounts();
    const todayStr = new Date().toISOString().slice(0, 10);
    const schedule = this.calculateDailyCashFlowSchedule({ baseDate: accounts[0]?.baseDate || '2026-10-31' });
    
    // 現在の資金残高（全口座合計）
    const totalCurrentCash = accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0);
    
    // 今後30日間の入出金予定
    const next30DaysEnd = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    const next30DaysTxs = this.data.transactions.filter(tx => tx.date >= todayStr && tx.date <= next30DaysEnd);
    
    const next30Income = next30DaysTxs.filter(t => t.type === 'income').reduce((sum, t) => sum + (Number(t.amount) || 0), 0);
    const next30Expense = next30DaysTxs.filter(t => t.type === 'expense').reduce((sum, t) => sum + (Number(t.amount) || 0), 0);
    
    // 未回収の請求書（未入金の売掛金）
    const uncollectedIncomes = this.data.transactions.filter(tx => tx.type === 'income' && !tx.isActual);
    const uncollectedTotal = uncollectedIncomes.reduce((sum, t) => sum + (Number(t.amount) || 0), 0);

    return {
      totalCurrentCash,
      accounts: accounts.map(a => ({
        ...a,
        currentBalance: schedule.finalAccountBalances[a.id] ?? a.baseBalance
      })),
      next30Income,
      next30Expense,
      next30Net: next30Income - next30Expense,
      uncollectedCount: uncollectedIncomes.length,
      uncollectedTotal,
      shortageAlerts: schedule.shortageAlerts,
      unassignedAlerts: schedule.unassignedAlerts
    };
  }"""

code = code.replace(old_daily_func, new_daily_func)

with open(store_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("StoneAppStore logic updated successfully.")
