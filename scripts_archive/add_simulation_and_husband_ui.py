import re

html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add "⚡ 資金シミュレーション" button next to 3/6/12 month buttons
old_forecast_buttons = """                <button class="top-forecast-btn px-2 py-1 rounded bg-sky-700 text-white text-[10px] font-bold" data-period="3">3か月</button>
                <button class="top-forecast-btn px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-[10px] font-bold" data-period="6">6か月</button>
                <button class="top-forecast-btn px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-[10px] font-bold" data-period="12">12か月</button>"""

new_forecast_buttons = """                <button class="top-forecast-btn px-2 py-1 rounded bg-sky-700 text-white text-[10px] font-bold" data-period="3">3か月</button>
                <button class="top-forecast-btn px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-[10px] font-bold" data-period="6">6か月</button>
                <button class="top-forecast-btn px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-[10px] font-bold" data-period="12">12か月</button>
                <button id="btnOpenSimulationModal" class="px-2 py-1 rounded bg-purple-700 hover:bg-purple-600 text-white text-[10px] font-bold shadow-sm transition ml-1 flex items-center space-x-1">
                  <span>⚡ 試算</span>
                </button>"""

if old_forecast_buttons in html:
    html = html.replace(old_forecast_buttons, new_forecast_buttons)

# 2. Add Husband Dedicated Summary Card right above task list (for husband role)
husband_card_html = """
        <!-- ご主人（朋さん）専用 現場・経営サマリー（操作者が「夫」の時に強調表示） -->
        <div id="husbandQuickDashboard" class="hidden bg-gradient-to-r from-slate-900 to-indigo-950 text-white p-4 sm:p-5 rounded-2xl shadow-md space-y-3 border border-indigo-700/60">
          <div class="flex items-center justify-between border-b border-indigo-800/80 pb-2.5">
            <div class="flex items-center space-x-2">
              <span class="text-xl">👨‍💼</span>
              <div>
                <h3 class="text-sm sm:text-base font-bold text-white">朋さん専用 現場・資金サマリー</h3>
                <p class="text-[10px] text-indigo-300">細かい簿記用語なしで、今の全体資金と現場の予定がひと目でわかります</p>
              </div>
            </div>
            <span class="bg-indigo-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">現場・経営閲覧モード</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
            <div class="bg-slate-800/80 p-3 rounded-xl border border-indigo-700/50">
              <div class="text-[11px] text-slate-300">今使える全体のお金</div>
              <div class="text-xl sm:text-2xl font-black text-emerald-400 mt-0.5" id="husbandTotalCash">¥5,000,000</div>
              <div class="text-[10px] text-slate-400 mt-0.5">全5口座＋手許現金の合計</div>
            </div>
            <div class="bg-slate-800/80 p-3 rounded-xl border border-indigo-700/50">
              <div class="text-[11px] text-slate-300">今月のお金の出入り予測</div>
              <div class="text-sm font-bold text-white mt-1 flex justify-center space-x-2">
                <span class="text-emerald-400">入金: <span id="husbandMonthIn">¥2,105,000</span></span>
                <span class="text-rose-400">支払: <span id="husbandMonthOut">¥1,698,000</span></span>
              </div>
              <div class="text-[10px] text-sky-300 font-bold mt-1" id="husbandMonthStatus">✅ 今月は黒字・資金安全です</div>
            </div>
            <div class="bg-slate-800/80 p-3 rounded-xl border border-indigo-700/50">
              <div class="text-[11px] text-slate-300">資金ショート警戒予報</div>
              <div class="text-sm font-bold text-emerald-300 mt-1" id="husbandShortageBadge">✅ 今後3か月は安全圏です</div>
              <div class="text-[10px] text-slate-400 mt-0.5">残高不足の恐れがあれば赤文字で警告</div>
            </div>
          </div>
        </div>
"""

home_anchor = '<div id="taskListContainer" class="space-y-2.5">'
if 'id="husbandQuickDashboard"' not in html:
    html = html.replace(home_anchor, husband_card_html + '\n        ' + home_anchor)

# 3. Add modalStressTest before <!-- Toast 通知コンテナ -->
simulation_modal_html = """
  <!-- J. 将来資金予測 ＆ シミュレーション（ストレステスト）モーダル -->
  <div id="modalStressTest" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-lg w-full p-4 sm:p-6 shadow-2xl space-y-4 max-h-[92vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b pb-3">
        <div>
          <h3 class="text-base font-bold text-slate-900 flex items-center">
            <span class="mr-1.5">⚡</span> 将来資金シミュレーション（ストレステスト）
          </h3>
          <p class="text-[11px] text-slate-500 mt-0.5">「もし大口入金が遅れたら？」「売上が減ったら？」「突発出費があったら？」を検証</p>
        </div>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- シナリオ設定フォーム -->
      <form id="formStressTest" class="space-y-3.5 text-xs">
        
        <!-- シナリオ1: 大口入金の遅延 -->
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5">
          <label class="flex items-center space-x-2 font-bold text-slate-800 cursor-pointer">
            <input type="checkbox" id="simCheckDelay" class="w-4 h-4 text-purple-600 rounded">
            <span>① 50万円以上の大口売掛金の入金が30日遅延した場合</span>
          </label>
          <p class="text-[10px] text-slate-500 pl-6">施主様のご都合等で着工金や完工金の支払いが1か月ズレ込んだ場合の耐性をテスト</p>
        </div>

        <!-- シナリオ2: 売上減少 -->
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
          <div class="flex items-center justify-between font-bold text-slate-800">
            <span>② 今後の売上が減少した場合の耐性</span>
            <span id="simSalesRateLabel" class="text-purple-700 font-black">通常 (0%減)</span>
          </div>
          <input type="range" id="simSalesRange" min="0" max="40" step="10" value="0" class="w-full">
          <div class="flex justify-between text-[10px] text-slate-400">
            <span>通常</span>
            <span>10%減</span>
            <span>20%減</span>
            <span>30%減</span>
            <span>40%減</span>
          </div>
        </div>

        <!-- シナリオ3: 突発的な大型出費 -->
        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5">
          <label class="block font-bold text-slate-800">③ 突発的な大型修繕・設備出費（円）</label>
          <div class="relative">
            <span class="absolute left-2.5 top-1.5 text-slate-400 font-bold">¥</span>
            <input type="number" id="simInputExtraExp" value="0" min="0" step="100000" placeholder="0" class="w-full border border-slate-300 rounded-lg pl-6 pr-2.5 py-1.5 text-xs font-bold text-slate-800 focus:outline-none">
          </div>
          <p class="text-[10px] text-slate-500">例: カニクレーン故障修繕費やトラック買替（1,000,000円など）を入力</p>
        </div>

        <!-- 試算結果表示カード -->
        <div id="simResultCard" class="p-4 rounded-xl border space-y-2 bg-slate-900 text-white shadow-sm">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-300 font-bold">シミュレーション判定結果</span>
            <span id="simSafetyBadge" class="px-2 py-0.5 rounded text-[10px] font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">安全</span>
          </div>
          <div class="flex justify-between items-baseline pt-1">
            <span class="text-[11px] text-slate-400">期間中 最低手元資金:</span>
            <span id="simMinBalVal" class="text-2xl font-black text-emerald-400">¥0</span>
          </div>
          <div id="simResultDetail" class="text-[11px] text-slate-300 border-t border-slate-800 pt-2 leading-relaxed">
            <!-- JSで動的解説 -->
          </div>
        </div>

        <div class="pt-2 flex justify-end">
          <button type="button" class="modal-close-btn px-4 py-2 bg-slate-800 text-white font-bold rounded-lg text-xs hover:bg-slate-700 transition">
            閉じる
          </button>
        </div>
      </form>
    </div>
  </div>
"""

if 'id="modalStressTest"' not in html:
    html = html.replace('<!-- Toast 通知コンテナ -->', simulation_modal_html + '\n  <!-- Toast 通知コンテナ -->')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html with simulation modal and husband quick dashboard.")
