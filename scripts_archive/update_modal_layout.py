app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace openAccountsModal and handleSaveAccounts
old_modal_methods = """  openAccountsModal() {
    const modal = document.getElementById('modalAccounts');
    const container = document.getElementById('accountsFormContainer');
    if (!modal || !container) return;

    const accounts = window.stoneStore.getAccounts();
    container.innerHTML = accounts.map((acc, idx) => `
      <div class="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-1.5 font-bold text-slate-800 text-xs">
            <span class="w-3 h-3 rounded-full flex-shrink-0" style="background-color: ${acc.color}"></span>
            <input type="text" name="accName_${acc.id}" value="${acc.name}" required class="border border-slate-300 rounded px-2 py-1 text-xs font-bold w-48 sm:w-64 bg-white">
          </div>
          <span class="text-[10px] text-slate-400 font-mono">${acc.id}</span>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-[10px] text-slate-500 font-semibold mb-0.5">基準日（確認日）</label>
            <input type="date" name="accDate_${acc.id}" value="${acc.baseDate || '2026-10-31'}" required class="w-full border border-slate-300 rounded p-1.5 text-xs bg-white">
          </div>
          <div>
            <label class="block text-[10px] text-slate-500 font-semibold mb-0.5">基準残高（円）</label>
            <div class="relative">
              <span class="absolute left-2 top-1.5 text-slate-400 font-bold">¥</span>
              <input type="number" name="accBal_${acc.id}" value="${acc.baseBalance}" required min="0" step="1" class="w-full border border-slate-300 rounded pl-5 pr-2 py-1.5 text-xs font-bold bg-white">
            </div>
          </div>
        </div>
      </div>
    `).join('');

    modal.classList.remove('hidden');
  }

  handleSaveAccounts(e) {
    e.preventDefault();
    const accounts = window.stoneStore.getAccounts();
    const form = e.target;

    accounts.forEach(acc => {
      const nameInput = form.querySelector(`input[name="accName_${acc.id}"]`);
      const dateInput = form.querySelector(`input[name="accDate_${acc.id}"]`);
      const balInput = form.querySelector(`input[name="accBal_${acc.id}"]`);

      if (nameInput && dateInput && balInput) {
        window.stoneStore.updateAccount(acc.id, {
          name: nameInput.value.trim(),
          baseDate: dateInput.value,
          baseBalance: parseInt(balInput.value, 10) || 0
        });
      }
    });

    document.getElementById('modalAccounts').classList.add('hidden');
    this.showToast('5口座＋手許現金の残高設定を更新しました');
    this.render();
  }"""

new_modal_methods = """  openAccountsModal() {
    const modal = document.getElementById('modalAccounts');
    const container = document.getElementById('accountsFormContainer');
    if (!modal || !container) return;

    const accounts = window.stoneStore.getAccounts();
    const commonDate = accounts[0]?.baseDate || '2026-10-31';

    let html = `
      <!-- 共通基準日（確認日）入力ヘッダー -->
      <div class="bg-blue-50/70 p-3 rounded-xl border border-blue-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <label class="block text-xs font-bold text-blue-950">📅 通帳・残高を確認した日（基準日）</label>
          <p class="text-[10px] text-blue-800">この日時点の残高を各口座に入力してください（以降の入出金を自動加減算）</p>
        </div>
        <div>
          <input type="date" id="accountsCommonDate" value="${commonDate}" required class="border border-blue-300 rounded-lg px-2.5 py-1.5 text-xs font-bold bg-white text-slate-800 focus:outline-none">
        </div>
      </div>

      <!-- 口座名 ＆ 金額 横並び一覧テーブル -->
      <div class="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <div class="bg-slate-100 px-3 py-2 border-b flex items-center justify-between text-[11px] font-bold text-slate-700">
          <span class="w-1/2 sm:w-3/5">銀行・口座名</span>
          <span class="w-1/2 sm:w-2/5 text-right pr-2">その日の残高（円）</span>
        </div>
        <div class="divide-y divide-slate-100">
    `;

    accounts.forEach(acc => {
      html += `
        <div class="p-2.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-slate-50 transition">
          <!-- 口座名（左側） -->
          <div class="flex items-center space-x-2 sm:w-3/5">
            <span class="w-3 h-3 rounded-full flex-shrink-0" style="background-color: ${acc.color};"></span>
            <input type="text" name="accName_${acc.id}" value="${acc.name}" required class="border border-slate-300 focus:border-blue-500 rounded-lg px-2.5 py-1.5 text-xs font-bold text-slate-800 w-full bg-white">
          </div>

          <!-- 金額入力欄（右横並び） -->
          <div class="relative sm:w-2/5 flex items-center">
            <span class="absolute left-2.5 text-slate-400 font-bold text-xs pointer-events-none">¥</span>
            <input type="number" name="accBal_${acc.id}" value="${acc.baseBalance}" required min="0" step="1" class="acc-bal-input w-full border border-slate-300 focus:border-blue-500 rounded-lg pl-6 pr-3 py-1.5 text-sm font-extrabold text-right text-slate-900 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="0">
          </div>
        </div>
      `;
    });

    html += `
        </div>
        <!-- 合計バー -->
        <div class="bg-slate-900 text-white px-3 py-2.5 flex items-center justify-between text-xs border-t border-slate-800">
          <span class="font-bold text-slate-300">全口座合計 手元資金:</span>
          <span id="accountsModalTotal" class="text-base sm:text-lg font-black text-sky-300">¥0</span>
        </div>
      </div>
    `;

    container.innerHTML = html;

    // リアルタイム合計計算
    const updateTotal = () => {
      let sum = 0;
      container.querySelectorAll('.acc-bal-input').forEach(inp => {
        sum += parseInt(inp.value, 10) || 0;
      });
      const totalSpan = document.getElementById('accountsModalTotal');
      if (totalSpan) totalSpan.textContent = `¥${sum.toLocaleString()}`;
    };

    container.querySelectorAll('.acc-bal-input').forEach(inp => {
      inp.addEventListener('input', updateTotal);
    });
    updateTotal();

    modal.classList.remove('hidden');
  }

  handleSaveAccounts(e) {
    e.preventDefault();
    const accounts = window.stoneStore.getAccounts();
    const form = e.target;
    const commonDateInput = document.getElementById('accountsCommonDate');
    const commonDate = commonDateInput ? commonDateInput.value : '2026-10-31';

    accounts.forEach(acc => {
      const nameInput = form.querySelector(`input[name="accName_${acc.id}"]`);
      const balInput = form.querySelector(`input[name="accBal_${acc.id}"]`);

      if (nameInput && balInput) {
        window.stoneStore.updateAccount(acc.id, {
          name: nameInput.value.trim(),
          baseDate: commonDate,
          baseBalance: parseInt(balInput.value, 10) || 0
        });
      }
    });

    document.getElementById('modalAccounts').classList.add('hidden');
    this.showToast('5口座＋手許現金の残高設定を更新しました');
    this.render();
  }"""

code = code.replace(old_modal_methods, new_modal_methods)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated openAccountsModal layout to inline horizontal bank and amount.")
