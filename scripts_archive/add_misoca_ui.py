import re

html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add "📑 Misoca連携" button next to "📥 弥生CSV取り込み"
misoca_btn = """              <button id="btnOpenMisocaModal" class="bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition flex items-center space-x-1.5 shadow-sm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                <span>📑 Misoca連携</span>
              </button>"""

if 'id="btnOpenMisocaModal"' not in html:
    html = html.replace('<button id="btnOpenAccountsModal"', misoca_btn + '\n              <button id="btnOpenAccountsModal"')

# 2. Make topUncollectedCard clickable
old_uncollected_card = """            <div class="bg-slate-800/80 p-3 rounded-xl border border-slate-700">
              <div class="text-[11px] text-amber-300 font-semibold flex items-center justify-between">
                <span>📑 未回収の請求書（売掛金）</span>
                <span id="topUncollectedCount" class="bg-amber-400/20 text-amber-300 text-[10px] px-1.5 py-0.2 rounded font-bold">0件</span>
              </div>
              <div class="text-lg font-black text-amber-200 mt-1" id="topUncollectedTotal">¥0</div>
              <div class="text-[10px] text-slate-400 mt-0.5">Misoca連携・入金予定日管理</div>
            </div>"""

new_uncollected_card = """            <div id="btnTopOpenUncollectedModal" class="bg-slate-800/90 hover:bg-slate-700/80 p-3 rounded-xl border border-slate-700 cursor-pointer transition shadow-sm group">
              <div class="text-[11px] text-amber-300 font-semibold flex items-center justify-between">
                <span class="group-hover:text-amber-200">📑 未回収の請求書（売掛金）</span>
                <span id="topUncollectedCount" class="bg-amber-400/20 text-amber-300 text-[10px] px-1.5 py-0.2 rounded font-bold">0件</span>
              </div>
              <div class="text-lg font-black text-amber-200 mt-1" id="topUncollectedTotal">¥0</div>
              <div class="text-[10px] text-sky-400 mt-0.5 flex items-center justify-between">
                <span>Misoca連携・入金予定</span>
                <span class="underline font-bold text-[10px]">一覧・入金消込 ➔</span>
              </div>
            </div>"""

html = html.replace(old_uncollected_card, new_uncollected_card)

# 3. Add Misoca Modals right before <!-- Toast 通知コンテナ -->
misoca_modals_html = """
  <!-- ============================================================== -->
  <!-- Misoca連携 ＆ 未回収金管理モーダル群 -->
  <!-- ============================================================== -->

  <!-- F. 未回収請求書（売掛金）一覧 ＆ 入金消込モーダル -->
  <div id="modalUncollectedInvoices" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-3xl w-full p-4 sm:p-6 shadow-2xl space-y-4 max-h-[92vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b pb-3">
        <div>
          <h3 class="text-base font-bold text-slate-900 flex items-center">
            <span>📑 未回収の請求書・売掛金一覧（Misoca連携）</span>
            <span class="ml-2 text-[10px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">入金消込・二重計上防止</span>
          </h3>
          <p class="text-[11px] text-slate-500 mt-0.5">請求書ごとの入金期日、一部入金対応、口座着金の実績化</p>
        </div>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- サマリーバー -->
      <div class="bg-gradient-to-r from-amber-500 to-amber-600 text-white p-3.5 rounded-xl flex items-center justify-between shadow-sm">
        <div>
          <div class="text-[11px] text-amber-100 font-bold">現在の未回収売掛金 総額</div>
          <div id="uncollectedModalTotalSum" class="text-2xl font-black mt-0.5">¥0</div>
        </div>
        <div class="text-right text-[11px] text-amber-100">
          <div>未回収件数: <strong id="uncollectedModalCount" class="text-white text-sm">0</strong> 件</div>
          <div class="text-[10px] text-amber-200 mt-0.5">※全額入金で自動的に予定から実績へ振替</div>
        </div>
      </div>

      <!-- 請求書一覧テーブル -->
      <div class="overflow-x-auto border border-slate-200 rounded-xl shadow-sm">
        <table class="w-full text-xs text-left border-collapse min-w-[620px]">
          <thead class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px] border-b">
            <tr>
              <th class="py-2.5 px-3">請求書番号 / 施主名</th>
              <th class="py-2.5 px-3">件名・内容</th>
              <th class="py-2.5 px-2">入金期日</th>
              <th class="py-2.5 px-3 text-right">請求金額</th>
              <th class="py-2.5 px-3 text-right">入金済額</th>
              <th class="py-2.5 px-3 text-right text-amber-700">未回収残高</th>
              <th class="py-2.5 px-2 text-center">入金消込 / 期日</th>
            </tr>
          </thead>
          <tbody id="uncollectedTableBody" class="divide-y divide-slate-100">
            <!-- JSで動的レンダリング -->
          </tbody>
        </table>
      </div>

      <div class="pt-2 flex justify-between items-center border-t text-xs">
        <button type="button" onclick="app.openMisocaImportModal()" class="text-blue-600 hover:underline font-bold text-xs flex items-center space-x-1">
          <span>📥 MisocaのCSVを取り込む</span>
        </button>
        <button type="button" class="modal-close-btn px-4 py-2 bg-slate-800 text-white font-bold rounded-lg hover:bg-slate-700 transition">
          閉じる
        </button>
      </div>
    </div>
  </div>

  <!-- G. 一部入金・入金記録モーダル -->
  <div id="modalRecordPayment" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-md w-full p-4 sm:p-5 shadow-2xl space-y-3 text-xs">
      <div class="flex items-center justify-between border-b pb-2">
        <h3 class="text-sm font-bold text-slate-900 flex items-center">
          <span class="mr-1.5">💰</span> 請求書の入金消込・実績登録
        </h3>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
        <div class="flex justify-between items-center text-[11px]">
          <span class="text-slate-500" id="payModalInvNo">INV-2026-000</span>
          <span class="font-bold text-blue-700" id="payModalPartner">施主名</span>
        </div>
        <div class="font-bold text-slate-800 text-xs" id="payModalSubject">件名</div>
        <div class="flex justify-between items-center text-xs pt-1 border-t">
          <span>請求金額: <strong id="payModalTotalAmt">¥0</strong></span>
          <span class="text-amber-700 font-bold">未回収残高: <strong id="payModalRemainingAmt" class="text-sm">¥0</strong></span>
        </div>
      </div>

      <form id="formRecordPayment" class="space-y-3">
        <input type="hidden" id="payModalInvoiceId">

        <div>
          <label class="block font-bold text-slate-700 mb-1">入金日（通帳に着金した日） <span class="text-red-500">*</span></label>
          <input type="date" id="payInputDate" required class="w-full border border-slate-300 rounded-lg p-2 text-xs focus:outline-none">
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">入金額（一部入金も可能） <span class="text-red-500">*</span></label>
          <div class="relative">
            <span class="absolute left-3 top-2 text-slate-400 font-bold">¥</span>
            <input type="number" id="payInputAmount" required min="1" step="1" class="w-full border border-slate-300 rounded-lg pl-7 pr-3 py-1.5 text-sm font-black text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500">
          </div>
          <p class="text-[10px] text-slate-500 mt-1">※全額ではなく内金や中間金などの一部入金にも対応しています。</p>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">着金口座（入金された銀行口座） <span class="text-red-500">*</span></label>
          <select id="payInputAccount" required class="w-full border border-slate-300 rounded-lg p-2 text-xs bg-white font-bold text-slate-800 focus:outline-none">
            <option value="bank-1">中京銀行（当座預金 / 主口座）</option>
            <option value="bank-2">十六銀行（普通預金）</option>
            <option value="bank-3">ゆうちょ銀行</option>
            <option value="bank-4">大垣共立銀行（普通預金）</option>
            <option value="bank-5">JAバンク（普通預金）</option>
            <option value="cash">手許現金</option>
          </select>
        </div>

        <div class="pt-2 flex justify-end space-x-2 border-t">
          <button type="button" class="modal-close-btn px-3 py-1.5 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition">キャンセル</button>
          <button type="submit" class="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg shadow transition">入金を確定（実績化）</button>
        </div>
      </form>
    </div>
  </div>

  <!-- H. Misoca CSV取り込みモーダル -->
  <div id="modalMisocaImport" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-lg w-full p-4 sm:p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b pb-3">
        <h3 class="text-base font-bold text-slate-900 flex items-center">
          <span class="mr-1.5">📑</span> Misoca（請求書・見積書）CSV取り込み
        </h3>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <div class="text-xs text-slate-600 space-y-1">
        <p>クラウド請求書サービス「Misoca」からダウンロードした<strong>請求書一覧CSV</strong>を取り込みます。</p>
        <p class="text-[11px] text-slate-500">・施主名、請求金額、入金期日を日別資金繰り表に自動反映<br>・<strong>弥生オンラインの売掛仕訳と重複しない安全設計</strong></p>
      </div>

      <!-- ドラッグ＆ドロップエリア -->
      <div id="misocaDropZone" class="border-2 border-dashed border-amber-300 hover:border-amber-500 rounded-xl p-6 text-center bg-amber-50/40 hover:bg-amber-50 transition cursor-pointer space-y-2">
        <svg class="w-10 h-10 text-amber-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
        <div class="font-bold text-slate-800 text-xs">Misocaの請求書CSVをここにドラッグ＆ドロップ</div>
        <p class="text-[10px] text-slate-500">または下のボタンからファイルを選択</p>
        <input type="file" id="misocaFileInput" accept=".csv,text/csv" class="hidden">
        <button type="button" onclick="document.getElementById('misocaFileInput').click()" class="bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-sm transition inline-block">
          CSVファイルを選択
        </button>
      </div>

      <!-- デモ用サンプル読込ボタン -->
      <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
        <div>
          <div class="font-bold text-slate-800 text-xs">🧪 サンプルデータで試す</div>
          <div class="text-[10px] text-slate-500">Misocaの請求書データを一発読み込み</div>
        </div>
        <button type="button" id="btnLoadSampleMisoca" class="bg-slate-800 hover:bg-slate-700 text-amber-300 text-xs font-bold px-3 py-1.5 rounded-lg transition border border-slate-700 shadow-sm">
          サンプル読込
        </button>
      </div>

      <!-- 結果表示 -->
      <div id="misocaImportResultArea" class="hidden p-3.5 rounded-xl border text-xs space-y-1"></div>

      <div class="pt-2 flex justify-end border-t">
        <button type="button" class="modal-close-btn px-4 py-2 bg-slate-800 text-white font-bold rounded-lg text-xs hover:bg-slate-700 transition">
          閉じる
        </button>
      </div>
    </div>
  </div>
"""

if 'id="modalUncollectedInvoices"' not in html:
    html = html.replace('<!-- Toast 通知コンテナ -->', misoca_modals_html + '\n  <!-- Toast 通知コンテナ -->')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html with Misoca modals and interactive uncollected card.")
