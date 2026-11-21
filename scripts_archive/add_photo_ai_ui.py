import re

html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add "📷 請求書撮影・AI読取" button
photo_btn_html = """              <button id="btnOpenPhotoScanModal" class="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 shadow-sm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                <span>📷 請求書撮影・AI読取</span>
              </button>"""

if 'id="btnOpenPhotoScanModal"' not in html:
    html = html.replace('<button id="btnOpenAccountsModal"', photo_btn_html + '\n              <button id="btnOpenAccountsModal"')

# 2. Add modalInvoicePhoto before <!-- Toast 通知コンテナ -->
photo_modal_html = """
  <!-- I. 請求書の写真登録 ＆ AI自動読み取りモーダル -->
  <div id="modalInvoicePhoto" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-lg w-full p-4 sm:p-6 shadow-2xl space-y-4 max-h-[92vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b pb-3">
        <div>
          <h3 class="text-base font-bold text-slate-900 flex items-center">
            <span class="mr-1.5">📷</span> 請求書写真登録 ＆ AI自動読み取り
          </h3>
          <p class="text-[11px] text-slate-500 mt-0.5">スマホで紙の請求書を撮影し、AIで支払先・金額・期日を読み取ります</p>
        </div>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- 写真アップロード / カメラ撮影エリア -->
      <div id="photoUploadSection" class="space-y-3">
        <input type="file" id="invoiceCameraInput" accept="image/*" capture="environment" class="hidden">
        <input type="file" id="invoiceFileInput" accept="image/*" class="hidden">

        <div class="grid grid-cols-2 gap-2.5">
          <button type="button" id="btnTriggerCamera" class="p-4 bg-purple-50 hover:bg-purple-100 border-2 border-dashed border-purple-300 rounded-xl text-center space-y-1.5 transition">
            <div class="w-10 h-10 bg-purple-600 text-white rounded-full flex items-center justify-center mx-auto shadow-sm">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            </div>
            <div class="font-bold text-xs text-purple-900">📸 カメラで撮影する</div>
            <p class="text-[10px] text-purple-700">スマホで紙の請求書をパシャリ</p>
          </button>

          <button type="button" id="btnTriggerFile" class="p-4 bg-slate-50 hover:bg-slate-100 border-2 border-dashed border-slate-300 rounded-xl text-center space-y-1.5 transition">
            <div class="w-10 h-10 bg-slate-700 text-white rounded-full flex items-center justify-center mx-auto shadow-sm">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            </div>
            <div class="font-bold text-xs text-slate-800">🖼️ 写真を選ぶ</div>
            <p class="text-[10px] text-slate-500">保存済みの請求書画像を選択</p>
          </button>
        </div>

        <!-- デモ用サンプル請求書ボタン -->
        <div class="p-2.5 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between text-xs">
          <span class="text-slate-600 font-medium">手元に紙の請求書がない場合:</span>
          <button type="button" id="btnLoadSampleInvoicePhoto" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-sky-300 rounded-lg font-bold text-[11px] transition shadow-sm">
            🧪 サンプル請求書で試す
          </button>
        </div>
      </div>

      <!-- 画像プレビュー ＆ AI解析ローディング -->
      <div id="photoPreviewSection" class="hidden space-y-2">
        <div class="relative bg-slate-900 rounded-xl overflow-hidden max-h-48 flex items-center justify-center">
          <img id="invoicePreviewImg" src="" alt="請求書プレビュー" class="max-h-48 object-contain">
          <div id="aiScanningOverlay" class="absolute inset-0 bg-slate-900/60 flex flex-col items-center justify-center text-white space-y-2">
            <div class="w-8 h-8 border-4 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
            <span class="text-xs font-bold animate-pulse text-purple-200">🤖 AIが請求書を読み取り中...</span>
          </div>
        </div>
      </div>

      <!-- 本人確認・修正フォーム（AI読み取り結果） -->
      <form id="formConfirmInvoiceAI" class="hidden space-y-3 text-xs border-t pt-3">
        <div class="bg-purple-50 p-2.5 rounded-xl border border-purple-200 text-purple-900 text-[11px] flex items-center space-x-1.5 font-bold">
          <span>✅ AIが自動読み取りしました。内容を確認・修正して登録してください。</span>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">支払先（取引先・業者名） <span class="text-red-500">*</span></label>
          <input type="text" id="aiInputPartner" required class="w-full border border-slate-300 rounded-lg p-2 text-xs font-bold text-slate-800 focus:outline-none focus:ring-1 focus:ring-purple-500">
        </div>

        <div class="grid grid-cols-2 gap-2.5">
          <div>
            <label class="block font-bold text-slate-700 mb-1">請求金額（円） <span class="text-red-500">*</span></label>
            <div class="relative">
              <span class="absolute left-2.5 top-1.5 text-slate-400 font-bold">¥</span>
              <input type="number" id="aiInputAmount" required min="1" step="1" class="w-full border border-slate-300 rounded-lg pl-6 pr-2.5 py-1.5 text-sm font-black text-rose-700 focus:outline-none focus:ring-1 focus:ring-purple-500">
            </div>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">支払期限（予定日） <span class="text-red-500">*</span></label>
            <input type="date" id="aiInputDueDate" required class="w-full border border-slate-300 rounded-lg p-1.5 text-xs font-bold bg-white text-slate-800 focus:outline-none">
          </div>
        </div>

        <div class="grid grid-cols-2 gap-2.5">
          <div>
            <label class="block font-bold text-slate-700 mb-1">請求日</label>
            <input type="date" id="aiInputIssueDate" class="w-full border border-slate-300 rounded-lg p-1.5 text-xs bg-white text-slate-700 focus:outline-none">
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">勘定科目・費目</label>
            <select id="aiInputCategory" class="w-full border border-slate-300 rounded-lg p-1.5 text-xs bg-white font-medium">
              <option value="石材仕入">石材仕入代（墓石・外柵）</option>
              <option value="建材仕入">基礎建材費（生コン・セメント）</option>
              <option value="重機リース">重機・クレーン運搬費</option>
              <option value="外注加工">字彫り・加工外注費</option>
              <option value="消耗品・工具">消耗品・工具（砥石等）</option>
              <option value="車両・燃料">車両費・ガソリン代</option>
              <option value="その他経費">その他経費</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">出金口座の指定 <span class="text-xs text-slate-500 font-normal">（本人が選択、未定も可）</span></label>
          <select id="aiInputAccount" class="w-full border border-slate-300 rounded-lg p-2 text-xs bg-white font-bold text-slate-800 focus:outline-none focus:ring-1 focus:ring-purple-500">
            <option value="unassigned">⚠️ 支払口座：未定（未配分額として警告管理）</option>
            <option value="bank-1">中京銀行（当座預金 / 主口座）</option>
            <option value="bank-2">十六銀行（普通預金）</option>
            <option value="bank-3">ゆうちょ銀行</option>
            <option value="bank-4">大垣共立銀行（普通預金）</option>
            <option value="bank-5">JAバンク（普通預金）</option>
            <option value="cash">手許現金</option>
          </select>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">摘要・メモ</label>
          <input type="text" id="aiInputNote" class="w-full border border-slate-300 rounded-lg p-1.5 text-xs text-slate-700 focus:outline-none">
        </div>

        <div class="pt-2 flex justify-end space-x-2 border-t">
          <button type="button" class="modal-close-btn px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition">キャンセル</button>
          <button type="submit" class="px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg shadow transition">
            この内容で支払予定に登録
          </button>
        </div>
      </form>
    </div>
  </div>
"""

if 'id="modalInvoicePhoto"' not in html:
    html = html.replace('<!-- Toast 通知コンテナ -->', photo_modal_html + '\n  <!-- Toast 通知コンテナ -->')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html with photo AI scan button and modal.")
