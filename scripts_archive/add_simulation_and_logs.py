import re

store_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js'

with open(store_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update updateTransaction and delayTransaction to automatically record activityLogs (変更履歴の自動保存)
log_hook = """  updateTransaction(txId, updates) {
    const idx = this.data.transactions.findIndex(t => t.id === txId);
    if (idx !== -1) {
      const oldTx = this.data.transactions[idx];
      const oldAmount = oldTx.amount;
      const oldDate = oldTx.date;
      
      this.data.transactions[idx] = { ...oldTx, ...updates };
      
      // 金額変更や期日変更の履歴を自動記録（指示書 第4項要件）
      const user = this.getCurrentUserLabel();
      let changeDesc = [];
      if (updates.amount && updates.amount !== oldAmount) {
        changeDesc.push(`金額変更: ¥${oldAmount.toLocaleString()} ➔ ¥${updates.amount.toLocaleString()}`);
      }
      if (updates.date && updates.date !== oldDate) {
        changeDesc.push(`期日変更: ${oldDate} ➔ ${updates.date}`);
      }
      if (updates.accountId && updates.accountId !== oldTx.accountId) {
        changeDesc.push(`口座変更: ${oldTx.accountId || '未定'} ➔ ${updates.accountId}`);
      }

      if (changeDesc.length > 0) {
        this.addActivityLog({
          user,
          category: '資金繰り変更',
          action: `【取引変更】${oldTx.partner} (${oldTx.category})`,
          details: changeDesc.join(' / ')
        });
      }

      this.saveData();
      return this.data.transactions[idx];
    }
    return null;
  }"""

old_update_tx = """  updateTransaction(txId, updates) {
    const idx = this.data.transactions.findIndex(t => t.id === txId);
    if (idx !== -1) {
      this.data.transactions[idx] = { ...this.data.transactions[idx], ...updates };
      this.saveData();
      return this.data.transactions[idx];
    }
    return null;
  }"""

if old_update_tx in code:
    code = code.replace(old_update_tx, log_hook)

# 2. Add runStressTestSimulation method to StoneAppStore
simulation_methods = """
  // ==============================================================
  // 将来資金予測 ＆ シナリオシミュレーション（ストレステスト）
  // ==============================================================
  runStressTestSimulation(options = {}) {
    const {
      delayBigIncomes = false, // 大口入金の30日遅延
      delayDays = 30,
      salesReductionRate = 0,  // 売上減少率 (0.0 〜 0.5)
      extraExpenseAmount = 0,  // 突発支出（機械修繕・車両等）
      months = 6               // 予測期間
    } = options;

    const accounts = this.getAccounts();
    const baseDate = accounts[0]?.baseDate || '2026-10-31';

    // 期間終了日の計算
    const endDate = new Date(new Date(baseDate).getTime() + months * 30 * 86400000).toISOString().slice(0, 10);

    // シミュレーション用取引の複製と適用
    let simulatedTxs = this.data.transactions
      .filter(tx => tx.date >= baseDate && tx.date <= endDate)
      .map(tx => ({ ...tx }));

    // ① 大口入金遅延シナリオ
    if (delayBigIncomes) {
      simulatedTxs = simulatedTxs.map(tx => {
        if (tx.type === 'income' && tx.amount >= 500000 && !tx.isActual) {
          const d = new Date(tx.date);
          d.setDate(d.getDate() + delayDays);
          return { ...tx, date: d.toISOString().slice(0, 10), note: tx.note + ' (シミュレーション: 遅延)' };
        }
        return tx;
      });
    }

    // ② 売上減少シナリオ
    if (salesReductionRate > 0) {
      simulatedTxs = simulatedTxs.map(tx => {
        if (tx.type === 'income' && !tx.isActual) {
          const reducedAmt = Math.round(tx.amount * (1 - salesReductionRate));
          return { ...tx, amount: reducedAmt, note: tx.note + ` (シミュレーション: ${Math.round(salesReductionRate*100)}%減)` };
        }
        return tx;
      });
    }

    // ③ 突発大型支出シナリオ
    if (extraExpenseAmount > 0) {
      const suddenDate = new Date(Date.now() + 14 * 86400000).toISOString().slice(0, 10);
      simulatedTxs.push({
        id: 'sim-extra-exp',
        date: suddenDate,
        type: 'expense',
        partner: '突発設備修繕・緊急出費',
        category: 'その他経費',
        amount: extraExpenseAmount,
        accountId: 'bank-1',
        isActual: false,
        note: 'シミュレーション: 突発的支出'
      });
    }

    // シミュレーション残高計算
    let totalBal = accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0);
    const accBals = {};
    accounts.forEach(a => { accBals[a.id] = Number(a.baseBalance) || 0; });

    let minTotalBal = totalBal;
    let minDate = baseDate;
    const shortages = [];

    const dateMap = {};
    simulatedTxs.sort((a, b) => a.date.localeCompare(b.date)).forEach(tx => {
      if (!dateMap[tx.date]) dateMap[tx.date] = [];
      dateMap[tx.date].push(tx);
    });

    Object.keys(dateMap).sort().forEach(d => {
      dateMap[d].forEach(tx => {
        if (tx.type === 'income') {
          totalBal += tx.amount;
          if (tx.accountId && accBals[tx.accountId] !== undefined) accBals[tx.accountId] += tx.amount;
        } else if (tx.type === 'expense') {
          totalBal -= tx.amount;
          if (tx.accountId && accBals[tx.accountId] !== undefined) accBals[tx.accountId] -= tx.amount;
        }
      });

      if (totalBal < minTotalBal) {
        minTotalBal = totalBal;
        minDate = d;
      }

      accounts.forEach(a => {
        if (accBals[a.id] < 0) {
          shortages.push({
            date: d,
            accountName: a.name,
            shortName: a.shortName,
            balance: accBals[a.id],
            shortageAmount: Math.abs(accBals[a.id])
          });
        }
      });
    });

    return {
      months,
      baseTotalCash: accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0),
      finalSimulatedBalance: totalBal,
      minTotalBal,
      minDate,
      hasShortage: minTotalBal < 0 || shortages.length > 0,
      shortages,
      safetyStatus: minTotalBal >= 1500000 ? 'safe' : (minTotalBal >= 0 ? 'warning' : 'danger')
    };
  }
"""

if "runStressTestSimulation" not in code:
    code = code.replace("  // ユーザー・権限制御\n  getCurrentUser() {", simulation_methods + "\n  // ユーザー・権限制御\n  getCurrentUser() {")

with open(store_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated store.js with activity logging hook and stress test simulation successfully.")
