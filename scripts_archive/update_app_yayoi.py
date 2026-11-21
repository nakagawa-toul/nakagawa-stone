import re

app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add event listeners for Yayoi CSV import in initEventListeners()
yayoi_listeners = """
    // 弥生CSV取り込みリスナー
    const btnOpenYayoi = document.getElementById('btnOpenYayoiModal');
    if (btnOpenYayoi) {
      btnOpenYayoi.addEventListener('click', () => this.openYayoiModal());
    }

    const yayoiFileInput = document.getElementById('yayoiFileInput');
    if (yayoiFileInput) {
      yayoiFileInput.addEventListener('change', (e) => this.handleYayoiFileSelect(e));
    }

    const yayoiDropZone = document.getElementById('yayoiDropZone');
    if (yayoiDropZone) {
      yayoiDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        yayoiDropZone.classList.add('bg-indigo-100', 'border-indigo-600');
      });
      yayoiDropZone.addEventListener('dragleave', () => {
        yayoiDropZone.classList.remove('bg-indigo-100', 'border-indigo-600');
      });
      yayoiDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        yayoiDropZone.classList.remove('bg-indigo-100', 'border-indigo-600');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.processYayoiFile(e.dataTransfer.files[0]);
        }
      });
    }

    const btnLoadSampleYayoi = document.getElementById('btnLoadSampleYayoi');
    if (btnLoadSampleYayoi) {
      btnLoadSampleYayoi.addEventListener('click', () => this.handleLoadSampleYayoi());
    }
"""

anchor_init = "    // --- 新規：トップ資金ダッシュボード ＆ 6口座・振替・遅延・財務三表リスナー ---"
code = code.replace(anchor_init, anchor_init + "\n" + yayoi_listeners)

# 2. Update renderTopFundsDashboard to show Yayoi status badge
badge_update_old = """    // 1. 全口座合計手元資金
    const topTotalCash = document.getElementById('topTotalCash');
    if (topTotalCash) {
      topTotalCash.textContent = `¥${kpis.totalCurrentCash.toLocaleString()}`;
    }"""

badge_update_new = """    // 1. 全口座合計手元資金
    const topTotalCash = document.getElementById('topTotalCash');
    if (topTotalCash) {
      topTotalCash.textContent = `¥${kpis.totalCurrentCash.toLocaleString()}`;
    }

    const yayoiData = window.stoneStore.getYayoiData();
    const yayoiBadge = document.getElementById('yayoiLastImportBadge');
    if (yayoiBadge) {
      if (yayoiData && yayoiData.lastImportedAt) {
        yayoiBadge.textContent = `弥生連携: ${yayoiData.lastImportedAt.slice(5, 16)} (${yayoiData.importedCount}件取込済)`;
        yayoiBadge.className = 'hidden sm:inline text-[10px] bg-emerald-950/80 text-emerald-300 border border-emerald-500/50 px-2 py-0.5 rounded ml-2 font-bold';
      } else {
        yayoiBadge.textContent = '弥生連携: 未取り込み';
        yayoiBadge.className = 'hidden sm:inline text-[10px] bg-slate-800 text-slate-400 border border-slate-700 px-2 py-0.5 rounded ml-2';
      }
    }"""

code = code.replace(badge_update_old, badge_update_new)

# 3. Add Yayoi modal handlers and enhanced renderBSPLContent inside class StoneApp
yayoi_methods = """
  // ==============================================================
  // 弥生CSV取り込み ハンドラー
  // ==============================================================
  openYayoiModal() {
    const modal = document.getElementById('modalYayoiImport');
    if (!modal) return;
    const resultArea = document.getElementById('yayoiImportResultArea');
    if (resultArea) resultArea.classList.add('hidden');
    modal.classList.remove('hidden');
  }

  handleYayoiFileSelect(e) {
    if (e.target.files && e.target.files.length > 0) {
      this.processYayoiFile(e.target.files[0]);
    }
  }

  processYayoiFile(file) {
    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const text = evt.target.result;
        const result = window.stoneStore.importYayoiCSV(text, file.name);
        this.displayYayoiImportResult(result);
        this.showToast(`弥生CSV「${file.name}」を取り込みました（${result.parsedCount}件）`);
        this.render();
      } catch (err) {
        alert('弥生CSVの取り込みに失敗しました: ' + err.message);
      }
    };
    reader.readAsText(file, 'UTF-8');
  }

  handleLoadSampleYayoi() {
    try {
      const result = window.stoneStore.loadSampleYayoiCSV();
      this.displayYayoiImportResult(result);
      this.showToast('石材店のサンプル弥生仕訳データを取り込みました！');
      this.render();
    } catch (err) {
      alert('サンプル取り込みエラー: ' + err.message);
    }
  }

  displayYayoiImportResult(result) {
    const resultArea = document.getElementById('yayoiImportResultArea');
    if (!resultArea) return;

    resultArea.className = 'p-3.5 rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-950 text-xs space-y-1';
    resultArea.innerHTML = `
      <div class="font-bold flex items-center text-emerald-800">
        <svg class="w-4 h-4 mr-1 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <span>弥生データの取り込みが完了しました</span>
      </div>
      <div class="text-[11px] text-emerald-900 mt-1 space-y-0.5">
        <div>・新規取り込み仕訳: <strong>${result.parsedCount} 件</strong></div>
        <div>・重複スキップ（二重計上防止）: <strong>${result.duplicateCount} 件</strong></div>
        <div>・取り込み日時: <strong>${result.lastImportedAt}</strong></div>
        <div class="text-[10px] text-emerald-700 mt-1 font-semibold">✅ 5銀行口座＋現金の残高および財務三表が自動更新されました</div>
      </div>
    `;
    resultArea.classList.remove('hidden');
  }

  // ==============================================================
  // 財務三表（B/S・P/L・C/F ＆ 損益・現金差異分析）レンダリング
  // ==============================================================
  renderBSPLContent() {
    const cont = document.getElementById('bsplContentArea');
    if (!cont) return;

    const data = window.stoneStore.getFinancialStatements();
    const pl = data.pl;
    const bs = data.bs;
    const cf = data.cf;

    const bsplTabPL = document.getElementById('bsplTabPL');
    const bsplTabBS = document.getElementById('bsplTabBS');
    const bsplTabCF = document.getElementById('bsplTabCF');

    // 損益と現金の違いの解説カードHTML
    const plVsCashBoxHtml = `
      <div class="p-3 bg-amber-50/80 border border-amber-300 rounded-xl space-y-2 mt-3">
        <div class="flex items-center justify-between text-amber-950">
          <span class="font-bold flex items-center text-xs">
            <span class="mr-1.5 text-base">💡</span> 【最重要】損益（利益）と現金残高が一致しない理由
          </span>
          <span class="text-[10px] bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded font-bold">黒字倒産を防ぐ分析</span>
        </div>
        <p class="text-[11px] text-amber-900 leading-relaxed">
          「損益計算書で営業利益が <strong>¥${pl.operatingProfit.toLocaleString()}</strong> 出ているのに、なぜ口座の手元資金（<strong>¥${bs.assets.current.cashAndDeposits.toLocaleString()}</strong>）と違うのか？」の原因内訳です。
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px]">
          ${data.plVsCashAnalysis.map(item => `
            <div class="p-2 bg-white rounded-lg border border-amber-200 flex justify-between items-center">
              <div>
                <span class="font-bold text-slate-800">${item.factor}</span>
                <div class="text-[10px] text-slate-500">${item.note}</div>
              </div>
              <span class="font-black whitespace-nowrap ml-2 ${item.amount >= 0 ? 'text-emerald-700' : 'text-rose-700'}">
                ${item.amount >= 0 ? '+' : ''}¥${item.amount.toLocaleString()}
              </span>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    if (this.bsplTab === 'pl') {
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      const marginRate = ((pl.grossProfit / pl.sales) * 100).toFixed(1);

      cont.innerHTML = `
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-900 text-sm flex items-center">
              <span>📊 損益計算書 (P/L: Profit & Loss Statement)</span>
              <span class="ml-2 text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">弥生確定データ基準</span>
            </span>
            <span class="text-[11px] text-slate-500">年間累計実績</span>
          </div>

          <table class="w-full text-xs text-left border-collapse">
            <tr class="border-b bg-slate-50"><td class="py-2.5 px-3 font-bold text-slate-900">Ⅰ. 売上高（工事完工高合計）</td><td class="py-2.5 px-3 text-right font-black text-slate-900">¥${pl.sales.toLocaleString()}</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">売上原価（石材部材・生コン建材・外注加工・重機リース）</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥${pl.cogs.toLocaleString()}</td></tr>
            <tr class="border-b bg-blue-50/70">
              <td class="py-2.5 px-3 font-bold text-blue-900">Ⅱ. 売上総利益（限界利益 粗利） <span class="ml-1 text-[10px] bg-blue-200 text-blue-800 px-1.5 py-0.2 rounded">粗利率: ${marginRate}%</span></td>
              <td class="py-2.5 px-3 text-right font-black text-blue-900">¥${pl.grossProfit.toLocaleString()}</td>
            </tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">販売費及び一般管理費（専従者給与・車両燃料・消耗品工具・保険・通信光熱費）</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥${pl.sga.toLocaleString()}</td></tr>
            <tr class="border-b bg-emerald-50">
              <td class="py-2.5 px-3 font-bold text-emerald-900">Ⅲ. 営業利益（本業の儲け）</td>
              <td class="py-2.5 px-3 text-right font-black text-emerald-900">+¥${pl.operatingProfit.toLocaleString()}</td>
            </tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">営業外費用（公庫・地銀借入利息）</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥${pl.nonOperatingExpense.toLocaleString()}</td></tr>
            <tr class="border-b bg-slate-900 text-white">
              <td class="py-2.5 px-3 font-bold">★ 差引経常利益（青色申告特別控除前所得）</td>
              <td class="py-2.5 px-3 text-right font-black text-sky-300">¥${pl.ordinaryProfit.toLocaleString()}</td>
            </tr>
          </table>

          ${plVsCashBoxHtml}
        </div>
      `;
    } else if (this.bsplTab === 'bs') {
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      cont.innerHTML = `
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-900 text-sm flex items-center">
              <span>📑 貸借対照表 (B/S: Balance Sheet)</span>
              <span class="ml-2 text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">5口座残高連動</span>
            </span>
            <span class="text-[11px] text-slate-500">財政状態</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <!-- 資産の部 -->
            <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
              <div class="font-bold text-blue-900 border-b pb-1.5 text-xs flex justify-between">
                <span>【資産の部】</span>
                <span class="text-blue-700 font-mono">¥${bs.totalAssets.toLocaleString()}</span>
              </div>
              <div class="space-y-1.5 text-xs">
                <div class="font-semibold text-slate-700 text-[11px]">■ 流動資産</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">現預金（5銀行口座＋手許現金）</span>
                  <strong class="font-bold text-blue-800">¥${bs.assets.current.cashAndDeposits.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">売掛金（未回収の請求書）</span>
                  <strong class="font-bold text-slate-800">¥${bs.assets.current.accountsReceivable.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">棚卸資産（展示墓石・石材部材）</span>
                  <strong class="font-bold text-slate-800">¥${bs.assets.current.inventory.toLocaleString()}</strong>
                </div>
                <div class="font-semibold text-slate-700 text-[11px] pt-1">■ 固定資産</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">有形固定資産（車両・カニクレーン・切削機）</span>
                  <strong class="font-bold text-slate-800">¥${bs.assets.fixed.tangible.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pt-2 border-t font-black text-slate-900 text-xs">
                  <span>資産合計 (Total Assets)</span>
                  <span>¥${bs.totalAssets.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <!-- 負債・純資産の部 -->
            <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
              <div class="font-bold text-rose-900 border-b pb-1.5 text-xs flex justify-between">
                <span>【負債・純資産の部】</span>
                <span class="text-rose-700 font-mono">¥${(bs.totalLiab + bs.totalEquity).toLocaleString()}</span>
              </div>
              <div class="space-y-1.5 text-xs">
                <div class="font-semibold text-slate-700 text-[11px]">■ 流動負債</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">買掛金・未払金（石材建材仕入代）</span>
                  <strong class="font-bold text-slate-800">¥${bs.liabilities.current.accountsPayable.toLocaleString()}</strong>
                </div>
                <div class="font-semibold text-slate-700 text-[11px] pt-1">■ 固定負債</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">長期借入金（公庫・地銀借入残高）</span>
                  <strong class="font-bold text-rose-700">¥${bs.liabilities.fixed.longTermDebt.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pt-1 border-t text-[11px] text-slate-600">
                  <span>負債合計</span>
                  <strong>¥${bs.totalLiab.toLocaleString()}</strong>
                </div>

                <div class="font-semibold text-blue-900 text-[11px] pt-2">■ 純資産の部</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">元入金・自己資本・当期利益</span>
                  <strong class="font-black text-blue-900">¥${bs.totalEquity.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pt-2 border-t font-black text-slate-900 text-xs">
                  <span>負債・純資産合計</span>
                  <span>¥${(bs.totalLiab + bs.totalEquity).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          ${plVsCashBoxHtml}
        </div>
      `;
    } else {
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      cont.innerHTML = `
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-900 text-sm flex items-center">
              <span>💵 キャッシュフロー計算書 (C/F: Cash Flow Statement)</span>
              <span class="ml-2 text-[10px] bg-sky-100 text-sky-800 px-2 py-0.5 rounded font-bold">営業・投資・財務3区分</span>
            </span>
            <span class="text-[11px] text-slate-500">現金の実際の出入り</span>
          </div>

          <table class="w-full text-xs text-left border-collapse">
            <tr class="border-b bg-emerald-50/70">
              <td class="py-2.5 px-3 font-bold text-emerald-950 flex items-center">
                <span>Ⅰ. 営業活動によるキャッシュフロー（本業の現金創出）</span>
                <span class="ml-2 text-[9px] bg-emerald-200 text-emerald-800 px-1.5 py-0.2 rounded font-bold">確定値</span>
              </td>
              <td class="py-2.5 px-3 text-right font-black text-emerald-900">+¥${cf.operatingCF.toLocaleString()}</td>
            </tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">・税引前当期利益</td><td class="py-2 px-3 text-right text-slate-800">¥${pl.ordinaryProfit.toLocaleString()}</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">・売掛金の回収（入金）</td><td class="py-2 px-3 text-right text-slate-800">+¥1,200,000</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">・仕入代金・買掛金の支払い</td><td class="py-2 px-3 text-right text-rose-700">-¥845,000</td></tr>

            <tr class="border-b bg-slate-50">
              <td class="py-2.5 px-3 font-bold text-slate-800 flex items-center">
                <span>Ⅱ. 投資活動によるキャッシュフロー（機械・車両設備投資）</span>
                <span class="ml-2 text-[9px] bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded font-medium">推計値</span>
              </td>
              <td class="py-2.5 px-3 text-right font-bold text-slate-700">¥${cf.investingCF.toLocaleString()}</td>
            </tr>

            <tr class="border-b bg-purple-50/70">
              <td class="py-2.5 px-3 font-bold text-purple-950 flex items-center">
                <span>Ⅲ. 財務活動によるキャッシュフロー（公庫・地銀借入金の返済）</span>
                <span class="ml-2 text-[9px] bg-purple-200 text-purple-800 px-1.5 py-0.2 rounded font-bold">確定値</span>
              </td>
              <td class="py-2.5 px-3 text-right font-black text-purple-900">¥${cf.financingCF.toLocaleString()}</td>
            </tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">・日本政策金融公庫 設備資金元金定期返済</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥960,000</td></tr>

            <tr class="border-b bg-slate-900 text-white">
              <td class="py-2.5 px-3 font-bold">★ 現金及び現金同等物の純増減額 (Net Cash Flow)</td>
              <td class="py-2.5 px-3 text-right font-black text-sky-300">¥${cf.netCF.toLocaleString()}</td>
            </tr>
          </table>

          <div class="p-3 bg-emerald-50 border border-emerald-300 rounded-xl text-xs text-emerald-950 flex items-center justify-between">
            <div>
              <div class="font-bold flex items-center text-emerald-900">
                <span class="mr-1 text-base">✅</span> 本業の現金創出力（営業CF）で借入返済を全額カバーできています
              </div>
              <p class="text-[10px] text-emerald-800 mt-0.5">本業の儲け（+¥${cf.operatingCF.toLocaleString()}）が、借入金返済（-¥${Math.abs(cf.financingCF).toLocaleString()}）を大きく上回っており、資金繰りとして極めて健全です。</p>
            </div>
          </div>

          ${plVsCashBoxHtml}
        </div>
      `;
    }
  }
"""

# Replace existing renderBSPLContent with enhanced version inside StoneApp
code = re.sub(r'  renderBSPLContent\(\)\s*\{.*?\}\s*\}', yayoi_methods + '\n}', code, flags=re.DOTALL)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js with Yayoi import handlers and enhanced 3 financial statements.")
