import re

html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Update modalInvoicePhoto to show Google Drive auto-folder destination
old_modal_note = """        <div>
          <label class="block font-bold text-slate-700 mb-1">摘要・メモ</label>
          <input type="text" id="aiInputNote" class="w-full border border-slate-300 rounded-lg p-1.5 text-xs text-slate-700 focus:outline-none">
        </div>"""

new_modal_gdrive = """        <!-- Google ドライブ自動保存先のご案内 -->
        <div class="p-2.5 bg-blue-50/80 rounded-xl border border-blue-200 text-xs space-y-1">
          <div class="flex items-center justify-between text-blue-950 font-bold text-[11px]">
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1 text-blue-600" viewBox="0 0 24 24" fill="currentColor"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95C8.08 7.14 9.94 6 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11c1.56.1 2.78 1.41 2.78 2.96 0 1.65-1.35 3-3 3z"/></svg>
              Google ドライブへ自動仕分け保存（Macの容量を消費しません）
            </span>
          </div>
          <div class="text-[10px] text-blue-900 bg-white p-2 rounded-lg border border-blue-100 font-mono flex items-center justify-between">
            <span id="gdriveFolderPath">Google ドライブ ➔ 請求書 ➔ 2026年11月 ➔ (自動保存)</span>
            <a id="btnOpenGDriveLink" href="https://drive.google.com" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline font-sans font-bold hover:text-blue-800 ml-2 whitespace-nowrap">
              フォルダを開く ➔
            </a>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">摘要・メモ</label>
          <input type="text" id="aiInputNote" class="w-full border border-slate-300 rounded-lg p-1.5 text-xs text-slate-700 focus:outline-none">
        </div>"""

if old_modal_note in html:
    html = html.replace(old_modal_note, new_modal_gdrive)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated index.html with Google Drive auto-folder display successfully.")
else:
    print("old_modal_note not found directly.")
