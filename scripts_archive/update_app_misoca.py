import re

app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add Misoca event listeners in initEventListeners()
misoca_listeners = """
    // Misoca連携 ＆ 未回収金モーダル リスナー
    const btnTopUncollected = document.getElementById('btnTopOpenUncollectedModal');
    if (btnTopUncollected) {
      btnTopUncollected.addEventListener('click', () => this.openUncollectedModal());
    }

    const btnOpenMisoca = document.getElementById('btnOpenMisocaModal');
    if (btnOpenMisoca) {
      btnOpenMisoca.addEventListener('click', () => this.openMisocaImportModal());
    }

    const formRecordPayment = document.getElementById('formRecordPayment');
    if (formRecordPayment) {
      formRecordPayment.addEventListener('submit', (e) => this.handleSaveRecordPayment(e));
    }

    const misocaFileInput = document.getElementById('misocaFileInput');
    if (misocaFileInput) {
      misocaFileInput.addEventListener('change', (e) => this.handleMisocaFileSelect(e));
    }

    const btnLoadSampleMisoca = document.getElementById('btnLoadSampleMisoca');
    if (btnLoadSampleMisoca) {
      btnLoadSampleMisoca.addEventListener('click', () => this.handleLoadSampleMisoca());
    }
"""

anchor_init = "    // 弥生CSV取り込みリスナー"
code = code.replace(anchor_init, misoca_listeners + "\n" + anchor_init)

# 2. Add Misoca handlers to StoneApp class
misoca_methods = """
  // ==============================================================
  // Misoca連携 ＆ 未回収売掛金・入金消込ハンドラー
  // ==============================================================
  openUncollectedModal() {
    const modal = document.getElementById('modalUncollectedInvoices');
    const tbody = document.getElementById('uncollectedTableBody');
    const totalSpan = document.getElementById('uncollectedModalTotalSum');
    const countSpan = document.getElementById('uncollectedModalCount');
    if (!modal || !tbody) return;

    const invoices = window.stoneStore.getUncollectedInvoices();
    const totalSum = invoices.reduce((sum, inv) => sum + inv.remainingAmount, 0);

    if (totalSpan) totalSpan.textContent = `¥${totalSum.toLocaleString()}`;
    if (countSpan) countSpan.textContent = invoices.length;

    if (invoices.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="p-6 text-center text-slate-400 text-xs">現在、未回収の請求書はありません（すべて回収済みです）</td></tr>';
    } else {
      tbody.innerHTML = invoices.map(inv => {
        const isPartial = inv.status === 'partial' || inv.receivedAmount > 0;
        const statusBadge = isPartial
          ? '<span class="bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-amber-300">一部入金済</span>'
          : '<span class="bg-rose-100 text-rose-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-rose-300">未入金</span>';

        const overdueClass = inv.isOverdue ? 'text-rose-600 font-black' : 'text-slate-700 font-bold';

        return `
          <tr class="hover:bg-slate-50 transition">
            <td class="py-2.5 px-3 whitespace-nowrap">
              <div class="font-bold text-slate-900">${inv.partner}</div>
              <div class="text-[10px] text-slate-400 font-mono">${inv.invoiceNumber}</div>
            </td>
            <td class="py-2.5 px-3">
              <div class="text-xs font-semibold text-slate-800 line-clamp-1">${inv.subject}</div>
              <div class="text-[10px] text-slate-400 mt-0.5">${statusBadge}</div>
            </td>
            <td class="py-2.5 px-2 whitespace-nowrap ${overdueClass}">
              ${inv.dueDate}
              ${inv.isOverdue ? '<span class="block text-[9px] text-rose-500">期日経過</span>' : ''}
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-slate-700 whitespace-nowrap">
              ¥${inv.totalAmount.toLocaleString()}
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-emerald-700 whitespace-nowrap">
              ${inv.receivedAmount > 0 ? `¥${inv.receivedAmount.toLocaleString()}` : '-'}
            </td>
            <td class="py-2.5 px-3 text-right font-black text-amber-700 whitespace-nowrap text-sm">
              ¥${inv.remainingAmount.toLocaleString()}
            </td>
            <td class="py-2.5 px-2 text-center whitespace-nowrap space-x-1">
              <button onclick="app.openRecordPaymentModal('${inv.id}')" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded font-bold text-[10px] shadow-sm transition">
                💰 入金消込
              </button>
              <button onclick="app.openDelayMisocaModal('${inv.id}')" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded font-medium text-[10px] border transition">
                期日変更
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    modal.classList.remove('hidden');
  }

  // 入金記録（消込）モーダル
  openRecordPaymentModal(invoiceId) {
    const modal = document.getElementById('modalRecordPayment');
    const inv = window.stoneStore.getMisocaData().invoices.find(i => i.id === invoiceId);
    if (!modal || !inv) return;

    const remaining = inv.totalAmount - (inv.receivedAmount || 0);

    document.getElementById('payModalInvoiceId').value = inv.id;
    document.getElementById('payModalInvNo').textContent = inv.invoiceNumber;
    document.getElementById('payModalPartner').textContent = inv.partner;
    document.getElementById('payModalSubject').textContent = inv.subject;
    document.getElementById('payModalTotalAmt').textContent = `¥${inv.totalAmount.toLocaleString()}`;
    document.getElementById('payModalRemainingAmt').textContent = `¥${remaining.toLocaleString()}`;

    document.getElementById('payInputDate').value = this.todayStr;
    document.getElementById('payInputAmount').value = remaining; // デフォルトで残額全額
    document.getElementById('payInputAccount').value = inv.accountId || 'bank-1';

    modal.classList.remove('hidden');
  }

  handleSaveRecordPayment(e) {
    e.preventDefault();
    const invoiceId = document.getElementById('payModalInvoiceId').value;
    const date = document.getElementById('payInputDate').value;
    const amount = parseInt(document.getElementById('payInputAmount').value, 10);
    const accountId = document.getElementById('payInputAccount').value;

    try {
      const updatedInv = window.stoneStore.recordInvoicePayment(invoiceId, amount, accountId, date);
      document.getElementById('modalRecordPayment').classList.add('hidden');
      this.showToast(`「${updatedInv.partner}」の入金（¥${amount.toLocaleString()}）を口座に確定反映しました！`);
      this.render();
      // 未回収一覧が開かれていれば再描画
      this.openUncollectedModal();
    } catch (err) {
      alert('入金記録エラー: ' + err.message);
    }
  }

  // Misoca期日変更モーダル連携
  openDelayMisocaModal(invoiceId) {
    const inv = window.stoneStore.getMisocaData().invoices.find(i => i.id === invoiceId);
    if (!inv) return;

    // 対応する取引を特定、または直接変更
    const newDate = prompt(`「${inv.partner}」の新しい入金予定日を入力してください (YYYY-MM-DD):`, inv.dueDate);
    if (newDate && /^\\d{4}-\\d{2}-\\d{2}$/.test(newDate)) {
      window.stoneStore.updateInvoiceDueDate(inv.id, newDate, 'Misoca画面から期日更新');
      this.showToast(`入金予定日を「${newDate}」に変更しました`);
      this.render();
      this.openUncollectedModal();
    }
  }

  // Misoca CSV取り込みモーダル
  openMisocaImportModal() {
    const modal = document.getElementById('modalMisocaImport');
    if (!modal) return;
    const resultArea = document.getElementById('misocaImportResultArea');
    if (resultArea) resultArea.classList.add('hidden');
    modal.classList.remove('hidden');
  }

  handleMisocaFileSelect(e) {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (evt) => {
        try {
          const text = evt.target.result;
          const result = window.stoneStore.importMisocaCSV(text, file.name);
          const resultArea = document.getElementById('misocaImportResultArea');
          if (resultArea) {
            resultArea.className = 'p-3 rounded-xl border border-amber-300 bg-amber-50 text-amber-950 text-xs space-y-0.5';
            resultArea.innerHTML = `
              <div class="font-bold text-amber-900">✅ Misocaの請求書CSVを取り込みました</div>
              <div>・取り込み件数: <strong>${result.count} 件</strong></div>
              <div>・日時: <strong>${result.lastImportedAt}</strong></div>
              <div class="text-[10px] text-amber-800 mt-1">※弥生の売掛仕訳と二重計上されないよう日別資金繰り表に同期されました。</div>
            `;
            resultArea.classList.remove('hidden');
          }
          this.showToast(`Misocaの請求書（${result.count}件）を取り込みました！`);
          this.render();
        } catch (err) {
          alert('Misoca CSV取り込みエラー: ' + err.message);
        }
      };
      reader.readAsText(file, 'UTF-8');
    }
  }

  handleLoadSampleMisoca() {
    this.showToast('Misocaのサンプル請求書データ（5件）が同期されています！');
    this.openUncollectedModal();
  }
"""

# Insert Misoca methods right before the final closing brace of class StoneApp
# Find the end of class StoneApp
split_marker = "\n}\n\n// アプリケーション初期化"
code = code.replace(split_marker, "\n" + misoca_methods + split_marker)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js with Misoca methods successfully.")
