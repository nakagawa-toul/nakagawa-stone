import re

html_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update modalTx to add account selector
account_select_html = """
        <div>
          <label class="block font-bold text-slate-700 mb-1">出金・入金口座 <span class="text-xs text-slate-500 font-normal">（支払口座は自動決定せず本人が指定／未定でも登録可能）</span></label>
          <select id="txInputAccount" class="w-full border border-slate-300 rounded-lg p-2.5 text-xs bg-white font-bold text-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500">
            <option value="bank-1">中京銀行（当座預金 / 主口座）</option>
            <option value="bank-2">十六銀行（普通預金）</option>
            <option value="bank-3">ゆうちょ銀行</option>
            <option value="bank-4">大垣共立銀行（普通預金）</option>
            <option value="bank-5">JAバンク（普通預金）</option>
            <option value="cash">手許現金</option>
            <option value="unassigned" class="text-rose-600 font-bold">⚠️ 支払口座：未定（未配分支払予定として警告管理）</option>
          </select>
          <p class="text-[10px] text-slate-500 mt-0.5">※口座未定のまま登録した支払いは、警告が表示され口座別予測の未配分額として管理されます。</p>
        </div>
"""

if 'id="txInputAccount"' not in html:
    html = html.replace('<div>\n          <label class="block font-bold text-slate-700 mb-1">備考・詳細</label>', account_select_html + '\n        <div>\n          <label class="block font-bold text-slate-700 mb-1">備考・詳細</label>')

# 2. Add New Modals right before <!-- Toast 通知コンテナ -->
new_modals_html = """
  <!-- ============================================================== -->
  <!-- 新設モーダル群（5銀行＋手許現金、振替、期日変更・遅延、財務三表） -->
  <!-- ============================================================== -->

  <!-- A. 6口座残高・口座名・基準日設定モーダル -->
  <div id="modalAccounts" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-lg w-full p-4 sm:p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b pb-3">
        <h3 class="text-base font-bold text-slate-800 flex items-center">
          <span class="mr-1.5">🏦</span> 5つの銀行口座＋手許現金（計6口座）の設定
        </h3>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <p class="text-xs text-slate-600">
        通帳やネットバンキングで確認した各口座の<strong>基準日時点の残高</strong>を登録します。この日以降の入出金・振替が日別資金繰り表に反映されます。
      </p>

      <form id="formAccounts" class="space-y-3 text-xs">
        <div id="accountsFormContainer" class="space-y-3">
          <!-- JSで6口座それぞれの編集欄を動的に生成 -->
        </div>

        <div class="pt-3 flex justify-end space-x-2 border-t">
          <button type="button" class="modal-close-btn px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition">キャンセル</button>
          <button type="submit" class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow transition">残高を保存</button>
        </div>
      </form>
    </div>
  </div>

  <!-- B. 口座間振替モーダル（二重計上なし） -->
  <div id="modalTransfer" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-md w-full p-4 sm:p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b pb-3">
        <h3 class="text-base font-bold text-slate-800 flex items-center">
          <span class="mr-1.5">🔄</span> 口座間振替の登録（資金移動）
        </h3>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <div class="bg-blue-50 border-l-4 border-blue-600 p-2.5 rounded-r-lg text-[11px] text-blue-900">
        💡 口座間の振替は、出金元から引かれ入金先へ加算されます。<strong>全口座合計の資金残高では相殺され、二重計上されません。</strong>
      </div>

      <form id="formTransfer" class="space-y-3 text-xs">
        <div>
          <label class="block font-bold text-slate-700 mb-1">振替日（予定日 / 実行日） <span class="text-red-500">*</span></label>
          <input type="date" id="trInputDate" required class="w-full border border-slate-300 rounded-lg p-2.5 text-xs focus:outline-none">
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block font-bold text-rose-700 mb-1">出金元 口座 <span class="text-red-500">*</span></label>
            <select id="trInputFrom" required class="w-full border border-rose-300 rounded-lg p-2 text-xs bg-rose-50/40 font-bold text-rose-900 focus:outline-none">
              <!-- JSで動的生成 -->
            </select>
          </div>
          <div>
            <label class="block font-bold text-emerald-700 mb-1">入金先 口座 <span class="text-red-500">*</span></label>
            <select id="trInputTo" required class="w-full border border-emerald-300 rounded-lg p-2 text-xs bg-emerald-50/40 font-bold text-emerald-900 focus:outline-none">
              <!-- JSで動的生成 -->
            </select>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">振替金額（円） <span class="text-red-500">*</span></label>
          <div class="relative">
            <span class="absolute left-3 top-2.5 text-slate-400 font-bold">¥</span>
            <input type="number" id="trInputAmount" required min="1" step="1" placeholder="300000" class="w-full border border-slate-300 rounded-lg pl-7 pr-3 py-2 text-sm font-bold focus:outline-none">
          </div>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block font-bold text-slate-700 mb-1">状態</label>
            <select id="trInputIsActual" class="w-full border border-slate-300 rounded-lg p-2 text-xs bg-white font-medium">
              <option value="false">振替予定（未実行）</option>
              <option value="true">振替済み（実行済実績）</option>
            </select>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">振替目的・メモ</label>
            <input type="text" id="trInputNote" placeholder="例: 給料・公庫返済の準備" class="w-full border border-slate-300 rounded-lg p-2 text-xs focus:outline-none">
          </div>
        </div>

        <div class="pt-3 flex justify-end space-x-2 border-t">
          <button type="button" class="modal-close-btn px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition">キャンセル</button>
          <button type="submit" class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow transition">振替を登録</button>
        </div>
      </form>
    </div>
  </div>

  <!-- C. 入金遅延・期日変更モーダル -->
  <div id="modalDelayTx" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-sm w-full p-4 sm:p-5 shadow-2xl space-y-3 text-xs">
      <div class="flex items-center justify-between border-b pb-2">
        <h3 class="text-sm font-bold text-slate-800 flex items-center">
          <span class="mr-1.5">⏱️</span> 入金遅延・支払予定日の変更
        </h3>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
        <div class="text-[10px] text-slate-500" id="delayModalPartner">相手先</div>
        <div class="font-bold text-slate-800 text-xs mt-0.5" id="delayModalTitle">案件名・内容</div>
        <div class="text-xs text-blue-700 font-bold mt-1" id="delayModalAmount">¥0</div>
        <div class="text-[10px] text-slate-500 mt-0.5">現在の予定日: <span id="delayModalCurrentDate" class="font-bold text-slate-700"></span></div>
      </div>

      <form id="formDelayTx" class="space-y-2.5">
        <input type="hidden" id="delayModalTxId">

        <!-- クイック延長ボタン -->
        <div>
          <label class="block font-bold text-slate-700 mb-1">クイック指定</label>
          <div class="flex items-center space-x-1.5">
            <button type="button" class="btn-quick-delay px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold" data-days="7">+7日延期</button>
            <button type="button" class="btn-quick-delay px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold" data-days="14">+14日延期</button>
            <button type="button" class="btn-quick-delay px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold" data-days="30">+1か月延期</button>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">変更後の新しい予定日 <span class="text-red-500">*</span></label>
          <input type="date" id="delayInputNewDate" required class="w-full border border-slate-300 rounded-lg p-2 text-xs focus:outline-none">
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">出金口座の設定（未定からの決定も可能）</label>
          <select id="delayInputAccount" class="w-full border border-slate-300 rounded-lg p-2 text-xs bg-white font-medium">
            <option value="bank-1">中京銀行</option>
            <option value="bank-2">十六銀行</option>
            <option value="bank-3">ゆうちょ銀行</option>
            <option value="bank-4">大垣共立銀行</option>
            <option value="bank-5">JAバンク</option>
            <option value="cash">手許現金</option>
            <option value="unassigned">⚠️ 口座未定のまま</option>
          </select>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">変更理由・メモ</label>
          <input type="text" id="delayInputReason" placeholder="例: 施主様ご都合、部材納期変更など" class="w-full border border-slate-300 rounded-lg p-2 text-xs focus:outline-none">
        </div>

        <div class="pt-2 flex justify-end space-x-2 border-t">
          <button type="button" class="modal-close-btn px-3 py-1.5 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 transition">キャンセル</button>
          <button type="submit" class="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow transition">期日を変更反映</button>
        </div>
      </form>
    </div>
  </div>

  <!-- D. 財務三表（B/S・P/L・C/F）クイック閲覧モーダル -->
  <div id="modalBSPL" class="fixed inset-0 z-50 hidden flex items-center justify-center p-3 sm:p-4 modal-backdrop">
    <div class="bg-white rounded-2xl max-w-4xl w-full p-4 sm:p-6 shadow-2xl space-y-4 max-h-[92vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b pb-3">
        <div>
          <h3 class="text-base font-bold text-slate-900 flex items-center">
            <span>📑 中川石材 財務三表（B/S・P/L・C/F）</span>
            <span class="ml-2 text-[10px] bg-sky-100 text-sky-800 px-2 py-0.5 rounded font-bold">弥生会計基準</span>
          </h3>
          <p class="text-[11px] text-slate-500 mt-0.5">利益と手元資金の違い、および営業・投資・財務の各キャッシュフローを統合可視化</p>
        </div>
        <button class="modal-close-btn text-slate-400 hover:text-slate-600 p-1">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- 三表タブ切り替え -->
      <div class="flex items-center space-x-2 border-b text-xs font-bold pb-2">
        <button id="bsplTabPL" class="px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm">1. 損益計算書 (P/L)</button>
        <button id="bsplTabBS" class="px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100">2. 貸借対照表 (B/S)</button>
        <button id="bsplTabCF" class="px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100">3. キャッシュフロー計算書 (C/F)</button>
      </div>

      <div id="bsplContentArea" class="text-xs space-y-3">
        <!-- JSでP/L, B/S, C/Fの表をレンダリング -->
      </div>

      <div class="pt-2 flex justify-end border-t">
        <button type="button" class="modal-close-btn px-4 py-1.5 bg-slate-800 text-white font-bold rounded-lg hover:bg-slate-700 transition">閉じる</button>
      </div>
    </div>
  </div>
"""

if 'id="modalAccounts"' not in html:
    html = html.replace('<!-- Toast 通知コンテナ -->', new_modals_html + '\n  <!-- Toast 通知コンテナ -->')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Added modalAccounts, modalTransfer, modalDelayTx, modalBSPL and txInputAccount successfully.")
