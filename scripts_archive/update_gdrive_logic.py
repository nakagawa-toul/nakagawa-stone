app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Update simulateInvoiceAIScan to dynamically update gdriveFolderPath
old_scan_end = """      document.getElementById('aiInputCategory').value = '石材仕入';
      document.getElementById('aiInputAccount').value = 'bank-1'; // 中京銀行
      document.getElementById('aiInputNote').value = 'AI読取: インド産黒御影 外柵・笠石部材一式（請求書写真登録）';

      this.showToast('🤖 AIが請求書から支払先・金額・期日を読み取りました！確認してください');
    }, 1200);"""

new_scan_end = """      document.getElementById('aiInputCategory').value = '石材仕入';
      document.getElementById('aiInputAccount').value = 'bank-1'; // 中京銀行
      document.getElementById('aiInputNote').value = 'AI読取: インド産黒御影 外柵・笠石部材一式（Googleドライブ保管）';

      // Google ドライブ保存先フォルダパスの動的更新
      const issueDate = document.getElementById('aiInputIssueDate').value || '2026-11-15';
      const parts = issueDate.split('-');
      const yMonth = parts[0] + '年' + (parts.length > 1 ? parseInt(parts[1], 10) : 11) + '月';
      const pathEl = document.getElementById('gdriveFolderPath');
      if (pathEl) {
        pathEl.textContent = `Google ドライブ ➔ 請求書 ➔ ${yMonth} ➔ (東日本石材_${issueDate.replace(/-/g, '')}.jpg)`;
      }

      this.showToast('🤖 AIが請求書を解析しました！Googleドライブの「請求書/' + yMonth + '」へ自動仕分け保存されます');
    }, 1200);"""

code = code.replace(old_scan_end, new_scan_end)

# Update handleSaveScannedInvoice toast message
old_save_toast = """    window.stoneStore.addTransaction(tx);
    document.getElementById('modalInvoicePhoto').classList.add('hidden');
    this.showToast(`請求書（¥${amount.toLocaleString()}）を支払予定に登録しました！`);
    this.render();"""

new_save_toast = """    window.stoneStore.addTransaction(tx);
    document.getElementById('modalInvoicePhoto').classList.add('hidden');
    
    // 年月フォルダの算出
    const dParts = dueDate.split('-');
    const yearMonth = dParts[0] + '年' + (dParts.length > 1 ? parseInt(dParts[1], 10) : 11) + '月';

    this.showToast(`請求書（¥${amount.toLocaleString()}）を登録しました！Googleドライブの「請求書 / ${yearMonth}」に自動仕分け保存されます（Macの容量消費ゼロ）`);
    this.render();"""

code = code.replace(old_save_toast, new_save_toast)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js with Google Drive folder auto-routing successfully.")
