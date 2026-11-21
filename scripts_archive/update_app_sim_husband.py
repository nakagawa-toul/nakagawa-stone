app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add listeners in initEventListeners()
sim_listeners = """
    // シミュレーションモーダル リスナー
    const btnOpenSim = document.getElementById('btnOpenSimulationModal');
    if (btnOpenSim) {
      btnOpenSim.addEventListener('click', () => this.openSimulationModal());
    }

    const simCheckDelay = document.getElementById('simCheckDelay');
    const simSalesRange = document.getElementById('simSalesRange');
    const simInputExtraExp = document.getElementById('simInputExtraExp');

    [simCheckDelay, simSalesRange, simInputExtraExp].forEach(el => {
      if (el) el.addEventListener('input', () => this.updateStressTestResult());
    });
"""

anchor = "    // 第4段階：請求書写真撮影・AI読取リスナー"
code = code.replace(anchor, sim_listeners + "\n" + anchor)

# 2. Add Simulation methods and update applyUserRoleView in StoneApp
sim_husband_methods = """
  // ==============================================================
  // 将来資金シミュレーション（ストレステスト）ハンドラー
  // ==============================================================
  openSimulationModal() {
    const modal = document.getElementById('modalStressTest');
    if (!modal) return;
    this.updateStressTestResult();
    modal.classList.remove('hidden');
  }

  updateStressTestResult() {
    const checkDelay = document.getElementById('simCheckDelay')?.checked || false;
    const salesRangeVal = parseInt(document.getElementById('simSalesRange')?.value || '0', 10);
    const extraExpVal = parseInt(document.getElementById('simInputExtraExp')?.value || '0', 10);

    const salesRateLabel = document.getElementById('simSalesRateLabel');
    if (salesRateLabel) {
      salesRateLabel.textContent = salesRangeVal === 0 ? '通常 (0%減)' : `▼ ${salesRangeVal}% 減少`;
    }

    const result = window.stoneStore.runStressTestSimulation({
      delayBigIncomes: checkDelay,
      salesReductionRate: salesRangeVal / 100,
      extraExpenseAmount: extraExpVal,
      months: 6
    });

    const badge = document.getElementById('simSafetyBadge');
    const minBalVal = document.getElementById('simMinBalVal');
    const detail = document.getElementById('simResultDetail');

    if (minBalVal) minBalVal.textContent = `¥${result.minTotalBal.toLocaleString()}`;

    if (badge) {
      if (result.safetyStatus === 'safe') {
        badge.className = 'px-2 py-0.5 rounded text-[10px] font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
        badge.textContent = '✅ 安全・余裕あり';
        if (minBalVal) minBalVal.className = 'text-2xl font-black text-emerald-400';
      } else if (result.safetyStatus === 'warning') {
        badge.className = 'px-2 py-0.5 rounded text-[10px] font-black bg-amber-500/20 text-amber-300 border border-amber-500/40';
        badge.textContent = '⚠️ 要注意ゾーン';
        if (minBalVal) minBalVal.className = 'text-2xl font-black text-amber-400';
      } else {
        badge.className = 'px-2 py-0.5 rounded text-[10px] font-black bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse';
        badge.textContent = '🚨 資金ショート予測！';
        if (minBalVal) minBalVal.className = 'text-2xl font-black text-rose-400';
      }
    }

    if (detail) {
      if (result.hasShortage) {
        detail.innerHTML = `
          <div class="text-rose-300 font-bold">⚠️ このシナリオでは資金が不足する日が発生します：</div>
          <div class="mt-1 text-slate-300">最短で <strong>${result.minDate}</strong> に最低手元残高が <strong class="text-rose-400">¥${result.minTotalBal.toLocaleString()}</strong> まで悪化します。事前に借入の準備や支払日の調整が必要です。</div>
        `;
      } else {
        detail.innerHTML = `
          <div class="text-emerald-300 font-bold">✅ このシミュレーション下でも手元資金は安全を維持できます：</div>
          <div class="mt-1 text-slate-300">最も残高が減る <strong>${result.minDate}</strong> でも <strong class="text-emerald-300">¥${result.minTotalBal.toLocaleString()}</strong> の手元資金が確保され、石材仕入代や給与・公庫返済に支障はありません。</div>
        `;
      }
    }
  }
"""

# Replace applyUserRoleView with enhanced version
old_role_view = """  // 夫婦別画面（管理者モード vs ご主人用シンプル閲覧モード）
  applyUserRoleView(role) {
    const isHusband = role === 'husband';
    
    // ご主人モードの場合：編集ボタンや設定ボタンを非表示にし、視認性をさらにシンプル化
    const editButtons = [
      'btnOpenAccountsModal',
      'btnOpenYayoiModal',
      'btnOpenMisocaModal',
      'btnOpenPhotoScanModal',
      'btnTopOpenTransferModal',
      'btnDailyOpenTransferModal',
      'btnDailyOpenAddTxModal'
    ];

    editButtons.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        if (isHusband) el.classList.add('opacity-40', 'pointer-events-none');
        else el.classList.remove('opacity-40', 'pointer-events-none');
      }
    });

    if (isHusband) {
      this.showToast('👨‍💼 夫モード（現場・閲覧専用）に切り替えました。複雑な会計設定を省き、資金状況が一目でわかります。');
    }
  }"""

new_role_view = """  // 夫婦別画面（管理者モード vs ご主人用シンプル閲覧モード）
  applyUserRoleView(role) {
    const isHusband = role === 'husband';
    const husbandDashboard = document.getElementById('husbandQuickDashboard');

    if (husbandDashboard) {
      if (isHusband) {
        husbandDashboard.classList.remove('hidden');
        // ご主人専用カードのデータ反映
        const accounts = window.stoneStore.getAccounts();
        const totalCash = accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0);
        const kpis = window.stoneStore.getDashboardKPIs();

        const husbandTotalCash = document.getElementById('husbandTotalCash');
        const husbandMonthIn = document.getElementById('husbandMonthIn');
        const husbandMonthOut = document.getElementById('husbandMonthOut');
        const husbandMonthStatus = document.getElementById('husbandMonthStatus');
        const husbandShortageBadge = document.getElementById('husbandShortageBadge');

        if (husbandTotalCash) husbandTotalCash.textContent = `¥${totalCash.toLocaleString()}`;
        if (husbandMonthIn) husbandMonthIn.textContent = `¥${kpis.next30Income.toLocaleString()}`;
        if (husbandMonthOut) husbandMonthOut.textContent = `¥${kpis.next30Expense.toLocaleString()}`;

        if (husbandMonthStatus) {
          if (kpis.next30Net >= 0) {
            husbandMonthStatus.textContent = `✅ 今月は黒字見込み（＋¥${kpis.next30Net.toLocaleString()}）`;
            husbandMonthStatus.className = 'text-[10px] text-emerald-300 font-bold mt-1';
          } else {
            husbandMonthStatus.textContent = `⚠️ 今月は出金先行（−¥${Math.abs(kpis.next30Net).toLocaleString()}）`;
            husbandMonthStatus.className = 'text-[10px] text-amber-300 font-bold mt-1';
          }
        }

        if (husbandShortageBadge) {
          if (kpis.shortageAlerts && kpis.shortageAlerts.length > 0) {
            husbandShortageBadge.textContent = '🚨 要注意: 資金不足の恐れあり！';
            husbandShortageBadge.className = 'text-sm font-black text-rose-400 mt-1 animate-pulse';
          } else {
            husbandShortageBadge.textContent = '✅ 今後3か月は安全圏です';
            husbandShortageBadge.className = 'text-sm font-bold text-emerald-300 mt-1';
          }
        }
      } else {
        husbandDashboard.classList.add('hidden');
      }
    }
    
    // ご主人モードの場合：編集ボタンや設定ボタンを非表示にし、誤操作を防止
    const editButtons = [
      'btnOpenAccountsModal',
      'btnOpenYayoiModal',
      'btnOpenMisocaModal',
      'btnOpenPhotoScanModal',
      'btnTopOpenTransferModal',
      'btnDailyOpenTransferModal',
      'btnDailyOpenAddTxModal'
    ];

    editButtons.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        if (isHusband) el.classList.add('opacity-40', 'pointer-events-none');
        else el.classList.remove('opacity-40', 'pointer-events-none');
      }
    });

    if (isHusband) {
      this.showToast('👨‍💼 夫モード（現場・閲覧専用）に切り替えました。複雑な会計設定を省き、資金状況が一目でわかります。');
    }
  }"""

code = code.replace(old_role_view, sim_husband_methods + "\n\n" + new_role_view)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js with simulation modal and enhanced husband role view.")
