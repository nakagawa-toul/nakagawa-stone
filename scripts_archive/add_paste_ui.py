import re

html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Update modalYayoiImport with tabs for File Upload and Direct Text Paste
old_yayoi_modal = """      <!-- ドラッグ＆ドロップエリア -->
      <div id="yayoiDropZone" class="border-2 border-dashed border-indigo-300 hover:border-indigo-500 rounded-xl p-6 text-center bg-indigo-50/40 hover:bg-indigo-50 transition cursor-pointer space-y-2">
        <svg class="w-10 h-10 text-indigo-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
        <div class="font-bold text-slate-800 text-xs">弥生CSVファイルをここにドラッグ＆ドロップ</div>
        <p class="text-[10px] text-slate-500">または下のボタンからファイルを選択</p>
        <input type="file" id="yayoiFileInput" accept=".csv,text/csv" class="hidden">
        <button type="button" onclick="document.getElementById('yayoiFileInput').click()" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-sm transition inline-block">
          CSVファイルを選択
        </button>
      </div>"""

new_yayoi_modal = """      <!-- 取り込み方法の切り替えタブ -->
      <div class="flex items-center space-x-2 border-b text-xs font-bold pb-2">
        <button type="button" id="yayoiTabFile" class="px-3 py-1.5 rounded-lg bg-indigo-600 text-white shadow-sm font-bold">
          📁 ファイルをドロップ / 選択
        </button>
        <button type="button" id="yayoiTabPaste" class="px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100 font-medium">
          📋 テキストを直接貼り付け（コピペ）
        </button>
      </div>

      <!-- 方法1: ドラッグ＆ドロップエリア -->
      <div id="yayoiAreaFile" class="space-y-2">
        <div id="yayoiDropZone" class="border-2 border-dashed border-indigo-300 hover:border-indigo-500 rounded-xl p-6 text-center bg-indigo-50/40 hover:bg-indigo-50 transition cursor-pointer space-y-2">
          <svg class="w-10 h-10 text-indigo-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
          <div class="font-bold text-slate-800 text-xs">弥生からダウンロードしたCSVファイルをここにドラッグ＆ドロップ</div>
          <p class="text-[10px] text-slate-500">または下のボタンからファイルを選択</p>
          <input type="file" id="yayoiFileInput" accept=".csv,text/csv" class="hidden">
          <button type="button" onclick="document.getElementById('yayoiFileInput').click()" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-sm transition inline-block">
            CSVファイルを選択
          </button>
        </div>
      </div>

      <!-- 方法2: テキスト直接貼り付け（コピペ）エリア -->
      <div id="yayoiAreaPaste" class="hidden space-y-2">
        <p class="text-[11px] text-slate-500">
          弥生のCSVをExcelやメモ帳で開き、文字をコピーして下の枠にそのまま貼り付けてください。
        </p>
        <textarea id="yayoiPasteText" rows="6" placeholder="ここに弥生CSVの文字を貼り付け（Cmd+V / Ctrl+V）してください&#10;例:&#10;取引日,借方勘定科目,借方金額,貸方勘定科目,貸方金額,摘要..." class="w-full border border-slate-300 rounded-xl p-3 text-xs font-mono bg-slate-50 focus:bg-white focus:outline-none focus:ring-1 focus:ring-indigo-500"></textarea>
        <button type="button" id="btnProcessYayoiPaste" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold py-2 rounded-lg shadow transition">
          貼り付けたデータを取り込む
        </button>
      </div>"""

if old_yayoi_modal in html:
    html = html.replace(old_yayoi_modal, new_yayoi_modal)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated index.html with paste support.")
else:
    print("old_yayoi_modal not matched directly.")
