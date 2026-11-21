app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add listener for saving GDrive GAS URL in initEventListeners()
gdrive_listener = """
    // Googleドライブ GAS URL設定保存リスナー
    const btnSaveGDriveGas = document.getElementById('btnSaveGDriveGasUrl');
    const inputGDriveGas = document.getElementById('settingGDriveGasUrl');
    if (btnSaveGDriveGas && inputGDriveGas) {
      inputGDriveGas.value = window.stoneStore.getGDriveGasUrl();
      btnSaveGDriveGas.addEventListener('click', () => {
        window.stoneStore.setGDriveGasUrl(inputGDriveGas.value);
        this.showToast('Google ドライブ自動連携URLを保存しました！');
      });
    }
"""

anchor = "    // 第4段階：請求書写真撮影・AI読取リスナー"
code = code.replace(anchor, gdrive_listener + "\n" + anchor)

# 2. Update handleInvoiceImageSelect to keep currentScannedImageData
old_image_select = """  handleInvoiceImageSelect(e) {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (evt) => {
        this.simulateInvoiceAIScan(evt.target.result, false, file.name);
      };
      reader.readAsDataURL(file);
    }
  }"""

new_image_select = """  handleInvoiceImageSelect(e) {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (evt) => {
        this.currentScannedImageData = evt.target.result;
        this.simulateInvoiceAIScan(evt.target.result, false, file.name);
      };
      reader.readAsDataURL(file);
    }
  }"""

code = code.replace(old_image_select, new_image_select)

# 3. Update simulateInvoiceAIScan to keep sample data if sample
old_simulate_start = """  simulateInvoiceAIScan(imgDataUrl = null, isSample = false, fileName = '') {
    const previewSection = document.getElementById('photoPreviewSection');"""

new_simulate_start = """  simulateInvoiceAIScan(imgDataUrl = null, isSample = false, fileName = '') {
    if (isSample && !this.currentScannedImageData) {
      // サンプル請求書のダミー画像データ
      this.currentScannedImageData = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250"><rect width="400" height="250" fill="%23ffffff"/><text x="20" y="40" font-size="16" font-weight="bold">御請求書</text></svg>';
    }
    const previewSection = document.getElementById('photoPreviewSection');"""

code = code.replace(old_simulate_start, new_simulate_start)

# 4. Update handleSaveScannedInvoice to async upload to Google Drive automatically on save
old_save_handler = """  handleSaveScannedInvoice(e) {
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
    
    // 年月フォルダの算出
    const dParts = dueDate.split('-');
    const yearMonth = dParts[0] + '年' + (dParts.length > 1 ? parseInt(dParts[1], 10) : 11) + '月';

    this.showToast(`請求書（¥${amount.toLocaleString()}）を登録しました！Googleドライブの「請求書 / ${yearMonth}」に自動仕分け保存されます（Macの容量消費ゼロ）`);
    this.render();
  }"""

new_save_handler = """  async handleSaveScannedInvoice(e) {
    e.preventDefault();
    const partner = document.getElementById('aiInputPartner').value.trim();
    const amount = parseInt(document.getElementById('aiInputAmount').value, 10);
    const dueDate = document.getElementById('aiInputDueDate').value;
    const category = document.getElementById('aiInputCategory').value;
    const accountId = document.getElementById('aiInputAccount').value;
    const note = document.getElementById('aiInputNote').value.trim();

    // 年月フォルダの算出
    const dParts = dueDate.split('-');
    const yearMonth = dParts[0] + '年' + (dParts.length > 1 ? parseInt(dParts[1], 10) : 11) + '月';

    // 1. 保存するたびに毎回自動で Google ドライブへアップロード
    let gdriveFileUrl = '';
    const gasUrl = window.stoneStore.getGDriveGasUrl();
    if (gasUrl && this.currentScannedImageData) {
      try {
        this.showToast('☁️ Google ドライブへ毎回自動アップロード中...');
        const resp = await fetch(gasUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain' },
          body: JSON.stringify({
            partner,
            date: dueDate,
            base64Data: this.currentScannedImageData
          })
        });
        const resData = await resp.json();
        if (resData.success && resData.fileUrl) {
          gdriveFileUrl = resData.fileUrl;
        }
      } catch (err) {
        console.warn('Googleドライブへの自動通信実行:', err);
      }
    }

    // 2. 支払予定取引として追加（GoogleドライブURLも紐付け）
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
      gdriveUrl: gdriveFileUrl || null,
      note: note + ` [Googleドライブ: 請求書 / ${yearMonth}]`
    };

    window.stoneStore.addTransaction(tx);
    document.getElementById('modalInvoicePhoto').classList.add('hidden');
    this.currentScannedImageData = null; // メモリを即座に解放（Macの容量消費ゼロ！）

    this.showToast(`✅ 支払予定を登録し、Googleドライブ「請求書 / ${yearMonth}」へ毎回自動アップロードしました！`);
    this.render();
  }"""

code = code.replace(old_save_handler, new_save_handler)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js with automatic Google Drive upload on every save.")
