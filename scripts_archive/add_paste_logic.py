app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Add paste listeners
paste_listeners = """
    // 弥生CSVのタブ切り替え（ファイルドロップ vs テキスト貼り付け）
    const yayoiTabFile = document.getElementById('yayoiTabFile');
    const yayoiTabPaste = document.getElementById('yayoiTabPaste');
    const yayoiAreaFile = document.getElementById('yayoiAreaFile');
    const yayoiAreaPaste = document.getElementById('yayoiAreaPaste');

    if (yayoiTabFile && yayoiTabPaste) {
      yayoiTabFile.addEventListener('click', () => {
        yayoiTabFile.className = 'px-3 py-1.5 rounded-lg bg-indigo-600 text-white shadow-sm font-bold';
        yayoiTabPaste.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100 font-medium';
        yayoiAreaFile.classList.remove('hidden');
        yayoiAreaPaste.classList.add('hidden');
      });
      yayoiTabPaste.addEventListener('click', () => {
        yayoiTabPaste.className = 'px-3 py-1.5 rounded-lg bg-indigo-600 text-white shadow-sm font-bold';
        yayoiTabFile.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100 font-medium';
        yayoiAreaPaste.classList.remove('hidden');
        yayoiAreaFile.classList.add('hidden');
      });
    }

    const btnProcessYayoiPaste = document.getElementById('btnProcessYayoiPaste');
    if (btnProcessYayoiPaste) {
      btnProcessYayoiPaste.addEventListener('click', () => this.handleProcessYayoiPaste());
    }
"""

anchor = "    const btnLoadSampleYayoi = document.getElementById('btnLoadSampleYayoi');"
code = code.replace(anchor, paste_listeners + "\n" + anchor)

# Add handleProcessYayoiPaste method
method_code = """
  handleProcessYayoiPaste() {
    const textarea = document.getElementById('yayoiPasteText');
    if (!textarea) return;
    const text = textarea.value.trim();
    if (!text) {
      alert('貼り付け枠に弥生CSVのテキストを入力してください。');
      return;
    }
    try {
      const result = window.stoneStore.importYayoiCSV(text, '貼り付けテキストデータ.csv');
      this.displayYayoiImportResult(result);
      this.showToast(`貼り付けた弥生データを取り込みました（${result.parsedCount}件）`);
      textarea.value = '';
      this.render();
    } catch (err) {
      alert('弥生データの取り込みに失敗しました: ' + err.message);
    }
  }
"""

anchor_method = "  handleLoadSampleYayoi() {"
code = code.replace(anchor_method, method_code + "\n" + anchor_method)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js with paste handlers.")
