import re

store_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js'

with open(store_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update INITIAL_DATA to include misocaData
misoca_init = """  // Misoca連携データ（請求書・見積書・売掛金・二重計上防止）
  misocaData: {
    lastImportedAt: null,
    invoices: [
      {
        id: 'inv-101',
        invoiceNumber: 'INV-2026-101',
        issueDate: '2026-10-25',
        dueDate: '2026-11-05',
        partner: '佐藤 正雄 様',
        subject: '墓所新設工事 着工時内金（半金）',
        totalAmount: 850000,
        receivedAmount: 0,
        status: 'unpaid',
        accountId: 'bank-1',
        matchedYayoiKey: null,
        note: 'Misoca発行請求書'
      },
      {
        id: 'inv-102',
        invoiceNumber: 'INV-2026-102',
        issueDate: '2026-11-02',
        dueDate: '2026-11-20',
        partner: '高橋 健一 様',
        subject: '戒名追加彫刻および納骨料',
        totalAmount: 55000,
        receivedAmount: 0,
        status: 'unpaid',
        accountId: 'bank-3',
        matchedYayoiKey: null,
        note: 'Misoca発行請求書'
      },
      {
        id: 'inv-103',
        invoiceNumber: 'INV-2026-103',
        issueDate: '2026-11-10',
        dueDate: '2026-11-30',
        partner: '宗教法人 田中寺',
        subject: '歴代住職墓補修・参道補修 一式完工代金',
        totalAmount: 1200000,
        receivedAmount: 0,
        status: 'unpaid',
        accountId: 'bank-1',
        matchedYayoiKey: null,
        note: 'Misoca発行請求書'
      },
      {
        id: 'inv-104',
        invoiceNumber: 'INV-2026-104',
        issueDate: '2026-11-15',
        dueDate: '2026-12-15',
        partner: '佐藤 正雄 様',
        subject: '墓所新設工事 完工時残金（お引き渡し時）',
        totalAmount: 850000,
        receivedAmount: 0,
        status: 'unpaid',
        accountId: 'bank-1',
        matchedYayoiKey: null,
        note: 'Misoca発行請求書'
      },
      {
        id: 'inv-105',
        invoiceNumber: 'INV-2026-105',
        issueDate: '2026-11-15',
        dueDate: '2027-01-20',
        partner: '渡辺 浩司 様',
        subject: '市営霊園 墓所撤去・更地返還工事代金',
        totalAmount: 450000,
        receivedAmount: 0,
        status: 'unpaid',
        accountId: 'bank-1',
        matchedYayoiKey: null,
        note: 'Misoca発行請求書'
      }
    ],
    estimates: [
      {
        id: 'est-201',
        estimateNumber: 'EST-2026-201',
        issueDate: '2026-11-12',
        partner: '伊藤 雅之 様',
        subject: '和型九寸墓石新規建立工事',
        totalAmount: 1650000,
        status: 'sent',
        validUntil: '2026-12-12',
        note: '霊園現地確認済み、字彫り原稿打合せ中'
      },
      {
        id: 'est-202',
        estimateNumber: 'EST-2026-202',
        issueDate: '2026-11-14',
        partner: '浄土真宗 専念寺様',
        subject: '本堂前 参道敷石改修・段差解消バリアフリー工事',
        totalAmount: 2200000,
        status: 'accepted',
        validUntil: '2026-12-31',
        note: '春彼岸前の着工希望、見積合意済'
      }
    ]
  },
"""

if "misocaData:" not in code:
    code = code.replace("  // 1. 口座残高（基準日付き手入力）", misoca_init + "  // 1. 口座残高（基準日付き手入力）")

# 2. Add Misoca methods to StoneAppStore
misoca_store_methods = """
  // ==============================================================
  // Misoca連携（請求書・見積書・未回収金 ＆ 弥生二重計上防止）
  // ==============================================================
  getMisocaData() {
    if (!this.data.misocaData) {
      this.data.misocaData = JSON.parse(JSON.stringify(INITIAL_DATA.misocaData));
    }
    return this.data.misocaData;
  }

  // 未回収請求書（売掛金）リストの取得
  getUncollectedInvoices() {
    const misoca = this.getMisocaData();
    return (misoca.invoices || []).filter(inv => inv.status !== 'paid').map(inv => {
      const remainingAmount = inv.totalAmount - (inv.receivedAmount || 0);
      const isOverdue = inv.dueDate < new Date().toISOString().slice(0, 10);
      return {
        ...inv,
        remainingAmount,
        isOverdue
      };
    }).sort((a, b) => a.dueDate.localeCompare(b.dueDate));
  }

  // 入金記録（一部入金・全額入金への対応）
  recordInvoicePayment(invoiceId, receivedAmount, accountId = null, paymentDate = null) {
    const misoca = this.getMisocaData();
    const inv = misoca.invoices.find(i => i.id === invoiceId);
    if (!inv) throw new Error('指定された請求書が見つかりません。');

    const amt = parseInt(receivedAmount, 10) || 0;
    inv.receivedAmount = (inv.receivedAmount || 0) + amt;
    const targetAcc = accountId || inv.accountId || 'bank-1';
    const date = paymentDate || new Date().toISOString().slice(0, 10);

    if (inv.receivedAmount >= inv.totalAmount) {
      inv.status = 'paid';
    } else {
      inv.status = 'partial'; // 一部入金
    }

    // 取引（入金実績）として資金繰り表に反映
    const actualTx = {
      id: 'misoca-pay-' + Date.now(),
      date,
      type: 'income',
      partner: inv.partner,
      category: '墓石新設代',
      amount: amt,
      accountId: targetAcc,
      projectId: null,
      isActual: true,
      note: `Misoca[${inv.invoiceNumber}] 入金（${inv.status === 'paid' ? '全額回収' : '一部入金'}）: ${inv.subject}`
    };
    this.addTransaction(actualTx);

    // 予定取引の金額を相殺（二重計上防止）
    const planTx = this.data.transactions.find(t => t.partner === inv.partner && !t.isActual && t.type === 'income');
    if (planTx) {
      if (inv.status === 'paid') {
        this.deleteTransaction(planTx.id);
      } else {
        planTx.amount = Math.max(0, planTx.amount - amt);
      }
    }

    this.saveData();
    return inv;
  }

  // 入金予定日の変更（入金遅延の反映）
  updateInvoiceDueDate(invoiceId, newDueDate, reason = '') {
    const misoca = this.getMisocaData();
    const inv = misoca.invoices.find(i => i.id === invoiceId);
    if (!inv) throw new Error('請求書が見つかりません。');

    const oldDate = inv.dueDate;
    inv.dueDate = newDueDate;
    if (reason) {
      inv.note = `${inv.note || ''} (期日変更: ${oldDate}➔${newDueDate} ${reason})`;
    }

    // 対応する入金予定取引の日付も自動同期
    const tx = this.data.transactions.find(t => t.partner === inv.partner && !t.isActual && t.type === 'income');
    if (tx) {
      this.delayTransaction(tx.id, newDueDate, `Misoca期日変更: ${reason}`);
    }

    this.saveData();
    return inv;
  }

  // Misoca CSV取り込み（請求書一覧CSV / 見積書一覧CSV）
  importMisocaCSV(csvText, fileName = 'Misoca請求書一覧.csv') {
    const lines = csvText.split(/\\r?\\n/).filter(line => line.trim().length > 0);
    if (lines.length < 2) throw new Error('CSVの内容が不足しています。');

    const misoca = this.getMisocaData();
    let importedInvoices = 0;
    const isEstimate = fileName.includes('見積') || csvText.includes('見積書番号');

    const headers = lines[0].split(',').map(h => h.trim().replace(/^[\"']|[\"']$/g, ''));

    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(',').map(c => c.trim().replace(/^[\"']|[\"']$/g, ''));
      if (cols.length < 3) continue;

      if (!isEstimate) {
        // 請求書CSV
        let invNoIdx = headers.findIndex(h => h.includes('請求書番号') || h.includes('番号'));
        let partnerIdx = headers.findIndex(h => h.includes('請求先') || h.includes('取引先'));
        let dateIdx = headers.findIndex(h => h.includes('請求日'));
        let dueIdx = headers.findIndex(h => h.includes('支払期限') || h.includes('お支払期限') || h.includes('入金期日'));
        let amtIdx = headers.findIndex(h => h.includes('合計金額') || h.includes('請求金額'));
        let subjectIdx = headers.findIndex(h => h.includes('件名') || h.includes('品名'));

        if (invNoIdx === -1) invNoIdx = 0;
        if (partnerIdx === -1) partnerIdx = 1;
        if (amtIdx === -1) amtIdx = 2;
        if (dueIdx === -1) dueIdx = 3;

        const invNo = cols[invNoIdx] || `INV-${Date.now()}-${i}`;
        const partner = cols[partnerIdx] || '施主様';
        const rawAmt = cols[amtIdx] || '0';
        const amount = parseInt(rawAmt.replace(/[^0-9]/g, ''), 10) || 0;
        const dueDate = (cols[dueIdx] || '').replace(/\\//g, '-');
        const subject = subjectIdx !== -1 ? cols[subjectIdx] : '石材工事代金';

        // 既存同一番号チェック（重複防止）
        const existingIdx = misoca.invoices.findIndex(inv => inv.invoiceNumber === invNo);
        const invObj = {
          id: existingIdx !== -1 ? misoca.invoices[existingIdx].id : 'inv-' + Date.now() + '-' + i,
          invoiceNumber: invNo,
          issueDate: dateIdx !== -1 ? cols[dateIdx].replace(/\\//g, '-') : new Date().toISOString().slice(0, 10),
          dueDate: dueDate || new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10),
          partner,
          subject,
          totalAmount: amount,
          receivedAmount: existingIdx !== -1 ? misoca.invoices[existingIdx].receivedAmount : 0,
          status: existingIdx !== -1 ? misoca.invoices[existingIdx].status : 'unpaid',
          accountId: 'bank-1',
          matchedYayoiKey: null,
          note: 'Misoca CSV取り込み'
        };

        if (existingIdx !== -1) {
          misoca.invoices[existingIdx] = invObj;
        } else {
          misoca.invoices.push(invObj);
        }
        importedInvoices++;

        // 弥生との二重計上防止チェックを行いながら資金繰り予定に同期
        const existingTx = this.data.transactions.find(t => t.partner === partner && t.amount === amount && !t.isActual);
        if (!existingTx && invObj.status !== 'paid') {
          this.data.transactions.push({
            id: 'misoca-tx-' + invObj.id,
            date: invObj.dueDate,
            type: 'income',
            partner: invObj.partner,
            category: '墓石新設代',
            amount: invObj.totalAmount - (invObj.receivedAmount || 0),
            accountId: 'bank-1',
            projectId: null,
            isActual: false,
            note: `Misoca[${invObj.invoiceNumber}] 入金予定: ${invObj.subject}`
          });
        }
      }
    }

    misoca.lastImportedAt = new Date().toLocaleString('ja-JP');
    this.saveData();
    return {
      success: true,
      count: importedInvoices,
      fileName,
      lastImportedAt: misoca.lastImportedAt
    };
  }
"""

if "getMisocaData" not in code:
    code = code.replace("  // ユーザー・権限制御\n  getCurrentUser() {", misoca_store_methods + "\n  // ユーザー・権限制御\n  getCurrentUser() {")

with open(store_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated store.js with Misoca methods.")
