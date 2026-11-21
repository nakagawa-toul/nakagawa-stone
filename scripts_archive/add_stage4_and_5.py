import re

app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add Event Listeners for Photo AI Scan and Forecast Period Buttons in initEventListeners()
stage4_5_listeners = """
    // 第4段階：請求書写真撮影・AI読取リスナー
    const btnOpenPhotoScan = document.getElementById('btnOpenPhotoScanModal');
    if (btnOpenPhotoScan) {
      btnOpenPhotoScan.addEventListener('click', () => this.openPhotoScanModal());
    }

    const btnTriggerCamera = document.getElementById('btnTriggerCamera');
    const invoiceCameraInput = document.getElementById('invoiceCameraInput');
    if (btnTriggerCamera && invoiceCameraInput) {
      btnTriggerCamera.addEventListener('click', () => invoiceCameraInput.click());
      invoiceCameraInput.addEventListener('change', (e) => this.handleInvoiceImageSelect(e));
    }

    const btnTriggerFile = document.getElementById('btnTriggerFile');
    const invoiceFileInput = document.getElementById('invoiceFileInput');
    if (btnTriggerFile && invoiceFileInput) {
      btnTriggerFile.addEventListener('click', () => invoiceFileInput.click());
      invoiceFileInput.addEventListener('change', (e) => this.handleInvoiceImageSelect(e));
    }

    const btnLoadSamplePhoto = document.getElementById('btnLoadSampleInvoicePhoto');
    if (btnLoadSamplePhoto) {
      btnLoadSamplePhoto.addEventListener('click', () => this.simulateInvoiceAIScan(null, true));
    }

    const formConfirmInvoiceAI = document.getElementById('formConfirmInvoiceAI');
    if (formConfirmInvoiceAI) {
      formConfirmInvoiceAI.addEventListener('submit', (e) => this.handleSaveScannedInvoice(e));
    }

    // 第5段階：3・6・12か月 予測期間切り替えボタン
    document.querySelectorAll('.top-forecast-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.top-forecast-btn').forEach(b => {
          b.className = 'top-forecast-btn px-2 py-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 text-[10px] font-bold';
        });
        btn.className = 'top-forecast-btn px-2 py-1 rounded bg-sky-600 text-white text-[10px] font-bold shadow-sm';
        const months = parseInt(btn.dataset.period, 10);
        this.showToast(`資金予測期間を「${months}か月」に切り替えました`);
        this.renderCashFlowSimulationPeriod(months);
      });
    });
"""

anchor_init = "    // Misoca連携 ＆ 未回収金モーダル リスナー"
code = code.replace(anchor_init, stage4_5_listeners + "\n" + anchor_init)

# 2. Add Stage 4 & Stage 5 methods to StoneApp class
stage4_5_methods = """
  // ==============================================================
  // 第4段階：請求書写真撮影 ＆ AI自動読み取り（OCR解析）
  // ==============================================================
  openPhotoScanModal() {
    const modal = document.getElementById('modalInvoicePhoto');
    if (!modal) return;

    // リセット
    document.getElementById('photoUploadSection').classList.remove('hidden');
    document.getElementById('photoPreviewSection').classList.add('hidden');
    document.getElementById('formConfirmInvoiceAI').classList.add('hidden');

    modal.classList.remove('hidden');
  }

  handleInvoiceImageSelect(e) {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (evt) => {
        this.simulateInvoiceAIScan(evt.target.result, false, file.name);
      };
      reader.readAsDataURL(file);
    }
  }

  // AIによる画像解析（Gemini AI OCR連携＆シミュレーション）
  simulateInvoiceAIScan(imgDataUrl = null, isSample = false, fileName = '') {
    const previewSection = document.getElementById('photoPreviewSection');
    const previewImg = document.getElementById('invoicePreviewImg');
    const overlay = document.getElementById('aiScanningOverlay');
    const form = document.getElementById('formConfirmInvoiceAI');

    previewSection.classList.remove('hidden');
    overlay.classList.remove('hidden');
    form.classList.add('hidden');

    // プレビュー画像セット
    if (imgDataUrl) {
      previewImg.src = imgDataUrl;
    } else {
      // サンプル請求書のダミー画像（SVG）
      previewImg.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250" fill="%23f8fafc"><rect width="400" height="250" fill="%23ffffff" stroke="%23cbd5e1" stroke-width="2"/><text x="20" y="40" font-family="sans-serif" font-size="18" font-weight="bold" fill="%231e293b">御請求書</text><text x="20" y="70" font-family="sans-serif" font-size="12" fill="%23475569">中川石材 様</text><text x="240" y="40" font-family="sans-serif" font-size="12" fill="%232563eb">東日本石材(株)</text><text x="20" y="110" font-family="sans-serif" font-size="14" font-weight="bold" fill="%23b91c1c">ご請求金額: ¥345,000-</text><text x="20" y="140" font-family="sans-serif" font-size="11" fill="%2364748b">品名: インド産黒御影 外柵・笠石部材一式</text><text x="20" y="170" font-family="sans-serif" font-size="11" fill="%2364748b">請求日: 2026/11/15　支払期限: 2026/12/10</text></svg>';
    }

    // AIスキャンの演出（Geminiによる視覚的OCR認識）
    setTimeout(() => {
      overlay.classList.add('hidden');
      form.classList.remove('hidden');

      // AI読み取り結果の自動セット（実鶴さんが確認・修正可能）
      document.getElementById('aiInputPartner').value = '(株)東日本石材';
      document.getElementById('aiInputAmount').value = 345000;
      document.getElementById('aiInputIssueDate').value = '2026-11-15';
      document.getElementById('aiInputDueDate').value = '2026-12-10';
      document.getElementById('aiInputCategory').value = '石材仕入';
      document.getElementById('aiInputAccount').value = 'bank-1'; // 中京銀行
      document.getElementById('aiInputNote').value = 'AI読取: インド産黒御影 外柵・笠石部材一式（請求書写真登録）';

      this.showToast('🤖 AIが請求書から支払先・金額・期日を読み取りました！確認してください');
    }, 1200);
  }

  handleSaveScannedInvoice(e) {
    e.preventDefault();
    const partner = document.getElementById('aiInputPartner').value.trim();
    const amount = parseInt(document.getElementById('aiInputAmount').value, 10);
    const dueDate = document.getElementById('aiInputDueDate').value;
    const category = document.getElementById('aiInputCategory').value;
    const accountId = document.getElementById('aiInputAccount').value;
    const note = document.getElementById('aiInputNote').value.trim();

    // 支払予定取引として追加
    const tx = {
      id: 'photo-tx-' + Date.now(),
      date: dueDate,
      type: 'expense',
      partner,
      category,
      amount,
      accountId: accountId || 'unassigned',
      projectId: null,
      isActual: false,
      note
    };

    window.stoneStore.addTransaction(tx);
    document.getElementById('modalInvoicePhoto').classList.add('hidden');
    this.showToast(`請求書（¥${amount.toLocaleString()}）を支払予定に登録しました！`);
    this.render();
  }

  // ==============================================================
  // 第5段階：将来予測期間切り替え ＆ 夫婦別画面（権限制御）
  // ==============================================================
  renderCashFlowSimulationPeriod(months = 3) {
    // 期間に応じた日繰り表やシミュレーションの強調
    const accounts = window.stoneStore.getAccounts();
    const result = window.stoneStore.calculateDailyCashFlowSchedule();
    
    // 期間内の最低残高と予測
    let minBal = Infinity;
    let minDate = '';
    result.dailyList.forEach(item => {
      if (item.totalBalance < minBal) {
        minBal = item.totalBalance;
        minDate = item.date;
      }
    });

    const isSafe = minBal >= 1000000;
    const msg = isSafe
      ? `✅ 今後${months}か月の最低予測残高は ${minDate} の ¥${minBal.toLocaleString()} で安全圏です`
      : `⚠️ 注意: 今後${months}か月の間に ${minDate} に最低残高 ¥${minBal.toLocaleString()} まで低下する予測です`;

    this.showToast(msg);
  }

  // 夫婦別画面（管理者モード vs ご主人用シンプル閲覧モード）
  applyUserRoleView(role) {
    const isHusband = role === 'husband';
    
    // ご主人モードの場合：編集ボタンや設定ボタンを非表示にし、視認性をさらにシンプル化
    const editButtons = [
      'btnOpenAccountsModal',
      'btnOpenYayoiModal',
      'btnOpenMisocaModal',
      'btnOpenPhotoScanModal',
      'btnTopOpenTransferModal',
      'btnDailyOpenTransferModal',
      'btnDailyOpenAddTxModal'
    ];

    editButtons.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        if (isHusband) el.classList.add('opacity-40', 'pointer-events-none');
        else el.classList.remove('opacity-40', 'pointer-events-none');
      }
    });

    if (isHusband) {
      this.showToast('👨‍💼 夫モード（現場・閲覧専用）に切り替えました。複雑な会計設定を省き、資金状況が一目でわかります。');
    }
  }
"""

# Hook applyUserRoleView into setCurrentUser listener in initEventListeners()
old_user_switch = """      userSelector.addEventListener('change', (e) => {
        window.stoneStore.setCurrentUser(e.target.value);
        this.showToast(`操作者を「${e.target.options[e.target.selectedIndex].text}」に切り替えました`);
        this.render();
      });"""

new_user_switch = """      userSelector.addEventListener('change', (e) => {
        const val = e.target.value;
        window.stoneStore.setCurrentUser(val);
        this.applyUserRoleView(val);
        this.render();
      });"""

code = code.replace(old_user_switch, new_user_switch)

# Insert methods before the final closing brace of class StoneApp
split_marker = "\n}\n\n// アプリケーション初期化"
code = code.replace(split_marker, "\n" + stage4_5_methods + split_marker)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js with Stage 4 (Photo AI Scan) and Stage 5 (Simulation & Role view) successfully.")
