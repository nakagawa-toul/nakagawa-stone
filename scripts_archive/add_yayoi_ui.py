import re

html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add "📥 弥生CSV取り込み" button to top dashboard
yayoi_btn_html = """              <button id="btnOpenYayoiModal" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 shadow-sm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                <span>📥 弥生CSV取り込み</span>
              </button>"""

if 'id="btnOpenYayoiModal"' not in html:
    html = html.replace('<button id="btnOpenAccountsModal"', yayoi_btn_html + '\n              <button id="btnOpenAccountsModal"')

# Add last import status badge to top bar
status_badge_html = """              <div class="flex items-center space-x-2 mt-1">
                <div class="text-xs text-slate-400 font-medium">全口座合計 手元資金:</div>
                <div id="topTotalCash" class="text-2xl sm:text-4xl font-black text-white tracking-tight">¥0</div>
                <span id="yayoiLastImportBadge" class="hidden sm:inline text-[10px] bg-indigo-950/80 text-indigo-300 border border-indigo-500/40 px-2 py-0.5 rounded ml-2">弥生連携: 未取り込み</span>
              </div>"""

html = re.sub(r'<div class="flex items-baseline space-x-2 mt-1">\s*<div class="text-xs text-slate-400 font-medium">全口座合計 手元資金:</div>\s*<div id="topTotalCash" class="text-2xl sm:text-4xl font-black text-white tracking-tight">¥0</div>\s*</div>', status_badge_html, html)

# 2. Add modalYayoiImport
yayoi_modal_html = """
  <!-- E. 弥生会計 CSV取り込みモーダル -->
  <div id="modalYayoiImport" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-lg w-full p-4 sm:p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b pb-3">
        <h3 class="text-base font-bold text-slate-900 flex items-center">
          <span class="mr-1.5">📥</span> やよいの青色申告オンライン CSV取り込み
        </h3>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <div class="text-xs text-slate-600 space-y-1">
        <p>「やよいの青色申告オンライン」からエクスポートした<strong>仕訳日記帳CSV</strong>を取り込みます。</p>
        <p class="text-[11px] text-slate-500">・5銀行口座＋手許現金の残高と仕訳を自動更新<br>・仕訳番号や日付・金額による<strong>二重取り込み防止</strong><br>・財務三表（B/S・P/L・C/F）を即座に再計算</p>
      </div>

      <!-- ドラッグ＆ドロップエリア -->
      <div id="yayoiDropZone" class="border-2 border-dashed border-indigo-300 hover:border-indigo-500 rounded-xl p-6 text-center bg-indigo-50/40 hover:bg-indigo-50 transition cursor-pointer space-y-2">
        <svg class="w-10 h-10 text-indigo-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
        <div class="font-bold text-slate-800 text-xs">弥生CSVファイルをここにドラッグ＆ドロップ</div>
        <p class="text-[10px] text-slate-500">または下のボタンからファイルを選択</p>
        <input type="file" id="yayoiFileInput" accept=".csv,text/csv" class="hidden">
        <button type="button" onclick="document.getElementById('yayoiFileInput').click()" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-sm transition inline-block">
          CSVファイルを選択
        </button>
      </div>

      <!-- デモ用サンプル取り込みボタン -->
      <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
        <div>
          <div class="font-bold text-slate-800 text-xs">🧪 サンプルデータで試す</div>
          <div class="text-[10px] text-slate-500">手元に弥生のCSVがない場合、石材店サンプル仕訳を一発読み込み</div>
        </div>
        <button type="button" id="btnLoadSampleYayoi" class="bg-slate-800 hover:bg-slate-700 text-sky-300 text-xs font-bold px-3 py-1.5 rounded-lg transition border border-slate-700 shadow-sm">
          サンプル読込
        </button>
      </div>

      <!-- 取り込み結果ステータスエリア -->
      <div id="yayoiImportResultArea" class="hidden p-3.5 rounded-xl border text-xs space-y-1.5">
        <!-- JSで動的に表示 -->
      </div>

      <div class="pt-2 flex justify-end border-t">
        <button type="button" class="modal-close-btn px-4 py-2 bg-slate-800 text-white font-bold rounded-lg text-xs hover:bg-slate-700 transition">
          閉じる
        </button>
      </div>
    </div>
  </div>
"""

if 'id="modalYayoiImport"' not in html:
    html = html.replace('<!-- Toast 通知コンテナ -->', yayoi_modal_html + '\n  <!-- Toast 通知コンテナ -->')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html with Yayoi import button and modal.")
