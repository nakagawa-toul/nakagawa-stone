import re

html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Insert topFundsDashboard right after <section id="view-home" class="view-panel space-y-4">
top_funds_html = """
        <!-- ============================================================ -->
        <!-- 【最優先】中川石材 資金繰り・口座別残高ダッシュボード（指示書準拠） -->
        <!-- ============================================================ -->
        <div id="topFundsDashboard" class="bg-gradient-to-br from-slate-900 via-slate-800 to-blue-950 text-white rounded-2xl p-4 sm:p-5 shadow-lg space-y-4 border border-slate-700/60">
          
          <!-- 最上段：現在資金残高（全口座合計） ＆ アクションボタン -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-700/80 pb-3">
            <div>
              <div class="flex items-center space-x-2">
                <span class="text-xs text-sky-400 font-bold uppercase tracking-wider">🏦 今日現在の資金繰り状況</span>
                <span class="bg-emerald-500/20 text-emerald-300 text-[10px] px-2 py-0.5 rounded-full border border-emerald-500/30 font-medium">5銀行口座＋手許現金（計6財布）</span>
              </div>
              <div class="flex items-baseline space-x-2 mt-1">
                <div class="text-xs text-slate-400 font-medium">全口座合計 手元資金:</div>
                <div id="topTotalCash" class="text-2xl sm:text-4xl font-black text-white tracking-tight">¥0</div>
              </div>
            </div>

            <!-- ショートカットボタン群 -->
            <div class="flex flex-wrap items-center gap-2">
              <button id="btnOpenAccountsModal" class="bg-slate-800 hover:bg-slate-700 text-sky-300 border border-slate-600 text-xs px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 shadow-sm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path></svg>
                <span>口座残高の確認・変更</span>
              </button>

              <button id="btnTopOpenTransferModal" class="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 shadow-sm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path></svg>
                <span>口座間振替</span>
              </button>

              <button id="btnGoToDailyCashFlow" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 shadow-sm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                <span>日別資金繰り表へ</span>
              </button>
            </div>
          </div>

          <!-- 2段目：口座別残高カード（5銀行＋手許現金） -->
          <div>
            <div class="text-[11px] font-bold text-slate-300 mb-2 flex items-center justify-between">
              <span>● 口座別残高（個別管理）</span>
              <span class="text-[10px] text-slate-400">クリックでその口座の推移を表示</span>
            </div>
            <div id="topAccountCardsContainer" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              <!-- JSで動的にレンダリング -->
            </div>
          </div>

          <!-- 3段目：資金不足・未配分警告エリア（条件付き表示） -->
          <div id="topAlertsArea" class="space-y-2">
            <!-- JSで資金ショート警告、口座未定警告をレンダリング -->
          </div>

          <!-- 4段目：サマリーKPIカード（今後30日予定、未回収請求書、財務三表リンク、期間予測） -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1 text-xs">
            <!-- 今後30日間の入金・支払予定 -->
            <div class="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
              <div class="text-[11px] text-slate-400 font-semibold">📅 今後30日間の入出金予定</div>
              <div class="flex items-center justify-between mt-1 text-xs">
                <span class="text-emerald-400">入金: <strong id="topNext30Income">¥0</strong></span>
                <span class="text-rose-400">支払: <strong id="topNext30Expense">¥0</strong></span>
              </div>
              <div class="mt-1 pt-1 border-t border-slate-700/60 flex items-center justify-between">
                <span class="text-[10px] text-slate-400">差引収支:</span>
                <span id="topNext30Net" class="font-bold text-xs">¥0</span>
              </div>
            </div>

            <!-- 未回収の請求書（Misoca連携予定枠） -->
            <div class="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
              <div class="text-[11px] text-amber-300 font-semibold flex items-center justify-between">
                <span>📑 未回収の請求書（売掛金）</span>
                <span id="topUncollectedCount" class="bg-amber-400/20 text-amber-300 text-[10px] px-1.5 py-0.2 rounded font-bold">0件</span>
              </div>
              <div class="text-lg font-black text-amber-200 mt-1" id="topUncollectedTotal">¥0</div>
              <div class="text-[10px] text-slate-400 mt-0.5">Misoca連携・入金予定日管理</div>
            </div>

            <!-- 財務三表リンク ＆ 予測期間切替 -->
            <div class="bg-slate-800/80 p-3 rounded-xl border border-slate-700 flex flex-col justify-between">
              <div class="flex items-center justify-between">
                <span class="text-[11px] text-sky-300 font-semibold">📊 財務三表 ＆ 予測</span>
                <button id="btnTopOpenBSPLModal" class="bg-sky-600 hover:bg-sky-500 text-white text-[10px] px-2 py-0.5 rounded font-bold transition">
                  三表を見る ➔
                </button>
              </div>
              <div class="flex items-center space-x-1 mt-2">
                <span class="text-[10px] text-slate-400">予測期間:</span>
                <button class="top-forecast-btn px-2 py-1 rounded bg-sky-700 text-white text-[10px] font-bold" data-period="3">3か月</button>
                <button class="top-forecast-btn px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-[10px] font-bold" data-period="6">6か月</button>
                <button class="top-forecast-btn px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-[10px] font-bold" data-period="12">12か月</button>
              </div>
            </div>
          </div>

        </div>
"""

home_anchor = '<section id="view-home" class="view-panel space-y-4">'
if "id=\"topFundsDashboard\"" not in html:
    html = html.replace(home_anchor, home_anchor + "\n" + top_funds_html)

# 2. Update subtab-panel-cashflow (日別資金繰り表の全面刷新)
cashflow_old_pattern = r'<div id="subtab-panel-cashflow" class="funds-subpanel hidden space-y-4">.*?<!-- ======================================================== -->\s*<!-- サブ画面 3: 従来の残高推移'

cashflow_new_html = """<div id="subtab-panel-cashflow" class="funds-subpanel hidden space-y-4">
            
            <!-- 日別資金繰り ヘッダー ＆ 操作バー -->
            <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-3 border-slate-100">
                <div>
                  <h3 class="text-sm sm:text-base font-bold text-slate-900 flex items-center">
                    <span>📅 5口座＋手許現金 日別資金繰り・口座別予測表</span>
                    <span class="ml-2 text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">最優先機能</span>
                  </h3>
                  <p class="text-[11px] text-slate-500 mt-0.5">口座別の入出金予定、口座間振替（二重計上なし）、資金ショート警告、支払口座未定の管理</p>
                </div>
                
                <div class="flex flex-wrap items-center gap-2">
                  <!-- 表示切り替えトグル -->
                  <div class="flex items-center bg-slate-100 p-1 rounded-lg text-xs font-bold border border-slate-200">
                    <button id="btnDailyViewTotal" class="px-2.5 py-1 rounded-md bg-white text-blue-700 shadow-sm transition">全口座合計</button>
                    <button id="btnDailyViewMatrix" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition">口座別マトリクス</button>
                  </div>

                  <button id="btnDailyOpenTransferModal" class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow transition flex items-center space-x-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"></path></svg>
                    <span>振替を登録</span>
                  </button>

                  <button id="btnDailyOpenAddTxModal" class="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow transition flex items-center space-x-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    <span>入出金を登録</span>
                  </button>
                </div>
              </div>

              <!-- 口座残高インジケーター（6口座） -->
              <div id="dailyAccountsIndicator" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs">
                <!-- JSで動的に口座現在残高を表示 -->
              </div>

              <!-- 警告バナーエリア -->
              <div id="dailyAlertsContainer" class="space-y-2"></div>

              <!-- 日別資金繰りテーブル（横スクロール対応） -->
              <div class="overflow-x-auto border border-slate-200 rounded-lg shadow-sm">
                <table id="dailyScheduleTable" class="w-full text-xs text-left border-collapse min-w-[700px]">
                  <!-- JSで動的に構築（全社合計ビュー / 口座別マトリクスビュー） -->
                </table>
              </div>

              <!-- 行クリック時の明細表示 ＆ 遅延・変更アクションエリア -->
              <div id="dailyDetailContainer" class="hidden p-3 bg-slate-50 rounded-lg border border-slate-300 text-xs space-y-2">
                <div class="flex items-center justify-between font-bold text-slate-800">
                  <span id="dailyDetailTitle">📅 当日の入出金・振替明細</span>
                  <button id="btnCloseDailyDetail" class="text-slate-400 hover:text-slate-600">閉じる ✕</button>
                </div>
                <div id="dailyDetailItemsList" class="space-y-1.5"></div>
              </div>

            </div>

            <!-- キャッシュフロー3区分（営業CF・財務CF） -->
            <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div class="flex items-center justify-between border-b pb-2">
                <h4 class="text-xs font-bold text-slate-700">💵 キャッシュフロー3区分分析（営業CF・財務CF・純増減）</h4>
                <span class="text-[10px] text-slate-400">本業の現金創出力と借入返済</span>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div class="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                  <div class="text-[11px] font-bold text-emerald-800">Ⅰ. 営業活動によるCF (本業)</div>
                  <div class="text-xl font-black text-emerald-900 mt-1" id="cfOperatingVal">¥0</div>
                  <p class="text-[10px] text-emerald-700 mt-0.5">売上入金 − (仕入・外注・給与・経費)</p>
                </div>
                <div class="p-3 bg-purple-50 rounded-xl border border-purple-200">
                  <div class="text-[11px] font-bold text-purple-800">Ⅱ. 財務活動によるCF (返済)</div>
                  <div class="text-xl font-black text-purple-900 mt-1" id="cfFinancingVal">¥0</div>
                  <p class="text-[10px] text-purple-700 mt-0.5">借入金元金の定期返済</p>
                </div>
                <div class="p-3 bg-blue-900 text-white rounded-xl shadow-sm">
                  <div class="text-[11px] font-bold text-blue-200">Ⅲ. フリーキャッシュフロー (純増減)</div>
                  <div class="text-xl font-black mt-1 text-white" id="cfNetVal">¥0</div>
                  <div class="text-[10px] text-blue-200 mt-0.5" id="cfSafetyBadge">✅ 本業CFで返済を賄えています</div>
                </div>
              </div>
            </div>

          </div>

          <!-- ======================================================== -->
          <!-- サブ画面 3: 従来の残高推移"""

html = re.sub(cashflow_old_pattern, cashflow_new_html, html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html topFundsDashboard and daily schedule table structure updated successfully.")
