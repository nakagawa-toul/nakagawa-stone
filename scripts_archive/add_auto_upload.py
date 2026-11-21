# 1. Update store.js to store gdriveGasUrl
store_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js'

with open(store_path, 'r', encoding='utf-8') as f:
    store_code = f.read()

gdrive_store_code = """
  // Googleドライブ自動アップロード設定（GAS URL）
  getGDriveGasUrl() {
    return this.data.gdriveGasUrl || localStorage.getItem('nakagawa_stone_gdrive_gas_url') || '';
  }

  setGDriveGasUrl(url) {
    this.data.gdriveGasUrl = url.trim();
    localStorage.setItem('nakagawa_stone_gdrive_gas_url', url.trim());
    this.saveData();
  }
"""

if "getGDriveGasUrl()" not in store_code:
    store_code = store_code.replace("  // ユーザー・権限制御\n  getCurrentUser() {", gdrive_store_code + "\n  // ユーザー・権限制御\n  getCurrentUser() {")
    with open(store_path, 'w', encoding='utf-8') as f:
        f.write(store_code)
    print("Updated store.js with gdriveGasUrl methods.")

# 2. Update index.html to add Google Drive GAS URL setting in view-settings
html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

gdrive_setting_ui = """
        <!-- Google ドライブ自動アップロード連携設定 -->
        <div class="bg-white p-4 sm:p-6 rounded-xl border border-blue-200 shadow-sm space-y-3">
          <div class="flex items-center space-x-2 border-b border-slate-200 pb-2.5">
            <svg class="w-5 h-5 text-blue-600" viewBox="0 0 24 24" fill="currentColor"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95C8.08 7.14 9.94 6 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11c1.56.1 2.78 1.41 2.78 2.96 0 1.65-1.35 3-3 3z"/></svg>
            <h3 class="text-sm sm:text-base font-bold text-slate-900">☁️ 請求書 Google ドライブ自動アップロード連携（GAS設定）</h3>
          </div>
          <p class="text-xs text-slate-600 leading-relaxed">
            請求書の写真を登録するたびに、<strong>Google ドライブの「請求書 / YYYY年MM月」フォルダへ毎回全自動で保存</strong>します（Macの容量を消費しません）。
          </p>
          <div class="space-y-2 text-xs">
            <label class="block font-bold text-slate-700">Google Apps Script (GAS) ウェブアプリURL</label>
            <div class="flex gap-2">
              <input type="url" id="settingGDriveGasUrl" placeholder="https://script.google.com/macros/s/.../exec" class="w-full border border-slate-300 rounded-lg p-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-blue-500">
              <button type="button" id="btnSaveGDriveGasUrl" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg text-xs whitespace-nowrap shadow transition">
                URLを保存
              </button>
            </div>
            <p class="text-[10px] text-slate-500">※未入力時でも、画面上からGoogleドライブの年月フォルダをワンクリックで開く連携が可能です。</p>
          </div>
        </div>
"""

if 'id="settingGDriveGasUrl"' not in html:
    html = html.replace('<section id="view-settings" class="view-panel hidden space-y-4">', '<section id="view-settings" class="view-panel hidden space-y-4">\n' + gdrive_setting_ui)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated index.html with Google Drive GAS URL setting UI.")
