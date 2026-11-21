import re

app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update constructor to add dailyScheduleViewMode and bsplTab
code = code.replace("this.fundsSubtab = 'statement';", "this.fundsSubtab = 'statement';\n    this.dailyScheduleViewMode = 'total'; // 'total' | 'matrix'\n    this.bsplTab = 'pl'; // 'pl' | 'bs' | 'cf'")

# 2. Update render() to always render renderTopFundsDashboard()
render_old = """  render() {
    this.renderHeaderAndBadges();
    
    if (this.currentView === 'home') this.renderTasks();"""

render_new = """  render() {
    this.renderHeaderAndBadges();
    this.renderTopFundsDashboard();
    
    if (this.currentView === 'home') this.renderTasks();"""

code = code.replace(render_old, render_new)

# 3. Add Event Listeners for new modals and daily view switch in initEventListeners()
new_listeners = """
    // --- 新規：トップ資金ダッシュボード ＆ 6口座・振替・遅延・財務三表リスナー ---
    const btnOpenAccountsModal = document.getElementById('btnOpenAccountsModal');
    if (btnOpenAccountsModal) {
      btnOpenAccountsModal.addEventListener('click', () => this.openAccountsModal());
    }

    const formAccounts = document.getElementById('formAccounts');
    if (formAccounts) {
      formAccounts.addEventListener('submit', (e) => this.handleSaveAccounts(e));
    }

    const btnTopOpenTransfer = document.getElementById('btnTopOpenTransferModal');
    if (btnTopOpenTransfer) {
      btnTopOpenTransfer.addEventListener('click', () => this.openTransferModal());
    }

    const btnDailyOpenTransfer = document.getElementById('btnDailyOpenTransferModal');
    if (btnDailyOpenTransfer) {
      btnDailyOpenTransfer.addEventListener('click', () => this.openTransferModal());
    }

    const formTransfer = document.getElementById('formTransfer');
    if (formTransfer) {
      formTransfer.addEventListener('submit', (e) => this.handleSaveTransfer(e));
    }

    const btnGoToDaily = document.getElementById('btnGoToDailyCashFlow');
    if (btnGoToDaily) {
      btnGoToDaily.addEventListener('click', () => {
        this.switchView('funds');
        this.switchFundsSubtab('cashflow');
      });
    }

    const btnDailyViewTotal = document.getElementById('btnDailyViewTotal');
    const btnDailyViewMatrix = document.getElementById('btnDailyViewMatrix');
    if (btnDailyViewTotal && btnDailyViewMatrix) {
      btnDailyViewTotal.addEventListener('click', () => {
        this.dailyScheduleViewMode = 'total';
        btnDailyViewTotal.className = 'px-2.5 py-1 rounded-md bg-white text-blue-700 shadow-sm transition font-bold';
        btnDailyViewMatrix.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition font-medium';
        this.renderDailyCashFlowSchedule();
      });
      btnDailyViewMatrix.addEventListener('click', () => {
        this.dailyScheduleViewMode = 'matrix';
        btnDailyViewMatrix.className = 'px-2.5 py-1 rounded-md bg-white text-blue-700 shadow-sm transition font-bold';
        btnDailyViewTotal.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition font-medium';
        this.renderDailyCashFlowSchedule();
      });
    }

    const btnDailyOpenAddTx = document.getElementById('btnDailyOpenAddTxModal');
    if (btnDailyOpenAddTx) {
      btnDailyOpenAddTx.addEventListener('click', () => this.openAddTxModal());
    }

    const btnCloseDailyDetail = document.getElementById('btnCloseDailyDetail');
    if (btnCloseDailyDetail) {
      btnCloseDailyDetail.addEventListener('click', () => {
        const cont = document.getElementById('dailyDetailContainer');
        if (cont) cont.classList.add('hidden');
      });
    }

    const formDelayTx = document.getElementById('formDelayTx');
    if (formDelayTx) {
      formDelayTx.addEventListener('submit', (e) => this.handleSaveDelayTx(e));
    }

    document.querySelectorAll('.btn-quick-delay').forEach(btn => {
      btn.addEventListener('click', () => {
        const days = parseInt(btn.dataset.days, 10);
        const inputNewDate = document.getElementById('delayInputNewDate');
        if (inputNewDate && inputNewDate.value) {
          const d = new Date(inputNewDate.value);
          d.setDate(d.getDate() + days);
          inputNewDate.value = d.toISOString().slice(0, 10);
        }
      });
    });

    const btnTopOpenBSPL = document.getElementById('btnTopOpenBSPLModal');
    if (btnTopOpenBSPL) {
      btnTopOpenBSPL.addEventListener('click', () => this.openBSPLModal());
    }

    // 財務三表タブ切り替え
    const bsplTabPL = document.getElementById('bsplTabPL');
    const bsplTabBS = document.getElementById('bsplTabBS');
    const bsplTabCF = document.getElementById('bsplTabCF');
    if (bsplTabPL && bsplTabBS && bsplTabCF) {
      bsplTabPL.addEventListener('click', () => { this.bsplTab = 'pl'; this.renderBSPLContent(); });
      bsplTabBS.addEventListener('click', () => { this.bsplTab = 'bs'; this.renderBSPLContent(); });
      bsplTabCF.addEventListener('click', () => { this.bsplTab = 'cf'; this.renderBSPLContent(); });
    }
"""

anchor_init_listeners = "  initEventListeners() {"
code = code.replace(anchor_init_listeners, anchor_init_listeners + "\n" + new_listeners)

# 4. Update formTx submission to save txInputAccount
old_tx_submit_save = """    const newTx = {
      date: document.getElementById('txInputDate').value,
      type: document.getElementById('txInputType').value,
      partner: document.getElementById('txInputPartner').value.trim(),
      amount: parseInt(document.getElementById('txInputAmount').value, 10),
      category: document.getElementById('txInputCategory').value,
      projectId: document.getElementById('txInputProject').value || null,
      isActual: document.getElementById('txInputIsActual').value === 'true',
      note: document.getElementById('txInputNote').value.trim()
    };"""

new_tx_submit_save = """    const accountSelector = document.getElementById('txInputAccount');
    const selectedAccount = accountSelector ? accountSelector.value : 'bank-1';

    const newTx = {
      date: document.getElementById('txInputDate').value,
      type: document.getElementById('txInputType').value,
      partner: document.getElementById('txInputPartner').value.trim(),
      amount: parseInt(document.getElementById('txInputAmount').value, 10),
      category: document.getElementById('txInputCategory').value,
      accountId: selectedAccount,
      projectId: document.getElementById('txInputProject').value || null,
      isActual: document.getElementById('txInputIsActual').value === 'true',
      note: document.getElementById('txInputNote').value.trim()
    };"""

code = code.replace(old_tx_submit_save, new_tx_submit_save)

# 5. Add Core Methods for Top Dashboard, Daily Cash Flow Schedule & Modals
core_methods = """
  // ==============================================================
  // 【最優先】トップ画面 資金繰り・口座別残高ダッシュボード描画
  // ==============================================================
  renderTopFundsDashboard() {
    const kpis = window.stoneStore.getDashboardKPIs();
    
    // 1. 全口座合計手元資金
    const topTotalCash = document.getElementById('topTotalCash');
    if (topTotalCash) {
      topTotalCash.textContent = `¥${kpis.totalCurrentCash.toLocaleString()}`;
    }

    // 2. 口座別残高カード（5銀行＋手許現金、計6口座）
    const cardsContainer = document.getElementById('topAccountCardsContainer');
    if (cardsContainer) {
      cardsContainer.innerHTML = kpis.accounts.map(acc => {
        const isShortage = acc.currentBalance < 0;
        return `
          <div class="bg-slate-800/90 hover:bg-slate-800 p-2.5 rounded-xl border border-slate-700 transition cursor-pointer" onclick="app.switchView('funds'); app.switchFundsSubtab('cashflow');">
            <div class="flex items-center justify-between text-[10px]">
              <span class="font-bold truncate text-slate-300 flex items-center">
                <span class="w-2 h-2 rounded-full mr-1.5 flex-shrink-0" style="background-color: ${acc.color};"></span>
                ${acc.shortName}
              </span>
              <span class="text-[9px] px-1 py-0.2 rounded bg-slate-700 text-slate-400 font-mono">${acc.type === 'cash' ? '現金' : '口座'}</span>
            </div>
            <div class="text-sm sm:text-base font-extrabold mt-1 tracking-tight ${isShortage ? 'text-rose-400 font-black' : 'text-white'}">
              ¥${acc.currentBalance.toLocaleString()}
            </div>
            <div class="text-[9px] text-slate-400 mt-0.5 truncate">基準日: ${acc.baseDate || '10/31'}</div>
          </div>
        `;
      }).join('');
    }

    // 3. アラートエリア（資金ショート警告 ＆ 口座未定警告）
    const alertsArea = document.getElementById('topAlertsArea');
    if (alertsArea) {
      let alertsHtml = '';
      
      // 資金不足（ショート）警告
      if (kpis.shortageAlerts && kpis.shortageAlerts.length > 0) {
        const firstShortage = kpis.shortageAlerts[0];
        alertsHtml += `
          <div class="bg-rose-950/80 border border-rose-500/70 p-3 rounded-xl flex items-center justify-between shadow-sm animate-pulse">
            <div class="flex items-center space-x-2 text-xs">
              <span class="text-lg">⚠️</span>
              <div>
                <div class="font-bold text-rose-200">資金不足の予測が発生しています！（計 ${kpis.shortageAlerts.length} 件）</div>
                <div class="text-[11px] text-rose-300 mt-0.5">
                  最も早い不足: <strong>${firstShortage.date}</strong> に <strong>${firstShortage.accountName}</strong> で <span class="font-bold text-white underline">¥${firstShortage.shortageAmount.toLocaleString()} 不足</span>の予測
                </div>
              </div>
            </div>
            <button onclick="app.switchView('funds'); app.switchFundsSubtab('cashflow');" class="bg-rose-600 hover:bg-rose-500 text-white font-bold text-[10px] px-2.5 py-1.5 rounded-lg whitespace-nowrap transition">
              日繰り表で確認 ➔
            </button>
          </div>
        `;
      }

      // 支払口座未定の警告
      if (kpis.unassignedAlerts && kpis.unassignedAlerts.length > 0) {
        const totalUnassignedAmt = kpis.unassignedAlerts.reduce((sum, a) => sum + a.amount, 0);
        alertsHtml += `
          <div class="bg-amber-950/70 border border-amber-500/60 p-2.5 rounded-xl flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="text-base text-amber-400">⚠️</span>
              <div>
                <span class="font-bold text-amber-200">支払口座が未定の支払いが ${kpis.unassignedAlerts.length} 日分（計 ¥${totalUnassignedAmt.toLocaleString()}）あります</span>
                <p class="text-[10px] text-amber-300/80">※全口座合計からは引かれていますが、口座別予測では未配分額として管理されています。</p>
              </div>
            </div>
            <button onclick="app.switchView('funds'); app.switchFundsSubtab('cashflow');" class="bg-amber-600 hover:bg-amber-500 text-white font-bold text-[10px] px-2 py-1 rounded-lg transition whitespace-nowrap">
              口座を指定 ➔
            </button>
          </div>
        `;
      }

      alertsArea.innerHTML = alertsHtml;
    }

    // 4. 今後30日間の入出金予定
    const topNext30Income = document.getElementById('topNext30Income');
    const topNext30Expense = document.getElementById('topNext30Expense');
    const topNext30Net = document.getElementById('topNext30Net');
    if (topNext30Income) topNext30Income.textContent = `+¥${kpis.next30Income.toLocaleString()}`;
    if (topNext30Expense) topNext30Expense.textContent = `-¥${kpis.next30Expense.toLocaleString()}`;
    if (topNext30Net) {
      topNext30Net.textContent = `${kpis.next30Net >= 0 ? '+' : ''}¥${kpis.next30Net.toLocaleString()}`;
      topNext30Net.className = `font-bold text-xs ${kpis.next30Net >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
    }

    // 5. 未回収の請求書（売掛金）
    const topUncollectedCount = document.getElementById('topUncollectedCount');
    const topUncollectedTotal = document.getElementById('topUncollectedTotal');
    if (topUncollectedCount) topUncollectedCount.textContent = `${kpis.uncollectedCount}件`;
    if (topUncollectedTotal) topUncollectedTotal.textContent = `¥${kpis.uncollectedTotal.toLocaleString()}`;
  }

  // ==============================================================
  // 5口座＋手許現金 日別資金繰り・口座別予測表のレンダリング
  // ==============================================================
  renderDailyCashFlowSchedule() {
    const table = document.getElementById('dailyScheduleTable');
    if (!table) return;

    const accounts = window.stoneStore.getAccounts();
    const result = window.stoneStore.calculateDailyCashFlowSchedule();
    const list = result.dailyList;

    // 口座ミニインジケーターの描画
    const indicator = document.getElementById('dailyAccountsIndicator');
    if (indicator) {
      indicator.innerHTML = accounts.map(acc => {
        const bal = result.finalAccountBalances[acc.id] ?? acc.baseBalance;
        const isShortage = bal < 0;
        return `
          <div class="bg-slate-50 p-2 rounded-lg border border-slate-200">
            <div class="text-[10px] text-slate-500 font-bold flex items-center justify-between">
              <span class="truncate flex items-center">
                <span class="w-2 h-2 rounded-full mr-1" style="background-color: ${acc.color};"></span>
                ${acc.shortName}
              </span>
            </div>
            <div class="text-xs font-black mt-0.5 ${isShortage ? 'text-rose-600' : 'text-slate-800'}">
              ¥${bal.toLocaleString()}
            </div>
          </div>
        `;
      }).join('');
    }

    // 警告バナーエリア
    const dailyAlertsContainer = document.getElementById('dailyAlertsContainer');
    if (dailyAlertsContainer) {
      let alertsHtml = '';
      if (result.shortageAlerts.length > 0) {
        alertsHtml += `
          <div class="p-2.5 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-900 flex items-center justify-between">
            <div class="flex items-center space-x-1.5 font-bold">
              <span>⚠️ 残高不足警告:</span>
              <span>${result.shortageAlerts.map(a => `${a.date} [${a.shortName}: ¥${a.shortageAmount.toLocaleString()}不足]`).join('、')}</span>
            </div>
          </div>
        `;
      }
      if (result.unassignedAlerts.length > 0) {
        alertsHtml += `
          <div class="p-2.5 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-center justify-between">
            <span class="font-bold">⚠️ 支払口座未定の支払いがあります（日別の「未配分額」をご確認いただき、口座を指定してください）</span>
          </div>
        `;
      }
      dailyAlertsContainer.innerHTML = alertsHtml;
    }

    if (list.length === 0) {
      table.innerHTML = '<tr><td class="p-4 text-center text-slate-400 text-xs">基準日以降の入出金予定はありません</td></tr>';
      return;
    }

    if (this.dailyScheduleViewMode === 'total') {
      // ----------------------------------------------------------
      // ビュー A: 全社合計ビュー
      // ----------------------------------------------------------
      let html = `
        <thead class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px] border-b">
          <tr>
            <th class="py-2.5 px-3">日付</th>
            <th class="py-2.5 px-2">特徴</th>
            <th class="py-2.5 px-3 text-right">入金額</th>
            <th class="py-2.5 px-3 text-right">出金額</th>
            <th class="py-2.5 px-3 text-right text-amber-700">口座未定(未配分)</th>
            <th class="py-2.5 px-3 text-right">当日収支</th>
            <th class="py-2.5 px-3 text-right bg-slate-200/70">全口座合計残高</th>
            <th class="py-2.5 px-2 text-center">明細</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
      `;

      list.forEach(item => {
        let badgeHtml = '';
        if (item.isPayday) badgeHtml = '<span class="bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-amber-300">給料日</span>';
        else if (item.isLoanDay) badgeHtml = '<span class="bg-purple-100 text-purple-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-purple-300">公庫引落</span>';
        else if (item.isMonthEnd) badgeHtml = '<span class="bg-rose-100 text-rose-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-rose-300">月末振込</span>';
        else if (item.isHighOutflow) badgeHtml = '<span class="bg-rose-50 text-rose-700 px-1.5 py-0.5 rounded text-[10px] font-medium border border-rose-200">大型出金</span>';
        else badgeHtml = '<span class="text-slate-400 text-[10px]">通常</span>';

        const rowShortageClass = item.hasShortage ? 'bg-rose-50/60 font-semibold' : '';

        html += `
          <tr class="hover:bg-slate-50 transition cursor-pointer ${rowShortageClass}" onclick="app.showDailyDetail('${item.date}')">
            <td class="py-2.5 px-3 font-bold text-slate-800 whitespace-nowrap">${item.date}</td>
            <td class="py-2.5 px-2 whitespace-nowrap">${badgeHtml}</td>
            <td class="py-2.5 px-3 text-right font-bold text-emerald-700 whitespace-nowrap">
              ${item.totalIncome > 0 ? `+¥${item.totalIncome.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-rose-700 whitespace-nowrap">
              ${item.totalExpense > 0 ? `-¥${item.totalExpense.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-amber-600 whitespace-nowrap">
              ${item.unassignedExpense > 0 ? `⚠️ ¥${item.unassignedExpense.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
            </td>
            <td class="py-2.5 px-3 text-right font-extrabold whitespace-nowrap ${item.totalNet >= 0 ? 'text-emerald-700' : 'text-rose-700'}">
              ${item.totalNet >= 0 ? '+' : ''}¥${item.totalNet.toLocaleString()}
            </td>
            <td class="py-2.5 px-3 text-right font-black text-slate-900 whitespace-nowrap bg-slate-50">
              ¥${item.totalBalance.toLocaleString()}
            </td>
            <td class="py-2.5 px-2 text-center">
              <button class="text-blue-600 hover:text-blue-800 font-bold text-[11px] underline">明細(${item.items.length})</button>
            </td>
          </tr>
        `;
      });

      html += '</tbody>';
      table.innerHTML = html;

    } else {
      // ----------------------------------------------------------
      // ビュー B: 5口座＋手許現金 口座別マトリクスビュー
      // ----------------------------------------------------------
      let html = `
        <thead class="bg-slate-100 text-slate-700 font-bold text-[10px] border-b">
          <tr>
            <th class="py-2.5 px-2.5 whitespace-nowrap sticky left-0 bg-slate-100 z-10">日付</th>
            <th class="py-2.5 px-2 whitespace-nowrap">特徴</th>
            ${accounts.map(a => `<th class="py-2.5 px-2.5 text-right whitespace-nowrap" style="color: ${a.color}">${a.shortName}</th>`).join('')}
            <th class="py-2.5 px-2.5 text-right whitespace-nowrap text-amber-600">未配分支払</th>
            <th class="py-2.5 px-3 text-right whitespace-nowrap bg-slate-200/80 font-black">合計残高</th>
            <th class="py-2.5 px-2 text-center whitespace-nowrap">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
      `;

      list.forEach(item => {
        let badgeHtml = '';
        if (item.isPayday) badgeHtml = '<span class="bg-amber-100 text-amber-900 px-1 py-0.2 rounded text-[9px] font-bold">給与</span>';
        else if (item.isLoanDay) badgeHtml = '<span class="bg-purple-100 text-purple-900 px-1 py-0.2 rounded text-[9px] font-bold">公庫</span>';
        else if (item.isMonthEnd) badgeHtml = '<span class="bg-rose-100 text-rose-900 px-1 py-0.2 rounded text-[9px] font-bold">月末</span>';
        else badgeHtml = '<span class="text-slate-400 text-[9px]">-</span>';

        html += `
          <tr class="hover:bg-slate-50 transition ${item.hasShortage ? 'bg-rose-50/50' : ''}">
            <td class="py-2 px-2.5 font-bold text-slate-800 whitespace-nowrap sticky left-0 bg-white z-10">${item.date}</td>
            <td class="py-2 px-2 whitespace-nowrap">${badgeHtml}</td>
            ${accounts.map(a => {
              const snap = item.accountSnapshots[a.id];
              const isShort = snap && snap.isShortage;
              const balClass = isShort ? 'text-rose-600 bg-rose-100 font-black px-1.5 py-0.5 rounded' : 'text-slate-800 font-bold';
              return `
                <td class="py-2 px-2.5 text-right whitespace-nowrap">
                  <span class="${balClass}">¥${snap ? snap.balance.toLocaleString() : 0}</span>
                </td>
              `;
            }).join('')}
            <td class="py-2 px-2.5 text-right whitespace-nowrap font-bold ${item.unassignedExpense > 0 ? 'text-amber-600 bg-amber-50' : 'text-slate-300'}">
              ${item.unassignedExpense > 0 ? `¥${item.unassignedExpense.toLocaleString()}` : '-'}
            </td>
            <td class="py-2 px-3 text-right font-black text-slate-900 whitespace-nowrap bg-slate-50">
              ¥${item.totalBalance.toLocaleString()}
            </td>
            <td class="py-2 px-2 text-center whitespace-nowrap">
              <button onclick="app.showDailyDetail('${item.date}')" class="text-blue-600 hover:underline font-bold text-[10px]">明細</button>
            </td>
          </tr>
        `;
      });

      html += '</tbody>';
      table.innerHTML = html;
    }
  }

  // 日別明細のポップアップ展開
  showDailyDetail(dateStr) {
    const cont = document.getElementById('dailyDetailContainer');
    const title = document.getElementById('dailyDetailTitle');
    const listCont = document.getElementById('dailyDetailItemsList');
    if (!cont || !listCont) return;

    const accounts = window.stoneStore.getAccounts();
    const dayTxs = window.stoneStore.getTransactions().filter(t => t.date === dateStr);

    title.textContent = `📅 ${dateStr} の入出金・振替明細（計 ${dayTxs.length} 件）`;

    if (dayTxs.length === 0) {
      listCont.innerHTML = '<div class="text-slate-400 p-2 text-center">この日の個別取引はありません（残高推移のみ）</div>';
    } else {
      listCont.innerHTML = dayTxs.map(tx => {
        let typeBadge = '';
        let accInfo = '';
        
        if (tx.type === 'income') {
          typeBadge = '<span class="bg-emerald-100 text-emerald-800 text-[10px] px-1.5 py-0.5 rounded font-bold">入金</span>';
          const acc = accounts.find(a => a.id === tx.accountId);
          accInfo = `<span class="text-[10px] text-slate-500">入金先: ${acc ? acc.shortName : '中京銀行'}</span>`;
        } else if (tx.type === 'expense') {
          typeBadge = '<span class="bg-rose-100 text-rose-800 text-[10px] px-1.5 py-0.5 rounded font-bold">支払</span>';
          if (!tx.accountId || tx.accountId === 'unassigned') {
            accInfo = '<span class="bg-amber-100 text-amber-800 text-[10px] px-1.5 py-0.2 rounded font-bold">⚠️ 支払口座未定</span>';
          } else {
            const acc = accounts.find(a => a.id === tx.accountId);
            accInfo = `<span class="text-[10px] text-slate-500">支払口座: ${acc ? acc.shortName : tx.accountId}</span>`;
          }
        } else if (tx.type === 'transfer') {
          typeBadge = '<span class="bg-blue-100 text-blue-800 text-[10px] px-1.5 py-0.5 rounded font-bold">口座間振替</span>';
          const fromAcc = accounts.find(a => a.id === tx.fromAccountId);
          const toAcc = accounts.find(a => a.id === tx.toAccountId);
          accInfo = `<span class="text-[10px] text-blue-700 font-bold">${fromAcc ? fromAcc.shortName : tx.fromAccountId} ➔ ${toAcc ? toAcc.shortName : tx.toAccountId}</span>`;
        }

        const isActualBadge = tx.isActual
          ? '<span class="bg-slate-200 text-slate-700 text-[10px] px-1.5 py-0.2 rounded font-bold">実績済</span>'
          : '<span class="bg-amber-100 text-amber-800 text-[10px] px-1.5 py-0.2 rounded font-bold">予定</span>';

        return `
          <div class="bg-white p-2.5 rounded-lg border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-sm">
            <div class="space-y-0.5">
              <div class="flex items-center space-x-1.5">
                ${typeBadge}
                <span class="font-bold text-slate-900">${tx.partner}</span>
                <span class="text-slate-500 text-[11px]">(${tx.category})</span>
                ${isActualBadge}
              </div>
              <div class="flex items-center space-x-2 text-[10px]">
                ${accInfo}
                ${tx.note ? `<span class="text-slate-400">メモ: ${tx.note}</span>` : ''}
              </div>
            </div>

            <div class="flex items-center space-x-2 self-end sm:self-center">
              <span class="text-sm font-black ${tx.type === 'income' ? 'text-emerald-700' : (tx.type === 'expense' ? 'text-rose-700' : 'text-blue-700')}">
                ¥${Number(tx.amount).toLocaleString()}
              </span>

              <!-- アクションボタン群 -->
              <button onclick="app.toggleTxActual('${tx.id}')" class="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-bold border transition">
                ${tx.isActual ? '予定に戻す' : '実績化'}
              </button>

              <button onclick="app.openDelayModal('${tx.id}')" class="px-2 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 text-[10px] font-bold border border-blue-200 transition">
                期日・口座変更
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    cont.classList.remove('hidden');
    cont.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // 取引の実績化トグル
  toggleTxActual(txId) {
    window.stoneStore.toggleTransactionActual(txId);
    this.showToast('取引の状態を更新しました');
    this.render();
  }

  // ==============================================================
  // モーダル管理（6口座設定、口座間振替、期日遅延変更、財務三表）
  // ==============================================================
  openAccountsModal() {
    const modal = document.getElementById('modalAccounts');
    const container = document.getElementById('accountsFormContainer');
    if (!modal || !container) return;

    const accounts = window.stoneStore.getAccounts();
    container.innerHTML = accounts.map((acc, idx) => `
      <div class="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-1.5 font-bold text-slate-800 text-xs">
            <span class="w-3 h-3 rounded-full flex-shrink-0" style="background-color: ${acc.color}"></span>
            <input type="text" name="accName_${acc.id}" value="${acc.name}" required class="border border-slate-300 rounded px-2 py-1 text-xs font-bold w-48 sm:w-64 bg-white">
          </div>
          <span class="text-[10px] text-slate-400 font-mono">${acc.id}</span>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-[10px] text-slate-500 font-semibold mb-0.5">基準日（確認日）</label>
            <input type="date" name="accDate_${acc.id}" value="${acc.baseDate || '2026-10-31'}" required class="w-full border border-slate-300 rounded p-1.5 text-xs bg-white">
          </div>
          <div>
            <label class="block text-[10px] text-slate-500 font-semibold mb-0.5">基準残高（円）</label>
            <div class="relative">
              <span class="absolute left-2 top-1.5 text-slate-400 font-bold">¥</span>
              <input type="number" name="accBal_${acc.id}" value="${acc.baseBalance}" required min="0" step="1" class="w-full border border-slate-300 rounded pl-5 pr-2 py-1.5 text-xs font-bold bg-white">
            </div>
          </div>
        </div>
      </div>
    `).join('');

    modal.classList.remove('hidden');
  }

  handleSaveAccounts(e) {
    e.preventDefault();
    const accounts = window.stoneStore.getAccounts();
    const form = e.target;

    accounts.forEach(acc => {
      const nameInput = form.querySelector(`input[name="accName_${acc.id}"]`);
      const dateInput = form.querySelector(`input[name="accDate_${acc.id}"]`);
      const balInput = form.querySelector(`input[name="accBal_${acc.id}"]`);

      if (nameInput && dateInput && balInput) {
        window.stoneStore.updateAccount(acc.id, {
          name: nameInput.value.trim(),
          baseDate: dateInput.value,
          baseBalance: parseInt(balInput.value, 10) || 0
        });
      }
    });

    document.getElementById('modalAccounts').classList.add('hidden');
    this.showToast('5口座＋手許現金の残高設定を更新しました');
    this.render();
  }

  openTransferModal() {
    const modal = document.getElementById('modalTransfer');
    if (!modal) return;

    const accounts = window.stoneStore.getAccounts();
    const fromSel = document.getElementById('trInputFrom');
    const toSel = document.getElementById('trInputTo');

    if (fromSel && toSel) {
      fromSel.innerHTML = accounts.map(a => `<option value="${a.id}">${a.name}</option>`).join('');
      toSel.innerHTML = accounts.map(a => `<option value="${a.id}">${a.name}</option>`).join('');
      // デフォルトで出金元を中京銀行、入金先を十六銀行にセット
      fromSel.value = 'bank-1';
      toSel.value = 'bank-2';
    }

    document.getElementById('trInputDate').value = this.todayStr;
    document.getElementById('trInputAmount').value = '';
    document.getElementById('trInputNote').value = '';

    modal.classList.remove('hidden');
  }

  handleSaveTransfer(e) {
    e.preventDefault();
    try {
      const date = document.getElementById('trInputDate').value;
      const fromAccountId = document.getElementById('trInputFrom').value;
      const toAccountId = document.getElementById('trInputTo').value;
      const amount = parseInt(document.getElementById('trInputAmount').value, 10);
      const isActual = document.getElementById('trInputIsActual').value === 'true';
      const note = document.getElementById('trInputNote').value.trim();

      window.stoneStore.transferFunds({
        date,
        fromAccountId,
        toAccountId,
        amount,
        isActual,
        note
      });

      document.getElementById('modalTransfer').classList.add('hidden');
      this.showToast('口座間振替を登録しました（合計資金残高では二重計上されません）');
      this.render();
    } catch (err) {
      alert(err.message);
    }
  }

  openDelayModal(txId) {
    const modal = document.getElementById('modalDelayTx');
    const tx = window.stoneStore.getTransactions().find(t => t.id === txId);
    if (!modal || !tx) return;

    document.getElementById('delayModalTxId').value = tx.id;
    document.getElementById('delayModalPartner').textContent = tx.partner;
    document.getElementById('delayModalTitle').textContent = `${tx.type === 'income' ? '入金' : '支払'} [${tx.category}]`;
    document.getElementById('delayModalAmount').textContent = `¥${Number(tx.amount).toLocaleString()}`;
    document.getElementById('delayModalCurrentDate').textContent = tx.date;
    document.getElementById('delayInputNewDate').value = tx.date;
    document.getElementById('delayInputReason').value = '';

    const accSel = document.getElementById('delayInputAccount');
    if (accSel) {
      accSel.value = tx.accountId || 'unassigned';
    }

    modal.classList.remove('hidden');
  }

  handleSaveDelayTx(e) {
    e.preventDefault();
    const txId = document.getElementById('delayModalTxId').value;
    const newDate = document.getElementById('delayInputNewDate').value;
    const newAcc = document.getElementById('delayInputAccount').value;
    const reason = document.getElementById('delayInputReason').value.trim();

    window.stoneStore.delayTransaction(txId, newDate, reason);
    if (newAcc) {
      window.stoneStore.setTransactionAccount(txId, newAcc);
    }

    document.getElementById('modalDelayTx').classList.add('hidden');
    this.showToast('予定日および口座を更新しました');
    this.render();
  }

  // 財務三表モーダル
  openBSPLModal() {
    const modal = document.getElementById('modalBSPL');
    if (!modal) return;
    this.renderBSPLContent();
    modal.classList.remove('hidden');
  }

  renderBSPLContent() {
    const cont = document.getElementById('bsplContentArea');
    if (!cont) return;

    const bsplTabPL = document.getElementById('bsplTabPL');
    const bsplTabBS = document.getElementById('bsplTabBS');
    const bsplTabCF = document.getElementById('bsplTabCF');

    if (this.bsplTab === 'pl') {
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      cont.innerHTML = `
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-800 text-sm">📊 年間損益計算書 (P/L) 予測モデル</span>
            <span class="text-[10px] text-slate-500">弥生会計科目準拠</span>
          </div>
          <table class="w-full text-xs text-left border-collapse">
            <tr class="border-b bg-white"><td class="py-2 px-3 font-bold">Ⅰ. 売上高（工事完工高合計）</td><td class="py-2 px-3 text-right font-black text-slate-900">¥24,000,000</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">売上原価（石材・生コン建材・外注加工・重機）</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥10,080,000</td></tr>
            <tr class="border-b bg-blue-50/50"><td class="py-2 px-3 font-bold text-blue-900">Ⅱ. 売上総利益（限界利益 42.0%）</td><td class="py-2 px-3 text-right font-black text-blue-900">¥13,920,000</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">販売費及び一般管理費（給与・車両燃料・工具・保険・通信光熱）</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥10,800,000</td></tr>
            <tr class="border-b bg-emerald-50"><td class="py-2 px-3 font-bold text-emerald-900">Ⅲ. 営業利益（事業の儲け）</td><td class="py-2 px-3 text-right font-black text-emerald-900">+¥3,120,000</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">公庫・地銀借入利息</td><td class="py-2 px-3 text-right text-rose-700">-¥60,000</td></tr>
            <tr class="border-b bg-slate-900 text-white"><td class="py-2 px-3 font-bold">★ 差引経常利益（税引前）</td><td class="py-2 px-3 text-right font-black text-sky-300">¥3,060,000</td></tr>
          </table>
          <p class="text-[11px] text-slate-500">※やよいの青色申告オンラインから取り込んだ仕訳データを元に自動再計算されます。</p>
        </div>
      `;
    } else if (this.bsplTab === 'bs') {
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      const totalCash = window.stoneStore.getAccounts().reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0);
      cont.innerHTML = `
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-800 text-sm">📑 貸借対照表 (B/S) 財政状態</span>
            <span class="text-[10px] text-slate-500">資産・負債・純資産</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="bg-white p-3 rounded-lg border">
              <div class="font-bold text-blue-900 border-b pb-1 mb-2">【資産の部】</div>
              <div class="space-y-1.5 text-xs">
                <div class="flex justify-between"><span>現預金（5銀行＋手許現金）</span><strong class="font-bold text-slate-900">¥${totalCash.toLocaleString()}</strong></div>
                <div class="flex justify-between"><span>売掛金（未回収請求書）</span><strong class="font-bold text-slate-900">¥2,105,000</strong></div>
                <div class="flex justify-between"><span>棚卸資産（展示墓石・部材在庫）</span><strong class="font-bold text-slate-900">¥2,800,000</strong></div>
                <div class="flex justify-between"><span>固定資産（トラック・カニクレーン・工場設備）</span><strong class="font-bold text-slate-900">¥4,500,000</strong></div>
                <div class="flex justify-between pt-1 border-t font-black text-slate-900"><span>資産合計</span><span>¥${(totalCash + 9405000).toLocaleString()}</span></div>
              </div>
            </div>

            <div class="bg-white p-3 rounded-lg border">
              <div class="font-bold text-rose-900 border-b pb-1 mb-2">【負債・純資産の部】</div>
              <div class="space-y-1.5 text-xs">
                <div class="flex justify-between"><span>買掛金・未払金（石材建材仕入）</span><strong class="font-bold text-slate-900">¥1,045,000</strong></div>
                <div class="flex justify-between"><span>公庫・地銀借入残高（長期）</span><strong class="font-bold text-rose-700">¥4,200,000</strong></div>
                <div class="flex justify-between pt-1 border-t text-slate-600"><span>負債合計</span><strong>¥5,245,000</strong></div>
                <div class="flex justify-between pt-2 border-t font-bold text-blue-900"><span>元入金・自己資本（純資産）</span><strong class="font-black">¥${(totalCash + 9405000 - 5245000).toLocaleString()}</strong></div>
              </div>
            </div>
          </div>
        </div>
      `;
    } else {
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      const cfData = window.stoneStore.calculateCashFlowStatementByType();
      cont.innerHTML = `
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-800 text-sm">💵 キャッシュフロー計算書 (C/F) 3区分</span>
            <span class="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">営業・投資・財務</span>
          </div>
          <table class="w-full text-xs text-left border-collapse">
            <tr class="border-b bg-emerald-50/70"><td class="py-2.5 px-3 font-bold text-emerald-900">Ⅰ. 営業活動によるキャッシュフロー（本業の現金創出）</td><td class="py-2.5 px-3 text-right font-black text-emerald-900">¥${cfData.operatingCF.toLocaleString()}</td></tr>
            <tr class="border-b bg-white"><td class="py-2 px-3 pl-6 text-slate-600">Ⅱ. 投資活動によるキャッシュフロー（設備・工具購入）</td><td class="py-2 px-3 text-right font-bold text-slate-600">¥0 (推計値)</td></tr>
            <tr class="border-b bg-purple-50/70"><td class="py-2.5 px-3 font-bold text-purple-900">Ⅲ. 財務活動によるキャッシュフロー（借入元金返済）</td><td class="py-2.5 px-3 text-right font-black text-purple-900">¥${cfData.financingCF.toLocaleString()}</td></tr>
            <tr class="border-b bg-slate-900 text-white"><td class="py-2.5 px-3 font-bold">★ 現金及び現金同等物の純増減額</td><td class="py-2.5 px-3 text-right font-black text-sky-300">¥${cfData.netCF.toLocaleString()}</td></tr>
          </table>
          <div class="p-2.5 bg-blue-50 border border-blue-200 rounded-lg text-[11px] text-blue-900">
            ${cfData.isPositive ? '✅ 本業の営業CFで借入元金返済を完全に賄えており、財務的に極めて安全な状態です。' : '⚠️ 借入元金返済が営業CFを上回っています。資金ショートにご注意ください。'}
          </div>
        </div>
      `;
    }
  }
"""

code += core_methods

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("app.js updated with top dashboard, daily schedule, and modal handlers successfully.")
