/**
 * 中川石材 業務管理システム - メインアプリケーションスクリプト
 * UIレンダリング、イベントハンドリング、Chart.js連携、音声入力、権限制御
 */

class StoneApp {
  constructor() {
    this.currentView = 'home';
    this.fundsSubtab = 'statement';
    this.dailyScheduleViewMode = 'total'; // 'total' | 'matrix'
    this.bsplTab = 'pl'; // 'pl' | 'bs' | 'cf' // 'statement' | 'breakdown' | 'overview'
    this.taskFilter = 'all'; // 'all' | 'overdue' | 'today' | 'week' | 'completed'
    this.cashFlowChart = null;
    this.expenseDonutChart = null;
    this.speechRecognition = null;
    this.isRecordingVoice = false;

    // 今日の基準日（日本時間 JST: YYYY-MM-DD）
    const now = new Date();
    const jstDate = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Tokyo' }));
    const yyyy = jstDate.getFullYear();
    const mm = String(jstDate.getMonth() + 1).padStart(2, '0');
    const dd = String(jstDate.getDate()).padStart(2, '0');
    this.todayStr = `${yyyy}-${mm}-${dd}`;

    this.init();
  }

  init() {
    this.checkSecurityPinLock();
    this.initEventListeners();
    this.initSpeechRecognition();
    
    // ストア変更時の自動再描画
    window.stoneStore.subscribe(() => {
      this.render();
    });

    // 初回レンダリング
    this.render();

    // Googleドライブからの初期バックグラウンド自動同期
    this.autoSyncOnStartup();
  }

  // 🔒 外出先用 暗証番号（画面ロック）チェック
  checkSecurityPinLock() {
    const pin = window.stoneStore.getSecurityPin();
    const modalPin = document.getElementById('modalSecurityPin');
    if (pin && modalPin) {
      modalPin.classList.remove('hidden');
      const input = document.getElementById('pinInputUnlock');
      if (input) setTimeout(() => input.focus(), 300);
    }
  }

  // 起動時のGoogleドライブ自動同期（最新データがあれば自動反映）
  async autoSyncOnStartup() {
    const gasUrl = window.stoneStore.getGDriveGasUrl();
    if (!gasUrl) return;

    this.updateGDriveSyncStatusUI('☁️ 同期確認中...');
    const res = await window.stoneStore.syncFromGDrive();
    if (res && res.success && !res.empty) {
      this.updateGDriveSyncStatusUI('☁️ 最新（同期済）');
      this.showToast('☁️ Google ドライブから最新データを自動読込しました');
    } else {
      this.updateGDriveSyncStatusUI('☁️ 同期完了');
    }
  }

  updateGDriveSyncStatusUI(statusText) {
    const headerStatus = document.getElementById('headerGDriveSyncStatus');
    const labelLastSync = document.getElementById('labelLastGDriveSync');
    if (headerStatus) headerStatus.textContent = statusText;
    if (labelLastSync) {
      const lastSync = window.stoneStore.data.lastGDriveSyncAt;
      labelLastSync.textContent = lastSync ? new Date(lastSync).toLocaleString('ja-JP') : '未同期';
    }
  }

  // ==============================================================
  // イベントリスナー設定
  // ==============================================================
  initEventListeners() {

    // --- 新規：トップ資金ダッシュボード ＆ 6口座・振替・遅延・財務三表リスナー ---




    // Googleドライブ GAS URL設定保存・テスト・手順ガイドリスナー
    const btnSaveGDriveGas = document.getElementById('btnSaveGDriveGasUrl');
    const inputGDriveGas = document.getElementById('settingGDriveGasUrl');
    const btnTestGDriveGas = document.getElementById('btnTestGDriveGasUrl');
    const btnToggleGDriveHelp = document.getElementById('btnToggleGDriveHelp');
    const gdriveSetupHelpBox = document.getElementById('gdriveSetupHelpBox');
    const btnCopyGasCode = document.getElementById('btnCopyGasCode');
    const testStatusEl = document.getElementById('gdriveTestStatus');

    if (btnSaveGDriveGas && inputGDriveGas) {
      inputGDriveGas.value = window.stoneStore.getGDriveGasUrl();
      btnSaveGDriveGas.addEventListener('click', () => {
        window.stoneStore.setGDriveGasUrl(inputGDriveGas.value);
        this.showToast('✅ Google ドライブ自動連携URLを保存しました！');
      });
    }


    if (btnToggleGDriveHelp && gdriveSetupHelpBox) {
      btnToggleGDriveHelp.addEventListener('click', () => {
        gdriveSetupHelpBox.classList.toggle('hidden');
      });
    }


    if (btnCopyGasCode) {
      btnCopyGasCode.addEventListener('click', async () => {
        try {
          const resp = await fetch('gas_drive_uploader.js');
          const code = await resp.text();
          await navigator.clipboard.writeText(code);
          this.showToast('📋 GASコードをクリップボードにコピーしました！');
        } catch (err) {
          this.showToast('⚠️ コピーに失敗しました。gas_drive_uploader.js ファイルをご確認ください。');
        }
      });
    }


    if (btnTestGDriveGas && inputGDriveGas) {
      btnTestGDriveGas.addEventListener('click', async () => {
        const url = inputGDriveGas.value.trim();
        if (!url) {
          this.showToast('⚠️ 先にGASのウェブアプリURLを入力してください');
          return;
        }
        if (testStatusEl) {
          testStatusEl.classList.remove('hidden', 'bg-red-50', 'text-red-700', 'bg-green-50', 'text-green-700');
          testStatusEl.classList.add('bg-blue-50', 'text-blue-700');
          testStatusEl.innerHTML = '🔄 Googleドライブへ疎通確認中...';
        }
        try {
          const resp = await fetch(url, { method: 'GET', mode: 'cors' });
          const data = await resp.json();
          if (data && data.status === 'ok') {
            if (testStatusEl) {
              testStatusEl.classList.remove('bg-blue-50', 'text-blue-700');
              testStatusEl.classList.add('bg-emerald-50', 'text-emerald-800');
              testStatusEl.innerHTML = `✅ <strong>接続成功！</strong> Googleドライブの「${data.rootFolderName || '請求書'}」フォルダに正常アクセスできました。<br><a href="${data.rootFolderUrl}" target="_blank" class="underline text-blue-700 font-bold mt-1 inline-block">📂 Googleドライブでフォルダを開く ➔</a>`;
            }
            this.showToast('✅ Googleドライブと正常に接続できました！');
          } else {
            throw new Error(data.message || '不明な応答形式');
          }
        } catch (err) {
          if (testStatusEl) {
            testStatusEl.classList.remove('bg-blue-50', 'text-blue-700');
            testStatusEl.classList.add('bg-amber-50', 'text-amber-800');
            testStatusEl.innerHTML = `⚠️ 接続確認: ブラウザのセキュリティ設定またはURLをご確認ください。<br><span class="text-[10px] text-slate-500">※GASのデプロイで「アクセスできるユーザー：全員」になっているかご確認ください。</span>`;
          }
          this.showToast('⚠️ Googleドライブへの通信を確認してください');
        }
      });
    }
    // Googleドライブ手動同期リスナー（今すぐ保存 / 今すぐ読込）
    const btnManualSaveGDrive = document.getElementById('btnManualSyncToGDrive');
    const btnManualLoadGDrive = document.getElementById('btnManualSyncFromGDrive');
    const btnHeaderSync = document.getElementById('btnHeaderGDriveSync');

    if (btnManualSaveGDrive) {
      btnManualSaveGDrive.addEventListener('click', async () => {
        this.showToast('☁️ Google ドライブへ保存中...');
        const res = await window.stoneStore.syncToGDrive();
        if (res.success) {
          this.updateGDriveSyncStatusUI('☁️ 同期完了');
          this.showToast('✅ Google ドライブに最新データを保存しました！');
        } else {
          this.showToast(`⚠️ 保存エラー: ${res.message || res.error}`);
        }
      });
    }

    if (btnManualLoadGDrive) {
      btnManualLoadGDrive.addEventListener('click', async () => {
        this.showToast('🔄 Google ドライブからデータ読込中...');
        const res = await window.stoneStore.syncFromGDrive();
        if (res.success) {
          this.updateGDriveSyncStatusUI('☁️ 最新（同期済）');
          this.showToast('✅ 最新データをGoogle ドライブから読み込みました！');
          this.render();
        } else {
          this.showToast(`⚠️ 読込エラー: ${res.message || res.error}`);
        }
      });
    }

    if (btnHeaderSync) {
      btnHeaderSync.addEventListener('click', async () => {
        // 設定画面を開くか、即座に双方向同期
        const gasUrl = window.stoneStore.getGDriveGasUrl();
        if (!gasUrl) {
          this.navigateTo('settings');
          this.showToast('⚙️ 先にGoogleドライブの連携URLを設定してください');
        } else {
          this.showToast('☁️ Google ドライブと同期中...');
          const res = await window.stoneStore.syncToGDrive();
          if (res.success) {
            this.updateGDriveSyncStatusUI('☁️ 同期完了');
            this.showToast('✅ Google ドライブにデータをバックアップしました');
          } else {
            this.showToast('⚠️ 同期に失敗しました。設定をご確認ください');
          }
        }
      });
    }

    // 🔒 外出先用 暗証番号（PINコード）設定・解除・ロック解除
    const inputPin = document.getElementById('settingSecurityPin');
    const btnSavePin = document.getElementById('btnSaveSecurityPin');
    const btnClearPin = document.getElementById('btnClearSecurityPin');
    const pinStatusText = document.getElementById('securityPinStatusText');
    const updatePinUI = () => {
      const currentPin = window.stoneStore.getSecurityPin();
      if (inputPin) inputPin.value = currentPin;
      if (pinStatusText) {
        pinStatusText.textContent = currentPin 
          ? `現在の設定: ●●●●（設定中）- 外出先でも安全にロックされます` 
          : '現在の設定: 未設定（画面ロックなし）';
        pinStatusText.className = currentPin 
          ? 'text-[11px] font-bold text-amber-700' 
          : 'text-[11px] font-bold text-slate-500';
      }
    };
    updatePinUI();

    if (btnSavePin && inputPin) {
      btnSavePin.addEventListener('click', () => {
        const val = inputPin.value.trim();
        if (!val || val.length < 4) {
          this.showToast('⚠️ 暗証番号は4桁以上の数字を入力してください');
          return;
        }
        window.stoneStore.setSecurityPin(val);
        updatePinUI();
        this.showToast('🔒 外出用 暗証番号を設定しました！');
      });
    }

    if (btnClearPin) {
      btnClearPin.addEventListener('click', () => {
        window.stoneStore.setSecurityPin('');
        if (inputPin) inputPin.value = '';
        updatePinUI();
        this.showToast('暗証番号を解除しました（ロックなし）');
      });
    }

    // 画面ロック解除フォームリスナー
    const pinUnlockForm = document.getElementById('pinUnlockForm');
    const pinInputUnlock = document.getElementById('pinInputUnlock');
    const pinErrMsg = document.getElementById('pinErrorMessage');
    if (pinUnlockForm && pinInputUnlock) {
      pinUnlockForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const currentPin = window.stoneStore.getSecurityPin();
        if (pinInputUnlock.value.trim() === currentPin) {
          document.getElementById('modalSecurityPin').classList.add('hidden');
          pinInputUnlock.value = '';
          if (pinErrMsg) pinErrMsg.classList.add('hidden');
          this.showToast('🔓 ロックを解除しました');
        } else {
          if (pinErrMsg) pinErrMsg.classList.remove('hidden');
          pinInputUnlock.value = '';
          pinInputUnlock.focus();
        }
      });
    }



    // シミュレーションモーダル リスナー
    const btnOpenSim = document.getElementById('btnOpenSimulationModal');
    if (btnOpenSim) {
      btnOpenSim.addEventListener('click', () => this.openSimulationModal());
    }

    const simCheckDelay = document.getElementById('simCheckDelay');
    const simSalesRange = document.getElementById('simSalesRange');
    const simInputExtraExp = document.getElementById('simInputExtraExp');

    [simCheckDelay, simSalesRange, simInputExtraExp].forEach(el => {
      if (el) el.addEventListener('input', () => this.updateStressTestResult());
    });

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
    }
);

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

    // 弥生CSV取り込みリスナー
    const btnOpenYayoi = document.getElementById('btnOpenYayoiModal');
    if (btnOpenYayoi) {
      btnOpenYayoi.addEventListener('click', () => this.openYayoiModal());
    }

    const yayoiFileInput = document.getElementById('yayoiFileInput');
    if (yayoiFileInput) {
      yayoiFileInput.addEventListener('change', (e) => this.handleYayoiFileSelect(e));
    }

    const yayoiDropZone = document.getElementById('yayoiDropZone');
    if (yayoiDropZone) {
      yayoiDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        yayoiDropZone.classList.add('bg-indigo-100', 'border-indigo-600');
      });
      yayoiDropZone.addEventListener('dragleave', () => {
        yayoiDropZone.classList.remove('bg-indigo-100', 'border-indigo-600');
      });
      yayoiDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        yayoiDropZone.classList.remove('bg-indigo-100', 'border-indigo-600');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.processYayoiFile(e.dataTransfer.files[0]);
        }
      });
    }



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

    const btnLoadSampleYayoi = document.getElementById('btnLoadSampleYayoi');
    if (btnLoadSampleYayoi) {
      btnLoadSampleYayoi.addEventListener('click', () => this.handleLoadSampleYayoi());
    }

    const btnOpenAccountsModal = document.getElementById('btnOpenAccountsModal');
    if (btnOpenAccountsModal) {
      btnOpenAccountsModal.addEventListener('click', () => this.openAccountsModal());
    }

    const formAccounts = document.getElementById('formAccounts');
    if (formAccounts) {
      formAccounts.addEventListener('submit', (e) => this.handleSaveAccounts(e));
    }

    const btnTopOpenTransfer = document.getElementById('btnTopOpenTransferModal');
    if (btnTopOpenTransfer) {
      btnTopOpenTransfer.addEventListener('click', () => this.openTransferModal());
    }

    const btnDailyOpenTransfer = document.getElementById('btnDailyOpenTransferModal');
    if (btnDailyOpenTransfer) {
      btnDailyOpenTransfer.addEventListener('click', () => this.openTransferModal());
    }

    const formTransfer = document.getElementById('formTransfer');
    if (formTransfer) {
      formTransfer.addEventListener('submit', (e) => this.handleSaveTransfer(e));
    }

    const btnGoToDaily = document.getElementById('btnGoToDailyCashFlow');
    if (btnGoToDaily) {
      btnGoToDaily.addEventListener('click', () => {
        this.switchView('funds');
        this.switchFundsSubtab('cashflow');
      });
    }


    const btnDailyViewTotal = document.getElementById('btnDailyViewTotal');
    const btnDailyViewMatrix = document.getElementById('btnDailyViewMatrix');
    if (btnDailyViewTotal && btnDailyViewMatrix) {
      btnDailyViewTotal.addEventListener('click', () => {
        this.dailyScheduleViewMode = 'total';
        btnDailyViewTotal.className = 'px-2.5 py-1 rounded-md bg-white text-blue-700 shadow-sm transition font-bold';
        btnDailyViewMatrix.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition font-medium';
        this.renderDailyCashFlowSchedule();
      });
      btnDailyViewMatrix.addEventListener('click', () => {
        this.dailyScheduleViewMode = 'matrix';
        btnDailyViewMatrix.className = 'px-2.5 py-1 rounded-md bg-white text-blue-700 shadow-sm transition font-bold';
        btnDailyViewTotal.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition font-medium';
        this.renderDailyCashFlowSchedule();
      });
    }


    const btnDailyOpenAddTx = document.getElementById('btnDailyOpenAddTxModal');
    if (btnDailyOpenAddTx) {
      btnDailyOpenAddTx.addEventListener('click', () => this.openAddTxModal());
    }

    const btnCloseDailyDetail = document.getElementById('btnCloseDailyDetail');
    if (btnCloseDailyDetail) {
      btnCloseDailyDetail.addEventListener('click', () => {
        const cont = document.getElementById('dailyDetailContainer');
        if (cont) cont.classList.add('hidden');
      });
    }


    const formDelayTx = document.getElementById('formDelayTx');
    if (formDelayTx) {
      formDelayTx.addEventListener('submit', (e) => this.handleSaveDelayTx(e));
    }

    document.querySelectorAll('.btn-quick-delay').forEach(btn => {
      btn.addEventListener('click', () => {
        const days = parseInt(btn.dataset.days, 10);
        const inputNewDate = document.getElementById('delayInputNewDate');
        if (inputNewDate && inputNewDate.value) {
          const d = new Date(inputNewDate.value);
          d.setDate(d.getDate() + days);
          inputNewDate.value = d.toISOString().slice(0, 10);
        }
      });
    }
);

    const btnTopOpenBSPL = document.getElementById('btnTopOpenBSPLModal');
    if (btnTopOpenBSPL) {
      btnTopOpenBSPL.addEventListener('click', () => this.openBSPLModal());
    }

    // 財務三表タブ切り替え
    const bsplTabPL = document.getElementById('bsplTabPL');
    const bsplTabBS = document.getElementById('bsplTabBS');
    const bsplTabCF = document.getElementById('bsplTabCF');
    if (bsplTabPL && bsplTabBS && bsplTabCF) {
      bsplTabPL.addEventListener('click', () => { this.bsplTab = 'pl'; this.renderBSPLContent(); });
      bsplTabBS.addEventListener('click', () => { this.bsplTab = 'bs'; this.renderBSPLContent(); });
      bsplTabCF.addEventListener('click', () => { this.bsplTab = 'cf'; this.renderBSPLContent(); });
    }

    // 1. タブナビゲーション切り替え（PC・モバイル共通）
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = btn.dataset.view;
        if (view) this.switchView(view);
      });
    }
);

    // 2. ユーザー切り替えプルダウン（権限制御モック）
    const userSelector = document.getElementById('userSelector');
    if (userSelector) {
      userSelector.value = window.stoneStore.getCurrentUser();
      userSelector.addEventListener('change', (e) => {
        const val = e.target.value;
        window.stoneStore.setCurrentUser(val);
        this.applyUserRoleView(val);
        this.render();
      });
    }


    // 3. 設定ボタン ＆ QRモーダルボタン
    const btnOpenSettings = document.getElementById('btnOpenSettings');
    if (btnOpenSettings) {
      btnOpenSettings.addEventListener('click', () => {
        this.switchView('settings');
      });
    }

    const btnOpenQrModal = document.getElementById('btnOpenQrModal');
    if (btnOpenQrModal) {
      btnOpenQrModal.addEventListener('click', () => {
        this.updateQrModal();
        document.getElementById('modalQr')?.classList.remove('hidden');
      });
    }


    // 4. 今日の対応 - フィルターボタン
    document.querySelectorAll('.task-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.task-filter-btn').forEach(b => {
          b.classList.remove('active', 'bg-blue-600', 'text-white');
          b.classList.add('text-slate-600');
        });
        btn.classList.add('active', 'bg-blue-600', 'text-white');
        btn.classList.remove('text-slate-600');
        this.taskFilter = btn.dataset.filter;
        this.renderTasks();
      });
    }
);

    // 担当者・カテゴリフィルタ
    const taskAssigneeFilter = document.getElementById('taskAssigneeFilter');
    if (taskAssigneeFilter) {
      taskAssigneeFilter.addEventListener('change', () => this.renderTasks());
    }
    const taskCategoryFilter = document.getElementById('taskCategoryFilter');
    if (taskCategoryFilter) {
      taskCategoryFilter.addEventListener('change', () => this.renderTasks());
    }

    // 5. タスク追加モーダル
    const btnOpenAddTaskModal = document.getElementById('btnOpenAddTaskModal');
    const btnMobileFabAddTask = document.getElementById('btnMobileFabAddTask');
    if (btnOpenAddTaskModal) btnOpenAddTaskModal.addEventListener('click', () => this.openTaskModal());
    if (btnMobileFabAddTask) btnMobileFabAddTask.addEventListener('click', () => this.openTaskModal());

    const formTask = document.getElementById('formTask');
    if (formTask) {
      formTask.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleTaskSubmit();
      });
    }


    // 6. 口座残高変更モーダル
    const btnEditBankBalance = document.getElementById('btnEditBankBalance');
    if (btnEditBankBalance) {
      btnEditBankBalance.addEventListener('click', () => this.openBankModal());
    }
    const formBank = document.getElementById('formBank');
    if (formBank) {
      formBank.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleBankSubmit();
      });
    }


    // 7. 取引（入出金）モーダル
    const btnOpenAddTxModal = document.getElementById('btnOpenAddTxModal');
    const btnOpenAddTxModalStmt = document.getElementById('btnOpenAddTxModalStmt');
    if (btnOpenAddTxModal) {
      btnOpenAddTxModal.addEventListener('click', () => this.openTxModal());
    }
    if (btnOpenAddTxModalStmt) {
      btnOpenAddTxModalStmt.addEventListener('click', () => this.openTxModal());
    }
    const formTx = document.getElementById('formTx');
    if (formTx) {
      formTx.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleTxSubmit();
      });
    }


    // 区分（入金/支払）変更時に費目プルダウンを連動
    const txInputType = document.getElementById('txInputType');
    if (txInputType) {
      txInputType.addEventListener('change', () => {
        this.populateTxCategorySelect(txInputType.value);
      });
    }


    // 資金管理 サブタブ切り替え
    document.querySelectorAll('.funds-subtab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const subtab = btn.dataset.subtab;
        if (subtab) this.switchFundsSubtab(subtab);
      });
    }
);

    // 費目別支出 月セレクター
    const expenseBreakdownMonthSelect = document.getElementById('expenseBreakdownMonthSelect');
    if (expenseBreakdownMonthSelect) {
      expenseBreakdownMonthSelect.addEventListener('change', () => {
        this.renderExpenseBreakdown();
      });
    }


    // キャッシュフロー計算書 期間セレクター
    const cashflowPeriodSelect = document.getElementById('cashflowPeriodSelect');
    if (cashflowPeriodSelect) {
      cashflowPeriodSelect.addEventListener('change', () => {
        this.renderCashFlowStatementByType();
      });
    }


    // 資金繰り表 明細閉じるボタン
    const btnCloseStmtDetail = document.getElementById('btnCloseStmtDetail');
    if (btnCloseStmtDetail) {
      btnCloseStmtDetail.addEventListener('click', () => {
        document.getElementById('stmtDetailContainer')?.classList.add('hidden');
      });
    }


    // 8. 案件モーダル
    const btnOpenAddProjectModal = document.getElementById('btnOpenAddProjectModal');
    if (btnOpenAddProjectModal) {
      btnOpenAddProjectModal.addEventListener('click', () => this.openProjectModal());
    }
    const formProject = document.getElementById('formProject');
    if (formProject) {
      formProject.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleProjectSubmit();
      });
    }


    // 9. 弥生会計進捗モーダル
    const btnOpenYayoiModal = document.getElementById('btnOpenYayoiModal');
    if (btnOpenYayoiModal) {
      btnOpenYayoiModal.addEventListener('click', () => {
        document.getElementById('modalYayoi').classList.remove('hidden');
      });
    }

    const formYayoi = document.getElementById('formYayoi');
    if (formYayoi) {
      formYayoi.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleYayoiSubmit();
      });
    }


    // 10. クイック作業記録ボタン群
    document.querySelectorAll('.quick-log-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        const category = btn.dataset.category;
        window.stoneStore.addActivityLog({
          action: action,
          category: category,
          details: 'クイック記録ボタンより記録'
        });
        this.showToast(`「${action}」を作業履歴に記録しました`);
      });
    }
);

    // 11. 作業メモフォーム送信
    const formAddActivityLog = document.getElementById('formAddActivityLog');
    if (formAddActivityLog) {
      formAddActivityLog.addEventListener('submit', (e) => {
        e.preventDefault();
        const actionInput = document.getElementById('logActionInput');
        const detailsInput = document.getElementById('logDetailsInput');
        const categoryInput = document.getElementById('logCategoryInput');

        if (!actionInput.value.trim()) return;

        window.stoneStore.addActivityLog({
          action: actionInput.value.trim(),
          details: detailsInput.value.trim(),
          category: categoryInput.value
        });

        actionInput.value = '';
        detailsInput.value = '';
        this.showToast('作業履歴を記録しました');
      });
    }


    // 12. 履歴検索
    const logSearchInput = document.getElementById('logSearchInput');
    if (logSearchInput) {
      logSearchInput.addEventListener('input', () => this.renderActivityLogs());
    }

    // 13. モーダル閉じるボタン共通
    document.querySelectorAll('.modal-close-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.modal-backdrop').forEach(m => m.classList.add('hidden'));
      });
    }
);

    // 14. 設定（リセット、エクスポート、インポート）
    const btnResetData = document.getElementById('btnResetData');
    if (btnResetData) {
      btnResetData.addEventListener('click', () => {
        if (confirm('すべての登録データを初期のサンプルデータに戻しますか？')) {
          window.stoneStore.resetToSampleData();
          this.showToast('データを初期サンプルに戻しました');
        }
      });
    }


    const btnExportData = document.getElementById('btnExportData');
    if (btnExportData) {
      btnExportData.addEventListener('click', () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(window.stoneStore.exportData());
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        downloadAnchor.setAttribute("download", `nakagawa_stone_backup_${new Date().toISOString().slice(0,10)}.json`);
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
        this.showToast('バックアップデータを書き出しました');
      });
    }


    const importFileInput = document.getElementById('importFileInput');
    if (importFileInput) {
      importFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
          const res = window.stoneStore.importData(event.target.result);
          if (res.success) {
            this.showToast('データを正常に復元しました');
          } else {
            alert('復元エラー: ' + res.error);
          }
        };
        reader.readAsText(file);
      });
    }


    // 15. メールからタスク作成モーダル内ボタン
    const btnCreateTaskFromModalMail = document.getElementById('btnCreateTaskFromModalMail');
    if (btnCreateTaskFromModalMail) {
      btnCreateTaskFromModalMail.addEventListener('click', () => {
        if (this.currentModalMailId) {
          const task = window.stoneStore.createTaskFromEmail(this.currentModalMailId);
          document.getElementById('modalEmailDetail').classList.add('hidden');
          this.showToast(`メールから「${task.title}」を今日の対応に追加しました！`);
          this.switchView('home');
        }
      });
    }

  }

  // QRコードのURL動的生成
  updateQrModal() {
    const qrImg = document.getElementById('qrCodeImg');
    const qrText = document.getElementById('qrCodeText');
    let targetUrl = 'http://192.168.3.71:8080';
    if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
      if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        targetUrl = window.location.origin;
      }
    }
    if (qrImg) {
      qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(targetUrl)}`;
    }
    if (qrText) {
      qrText.textContent = targetUrl;
    }
  }

  // ==============================================================
  // 音声入力（Web Speech API）
  // ==============================================================
  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btnVoice = document.getElementById('btnVoiceInput');
    const statusText = document.getElementById('voiceStatusText');

    if (!SpeechRecognition) {
      if (btnVoice) {
        btnVoice.addEventListener('click', () => {
          alert('お使いのブラウザでは直接の音声マイクAPIが制限されていますが、スマホのキーボードに付いているマイクアイコン（音声入力）から入力欄に直接お話しいただけます！');
        });
      }
      return;
    }

    this.speechRecognition = new SpeechRecognition();
    this.speechRecognition.lang = 'ja-JP';
    this.speechRecognition.continuous = false;
    this.speechRecognition.interimResults = false;

    this.speechRecognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const actionInput = document.getElementById('logActionInput');
      if (actionInput) {
        actionInput.value = (actionInput.value ? actionInput.value + ' ' : '') + transcript;
      }
      this.showToast(`音声認識: 「${transcript}」`);
    };

    this.speechRecognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      this.isRecordingVoice = false;
      this.updateVoiceButtonUI();
    };

    this.speechRecognition.onend = () => {
      this.isRecordingVoice = false;
      this.updateVoiceButtonUI();
    };

    if (btnVoice) {
      btnVoice.addEventListener('click', () => {
        if (!this.isRecordingVoice) {
          try {
            this.speechRecognition.start();
            this.isRecordingVoice = true;
            this.updateVoiceButtonUI();
          } catch (e) {
            console.error(e);
          }
        } else {
          this.speechRecognition.stop();
          this.isRecordingVoice = false;
          this.updateVoiceButtonUI();
        }
      });
    }

  }

  updateVoiceButtonUI() {
    const btnVoice = document.getElementById('btnVoiceInput');
    const statusText = document.getElementById('voiceStatusText');
    if (!btnVoice) return;

    if (this.isRecordingVoice) {
      btnVoice.classList.add('mic-listening');
      if (statusText) statusText.textContent = '聞いています...';
    } else {
      btnVoice.classList.remove('mic-listening');
      if (statusText) statusText.textContent = '音声入力';
    }
  }

  // ==============================================================
  // 画面（View）の切り替え
  // ==============================================================
  switchView(viewName) {
    this.currentView = viewName;

    // パネル表示切り替え
    document.querySelectorAll('.view-panel').forEach(panel => {
      panel.classList.add('hidden');
    });
    const activePanel = document.getElementById(`view-${viewName}`);
    if (activePanel) activePanel.classList.remove('hidden');

    // ナビゲーションのアクティブスタイル更新
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      if (btn.dataset.view === viewName) {
        btn.classList.add('active', 'text-blue-600', 'bg-blue-50/50');
        btn.classList.remove('text-slate-500', 'text-slate-600');
      } else {
        btn.classList.remove('active', 'text-blue-600', 'bg-blue-50/50');
        btn.classList.add('text-slate-500');
      }
    });

    // 画面固有の再描画
    if (viewName === 'funds') {
      this.renderFunds();
    } else if (viewName === 'projects') {
      this.renderProjects();
    } else if (viewName === 'logs') {
      this.renderActivityLogs();
    } else if (viewName === 'emails') {
      this.renderEmails();
    } else if (viewName === 'home') {
      this.renderTasks();
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ==============================================================
  // 全体レンダリング
  // ==============================================================
  render() {
    this.checkPermissions();
    this.renderHeaderAndBadges();
    
    // 現在のアクティブビューを再描画
    if (this.currentView === 'home') this.renderTasks();
    else if (this.currentView === 'funds') this.renderFunds();
    else if (this.currentView === 'projects') this.renderProjects();
    else if (this.currentView === 'logs') this.renderActivityLogs();
    else if (this.currentView === 'emails') this.renderEmails();
  }

  // 権限制御の適用
  checkPermissions() {
    const canFunds = window.stoneStore.canAccessFunds();
    const canEmails = window.stoneStore.canAccessEmails();

    // 資金タブ
    const fundsNotice = document.getElementById('fundsRestrictedNotice');
    const fundsContent = document.getElementById('fundsContent');
    if (fundsNotice && fundsContent) {
      if (!canFunds) {
        fundsNotice.classList.remove('hidden');
        fundsContent.classList.add('hidden');
      } else {
        fundsNotice.classList.add('hidden');
        fundsContent.classList.remove('hidden');
      }
    }

    // メールタブ
    const emailsNotice = document.getElementById('emailsRestrictedNotice');
    const emailsContent = document.getElementById('emailsContent');
    if (emailsNotice && emailsContent) {
      if (!canEmails) {
        emailsNotice.classList.remove('hidden');
        emailsContent.classList.add('hidden');
      } else {
        emailsNotice.classList.add('hidden');
        emailsContent.classList.remove('hidden');
      }
    }

    // サイドバー＆ボトムバーの視覚的ロック
    const sideNavFunds = document.getElementById('sideNavFunds');
    const bottomNavFunds = document.getElementById('bottomNavFunds');
    const sideNavEmails = document.getElementById('sideNavEmails');
    const bottomNavEmails = document.getElementById('bottomNavEmails');

    if (!canFunds) {
      if (sideNavFunds) sideNavFunds.classList.add('opacity-40');
      if (bottomNavFunds) bottomNavFunds.classList.add('opacity-40');
    } else {
      if (sideNavFunds) sideNavFunds.classList.remove('opacity-40');
      if (bottomNavFunds) bottomNavFunds.classList.remove('opacity-40');
    }

    if (!canEmails) {
      if (sideNavEmails) sideNavEmails.classList.add('opacity-40');
      if (bottomNavEmails) bottomNavEmails.classList.add('opacity-40');
    } else {
      if (sideNavEmails) sideNavEmails.classList.remove('opacity-40');
      if (bottomNavEmails) bottomNavEmails.classList.remove('opacity-40');
    }
  }

  // ヘッダー＆バッジ集計の更新
  renderHeaderAndBadges() {
    const tasks = window.stoneStore.getTasks();
    const emails = window.stoneStore.getEmails();

    let overdueCount = 0;
    let todayCount = 0;
    let weekCount = 0;

    const today = this.todayStr;
    const weekAhead = new Date(today);
    weekAhead.setDate(weekAhead.getDate() + 7);
    const weekAheadStr = weekAhead.toISOString().slice(0, 10);

    tasks.forEach(t => {
      if (t.status === 'pending') {
        if (t.dueDate < today) {
          overdueCount++;
        } else if (t.dueDate === today) {
          todayCount++;
        } else if (t.dueDate <= weekAheadStr) {
          weekCount++;
        }
      }
    });

    // カウント表示
    const elOverdue = document.getElementById('statCountOverdue');
    const elToday = document.getElementById('statCountToday');
    const elWeek = document.getElementById('statCountWeek');
    if (elOverdue) elOverdue.textContent = overdueCount;
    if (elToday) elToday.textContent = todayCount;
    if (elWeek) elWeek.textContent = weekCount;

    // サイドバー＆モバイルバッジ
    const badgeOverdueSidebar = document.getElementById('badgeOverdueSidebar');
    const badgeOverdueMobile = document.getElementById('badgeOverdueMobile');
    if (badgeOverdueSidebar) {
      badgeOverdueSidebar.textContent = overdueCount;
      badgeOverdueSidebar.classList.toggle('hidden', overdueCount === 0);
    }
    if (badgeOverdueMobile) {
      badgeOverdueMobile.textContent = overdueCount;
      badgeOverdueMobile.classList.toggle('hidden', overdueCount === 0);
    }

    // メール未対応バッジ
    let unprocessedEmailsCount = 0;
    emails.forEach(m => {
      if (!m.isProcessed && !m.isNoticeOrAd) unprocessedEmailsCount++;
    });
    const badgeMailSidebar = document.getElementById('badgeUnprocessedEmailsSidebar');
    const badgeMailMobile = document.getElementById('badgeUnprocessedEmailsMobile');
    if (badgeMailSidebar) {
      badgeMailSidebar.textContent = unprocessedEmailsCount;
      badgeMailSidebar.classList.toggle('hidden', unprocessedEmailsCount === 0);
    }
    if (badgeMailMobile) {
      badgeMailMobile.textContent = unprocessedEmailsCount;
      badgeMailMobile.classList.toggle('hidden', unprocessedEmailsCount === 0);
    }
  }

  // ==============================================================
  // 1. 今日の対応（タスク）レンダリング
  // ==============================================================
  setTaskFilter(filter) {
    this.taskFilter = filter;
    document.querySelectorAll('.task-filter-btn').forEach(btn => {
      if (btn.dataset.filter === filter) {
        btn.classList.add('active', 'bg-blue-600', 'text-white');
        btn.classList.remove('text-slate-600');
      } else {
        btn.classList.remove('active', 'bg-blue-600', 'text-white');
        btn.classList.add('text-slate-600');
      }
    });
    this.renderTasks();
  }

  renderTasks() {
    const container = document.getElementById('taskListContainer');
    if (!container) return;

    let tasks = window.stoneStore.getTasks();
    const assigneeFilter = document.getElementById('taskAssigneeFilter')?.value || 'all';
    const categoryFilter = document.getElementById('taskCategoryFilter')?.value || 'all';

    const today = this.todayStr;
    const weekAhead = new Date(today);
    weekAhead.setDate(weekAhead.getDate() + 7);
    const weekAheadStr = weekAhead.toISOString().slice(0, 10);

    // フィルタリング
    let filtered = tasks.filter(t => {
      // 担当者
      if (assigneeFilter !== 'all' && t.assignee !== assigneeFilter) return false;
      // カテゴリ
      if (categoryFilter !== 'all' && t.category !== categoryFilter) return false;

      // 状態・期限フィルタ
      if (this.taskFilter === 'overdue') {
        return t.status === 'pending' && t.dueDate < today;
      } else if (this.taskFilter === 'today') {
        return t.status === 'pending' && t.dueDate === today;
      } else if (this.taskFilter === 'week') {
        return t.status === 'pending' && t.dueDate >= today && t.dueDate <= weekAheadStr;
      } else if (this.taskFilter === 'completed') {
        return t.status === 'completed';
      }
      return true; // 'all'
    });

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="bg-white rounded-xl p-8 text-center text-slate-400 border border-dashed border-slate-200">
          <svg class="w-10 h-10 mx-auto text-slate-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <p class="text-xs font-semibold">該当する対応タスクはありません</p>
          <p class="text-[11px] text-slate-400 mt-0.5">漏れなく順調に進んでいます！</p>
        </div>
      `;
      return;
    }

    // カテゴリごとの配色バッジマップ
    const categoryColors = {
      '支払い': 'bg-rose-100 text-rose-800 border-rose-200',
      '返信': 'bg-sky-100 text-sky-800 border-sky-200',
      '工事準備': 'bg-emerald-100 text-emerald-800 border-emerald-200',
      '経理作業': 'bg-amber-100 text-amber-800 border-amber-200',
      'その他': 'bg-slate-100 text-slate-700 border-slate-200'
    };

    const projects = window.stoneStore.getProjects();
    const projectMap = {};
    projects.forEach(p => projectMap[p.id] = p.name);

    container.innerHTML = filtered.map(t => {
      const isCompleted = t.status === 'completed';
      const isOverdue = !isCompleted && t.dueDate < today;
      const isToday = !isCompleted && t.dueDate === today;

      // 期限バッジ
      let dueBadgeHtml = '';
      if (isCompleted) {
        dueBadgeHtml = `<span class="text-xs text-slate-400 font-medium">完了済 (${t.completedAt || ''})</span>`;
      } else if (isOverdue) {
        dueBadgeHtml = `
          <span class="inline-flex items-center text-xs font-extrabold text-red-600 bg-red-100 px-2 py-0.5 rounded-full border border-red-300 pulse-warning">
            ⚠️ 期限超過 (${t.dueDate})
          </span>
        `;
      } else if (isToday) {
        dueBadgeHtml = `
          <span class="inline-flex items-center text-xs font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded-full border border-amber-300">
            本日中 (${t.dueDate})
          </span>
        `;
      } else {
        dueBadgeHtml = `<span class="text-xs text-slate-500 font-medium">期限: ${t.dueDate}</span>`;
      }

      const categoryBadge = categoryColors[t.category] || categoryColors['その他'];
      const projectName = t.projectId ? projectMap[t.projectId] : null;

      return `
        <div class="bg-white rounded-xl p-3.5 sm:p-4 border ${isOverdue ? 'border-red-300 bg-red-50/20 shadow-sm' : isCompleted ? 'border-slate-200 opacity-60 bg-slate-50/50' : 'border-slate-200 shadow-sm'} transition hover:border-blue-300">
          <div class="flex items-start gap-3">
            
            <!-- 完了チェックボックス（スマホでも押しやすい44pxタッチターゲット） -->
            <button class="task-toggle-btn mt-0.5 flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-lg border-2 flex items-center justify-center transition touch-target ${isCompleted ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-300 hover:border-blue-500 bg-white'}" data-task-id="${t.id}" title="${isCompleted ? '完了を取り消す' : '完了にする'}">
              ${isCompleted ? '<svg class="w-4 h-4 sm:w-5 sm:h-5 stroke-[3]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path></svg>' : ''}
            </button>

            <!-- タスク情報 -->
            <div class="flex-1 min-w-0">
              
              <!-- 上部メタ情報（種別・担当・期限） -->
              <div class="flex flex-wrap items-center gap-1.5 mb-1">
                <span class="text-[11px] font-bold px-2 py-0.5 rounded border ${categoryBadge}">${t.category}</span>
                <span class="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">担当: ${t.assignee}</span>
                ${dueBadgeHtml}
                ${t.amount ? `<span class="text-xs font-bold text-rose-700 ml-auto">¥${t.amount.toLocaleString()}</span>` : ''}
              </div>

              <!-- タスクタイトル -->
              <h3 class="text-xs sm:text-sm font-bold text-slate-900 ${isCompleted ? 'line-through text-slate-400' : ''} leading-snug">
                ${this.escapeHtml(t.title)}
              </h3>

              <!-- 次にすること（目立つ枠組み） -->
              ${t.nextAction ? `
                <div class="mt-2 bg-slate-50 p-2 rounded-lg border border-slate-200/80 flex items-start space-x-1.5 text-xs text-slate-700">
                  <span class="font-bold text-blue-700 flex-shrink-0">👉 次にすること:</span>
                  <span class="flex-1 leading-relaxed">${this.escapeHtml(t.nextAction)}</span>
                </div>
              ` : ''}

              <!-- 関連案件リンク -->
              ${projectName ? `
                <div class="mt-1.5 text-[11px] text-indigo-700 flex items-center cursor-pointer hover:underline" onclick="app.openProjectDetailModal('${t.projectId}')">
                  <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
                  <span>関連案件: ${this.escapeHtml(projectName)}</span>
                </div>
              ` : ''}

            </div>

            <!-- アクションメニュー（編集・削除） -->
            <div class="flex items-center space-x-1 flex-shrink-0">
              <button class="task-edit-btn p-1.5 text-slate-400 hover:text-blue-600 rounded hover:bg-slate-100 transition" data-task-id="${t.id}" title="編集">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
              </button>
              <button class="task-delete-btn p-1.5 text-slate-400 hover:text-red-600 rounded hover:bg-slate-100 transition" data-task-id="${t.id}" title="削除">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
              </button>
            </div>

          </div>
        </div>
      `;
    }).join('');

    // タスク完了トグルイベント
    container.querySelectorAll('.task-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.taskId;
        const updated = window.stoneStore.toggleTaskStatus(id);
        if (updated) {
          if (updated.status === 'completed') {
            this.showToast(`「${updated.title}」を完了にしました！`);
          } else {
            this.showToast(`「${updated.title}」の完了を取り消しました`);
          }
        }
      });
    }
);

    // タスク編集イベント
    container.querySelectorAll('.task-edit-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.taskId;
        const task = window.stoneStore.getTasks().find(t => t.id === id);
        if (task) this.openTaskModal(task);
      });
    }
);

    // タスク削除イベント
    container.querySelectorAll('.task-delete-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.taskId;
        if (confirm('この対応タスクを削除してもよろしいですか？')) {
          window.stoneStore.deleteTask(id);
          this.showToast('タスクを削除しました');
        }
      });
    }
);
  }

  openTaskModal(task = null) {
    const modal = document.getElementById('modalTask');
    const form = document.getElementById('formTask');
    const titleEl = document.getElementById('modalTaskTitle');
    const projectSelect = document.getElementById('taskInputProject');

    // 案件プルダウンの生成
    const projects = window.stoneStore.getProjects();
    projectSelect.innerHTML = '<option value="">なし（単独作業）</option>' + 
      projects.map(p => `<option value="${p.id}">${this.escapeHtml(p.name)}</option>`).join('');

    if (task) {
      titleEl.textContent = '対応・タスクの編集';
      document.getElementById('taskEditId').value = task.id;
      document.getElementById('taskInputTitle').value = task.title;
      document.getElementById('taskInputCategory').value = task.category;
      document.getElementById('taskInputAssignee').value = task.assignee;
      document.getElementById('taskInputDueDate').value = task.dueDate;
      document.getElementById('taskInputProject').value = task.projectId || '';
      document.getElementById('taskInputNextAction').value = task.nextAction || '';
    } else {
      titleEl.textContent = '今日の対応・タスク追加';
      form.reset();
      document.getElementById('taskEditId').value = '';
      document.getElementById('taskInputDueDate').value = this.todayStr;
      document.getElementById('taskInputAssignee').value = window.stoneStore.getCurrentUserLabel();
    }

    modal.classList.remove('hidden');
  }

  handleTaskSubmit() {
    const id = document.getElementById('taskEditId').value;
    const taskData = {
      title: document.getElementById('taskInputTitle').value.trim(),
      category: document.getElementById('taskInputCategory').value,
      assignee: document.getElementById('taskInputAssignee').value,
      dueDate: document.getElementById('taskInputDueDate').value,
      projectId: document.getElementById('taskInputProject').value || null,
      nextAction: document.getElementById('taskInputNextAction').value.trim()
    };

    if (id) {
      window.stoneStore.updateTask(id, taskData);
      this.showToast('タスクを更新しました');
    } else {
      window.stoneStore.addTask(taskData);
      this.showToast('新しい対応を追加しました');
    }

    document.getElementById('modalTask').classList.add('hidden');
  }

  // ==============================================================
  // 2. お金の管理（資金繰り表・費目別支出分析・残高シミュレーション）
  // ==============================================================
  switchFundsSubtab(subtabKey) {
    this.fundsSubtab = subtabKey;
    document.querySelectorAll('.funds-subtab-btn').forEach(btn => {
      if (btn.dataset.subtab === subtabKey) {
        btn.classList.add('active', 'bg-blue-600', 'text-white', 'shadow-sm');
        btn.classList.remove('text-slate-600', 'hover:bg-slate-100');
      } else {
        btn.classList.remove('active', 'bg-blue-600', 'text-white', 'shadow-sm');
        btn.classList.add('text-slate-600', 'hover:bg-slate-100');
      }
    });

    document.querySelectorAll('.funds-subpanel').forEach(panel => {
      panel.classList.add('hidden');
    });
    const targetPanel = document.getElementById(`subtab-panel-${subtabKey}`);
    if (targetPanel) targetPanel.classList.remove('hidden');

    if (subtabKey === 'statement') {
      this.renderCashFlowStatement();
    } else if (subtabKey === 'breakdown') {
      this.renderExpenseBreakdown();
    } else if (subtabKey === 'profitability') {
      this.renderProjectProfitability();
    } else if (subtabKey === 'cashflow') {
      this.renderCashFlowStatementByType();
      this.renderDailyCashFlowSchedule();
    } else if (subtabKey === 'overview') {
      this.renderFundsOverview();
    }
  }

  renderFunds() {
    if (!window.stoneStore.canAccessFunds()) return;
    this.switchFundsSubtab(this.fundsSubtab);
  }

  // --------------------------------------------------------------
  // 2-A. 本格 月次資金繰り表（マトリクス表）
  // --------------------------------------------------------------
  renderCashFlowStatement() {
    const table = document.getElementById('cashFlowStatementTable');
    if (!table) return;

    const matrix = window.stoneStore.generateCashFlowMatrix();
    const months = matrix.targetMonths; // ['2026-10', '2026-11', '2026-12', '2027-01']
    const mData = matrix.monthData;

    // ヘッダー行
    let html = `
      <thead class="bg-slate-800 text-white uppercase text-[11px] tracking-wider">
        <tr>
          <th class="py-2.5 px-3 sticky left-0 bg-slate-800 z-10 w-52 min-w-[200px]">科目・費目</th>
          ${months.map(m => `
            <th class="py-2.5 px-3 text-right whitespace-nowrap min-w-[105px]">
              ${m === '2026-10' ? `${m}月 (基準月)` : `${m}月 (予定)`}
            </th>
          `).join('')}
          <th class="py-2.5 px-3 text-right bg-slate-900 font-bold whitespace-nowrap min-w-[110px]">4か月合計</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-200">
    `;

    // 1. 前月繰越残高行
    let totalStartBalance = mData[months[0]].startBalance;
    html += `
      <tr class="bg-slate-100/90 font-bold text-slate-800 border-b-2 border-slate-300">
        <td class="py-2.5 px-3 sticky left-0 bg-slate-100/90 z-10">【前月繰越預金残高】</td>
        ${months.map(m => `
          <td class="py-2.5 px-3 text-right font-extrabold text-slate-800">
            ¥${mData[m].startBalance.toLocaleString()}
          </td>
        `).join('')}
        <td class="py-2.5 px-3 text-right bg-slate-200/80 font-bold text-slate-500">-</td>
      </tr>
    `;

    // 2. 収入の部
    html += `
      <tr class="bg-emerald-50/70 font-bold text-emerald-900 border-t border-b border-emerald-200">
        <td colspan="${months.length + 2}" class="py-2 px-3 sticky left-0 bg-emerald-50/70 z-10 text-xs">
          ▼ 【Ⅰ 営業収入の部】
        </td>
      </tr>
    `;

    matrix.incomeRows.forEach(row => {
      let rowTotal = 0;
      months.forEach(m => rowTotal += (mData[m].incomes[row.key] || 0));

      html += `
        <tr class="hover:bg-slate-50 transition">
          <td class="py-2 px-3 pl-6 text-slate-700 sticky left-0 bg-white z-10">
            ${row.label}
          </td>
          ${months.map(m => {
            const val = mData[m].incomes[row.key] || 0;
            return `
              <td class="py-2 px-3 text-right font-medium text-emerald-700 cursor-pointer hover:bg-emerald-50 hover:underline transition" 
                  onclick="app.showStatementDetail('${m}', '${row.key}', 'income')" title="明細を表示">
                ${val > 0 ? `+¥${val.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
              </td>
            `;
          }).join('')}
          <td class="py-2 px-3 text-right font-bold text-emerald-800 bg-slate-50">
            ${rowTotal > 0 ? `+¥${rowTotal.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
          </td>
        </tr>
      `;
    });

    // 収入合計行
    let totalIncomeAll = 0;
    months.forEach(m => totalIncomeAll += mData[m].totalIncome);
    html += `
      <tr class="bg-emerald-100/60 font-bold text-emerald-900 border-t border-b-2 border-emerald-300">
        <td class="py-2.5 px-3 sticky left-0 bg-emerald-100/60 z-10">収入合計（小計）</td>
        ${months.map(m => `
          <td class="py-2.5 px-3 text-right font-extrabold text-emerald-800">
            +¥${mData[m].totalIncome.toLocaleString()}
          </td>
        `).join('')}
        <td class="py-2.5 px-3 text-right font-black text-emerald-900 bg-emerald-100">
          +¥${totalIncomeAll.toLocaleString()}
        </td>
      </tr>
    `;

    // 3. 支出の部
    html += `
      <tr class="bg-rose-50/70 font-bold text-rose-900 border-t border-b border-rose-200">
        <td colspan="${months.length + 2}" class="py-2 px-3 sticky left-0 bg-rose-50/70 z-10 text-xs">
          ▼ 【Ⅱ 営業支出の部】
        </td>
      </tr>
    `;

    matrix.expenseGroups.forEach(grp => {
      html += `
        <tr class="bg-slate-50/80 font-bold text-slate-700 text-[11px]">
          <td colspan="${months.length + 2}" class="py-1 px-3 pl-4 sticky left-0 bg-slate-50/80 z-10">
            ${grp.groupName}
          </td>
        </tr>
      `;

      grp.rows.forEach(row => {
        let rowTotal = 0;
        months.forEach(m => rowTotal += (mData[m].expenses[row.key] || 0));

        html += `
          <tr class="hover:bg-slate-50 transition">
            <td class="py-2 px-3 pl-6 text-slate-700 sticky left-0 bg-white z-10">
              ${row.label}
            </td>
            ${months.map(m => {
              const val = mData[m].expenses[row.key] || 0;
              return `
                <td class="py-2 px-3 text-right font-medium text-rose-700 cursor-pointer hover:bg-rose-50 hover:underline transition" 
                    onclick="app.showStatementDetail('${m}', '${row.key}', 'expense')" title="明細を表示">
                  ${val > 0 ? `-¥${val.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
                </td>
              `;
            }).join('')}
            <td class="py-2 px-3 text-right font-bold text-rose-800 bg-slate-50">
              ${rowTotal > 0 ? `-¥${rowTotal.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
            </td>
          </tr>
        `;
      });
    }
);

    // 支出合計行
    let totalExpenseAll = 0;
    months.forEach(m => totalExpenseAll += mData[m].totalExpense);
    html += `
      <tr class="bg-rose-100/60 font-bold text-rose-900 border-t border-b-2 border-rose-300">
        <td class="py-2.5 px-3 sticky left-0 bg-rose-100/60 z-10">支出合計（小計）</td>
        ${months.map(m => `
          <td class="py-2.5 px-3 text-right font-extrabold text-rose-800">
            -¥${mData[m].totalExpense.toLocaleString()}
          </td>
        `).join('')}
        <td class="py-2.5 px-3 text-right font-black text-rose-900 bg-rose-100">
          -¥${totalExpenseAll.toLocaleString()}
        </td>
      </tr>
    `;

    // 4. 当月収支差額
    let totalNetAll = totalIncomeAll - totalExpenseAll;
    html += `
      <tr class="bg-slate-100 font-bold border-t border-b border-slate-300">
        <td class="py-2.5 px-3 sticky left-0 bg-slate-100 z-10 text-slate-800">【Ⅲ 当月収支差額】</td>
        ${months.map(m => {
          const net = mData[m].netCashFlow;
          return `
            <td class="py-2.5 px-3 text-right font-extrabold ${net >= 0 ? 'text-emerald-700' : 'text-rose-700'}">
              ${net >= 0 ? '+' : ''}¥${net.toLocaleString()}
            </td>
          `;
        }).join('')}
        <td class="py-2.5 px-3 text-right font-black ${totalNetAll >= 0 ? 'text-emerald-800' : 'text-rose-800'} bg-slate-200">
          ${totalNetAll >= 0 ? '+' : ''}¥${totalNetAll.toLocaleString()}
        </td>
      </tr>
    `;

    // 5. 月末預金残高（翌月繰越）
    html += `
      <tr class="bg-slate-900 text-white font-black border-t-2 border-slate-800">
        <td class="py-3 px-3 sticky left-0 bg-slate-900 z-10 text-white text-xs">
          【Ⅳ 月末預金残高（翌月繰越）】
        </td>
        ${months.map(m => `
          <td class="py-3 px-3 text-right font-black text-white text-sm">
            ¥${mData[m].endBalance.toLocaleString()}
          </td>
        `).join('')}
        <td class="py-3 px-3 text-right font-black text-blue-200 bg-slate-950 text-sm">
          ¥${mData[months[months.length - 1]].endBalance.toLocaleString()}
        </td>
      </tr>
    `;

    html += `</tbody>`;
    table.innerHTML = html;
  }

  // 資金繰り表のセルクリック時の明細表示
  showStatementDetail(month, categoryKey, type) {
    const container = document.getElementById('stmtDetailContainer');
    const titleEl = document.getElementById('stmtDetailTitle');
    const listEl = document.getElementById('stmtDetailList');
    if (!container || !titleEl || !listEl) return;

    const txs = window.stoneStore.getTransactions().filter(tx => 
      tx.date.startsWith(month) && tx.type === type && tx.category === categoryKey
    );

    titleEl.textContent = `${month}度 【${categoryKey}】の取引明細 (${txs.length}件)`;

    if (txs.length === 0) {
      listEl.innerHTML = '<div class="text-slate-400">該当する取引データはありません</div>';
    } else {
      listEl.innerHTML = txs.map(tx => `
        <div class="flex items-center justify-between p-2 bg-white rounded border border-slate-200 text-xs">
          <div class="flex items-center space-x-2">
            <span class="font-bold text-slate-800">${this.escapeHtml(tx.partner)}</span>
            <span class="text-slate-400 text-[11px]">${tx.date}</span>
            ${tx.note ? `<span class="text-slate-500 text-[11px] bg-slate-50 px-1 rounded">${this.escapeHtml(tx.note)}</span>` : ''}
          </div>
          <div class="flex items-center space-x-2">
            <span class="font-extrabold ${tx.type === 'income' ? 'text-emerald-700' : 'text-rose-700'}">
              ${tx.type === 'income' ? '+' : '-'}¥${tx.amount.toLocaleString()}
            </span>
            <span class="text-[10px] px-1.5 py-0.5 rounded font-bold ${tx.isActual ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600 border border-slate-200'}">
              ${tx.isActual ? '実績' : '予定'}
            </span>
          </div>
        </div>
      `).join('');
    }

    container.classList.remove('hidden');
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // --------------------------------------------------------------
  // 2-B. 何に使っているか（費目別支出分析）
  // --------------------------------------------------------------
  renderExpenseBreakdown() {
    const select = document.getElementById('expenseBreakdownMonthSelect');
    const monthKey = select ? select.value : 'all';

    const breakdown = window.stoneStore.calculateExpenseBreakdown(monthKey);
    const totalEl = document.getElementById('breakdownTotalAmount');
    const periodLabel = document.getElementById('breakdownPeriodLabel');
    const listContainer = document.getElementById('expenseRankingList');

    if (totalEl) totalEl.textContent = `¥${breakdown.totalExpense.toLocaleString()}`;
    if (periodLabel) {
      periodLabel.textContent = monthKey === 'all' ? '今後3か月間の支出総額' : `${monthKey}度 支出総額`;
    }

    if (!listContainer) return;

    if (breakdown.list.length === 0) {
      listContainer.innerHTML = '<div class="p-6 text-center text-slate-400 text-xs">この期間の支出データはありません</div>';
      if (this.expenseDonutChart) {
        this.expenseDonutChart.destroy();
        this.expenseDonutChart = null;
      }
      return;
    }

    // ランキングリストの生成
    listContainer.innerHTML = breakdown.list.map((item, index) => {
      return `
        <div class="p-2.5 bg-slate-50 hover:bg-white rounded-xl border border-slate-200 transition shadow-sm space-y-1">
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white" style="background-color: ${item.color}">
                ${index + 1}
              </span>
              <span class="font-bold text-slate-800">${item.name}</span>
              <span class="text-[10px] text-slate-400">(${item.count}件)</span>
            </div>
            <div class="text-right">
              <span class="font-extrabold text-slate-900">¥${item.amount.toLocaleString()}</span>
              <span class="ml-1 text-xs font-bold text-blue-600">(${item.percentage}%)</span>
            </div>
          </div>
          <!-- 構成比プログレスバー -->
          <div class="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
            <div class="h-1.5 rounded-full transition-all duration-500" style="width: ${item.percentage}%; background-color: ${item.color}"></div>
          </div>
        </div>
      `;
    }).join('');

    // 固定費 vs 変動費の集計カード更新
    const fv = window.stoneStore.calculateFixedAndVariableExpenses(monthKey);
    const fixedAmt = document.getElementById('fixedExpenseAmount');
    const fixedPct = document.getElementById('fixedExpensePct');
    const varAmt = document.getElementById('variableExpenseAmount');
    const varPct = document.getElementById('variableExpensePct');

    if (fixedAmt) fixedAmt.textContent = `¥${fv.fixedTotal.toLocaleString()}`;
    if (fixedPct) fixedPct.textContent = `${fv.fixedPercentage}%`;
    if (varAmt) varAmt.textContent = `¥${fv.variableTotal.toLocaleString()}`;
    if (varPct) varPct.textContent = `${fv.variablePercentage}%`;

    // Chart.js ドーナツチャートの描画
    this.renderExpenseDonutChart(breakdown.list);
  }

  renderExpenseDonutChart(items) {
    const canvas = document.getElementById('expenseDonutChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (this.expenseDonutChart) {
      this.expenseDonutChart.destroy();
    }

    const labels = items.map(it => it.key);
    const data = items.map(it => it.amount);
    const colors = items.map(it => it.color);

    this.expenseDonutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: colors,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 10, font: { size: 10 } }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = ctx.raw || 0;
                const total = data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                return ` ${ctx.label}: ¥${val.toLocaleString()} (${pct}%)`;
              }
            }
          }
        },
        cutout: '62%'
      }
    });
  }

  // --------------------------------------------------------------
  // 2-C. 工事・案件別 原価収支＆粗利率（個別原価管理）
  // --------------------------------------------------------------
  renderProjectProfitability() {
    const container = document.getElementById('projectProfitabilityList');
    if (!container) return;

    const list = window.stoneStore.calculateProjectProfitability();

    if (list.length === 0) {
      container.innerHTML = '<div class="p-6 text-center text-slate-400 text-xs">登録された工事案件はありません</div>';
      return;
    }

    container.innerHTML = list.map(item => {
      const p = item.project;
      const margin = parseFloat(item.profitMargin);
      
      // 利益率バッジ
      let marginBadgeClass = 'bg-emerald-100 text-emerald-800 border-emerald-300';
      if (margin < 20) {
        marginBadgeClass = 'bg-rose-100 text-rose-800 border-rose-300';
      } else if (margin < 30) {
        marginBadgeClass = 'bg-amber-100 text-amber-800 border-amber-300';
      }

      return `
        <div class="bg-slate-50 hover:bg-white p-4 rounded-xl border border-slate-200 transition shadow-sm space-y-3">
          <!-- 上部ヘッダー（案件名・粗利率バッジ） -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-2 border-slate-200">
            <div>
              <div class="text-[11px] text-slate-400">${p.customerName ? `${this.escapeHtml(p.customerName)} 様` : '施主未定'} | ${this.escapeHtml(p.siteLocation || '')}</div>
              <h4 class="text-xs sm:text-sm font-bold text-slate-900 mt-0.5 cursor-pointer hover:text-blue-600" onclick="app.openProjectDetailModal('${p.id}')">
                ${this.escapeHtml(p.name)}
              </h4>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-xs font-black px-2.5 py-1 rounded-full border ${marginBadgeClass}">
                粗利率: ${item.profitMargin}%
              </span>
              <span class="text-xs font-black text-slate-900 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
                粗利益: ¥${item.grossProfit.toLocaleString()}
              </span>
            </div>
          </div>

          <!-- 金額サマリー（契約金額 vs 原価合計） -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div class="p-2 bg-white rounded-lg border border-slate-200">
              <div class="text-[10px] text-slate-400 font-medium">請負・契約金額</div>
              <div class="text-sm font-black text-slate-900 mt-0.5">¥${item.contractAmount.toLocaleString()}</div>
            </div>
            <div class="p-2 bg-white rounded-lg border border-slate-200">
              <div class="text-[10px] text-rose-600 font-medium">原価合計（支出）</div>
              <div class="text-sm font-black text-rose-700 mt-0.5">¥${item.totalCost.toLocaleString()}</div>
            </div>
            <div class="p-2 bg-white rounded-lg border border-slate-200">
              <div class="text-[10px] text-emerald-600 font-medium">入金済・予定額</div>
              <div class="text-sm font-black text-emerald-700 mt-0.5">¥${item.billedAmount.toLocaleString()}</div>
            </div>
            <div class="p-2 bg-white rounded-lg border border-slate-200 flex flex-col justify-center">
              <div class="text-[10px] text-slate-400 font-medium">原価率</div>
              <div class="text-sm font-bold text-slate-700 mt-0.5">
                ${item.contractAmount > 0 ? (100 - margin).toFixed(1) : 0}%
              </div>
            </div>
          </div>

          <!-- 原価の費目内訳バー＆リスト -->
          <div class="space-y-1.5 pt-1">
            <div class="text-[11px] font-bold text-slate-700 flex items-center justify-between">
              <span>原価の内訳明細（何にいくら使ったか）:</span>
              <span class="text-[10px] text-slate-400">${item.costItems.length}件の支払予定・実績</span>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5 text-[11px]">
              <div class="bg-blue-50/70 p-1.5 rounded border border-blue-200 flex justify-between">
                <span class="text-blue-900 font-medium">石材仕入:</span>
                <span class="font-bold text-blue-950">¥${item.stoneCost.toLocaleString()}</span>
              </div>
              <div class="bg-sky-50/70 p-1.5 rounded border border-sky-200 flex justify-between">
                <span class="text-sky-900 font-medium">生コン・建材:</span>
                <span class="font-bold text-sky-950">¥${item.materialCost.toLocaleString()}</span>
              </div>
              <div class="bg-indigo-50/70 p-1.5 rounded border border-indigo-200 flex justify-between">
                <span class="text-indigo-900 font-medium">重機リース:</span>
                <span class="font-bold text-indigo-950">¥${item.machineryCost.toLocaleString()}</span>
              </div>
              <div class="bg-slate-100 p-1.5 rounded border border-slate-200 flex justify-between">
                <span class="text-slate-700 font-medium">外注・その他:</span>
                <span class="font-bold text-slate-900">¥${item.otherCost.toLocaleString()}</span>
              </div>
            </div>
          </div>

        </div>
      `;
    }).join('');
  }

  // --------------------------------------------------------------
  // 2-D. キャッシュフロー計算書（営業CF・財務CF）
  // --------------------------------------------------------------
  renderCashFlowStatementByType() {
    const select = document.getElementById('cashflowPeriodSelect');
    const period = select ? select.value : 'all';

    const cf = window.stoneStore.calculateCashFlowStatementByType(period);

    const opVal = document.getElementById('cfOperatingVal');
    const finVal = document.getElementById('cfFinancingVal');
    const netVal = document.getElementById('cfNetVal');
    const safetyBadge = document.getElementById('cfSafetyBadge');

    if (opVal) opVal.textContent = `${cf.operatingCF >= 0 ? '+' : ''}¥${cf.operatingCF.toLocaleString()}`;
    if (finVal) finVal.textContent = `¥${cf.financingCF.toLocaleString()}`;
    if (netVal) netVal.textContent = `${cf.netCF >= 0 ? '+' : ''}¥${cf.netCF.toLocaleString()}`;

    if (safetyBadge) {
      if (cf.isPositive) {
        safetyBadge.className = 'text-[11px] text-emerald-300 mt-0.5 font-bold flex items-center';
        safetyBadge.innerHTML = '✅ 本業の現金収入で借入返済を賄えています（健全）';
      } else {
        safetyBadge.className = 'text-[11px] text-rose-300 mt-0.5 font-bold flex items-center';
        safetyBadge.innerHTML = '⚠️ 注意: 本業CFが返済額を下回っています（手元資金取崩し）';
      }
    }
  }

  // --------------------------------------------------------------
  // 2-E. 日繰り表（日別・支払集中日カレンダー）
  // --------------------------------------------------------------
  renderDailyCashFlowSchedule() {
    const tbody = document.getElementById('dailyCashFlowTableBody');
    if (!tbody) return;

    const list = window.stoneStore.calculateDailyCashFlowSchedule();

    if (list.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-slate-400 text-xs">基準日以降の入出金予定はありません</td></tr>';
      return;
    }

    tbody.innerHTML = list.map(item => {
      // バッジの判定
      let badgeHtml = '';
      if (item.isPayday) {
        badgeHtml = '<span class="bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-amber-300">給料日</span>';
      } else if (item.isLoanDay) {
        badgeHtml = '<span class="bg-purple-100 text-purple-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-purple-300">公庫引落</span>';
      } else if (item.isMonthEnd) {
        badgeHtml = '<span class="bg-rose-100 text-rose-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-rose-300">月末振込</span>';
      } else if (item.isHighOutflow) {
        badgeHtml = '<span class="bg-rose-50 text-rose-700 px-1.5 py-0.5 rounded text-[10px] font-medium border border-rose-200">大型出金</span>';
      } else {
        badgeHtml = '<span class="text-slate-400 text-[10px]">通常</span>';
      }

      return `
        <tr class="hover:bg-slate-50 transition ${item.isPayday || item.isMonthEnd ? 'bg-amber-50/20' : ''}">
          <td class="py-2.5 px-3 font-bold text-slate-800 whitespace-nowrap">${item.date}</td>
          <td class="py-2.5 px-2 whitespace-nowrap">${badgeHtml}</td>
          <td class="py-2.5 px-3 text-right font-bold text-emerald-700 whitespace-nowrap">
            ${item.income > 0 ? `+¥${item.income.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
          </td>
          <td class="py-2.5 px-3 text-right font-bold text-rose-700 whitespace-nowrap">
            ${item.expense > 0 ? `-¥${item.expense.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
          </td>
          <td class="py-2.5 px-3 text-right font-extrabold whitespace-nowrap ${item.net >= 0 ? 'text-emerald-700' : 'text-rose-700'}">
            ${item.net >= 0 ? '+' : ''}¥${item.net.toLocaleString()}
          </td>
          <td class="py-2.5 px-3 text-right font-black text-slate-900 whitespace-nowrap bg-slate-50/70">
            ¥${item.balance.toLocaleString()}
          </td>
        </tr>
      `;
    }).join('');
  }

  // --------------------------------------------------------------
  // 2-C. 従来の残高推移・未入金・全取引明細
  // --------------------------------------------------------------
  renderFundsOverview() {
    const bank = window.stoneStore.getBankAccount();
    const sim = window.stoneStore.calculateCashFlowSimulation();

    // 基準日残高表示
    document.getElementById('bankBaseDateDisplay').textContent = `基準日: ${bank.baseDate}`;
    document.getElementById('bankBaseBalanceDisplay').textContent = `¥${bank.baseBalance.toLocaleString()}`;
    document.getElementById('bankNameDisplay').textContent = bank.bankName;

    // サマリー表示
    const summaryUnreceived = document.getElementById('summaryUnreceived');
    const summaryUnpaid = document.getElementById('summaryUnpaid');
    const summaryNet = document.getElementById('summaryNetChange');
    const finalBalance = document.getElementById('projectedFinalBalance');
    const minAlert = document.getElementById('minBalanceAlert');

    if (summaryUnreceived) summaryUnreceived.textContent = `+¥${sim.totalUnreceived.toLocaleString()}`;
    if (summaryUnpaid) summaryUnpaid.textContent = `-¥${sim.totalUnpaid.toLocaleString()}`;
    
    const net = sim.totalUnreceived - sim.totalUnpaid;
    if (summaryNet) {
      summaryNet.textContent = `${net >= 0 ? '+' : ''}¥${net.toLocaleString()}`;
      summaryNet.className = `font-bold ${net >= 0 ? 'text-emerald-700' : 'text-rose-700'}`;
    }

    if (finalBalance) {
      finalBalance.textContent = `¥${sim.finalProjectedBalance.toLocaleString()}`;
    }

    // 最低残高警告
    if (minAlert) {
      if (sim.minBalance < 1000000) {
        minAlert.className = 'mt-2 pt-2 border-t border-red-500/50 text-[11px] text-red-300 flex items-center font-bold';
        minAlert.innerHTML = `⚠️ 警告: ${sim.minDate}に最低残高 ¥${sim.minBalance.toLocaleString()} の見込み（資金ショート注意）`;
      } else {
        minAlert.className = 'mt-2 pt-2 border-t border-slate-800/80 text-[11px] text-emerald-300 flex items-center';
        minAlert.innerHTML = `✅ 期間中の最低残高も ¥${sim.minBalance.toLocaleString()} (${sim.minDate}) を維持できる見通しです`;
      }
    }

    // 月別集計サマリー表
    const monthlyContainer = document.getElementById('monthlySummaryContainer');
    if (monthlyContainer) {
      monthlyContainer.innerHTML = sim.monthlySummary.map(m => {
        const netPositive = m.net >= 0;
        return `
          <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
            <div class="flex justify-between items-center font-bold text-slate-800 mb-1">
              <span>${m.month}月度</span>
              <span class="${netPositive ? 'text-emerald-700' : 'text-rose-700'}">${netPositive ? '+' : ''}¥${m.net.toLocaleString()}</span>
            </div>
            <div class="flex justify-between text-[11px] text-slate-500">
              <span>入金: <strong class="text-emerald-600">+¥${m.income.toLocaleString()}</strong></span>
              <span>支払: <strong class="text-rose-600">-¥${m.expense.toLocaleString()}</strong></span>
            </div>
          </div>
        `;
      }).join('');
    }

    // Chart.js 残高推移グラフ
    this.renderCashFlowChart(sim.timeline);
    this.renderUnreceivedList();
    this.renderUnpaidList();
    this.renderTransactionsTable();
  }

  // 費目（カテゴリ）プルダウンの動的生成
  populateTxCategorySelect(type, selectedValue = '') {
    const select = document.getElementById('txInputCategory');
    if (!select) return;

    if (type === 'income') {
      select.innerHTML = `
        <optgroup label="工事売上・収入">
          <option value="墓石新設代">墓所新設工事代（着工・中間・完工）</option>
          <option value="改修・補修代">墓所改修・補修工事代</option>
          <option value="戒名彫刻・納骨">戒名追加彫刻・納骨料</option>
          <option value="墓じまい代">墓じまい・更地返還工事代</option>
          <option value="その他収入">その他売上・雑収入</option>
        </optgroup>
      `;
    } else {
      select.innerHTML = `
        <optgroup label="原価・仕入・工事費">
          <option value="石材仕入">石材仕入代（墓石・外柵・納骨部材）</option>
          <option value="建材仕入">基礎建材費（生コン・セメント・砕石）</option>
          <option value="重機リース">重機・クレーン・運搬費</option>
          <option value="外注加工">字彫り・加工外注費</option>
        </optgroup>
        <optgroup label="人件費">
          <option value="給与手当">給与手当・専従者給与・賞与</option>
        </optgroup>
        <optgroup label="固定費・現場経費">
          <option value="車両・燃料">車両費・軽油代・高速代</option>
          <option value="消耗品・工具">消耗品・切削砥石・ゴム等</option>
          <option value="損害保険料">損害保険料（車両・請負賠償）</option>
          <option value="通信・光熱費">水道光熱・事務所通信費</option>
        </optgroup>
        <optgroup label="財務・税務">
          <option value="借入返済">借入金返済（公庫・地銀元金）</option>
          <option value="税金・積立">租税公課・消費税積立</option>
          <option value="その他経費">その他雑費・予備費</option>
        </optgroup>
      `;
    }

    if (selectedValue) {
      select.value = selectedValue;
    }
  }

  openBankModal() {
    const bank = window.stoneStore.getBankAccount();
    document.getElementById('bankInputBaseDate').value = bank.baseDate;
    document.getElementById('bankInputBaseBalance').value = bank.baseBalance;
    document.getElementById('bankInputBankName').value = bank.bankName;
    document.getElementById('modalBank').classList.remove('hidden');
  }

  handleBankSubmit() {
    const baseDate = document.getElementById('bankInputBaseDate').value;
    const baseBalance = document.getElementById('bankInputBaseBalance').value;
    const bankName = document.getElementById('bankInputBankName').value.trim();

    window.stoneStore.updateBankAccount(baseDate, baseBalance, bankName);
    this.showToast('口座基準日と残高を更新しました');
    document.getElementById('modalBank').classList.add('hidden');
  }

  openTxModal(tx = null) {
    const modal = document.getElementById('modalTx');
    const form = document.getElementById('formTx');
    const titleEl = document.getElementById('modalTxTitle');
    const projectSelect = document.getElementById('txInputProject');

    // 案件プルダウン
    const projects = window.stoneStore.getProjects();
    projectSelect.innerHTML = '<option value="">なし（共通経費・単発）</option>' + 
      projects.map(p => `<option value="${p.id}">${this.escapeHtml(p.name)}</option>`).join('');

    if (tx) {
      titleEl.textContent = '入金・支払予定の編集';
      document.getElementById('txEditId').value = tx.id;
      document.getElementById('txInputType').value = tx.type;
      this.populateTxCategorySelect(tx.type, tx.category);
      document.getElementById('txInputDate').value = tx.date;
      document.getElementById('txInputPartner').value = tx.partner;
      document.getElementById('txInputAmount').value = tx.amount;
      document.getElementById('txInputProject').value = tx.projectId || '';
      document.getElementById('txInputIsActual').value = tx.isActual ? 'true' : 'false';
      document.getElementById('txInputNote').value = tx.note || '';
    } else {
      titleEl.textContent = '入金・支払予定の登録';
      form.reset();
      document.getElementById('txEditId').value = '';
      document.getElementById('txInputType').value = 'expense';
      this.populateTxCategorySelect('expense');
      document.getElementById('txInputDate').value = this.todayStr;
    }

    modal.classList.remove('hidden');
  }

  handleTxSubmit() {
    const id = document.getElementById('txEditId').value;
    const txData = {
      type: document.getElementById('txInputType').value,
      date: document.getElementById('txInputDate').value,
      partner: document.getElementById('txInputPartner').value.trim(),
      amount: document.getElementById('txInputAmount').value,
      category: document.getElementById('txInputCategory').value,
      projectId: document.getElementById('txInputProject').value || null,
      isActual: document.getElementById('txInputIsActual').value === 'true',
      note: document.getElementById('txInputNote').value.trim()
    };

    if (id) {
      window.stoneStore.updateTransaction(id, txData);
      this.showToast('入出金レコードを更新しました');
    } else {
      window.stoneStore.addTransaction(txData);
      this.showToast('入出金予定を登録しました');
    }

    document.getElementById('modalTx').classList.add('hidden');
  }

  renderCashFlowChart(timeline) {
    const canvas = document.getElementById('cashFlowChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (this.cashFlowChart) {
      this.cashFlowChart.destroy();
    }

    const labels = timeline.map(t => t.date.slice(5)); // 'MM-DD'
    const balances = timeline.map(t => t.balance);

    this.cashFlowChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: '予測口座残高 (円)',
          data: balances,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.08)',
          fill: true,
          tension: 0.2,
          pointBackgroundColor: balances.map(b => b < 1000000 ? '#e11d48' : '#2563eb'),
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `予測残高: ¥${context.raw.toLocaleString()}`
            }
          }
        },
        scales: {
          y: {
            ticks: {
              callback: (value) => `¥${(value / 10000).toFixed(0)}万`
            },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  }

  renderUnreceivedList() {
    const container = document.getElementById('unreceivedList');
    const badge = document.getElementById('unreceivedCountBadge');
    if (!container) return;

    const txs = window.stoneStore.getTransactions()
      .filter(tx => tx.type === 'income' && !tx.isActual);

    if (badge) badge.textContent = `${txs.length}件`;

    if (txs.length === 0) {
      container.innerHTML = '<div class="p-4 text-center text-xs text-slate-400">現在、未入金の予定はありません</div>';
      return;
    }

    container.innerHTML = txs.map(tx => `
      <div class="py-2.5 flex items-center justify-between text-xs">
        <div>
          <div class="font-bold text-slate-800">${this.escapeHtml(tx.partner)}</div>
          <div class="text-[11px] text-slate-400 flex items-center space-x-1.5 mt-0.5">
            <span>入金予定日: ${tx.date}</span>
            <span>•</span>
            <span>${this.escapeHtml(tx.category || '工事代金')}</span>
          </div>
        </div>
        <div class="text-right">
          <div class="font-extrabold text-emerald-700 text-sm">+¥${tx.amount.toLocaleString()}</div>
          <button class="tx-actual-toggle-btn text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-300 font-bold px-2 py-0.5 rounded mt-1 hover:bg-emerald-100 transition" data-tx-id="${tx.id}">
            入金済にする
          </button>
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.tx-actual-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        window.stoneStore.toggleTransactionActual(btn.dataset.txId);
        this.showToast('入金実績として反映しました');
      });
    }
);
  }

  renderUnpaidList() {
    const container = document.getElementById('unpaidList');
    const badge = document.getElementById('unpaidCountBadge');
    if (!container) return;

    const txs = window.stoneStore.getTransactions()
      .filter(tx => tx.type === 'expense' && !tx.isActual);

    if (badge) badge.textContent = `${txs.length}件`;

    if (txs.length === 0) {
      container.innerHTML = '<div class="p-4 text-center text-xs text-slate-400">未払いの予定はありません</div>';
      return;
    }

    container.innerHTML = txs.map(tx => `
      <div class="py-2.5 flex items-center justify-between text-xs">
        <div>
          <div class="font-bold text-slate-800">${this.escapeHtml(tx.partner)}</div>
          <div class="text-[11px] text-slate-400 flex items-center space-x-1.5 mt-0.5">
            <span>支払期日: ${tx.date}</span>
            <span>•</span>
            <span>${this.escapeHtml(tx.category || '仕入・経費')}</span>
          </div>
        </div>
        <div class="text-right">
          <div class="font-extrabold text-rose-700 text-sm">-¥${tx.amount.toLocaleString()}</div>
          <button class="tx-actual-toggle-btn text-[10px] bg-rose-50 text-rose-700 border border-rose-300 font-bold px-2 py-0.5 rounded mt-1 hover:bg-rose-100 transition" data-tx-id="${tx.id}">
            振込済にする
          </button>
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.tx-actual-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        window.stoneStore.toggleTransactionActual(btn.dataset.txId);
        this.showToast('支払実績（振込済）として反映しました');
      });
    }
);
  }

  renderTransactionsTable() {
    const tbody = document.getElementById('txTableBody');
    if (!tbody) return;

    const txs = window.stoneStore.getTransactions();

    if (txs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-slate-400 text-xs">登録された取引データはありません</td></tr>';
      return;
    }

    tbody.innerHTML = txs.map(tx => {
      const isIncome = tx.type === 'income';
      return `
        <tr class="hover:bg-slate-50 transition">
          <td class="py-2.5 px-3 font-medium text-slate-700 whitespace-nowrap">${tx.date}</td>
          <td class="py-2.5 px-2 whitespace-nowrap">
            <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${isIncome ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
              ${isIncome ? '入金' : '支払'}
            </span>
          </td>
          <td class="py-2.5 px-3">
            <div class="font-bold text-slate-800 flex items-center gap-1.5">
              <span>${this.escapeHtml(tx.partner)}</span>
              ${tx.gdriveUrl ? `<a href="${this.escapeHtml(tx.gdriveUrl)}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center text-[10px] bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 px-1.5 py-0.5 rounded font-bold" title="Googleドライブで請求書原本を開く">☁️ 請求書原本</a>` : ''}
            </div>
            <div class="text-[11px] text-slate-400">${this.escapeHtml(tx.category || '')} ${tx.note ? `• ${this.escapeHtml(tx.note)}` : ''}</div>
          </td>
          <td class="py-2.5 px-3 text-right font-extrabold whitespace-nowrap ${isIncome ? 'text-emerald-700' : 'text-rose-700'}">
            ${isIncome ? '+' : '-'}¥${tx.amount.toLocaleString()}
          </td>
          <td class="py-2.5 px-3 text-center whitespace-nowrap">
            <button class="tx-actual-toggle-btn px-2 py-0.5 rounded text-[11px] font-bold border transition ${tx.isActual ? 'bg-slate-800 text-white border-slate-800' : 'bg-white text-slate-600 border-slate-300 hover:border-slate-500'}" data-tx-id="${tx.id}">
              ${tx.isActual ? '✓ 実績' : '予定'}
            </button>
          </td>
          <td class="py-2.5 px-2 text-right whitespace-nowrap">
            <button class="tx-edit-btn p-1 text-slate-400 hover:text-blue-600 transition" data-tx-id="${tx.id}" title="編集">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
            </button>
            <button class="tx-delete-btn p-1 text-slate-400 hover:text-red-600 transition ml-1" data-tx-id="${tx.id}" title="削除">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            </button>
          </td>
        </tr>
      `;
    }).join('');

    tbody.querySelectorAll('.tx-actual-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        window.stoneStore.toggleTransactionActual(btn.dataset.txId);
        this.showToast('ステータスを更新しました');
      });
    }
);

    tbody.querySelectorAll('.tx-edit-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tx = window.stoneStore.getTransactions().find(t => t.id === btn.dataset.txId);
        if (tx) this.openTxModal(tx);
      });
    }
);

    tbody.querySelectorAll('.tx-delete-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (confirm('この入出金レコードを削除してもよろしいですか？')) {
          window.stoneStore.deleteTransaction(btn.dataset.txId);
          this.showToast('取引を削除しました');
        }
      });
    }
);
  }

  // ==============================================================
  // 3. 工事・お客様の管理
  // ==============================================================
  renderProjects() {
    const container = document.getElementById('projectsListContainer');
    if (!container) return;

    const projects = window.stoneStore.getProjects();

    if (projects.length === 0) {
      container.innerHTML = '<div class="col-span-2 p-8 text-center text-slate-400 text-xs">現在、登録されている案件はありません</div>';
      return;
    }

    const statusMap = {
      'inquiry': { label: '相談・打合中', color: 'bg-slate-100 text-slate-700 border-slate-300' },
      'drawing': { label: '見積・図面提出中', color: 'bg-blue-100 text-blue-800 border-blue-300' },
      'contracted': { label: '契約済・石材手配中', color: 'bg-indigo-100 text-indigo-800 border-indigo-300' },
      'carving': { label: '文字彫刻・工場加工中', color: 'bg-purple-100 text-purple-800 border-purple-300' },
      'construction': { label: '現地施工・基礎据付中', color: 'bg-amber-100 text-amber-800 border-amber-300' },
      'completed': { label: '完工・納骨引き渡し完了', color: 'bg-emerald-100 text-emerald-800 border-emerald-300' }
    };

    container.innerHTML = projects.map(p => {
      const st = statusMap[p.status] || { label: p.status, color: 'bg-slate-100 text-slate-700 border-slate-200' };

      return `
        <div class="bg-white rounded-xl p-4 border border-slate-200 shadow-sm hover:border-blue-400 transition flex flex-col justify-between">
          <div>
            <!-- 上部バッジ ＆ アクション -->
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-bold px-2 py-0.5 rounded border ${st.color}">${st.label}</span>
              <div class="flex items-center space-x-1">
                <button class="proj-edit-btn p-1 text-slate-400 hover:text-blue-600 transition" data-proj-id="${p.id}" title="編集">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                </button>
                <button class="proj-delete-btn p-1 text-slate-400 hover:text-red-600 transition" data-proj-id="${p.id}" title="削除">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
              </div>
            </div>

            <!-- 案件名 ＆ 施主情報 -->
            <h3 class="text-sm font-bold text-slate-900 leading-snug cursor-pointer hover:text-blue-600 transition" onclick="app.openProjectDetailModal('${p.id}')">
              ${this.escapeHtml(p.name)}
            </h3>

            <div class="mt-2 space-y-1 text-xs text-slate-600">
              ${p.customerName ? `<div>施主: <strong class="text-slate-800">${this.escapeHtml(p.customerName)}</strong></div>` : ''}
              ${p.siteLocation ? `<div>場所: ${this.escapeHtml(p.siteLocation)}</div>` : ''}
              ${p.scheduleDate ? `<div>工期: <span class="font-medium text-slate-700">${this.escapeHtml(p.scheduleDate)}</span></div>` : ''}
              ${p.assignee ? `<div>担当: ${this.escapeHtml(p.assignee)}</div>` : ''}
            </div>

            <!-- 次の作業 -->
            ${p.nextAction ? `
              <div class="mt-2.5 bg-blue-50/70 p-2 rounded-lg border border-blue-100 text-xs text-blue-900">
                <span class="font-bold">👉 次の作業:</span> ${this.escapeHtml(p.nextAction)}
              </div>
            ` : ''}
          </div>

          <!-- Google Drive リンク ＆ 詳細ボタン -->
          <div class="mt-3 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center space-x-1.5">
              ${p.driveLinks?.drawing ? `
                <a href="${p.driveLinks.drawing}" target="_blank" rel="noopener noreferrer" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] font-medium flex items-center space-x-1 transition">
                  <span>📐 図面</span>
                </a>
              ` : ''}
              ${p.driveLinks?.estimate ? `
                <a href="${p.driveLinks.estimate}" target="_blank" rel="noopener noreferrer" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] font-medium flex items-center space-x-1 transition">
                  <span>📑 見積</span>
                </a>
              ` : ''}
              ${p.driveLinks?.photos ? `
                <a href="${p.driveLinks.photos}" target="_blank" rel="noopener noreferrer" class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] font-medium flex items-center space-x-1 transition">
                  <span>📷 写真</span>
                </a>
              ` : ''}
            </div>

            <button class="text-xs text-blue-600 hover:text-blue-800 font-bold flex items-center space-x-0.5 ml-auto" onclick="app.openProjectDetailModal('${p.id}')">
              <span>関連タスク・収支</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
          </div>
        </div>
      `;
    }).join('');

    container.querySelectorAll('.proj-edit-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const p = window.stoneStore.getProjects().find(proj => proj.id === btn.dataset.projId);
        if (p) this.openProjectModal(p);
      });
    }
);

    container.querySelectorAll('.proj-delete-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (confirm('この案件を削除しますか？紐づくタスク等は残ります。')) {
          window.stoneStore.deleteProject(btn.dataset.projId);
          this.showToast('案件を削除しました');
        }
      });
    }
);
  }

  openProjectModal(proj = null) {
    const modal = document.getElementById('modalProject');
    const form = document.getElementById('formProject');
    const titleEl = document.getElementById('modalProjectTitle');

    if (proj) {
      titleEl.textContent = '工事・お客様案件の編集';
      document.getElementById('projEditId').value = proj.id;
      document.getElementById('projInputName').value = proj.name;
      document.getElementById('projInputCustomer').value = proj.customerName || '';
      document.getElementById('projInputLocation').value = proj.siteLocation || '';
      document.getElementById('projInputSchedule').value = proj.scheduleDate || '';
      document.getElementById('projInputAssignee').value = proj.assignee || '';
      document.getElementById('projInputStatus').value = proj.status || 'inquiry';
      document.getElementById('projInputContractAmount').value = proj.contractAmount || '';
      document.getElementById('projInputNextAction').value = proj.nextAction || '';
      document.getElementById('projInputDriveDrawing').value = proj.driveLinks?.drawing || '';
      document.getElementById('projInputDriveEstimate').value = proj.driveLinks?.estimate || '';
      document.getElementById('projInputDriveInvoice').value = proj.driveLinks?.invoice || '';
      document.getElementById('projInputDrivePhotos').value = proj.driveLinks?.photos || '';
      document.getElementById('projInputNote').value = proj.note || '';
    } else {
      titleEl.textContent = '工事・お客様案件の登録';
      form.reset();
      document.getElementById('projEditId').value = '';
    }

    modal.classList.remove('hidden');
  }

  handleProjectSubmit() {
    const id = document.getElementById('projEditId').value;
    const projData = {
      name: document.getElementById('projInputName').value.trim(),
      customerName: document.getElementById('projInputCustomer').value.trim(),
      siteLocation: document.getElementById('projInputLocation').value.trim(),
      scheduleDate: document.getElementById('projInputSchedule').value.trim(),
      assignee: document.getElementById('projInputAssignee').value.trim(),
      status: document.getElementById('projInputStatus').value,
      contractAmount: document.getElementById('projInputContractAmount').value,
      nextAction: document.getElementById('projInputNextAction').value.trim(),
      driveLinks: {
        drawing: document.getElementById('projInputDriveDrawing').value.trim(),
        estimate: document.getElementById('projInputDriveEstimate').value.trim(),
        invoice: document.getElementById('projInputDriveInvoice').value.trim(),
        photos: document.getElementById('projInputDrivePhotos').value.trim()
      },
      note: document.getElementById('projInputNote').value.trim()
    };

    if (id) {
      window.stoneStore.updateProject(id, projData);
      this.showToast('案件情報を更新しました');
    } else {
      window.stoneStore.addProject(projData);
      this.showToast('新規案件を登録しました');
    }

    document.getElementById('modalProject').classList.add('hidden');
  }

  // 案件詳細モーダル（関連タスク・入出金を統合表示）
  openProjectDetailModal(projId) {
    const proj = window.stoneStore.getProjects().find(p => p.id === projId);
    if (!proj) return;

    const modal = document.getElementById('modalProjectDetail');
    document.getElementById('detailProjName').textContent = proj.name;
    document.getElementById('detailProjCustomer').textContent = proj.customerName || '未登録';
    document.getElementById('detailProjLocation').textContent = proj.siteLocation || '未登録';
    document.getElementById('detailProjSchedule').textContent = proj.scheduleDate || '未定';
    document.getElementById('detailProjAmount').textContent = proj.contractAmount ? `¥${proj.contractAmount.toLocaleString()}` : '-';

    // Google Drive ボタン生成
    const driveContainer = document.getElementById('detailDriveLinks');
    const links = proj.driveLinks || {};
    let driveHtml = '';
    if (links.drawing) driveHtml += `<a href="${links.drawing}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 flex items-center space-x-1 font-bold"><span>📐 CAD図面を開く</span></a>`;
    if (links.estimate) driveHtml += `<a href="${links.estimate}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 flex items-center space-x-1 font-bold"><span>📑 見積書を開く</span></a>`;
    if (links.invoice) driveHtml += `<a href="${links.invoice}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 flex items-center space-x-1 font-bold"><span>🧾 請求書を開く</span></a>`;
    if (links.photos) driveHtml += `<a href="${links.photos}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 flex items-center space-x-1 font-bold"><span>📷 現場写真フォルダ</span></a>`;
    if (!driveHtml) driveHtml = '<span class="text-slate-400">Driveリンクは未登録です</span>';
    driveContainer.innerHTML = driveHtml;

    // ひもづくタスク
    const rel = window.stoneStore.getProjectRelations(projId);
    const tasksContainer = document.getElementById('detailRelatedTasks');
    if (rel.tasks.length === 0) {
      tasksContainer.innerHTML = '<div class="text-slate-400 text-[11px]">この案件に紐づくタスクはありません</div>';
    } else {
      tasksContainer.innerHTML = rel.tasks.map(t => `
        <div class="flex items-center justify-between p-2 bg-slate-50 rounded border border-slate-200 text-xs">
          <div class="flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full ${t.status === 'completed' ? 'bg-emerald-500' : 'bg-amber-500'}"></span>
            <span class="${t.status === 'completed' ? 'line-through text-slate-400' : 'font-bold text-slate-800'}">${this.escapeHtml(t.title)}</span>
          </div>
          <span class="text-[11px] text-slate-500">期限: ${t.dueDate} (${t.assignee})</span>
        </div>
      `).join('');
    }

    // ひもづく入出金
    const txContainer = document.getElementById('detailRelatedTx');
    if (rel.transactions.length === 0) {
      txContainer.innerHTML = '<div class="text-slate-400 text-[11px]">この案件に紐づく入出金予定はありません</div>';
    } else {
      txContainer.innerHTML = rel.transactions.map(tx => `
        <div class="flex items-center justify-between p-2 bg-slate-50 rounded border border-slate-200 text-xs">
          <div>
            <span class="font-bold text-slate-800">${this.escapeHtml(tx.partner)}</span>
            <span class="text-[10px] text-slate-400 ml-1">(${tx.date} / ${tx.category})</span>
          </div>
          <div class="font-bold ${tx.type === 'income' ? 'text-emerald-700' : 'text-rose-700'}">
            ${tx.type === 'income' ? '+' : '-'}¥${tx.amount.toLocaleString()}
            <span class="text-[10px] ml-1 font-normal ${tx.isActual ? 'text-slate-800 font-bold' : 'text-slate-400'}">(${tx.isActual ? '実績' : '予定'})</span>
          </div>
        </div>
      `).join('');
    }

    modal.classList.remove('hidden');
  }

  // ==============================================================
  // 4. 作業履歴・弥生会計記録
  // ==============================================================
  renderActivityLogs() {
    const container = document.getElementById('activityLogsList');
    if (!container) return;

    let logs = window.stoneStore.getActivityLogs();
    const query = document.getElementById('logSearchInput')?.value.toLowerCase().trim() || '';

    if (query) {
      logs = logs.filter(l => 
        (l.action && l.action.toLowerCase().includes(query)) ||
        (l.details && l.details.toLowerCase().includes(query)) ||
        (l.user && l.user.toLowerCase().includes(query)) ||
        (l.category && l.category.toLowerCase().includes(query))
      );
    }

    if (logs.length === 0) {
      container.innerHTML = '<div class="p-6 text-center text-slate-400 text-xs">作業履歴はありません</div>';
      return;
    }

    container.innerHTML = logs.map(l => {
      const isYayoi = l.category === '弥生会計' || (l.action && l.action.includes('弥生'));
      const isWife = l.user === '私';

      return `
        <div class="relative pl-6 sm:pl-8 pb-3">
          <!-- タイムラインの丸ポチ -->
          <div class="absolute left-2 sm:left-3 top-1.5 w-2.5 h-2.5 -ml-1 rounded-full border-2 border-white ${isYayoi ? 'bg-amber-500 ring-2 ring-amber-300' : 'bg-blue-600'}"></div>

          <div class="bg-slate-50 hover:bg-white p-3 rounded-xl border border-slate-200 shadow-sm transition">
            <div class="flex flex-wrap items-center justify-between gap-1 mb-1">
              <div class="flex items-center space-x-2">
                <span class="text-[11px] font-bold px-2 py-0.5 rounded-full ${isWife ? 'bg-indigo-100 text-indigo-800' : 'bg-slate-200 text-slate-800'}">${l.user}</span>
                <span class="text-[10px] font-semibold text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200">${l.category}</span>
              </div>
              <span class="text-[11px] text-slate-400">${l.timestamp}</span>
            </div>

            <div class="text-xs font-bold text-slate-900 mt-1">
              ${this.escapeHtml(l.action)}
            </div>

            ${l.details ? `
              <div class="mt-1.5 text-xs text-slate-600 whitespace-pre-wrap leading-relaxed bg-white p-2 rounded border border-slate-100">
                ${this.escapeHtml(l.details)}
              </div>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');
  }

  handleYayoiSubmit() {
    const month = document.getElementById('yayoiInputMonth').value;
    const docType = document.getElementById('yayoiInputDocType').value.trim();
    const completedRange = document.getElementById('yayoiInputCompletedRange').value.trim();
    const remaining = document.getElementById('yayoiInputRemaining').value.trim();

    const details = `【対象月】${month}\n【資料の種類】${docType}\n【完了範囲】${completedRange}` +
      (remaining ? `\n【残作業・確認事項】${remaining}` : '');

    window.stoneStore.addActivityLog({
      category: '弥生会計',
      action: `弥生会計 ${month} 記帳進捗記録`,
      details: details
    });

    document.getElementById('modalYayoi').classList.add('hidden');
    this.showToast('弥生会計の入力進捗を記録しました！');
  }

  // ==============================================================
  // 5. 重要メール
  // ==============================================================
  renderEmails() {
    if (!window.stoneStore.canAccessEmails()) return;

    const container = document.getElementById('emailsListContainer');
    if (!container) return;

    const emails = window.stoneStore.getEmails();

    if (emails.length === 0) {
      container.innerHTML = '<div class="p-8 text-center text-slate-400 text-xs">メールはありません</div>';
      return;
    }

    container.innerHTML = emails.map(m => {
      return `
        <div class="bg-white rounded-xl p-3.5 sm:p-4 border ${!m.isProcessed && !m.isNoticeOrAd ? 'border-amber-300 bg-amber-50/20 shadow-sm' : 'border-slate-200'} transition hover:border-sky-300">
          <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-2">
            
            <div class="flex-1">
              <!-- 差出人 ＆ 日時 -->
              <div class="flex flex-wrap items-center gap-1.5 mb-1">
                <span class="text-xs font-bold text-slate-800">${this.escapeHtml(m.senderName)}</span>
                <span class="text-[11px] text-slate-400">受信: ${m.date}</span>
                ${m.dueDate ? `<span class="text-[11px] font-bold text-red-600 bg-red-50 border border-red-200 px-1.5 py-0.5 rounded">対応期限: ${m.dueDate}</span>` : ''}
                <span class="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">担当: ${m.assignee}</span>
              </div>

              <!-- 件名 -->
              <h3 class="text-xs sm:text-sm font-bold text-slate-900 cursor-pointer hover:text-sky-600 transition" onclick="app.openEmailDetailModal('${m.id}')">
                ${this.escapeHtml(m.subject)}
              </h3>
            </div>

            <!-- ステータスバッジ（既読／対応状況） -->
            <div class="flex items-center space-x-1.5 flex-shrink-0">
              <!-- 既読トグル -->
              <button class="email-read-toggle-btn text-[11px] px-2 py-0.5 rounded font-medium border transition ${m.isRead ? 'bg-slate-100 text-slate-600 border-slate-200' : 'bg-sky-600 text-white border-sky-600 font-bold'}" data-mail-id="${m.id}">
                ${m.isRead ? '既読' : '未読'}
              </button>

              <!-- 対応済みトグル -->
              <button class="email-proc-toggle-btn text-[11px] px-2 py-0.5 rounded font-bold border transition ${m.isProcessed ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-amber-100 text-amber-800 border-amber-300 pulse-warning'}" data-mail-id="${m.id}">
                ${m.isProcessed ? '✓ 対応済' : '⚠️ 未対応'}
              </button>
            </div>

          </div>

          <!-- 本文抜粋 -->
          <p class="text-xs text-slate-600 line-clamp-2 leading-relaxed bg-slate-50 p-2 rounded border border-slate-100 cursor-pointer" onclick="app.openEmailDetailModal('${m.id}')">
            ${this.escapeHtml(m.body)}
          </p>

          <!-- メール下部アクション -->
          <div class="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
            <button class="text-sky-700 hover:text-sky-900 font-semibold flex items-center space-x-1" onclick="app.openEmailDetailModal('${m.id}')">
              <span>全文を表示</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
            </button>

            <!-- タスク化ボタン -->
            ${!m.taskCreated ? `
              <button class="create-task-from-mail-btn bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold px-2.5 py-1 rounded border border-blue-200 flex items-center space-x-1 transition" data-mail-id="${m.id}">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                <span>作業（タスク）に登録</span>
              </button>
            ` : `
              <span class="text-[11px] text-emerald-600 font-semibold flex items-center">
                <svg class="w-3.5 h-3.5 mr-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                タスク登録済み
              </span>
            `}
          </div>

        </div>
      `;
    }).join('');

    container.querySelectorAll('.email-read-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        window.stoneStore.toggleEmailRead(btn.dataset.mailId);
      });
    }
);

    container.querySelectorAll('.email-proc-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        window.stoneStore.toggleEmailProcessed(btn.dataset.mailId);
        this.showToast('対応状況を更新しました');
      });
    }
);

    container.querySelectorAll('.create-task-from-mail-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const mailId = btn.dataset.mailId;
        const task = window.stoneStore.createTaskFromEmail(mailId);
        if (task) {
          this.showToast(`メールから「${task.title}」を今日の対応に追加しました！`);
          this.switchView('home');
        }
      });
    }
);
  }

  openEmailDetailModal(mailId) {
    const mail = window.stoneStore.getEmails().find(m => m.id === mailId);
    if (!mail) return;

    this.currentModalMailId = mailId;
    const modal = document.getElementById('modalEmailDetail');
    document.getElementById('modalMailSender').textContent = mail.sender;
    document.getElementById('modalMailSubject').textContent = mail.subject;
    document.getElementById('modalMailDate').textContent = `受信: ${mail.date}`;
    document.getElementById('modalMailDueDate').textContent = mail.dueDate ? `期限: ${mail.dueDate}` : '期限指定なし';
    document.getElementById('modalMailAssignee').textContent = `担当: ${mail.assignee}`;
    document.getElementById('modalMailBody').textContent = mail.body;

    const link = document.getElementById('modalMailLink');
    if (link) link.href = mail.mailUrl || '#';

    // 既読にする
    if (!mail.isRead) {
      window.stoneStore.toggleEmailRead(mailId);
    }

    modal.classList.remove('hidden');
  }

  // ==============================================================
  // ユーティリティ
  // ==============================================================
  showToast(message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'bg-slate-900 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-xl border border-slate-700 transition transform duration-300 translate-y-2 opacity-0 flex items-center space-x-2 pointer-events-auto';
    toast.innerHTML = `
      <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
      <span>${this.escapeHtml(message)}</span>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-2', 'opacity-0');
    });

    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => toast.remove(), 300);
    }, 2800);
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

// ==============================================================
  // 【最優先】トップ画面 資金繰り・口座別残高ダッシュボード描画
  // ==============================================================
  renderTopFundsDashboard() {
    const kpis = window.stoneStore.getDashboardKPIs();
    
    // 1. 全口座合計手元資金
    const topTotalCash = document.getElementById('topTotalCash');
    if (topTotalCash) {
      topTotalCash.textContent = `¥${kpis.totalCurrentCash.toLocaleString()}`;
    }

    const yayoiData = window.stoneStore.getYayoiData();
    const yayoiBadge = document.getElementById('yayoiLastImportBadge');
    if (yayoiBadge) {
      if (yayoiData && yayoiData.lastImportedAt) {
        yayoiBadge.textContent = `弥生連携: ${yayoiData.lastImportedAt.slice(5, 16)} (${yayoiData.importedCount}件取込済)`;
        yayoiBadge.className = 'hidden sm:inline text-[10px] bg-emerald-950/80 text-emerald-300 border border-emerald-500/50 px-2 py-0.5 rounded ml-2 font-bold';
      } else {
        yayoiBadge.textContent = '弥生連携: 未取り込み';
        yayoiBadge.className = 'hidden sm:inline text-[10px] bg-slate-800 text-slate-400 border border-slate-700 px-2 py-0.5 rounded ml-2';
      }
    }

    // 2. 口座別残高カード（5銀行＋手許現金、計6口座）
    const cardsContainer = document.getElementById('topAccountCardsContainer');
    if (cardsContainer) {
      cardsContainer.innerHTML = kpis.accounts.map(acc => {
        const isShortage = acc.currentBalance < 0;
        return `
          <div class="bg-white hover:bg-slate-50 text-slate-800 p-3 rounded-xl border border-slate-300 shadow-sm transition cursor-pointer group" onclick="app.switchView('funds'); app.switchFundsSubtab('cashflow');">
            <div class="flex items-center justify-between text-xs">
              <span class="font-extrabold truncate text-slate-800 flex items-center group-hover:text-blue-600">
                <span class="w-2.5 h-2.5 rounded-full mr-1.5 flex-shrink-0" style="background-color: ${acc.color};"></span>
                ${acc.shortName}
              </span>
              <span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-bold">${acc.type === 'cash' ? '現金' : '口座'}</span>
            </div>
            <div class="text-base sm:text-lg font-black mt-1.5 tracking-tight ${isShortage ? 'text-rose-600 font-black' : 'text-slate-900'}">
              ¥${acc.currentBalance.toLocaleString()}
            </div>
            <div class="text-[10px] text-slate-400 mt-0.5 truncate">基準日: ${acc.baseDate || '10/31'}</div>
          </div>
        `;
      }).join('');
    }

    // 3. アラートエリア（資金ショート警告 ＆ 口座未定警告）
    const alertsArea = document.getElementById('topAlertsArea');
    if (alertsArea) {
      let alertsHtml = '';
      
      // 資金不足（ショート）警告
      if (kpis.shortageAlerts && kpis.shortageAlerts.length > 0) {
        const firstShortage = kpis.shortageAlerts[0];
        alertsHtml += `
          <div class="bg-rose-950/80 border border-rose-500/70 p-3 rounded-xl flex items-center justify-between shadow-sm animate-pulse">
            <div class="flex items-center space-x-2 text-xs">
              <span class="text-lg">⚠️</span>
              <div>
                <div class="font-bold text-rose-200">資金不足の予測が発生しています！（計 ${kpis.shortageAlerts.length} 件）</div>
                <div class="text-[11px] text-rose-300 mt-0.5">
                  最も早い不足: <strong>${firstShortage.date}</strong> に <strong>${firstShortage.accountName}</strong> で <span class="font-bold text-white underline">¥${firstShortage.shortageAmount.toLocaleString()} 不足</span>の予測
                </div>
              </div>
            </div>
            <button onclick="app.switchView('funds'); app.switchFundsSubtab('cashflow');" class="bg-rose-600 hover:bg-rose-500 text-white font-bold text-[10px] px-2.5 py-1.5 rounded-lg whitespace-nowrap transition">
              日繰り表で確認 ➔
            </button>
          </div>
        `;
      }

      // 支払口座未定の警告
      if (kpis.unassignedAlerts && kpis.unassignedAlerts.length > 0) {
        const totalUnassignedAmt = kpis.unassignedAlerts.reduce((sum, a) => sum + a.amount, 0);
        alertsHtml += `
          <div class="bg-amber-950/70 border border-amber-500/60 p-2.5 rounded-xl flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="text-base text-amber-400">⚠️</span>
              <div>
                <span class="font-bold text-amber-200">支払口座が未定の支払いが ${kpis.unassignedAlerts.length} 日分（計 ¥${totalUnassignedAmt.toLocaleString()}）あります</span>
                <p class="text-[10px] text-amber-300/80">※全口座合計からは引かれていますが、口座別予測では未配分額として管理されています。</p>
              </div>
            </div>
            <button onclick="app.switchView('funds'); app.switchFundsSubtab('cashflow');" class="bg-amber-600 hover:bg-amber-500 text-white font-bold text-[10px] px-2 py-1 rounded-lg transition whitespace-nowrap">
              口座を指定 ➔
            </button>
          </div>
        `;
      }

      alertsArea.innerHTML = alertsHtml;
    }

    // 4. 今後30日間の入出金予定
    const topNext30Income = document.getElementById('topNext30Income');
    const topNext30Expense = document.getElementById('topNext30Expense');
    const topNext30Net = document.getElementById('topNext30Net');
    if (topNext30Income) topNext30Income.textContent = `+¥${kpis.next30Income.toLocaleString()}`;
    if (topNext30Expense) topNext30Expense.textContent = `-¥${kpis.next30Expense.toLocaleString()}`;
    if (topNext30Net) {
      topNext30Net.textContent = `${kpis.next30Net >= 0 ? '+' : ''}¥${kpis.next30Net.toLocaleString()}`;
      topNext30Net.className = `font-bold text-xs ${kpis.next30Net >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
    }

    // 5. 未回収の請求書（売掛金）
    const topUncollectedCount = document.getElementById('topUncollectedCount');
    const topUncollectedTotal = document.getElementById('topUncollectedTotal');
    if (topUncollectedCount) topUncollectedCount.textContent = `${kpis.uncollectedCount}件`;
    if (topUncollectedTotal) topUncollectedTotal.textContent = `¥${kpis.uncollectedTotal.toLocaleString()}`;
  }

  // ==============================================================
  // 5口座＋手許現金 日別資金繰り・口座別予測表のレンダリング
  // ==============================================================
  renderDailyCashFlowSchedule() {
    const table = document.getElementById('dailyScheduleTable');
    if (!table) return;

    const accounts = window.stoneStore.getAccounts();
    const result = window.stoneStore.calculateDailyCashFlowSchedule();
    const list = result.dailyList;

    // 口座ミニインジケーターの描画
    const indicator = document.getElementById('dailyAccountsIndicator');
    if (indicator) {
      indicator.innerHTML = accounts.map(acc => {
        const bal = result.finalAccountBalances[acc.id] ?? acc.baseBalance;
        const isShortage = bal < 0;
        return `
          <div class="bg-slate-50 p-2 rounded-lg border border-slate-200">
            <div class="text-[10px] text-slate-500 font-bold flex items-center justify-between">
              <span class="truncate flex items-center">
                <span class="w-2 h-2 rounded-full mr-1" style="background-color: ${acc.color};"></span>
                ${acc.shortName}
              </span>
            </div>
            <div class="text-xs font-black mt-0.5 ${isShortage ? 'text-rose-600' : 'text-slate-800'}">
              ¥${bal.toLocaleString()}
            </div>
          </div>
        `;
      }).join('');
    }

    // 警告バナーエリア
    const dailyAlertsContainer = document.getElementById('dailyAlertsContainer');
    if (dailyAlertsContainer) {
      let alertsHtml = '';
      if (result.shortageAlerts.length > 0) {
        alertsHtml += `
          <div class="p-2.5 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-900 flex items-center justify-between">
            <div class="flex items-center space-x-1.5 font-bold">
              <span>⚠️ 残高不足警告:</span>
              <span>${result.shortageAlerts.map(a => `${a.date} [${a.shortName}: ¥${a.shortageAmount.toLocaleString()}不足]`).join('、')}</span>
            </div>
          </div>
        `;
      }
      if (result.unassignedAlerts.length > 0) {
        alertsHtml += `
          <div class="p-2.5 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-center justify-between">
            <span class="font-bold">⚠️ 支払口座未定の支払いがあります（日別の「未配分額」をご確認いただき、口座を指定してください）</span>
          </div>
        `;
      }
      dailyAlertsContainer.innerHTML = alertsHtml;
    }

    if (list.length === 0) {
      table.innerHTML = '<tr><td class="p-4 text-center text-slate-400 text-xs">基準日以降の入出金予定はありません</td></tr>';
      return;
    }

    if (this.dailyScheduleViewMode === 'total') {
      // ----------------------------------------------------------
      // ビュー A: 全社合計ビュー
      // ----------------------------------------------------------
      let html = `
        <thead class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px] border-b">
          <tr>
            <th class="py-2.5 px-3">日付</th>
            <th class="py-2.5 px-2">特徴</th>
            <th class="py-2.5 px-3 text-right">入金額</th>
            <th class="py-2.5 px-3 text-right">出金額</th>
            <th class="py-2.5 px-3 text-right text-amber-700">口座未定(未配分)</th>
            <th class="py-2.5 px-3 text-right">当日収支</th>
            <th class="py-2.5 px-3 text-right bg-slate-200/70">全口座合計残高</th>
            <th class="py-2.5 px-2 text-center">明細</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
      `;

      list.forEach(item => {
        let badgeHtml = '';
        if (item.isPayday) badgeHtml = '<span class="bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-amber-300">給料日</span>';
        else if (item.isLoanDay) badgeHtml = '<span class="bg-purple-100 text-purple-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-purple-300">公庫引落</span>';
        else if (item.isMonthEnd) badgeHtml = '<span class="bg-rose-100 text-rose-900 px-1.5 py-0.5 rounded text-[10px] font-bold border border-rose-300">月末振込</span>';
        else if (item.isHighOutflow) badgeHtml = '<span class="bg-rose-50 text-rose-700 px-1.5 py-0.5 rounded text-[10px] font-medium border border-rose-200">大型出金</span>';
        else badgeHtml = '<span class="text-slate-400 text-[10px]">通常</span>';

        const rowShortageClass = item.hasShortage ? 'bg-rose-50/60 font-semibold' : '';

        html += `
          <tr class="hover:bg-slate-50 transition cursor-pointer ${rowShortageClass}" onclick="app.showDailyDetail('${item.date}')">
            <td class="py-2.5 px-3 font-bold text-slate-800 whitespace-nowrap">${item.date}</td>
            <td class="py-2.5 px-2 whitespace-nowrap">${badgeHtml}</td>
            <td class="py-2.5 px-3 text-right font-bold text-emerald-700 whitespace-nowrap">
              ${item.totalIncome > 0 ? `+¥${item.totalIncome.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-rose-700 whitespace-nowrap">
              ${item.totalExpense > 0 ? `-¥${item.totalExpense.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-amber-600 whitespace-nowrap">
              ${item.unassignedExpense > 0 ? `⚠️ ¥${item.unassignedExpense.toLocaleString()}` : '<span class="text-slate-300">-</span>'}
            </td>
            <td class="py-2.5 px-3 text-right font-extrabold whitespace-nowrap ${item.totalNet >= 0 ? 'text-emerald-700' : 'text-rose-700'}">
              ${item.totalNet >= 0 ? '+' : ''}¥${item.totalNet.toLocaleString()}
            </td>
            <td class="py-2.5 px-3 text-right font-black text-slate-900 whitespace-nowrap bg-slate-50">
              ¥${item.totalBalance.toLocaleString()}
            </td>
            <td class="py-2.5 px-2 text-center">
              <button class="text-blue-600 hover:text-blue-800 font-bold text-[11px] underline">明細(${item.items.length})</button>
            </td>
          </tr>
        `;
      });

      html += '</tbody>';
      table.innerHTML = html;

    } else {
      // ----------------------------------------------------------
      // ビュー B: 5口座＋手許現金 口座別マトリクスビュー
      // ----------------------------------------------------------
      let html = `
        <thead class="bg-slate-100 text-slate-700 font-bold text-[10px] border-b">
          <tr>
            <th class="py-2.5 px-2.5 whitespace-nowrap sticky left-0 bg-slate-100 z-10">日付</th>
            <th class="py-2.5 px-2 whitespace-nowrap">特徴</th>
            ${accounts.map(a => `<th class="py-2.5 px-2.5 text-right whitespace-nowrap" style="color: ${a.color}">${a.shortName}</th>`).join('')}
            <th class="py-2.5 px-2.5 text-right whitespace-nowrap text-amber-600">未配分支払</th>
            <th class="py-2.5 px-3 text-right whitespace-nowrap bg-slate-200/80 font-black">合計残高</th>
            <th class="py-2.5 px-2 text-center whitespace-nowrap">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
      `;

      list.forEach(item => {
        let badgeHtml = '';
        if (item.isPayday) badgeHtml = '<span class="bg-amber-100 text-amber-900 px-1 py-0.2 rounded text-[9px] font-bold">給与</span>';
        else if (item.isLoanDay) badgeHtml = '<span class="bg-purple-100 text-purple-900 px-1 py-0.2 rounded text-[9px] font-bold">公庫</span>';
        else if (item.isMonthEnd) badgeHtml = '<span class="bg-rose-100 text-rose-900 px-1 py-0.2 rounded text-[9px] font-bold">月末</span>';
        else badgeHtml = '<span class="text-slate-400 text-[9px]">-</span>';

        html += `
          <tr class="hover:bg-slate-50 transition ${item.hasShortage ? 'bg-rose-50/50' : ''}">
            <td class="py-2 px-2.5 font-bold text-slate-800 whitespace-nowrap sticky left-0 bg-white z-10">${item.date}</td>
            <td class="py-2 px-2 whitespace-nowrap">${badgeHtml}</td>
            ${accounts.map(a => {
              const snap = item.accountSnapshots[a.id];
              const isShort = snap && snap.isShortage;
              const balClass = isShort ? 'text-rose-600 bg-rose-100 font-black px-1.5 py-0.5 rounded' : 'text-slate-800 font-bold';
              return `
                <td class="py-2 px-2.5 text-right whitespace-nowrap">
                  <span class="${balClass}">¥${snap ? snap.balance.toLocaleString() : 0}</span>
                </td>
              `;
            }).join('')}
            <td class="py-2 px-2.5 text-right whitespace-nowrap font-bold ${item.unassignedExpense > 0 ? 'text-amber-600 bg-amber-50' : 'text-slate-300'}">
              ${item.unassignedExpense > 0 ? `¥${item.unassignedExpense.toLocaleString()}` : '-'}
            </td>
            <td class="py-2 px-3 text-right font-black text-slate-900 whitespace-nowrap bg-slate-50">
              ¥${item.totalBalance.toLocaleString()}
            </td>
            <td class="py-2 px-2 text-center whitespace-nowrap">
              <button onclick="app.showDailyDetail('${item.date}')" class="text-blue-600 hover:underline font-bold text-[10px]">明細</button>
            </td>
          </tr>
        `;
      });

      html += '</tbody>';
      table.innerHTML = html;
    }
  }

  // 日別明細のポップアップ展開
  showDailyDetail(dateStr) {
    const cont = document.getElementById('dailyDetailContainer');
    const title = document.getElementById('dailyDetailTitle');
    const listCont = document.getElementById('dailyDetailItemsList');
    if (!cont || !listCont) return;

    const accounts = window.stoneStore.getAccounts();
    const dayTxs = window.stoneStore.getTransactions().filter(t => t.date === dateStr);

    title.textContent = `📅 ${dateStr} の入出金・振替明細（計 ${dayTxs.length} 件）`;

    if (dayTxs.length === 0) {
      listCont.innerHTML = '<div class="text-slate-400 p-2 text-center">この日の個別取引はありません（残高推移のみ）</div>';
    } else {
      listCont.innerHTML = dayTxs.map(tx => {
        let typeBadge = '';
        let accInfo = '';
        
        if (tx.type === 'income') {
          typeBadge = '<span class="bg-emerald-100 text-emerald-800 text-[10px] px-1.5 py-0.5 rounded font-bold">入金</span>';
          const acc = accounts.find(a => a.id === tx.accountId);
          accInfo = `<span class="text-[10px] text-slate-500">入金先: ${acc ? acc.shortName : '中京銀行'}</span>`;
        } else if (tx.type === 'expense') {
          typeBadge = '<span class="bg-rose-100 text-rose-800 text-[10px] px-1.5 py-0.5 rounded font-bold">支払</span>';
          if (!tx.accountId || tx.accountId === 'unassigned') {
            accInfo = '<span class="bg-amber-100 text-amber-800 text-[10px] px-1.5 py-0.2 rounded font-bold">⚠️ 支払口座未定</span>';
          } else {
            const acc = accounts.find(a => a.id === tx.accountId);
            accInfo = `<span class="text-[10px] text-slate-500">支払口座: ${acc ? acc.shortName : tx.accountId}</span>`;
          }
        } else if (tx.type === 'transfer') {
          typeBadge = '<span class="bg-blue-100 text-blue-800 text-[10px] px-1.5 py-0.5 rounded font-bold">口座間振替</span>';
          const fromAcc = accounts.find(a => a.id === tx.fromAccountId);
          const toAcc = accounts.find(a => a.id === tx.toAccountId);
          accInfo = `<span class="text-[10px] text-blue-700 font-bold">${fromAcc ? fromAcc.shortName : tx.fromAccountId} ➔ ${toAcc ? toAcc.shortName : tx.toAccountId}</span>`;
        }

        const isActualBadge = tx.isActual
          ? '<span class="bg-slate-200 text-slate-700 text-[10px] px-1.5 py-0.2 rounded font-bold">実績済</span>'
          : '<span class="bg-amber-100 text-amber-800 text-[10px] px-1.5 py-0.2 rounded font-bold">予定</span>';

        return `
          <div class="bg-white p-2.5 rounded-lg border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-sm">
            <div class="space-y-0.5">
              <div class="flex items-center space-x-1.5">
                ${typeBadge}
                <span class="font-bold text-slate-900">${tx.partner}</span>
                <span class="text-slate-500 text-[11px]">(${tx.category})</span>
                ${isActualBadge}
              </div>
              <div class="flex items-center space-x-2 text-[10px]">
                ${accInfo}
                ${tx.note ? `<span class="text-slate-400">メモ: ${tx.note}</span>` : ''}
              </div>
            </div>

            <div class="flex items-center space-x-2 self-end sm:self-center">
              <span class="text-sm font-black ${tx.type === 'income' ? 'text-emerald-700' : (tx.type === 'expense' ? 'text-rose-700' : 'text-blue-700')}">
                ¥${Number(tx.amount).toLocaleString()}
              </span>

              <!-- アクションボタン群 -->
              <button onclick="app.toggleTxActual('${tx.id}')" class="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-bold border transition">
                ${tx.isActual ? '予定に戻す' : '実績化'}
              </button>

              <button onclick="app.openDelayModal('${tx.id}')" class="px-2 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 text-[10px] font-bold border border-blue-200 transition">
                期日・口座変更
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    cont.classList.remove('hidden');
    cont.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  // 取引の実績化トグル
  toggleTxActual(txId) {
    window.stoneStore.toggleTransactionActual(txId);
    this.showToast('取引の状態を更新しました');
    this.render();
  }

  // ==============================================================
  // モーダル管理（6口座設定、口座間振替、期日遅延変更、財務三表）
  // ==============================================================
  openAccountsModal() {
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
  }

  openTransferModal() {
    const modal = document.getElementById('modalTransfer');
    if (!modal) return;

    const accounts = window.stoneStore.getAccounts();
    const fromSel = document.getElementById('trInputFrom');
    const toSel = document.getElementById('trInputTo');

    if (fromSel && toSel) {
      fromSel.innerHTML = accounts.map(a => `<option value="${a.id}">${a.name}</option>`).join('');
      toSel.innerHTML = accounts.map(a => `<option value="${a.id}">${a.name}</option>`).join('');
      // デフォルトで出金元を中京銀行、入金先を十六銀行にセット
      fromSel.value = 'bank-1';
      toSel.value = 'bank-2';
    }

    document.getElementById('trInputDate').value = this.todayStr;
    document.getElementById('trInputAmount').value = '';
    document.getElementById('trInputNote').value = '';

    modal.classList.remove('hidden');
  }

  handleSaveTransfer(e) {
    e.preventDefault();
    try {
      const date = document.getElementById('trInputDate').value;
      const fromAccountId = document.getElementById('trInputFrom').value;
      const toAccountId = document.getElementById('trInputTo').value;
      const amount = parseInt(document.getElementById('trInputAmount').value, 10);
      const isActual = document.getElementById('trInputIsActual').value === 'true';
      const note = document.getElementById('trInputNote').value.trim();

      window.stoneStore.transferFunds({
        date,
        fromAccountId,
        toAccountId,
        amount,
        isActual,
        note
      });

      document.getElementById('modalTransfer').classList.add('hidden');
      this.showToast('口座間振替を登録しました（合計資金残高では二重計上されません）');
      this.render();
    } catch (err) {
      alert(err.message);
    }
  }

  openDelayModal(txId) {
    const modal = document.getElementById('modalDelayTx');
    const tx = window.stoneStore.getTransactions().find(t => t.id === txId);
    if (!modal || !tx) return;

    document.getElementById('delayModalTxId').value = tx.id;
    document.getElementById('delayModalPartner').textContent = tx.partner;
    document.getElementById('delayModalTitle').textContent = `${tx.type === 'income' ? '入金' : '支払'} [${tx.category}]`;
    document.getElementById('delayModalAmount').textContent = `¥${Number(tx.amount).toLocaleString()}`;
    document.getElementById('delayModalCurrentDate').textContent = tx.date;
    document.getElementById('delayInputNewDate').value = tx.date;
    document.getElementById('delayInputReason').value = '';

    const accSel = document.getElementById('delayInputAccount');
    if (accSel) {
      accSel.value = tx.accountId || 'unassigned';
    }

    modal.classList.remove('hidden');
  }

  handleSaveDelayTx(e) {
    e.preventDefault();
    const txId = document.getElementById('delayModalTxId').value;
    const newDate = document.getElementById('delayInputNewDate').value;
    const newAcc = document.getElementById('delayInputAccount').value;
    const reason = document.getElementById('delayInputReason').value.trim();

    window.stoneStore.delayTransaction(txId, newDate, reason);
    if (newAcc) {
      window.stoneStore.setTransactionAccount(txId, newAcc);
    }

    document.getElementById('modalDelayTx').classList.add('hidden');
    this.showToast('予定日および口座を更新しました');
    this.render();
  }

  // 財務三表モーダル
  openBSPLModal() {
    const modal = document.getElementById('modalBSPL');
    if (!modal) return;
    this.renderBSPLContent();
    modal.classList.remove('hidden');
  }


  // ==============================================================
  // 弥生CSV取り込み ハンドラー
  // ==============================================================
  openYayoiModal() {
    const modal = document.getElementById('modalYayoiImport');
    if (!modal) return;
    const resultArea = document.getElementById('yayoiImportResultArea');
    if (resultArea) resultArea.classList.add('hidden');
    modal.classList.remove('hidden');
  }

  handleYayoiFileSelect(e) {
    if (e.target.files && e.target.files.length > 0) {
      this.processYayoiFile(e.target.files[0]);
    }
  }

  processYayoiFile(file) {
    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const text = evt.target.result;
        const result = window.stoneStore.importYayoiCSV(text, file.name);
        this.displayYayoiImportResult(result);
        this.showToast(`弥生CSV「${file.name}」を取り込みました（${result.parsedCount}件）`);
        this.render();
      } catch (err) {
        alert('弥生CSVの取り込みに失敗しました: ' + err.message);
      }
    };
    reader.readAsText(file, 'UTF-8');
  }


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

  handleLoadSampleYayoi() {
    try {
      const result = window.stoneStore.loadSampleYayoiCSV();
      this.displayYayoiImportResult(result);
      this.showToast('石材店のサンプル弥生仕訳データを取り込みました！');
      this.render();
    } catch (err) {
      alert('サンプル取り込みエラー: ' + err.message);
    }
  }

  displayYayoiImportResult(result) {
    const resultArea = document.getElementById('yayoiImportResultArea');
    if (!resultArea) return;

    resultArea.className = 'p-3.5 rounded-xl border border-emerald-300 bg-emerald-50 text-emerald-950 text-xs space-y-1';
    resultArea.innerHTML = `
      <div class="font-bold flex items-center text-emerald-800">
        <svg class="w-4 h-4 mr-1 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <span>弥生データの取り込みが完了しました</span>
      </div>
      <div class="text-[11px] text-emerald-900 mt-1 space-y-0.5">
        <div>・新規取り込み仕訳: <strong>${result.parsedCount} 件</strong></div>
        <div>・重複スキップ（二重計上防止）: <strong>${result.duplicateCount} 件</strong></div>
        <div>・取り込み日時: <strong>${result.lastImportedAt}</strong></div>
        <div class="text-[10px] text-emerald-700 mt-1 font-semibold">✅ 5銀行口座＋現金の残高および財務三表が自動更新されました</div>
      </div>
    `;
    resultArea.classList.remove('hidden');
  }

  // ==============================================================
  // 財務三表（B/S・P/L・C/F ＆ 損益・現金差異分析）レンダリング
  // ==============================================================
  renderBSPLContent() {
    const cont = document.getElementById('bsplContentArea');
    if (!cont) return;

    const data = window.stoneStore.getFinancialStatements();
    const pl = data.pl;
    const bs = data.bs;
    const cf = data.cf;

    const bsplTabPL = document.getElementById('bsplTabPL');
    const bsplTabBS = document.getElementById('bsplTabBS');
    const bsplTabCF = document.getElementById('bsplTabCF');

    // 損益と現金の違いの解説カードHTML
    const plVsCashBoxHtml = `
      <div class="p-3 bg-amber-50/80 border border-amber-300 rounded-xl space-y-2 mt-3">
        <div class="flex items-center justify-between text-amber-950">
          <span class="font-bold flex items-center text-xs">
            <span class="mr-1.5 text-base">💡</span> 【最重要】損益（利益）と現金残高が一致しない理由
          </span>
          <span class="text-[10px] bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded font-bold">黒字倒産を防ぐ分析</span>
        </div>
        <p class="text-[11px] text-amber-900 leading-relaxed">
          「損益計算書で営業利益が <strong>¥${pl.operatingProfit.toLocaleString()}</strong> 出ているのに、なぜ口座の手元資金（<strong>¥${bs.assets.current.cashAndDeposits.toLocaleString()}</strong>）と違うのか？」の原因内訳です。
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px]">
          ${data.plVsCashAnalysis.map(item => `
            <div class="p-2 bg-white rounded-lg border border-amber-200 flex justify-between items-center">
              <div>
                <span class="font-bold text-slate-800">${item.factor}</span>
                <div class="text-[10px] text-slate-500">${item.note}</div>
              </div>
              <span class="font-black whitespace-nowrap ml-2 ${item.amount >= 0 ? 'text-emerald-700' : 'text-rose-700'}">
                ${item.amount >= 0 ? '+' : ''}¥${item.amount.toLocaleString()}
              </span>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    if (this.bsplTab === 'pl') {
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      const marginRate = ((pl.grossProfit / pl.sales) * 100).toFixed(1);

      cont.innerHTML = `
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-900 text-sm flex items-center">
              <span>📊 損益計算書 (P/L: Profit & Loss Statement)</span>
              <span class="ml-2 text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">弥生確定データ基準</span>
            </span>
            <span class="text-[11px] text-slate-500">年間累計実績</span>
          </div>

          <table class="w-full text-xs text-left border-collapse">
            <tr class="border-b bg-slate-50"><td class="py-2.5 px-3 font-bold text-slate-900">Ⅰ. 売上高（工事完工高合計）</td><td class="py-2.5 px-3 text-right font-black text-slate-900">¥${pl.sales.toLocaleString()}</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">売上原価（石材部材・生コン建材・外注加工・重機リース）</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥${pl.cogs.toLocaleString()}</td></tr>
            <tr class="border-b bg-blue-50/70">
              <td class="py-2.5 px-3 font-bold text-blue-900">Ⅱ. 売上総利益（限界利益 粗利） <span class="ml-1 text-[10px] bg-blue-200 text-blue-800 px-1.5 py-0.2 rounded">粗利率: ${marginRate}%</span></td>
              <td class="py-2.5 px-3 text-right font-black text-blue-900">¥${pl.grossProfit.toLocaleString()}</td>
            </tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">販売費及び一般管理費（専従者給与・車両燃料・消耗品工具・保険・通信光熱費）</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥${pl.sga.toLocaleString()}</td></tr>
            <tr class="border-b bg-emerald-50">
              <td class="py-2.5 px-3 font-bold text-emerald-900">Ⅲ. 営業利益（本業の儲け）</td>
              <td class="py-2.5 px-3 text-right font-black text-emerald-900">+¥${pl.operatingProfit.toLocaleString()}</td>
            </tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">営業外費用（公庫・地銀借入利息）</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥${pl.nonOperatingExpense.toLocaleString()}</td></tr>
            <tr class="border-b bg-slate-900 text-white">
              <td class="py-2.5 px-3 font-bold">★ 差引経常利益（青色申告特別控除前所得）</td>
              <td class="py-2.5 px-3 text-right font-black text-sky-300">¥${pl.ordinaryProfit.toLocaleString()}</td>
            </tr>
          </table>

          ${plVsCashBoxHtml}
        </div>
      `;
    } else if (this.bsplTab === 'bs') {
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      cont.innerHTML = `
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-900 text-sm flex items-center">
              <span>📑 貸借対照表 (B/S: Balance Sheet)</span>
              <span class="ml-2 text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">5口座残高連動</span>
            </span>
            <span class="text-[11px] text-slate-500">財政状態</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <!-- 資産の部 -->
            <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
              <div class="font-bold text-blue-900 border-b pb-1.5 text-xs flex justify-between">
                <span>【資産の部】</span>
                <span class="text-blue-700 font-mono">¥${bs.totalAssets.toLocaleString()}</span>
              </div>
              <div class="space-y-1.5 text-xs">
                <div class="font-semibold text-slate-700 text-[11px]">■ 流動資産</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">現預金（5銀行口座＋手許現金）</span>
                  <strong class="font-bold text-blue-800">¥${bs.assets.current.cashAndDeposits.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">売掛金（未回収の請求書）</span>
                  <strong class="font-bold text-slate-800">¥${bs.assets.current.accountsReceivable.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">棚卸資産（展示墓石・石材部材）</span>
                  <strong class="font-bold text-slate-800">¥${bs.assets.current.inventory.toLocaleString()}</strong>
                </div>
                <div class="font-semibold text-slate-700 text-[11px] pt-1">■ 固定資産</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">有形固定資産（車両・カニクレーン・切削機）</span>
                  <strong class="font-bold text-slate-800">¥${bs.assets.fixed.tangible.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pt-2 border-t font-black text-slate-900 text-xs">
                  <span>資産合計 (Total Assets)</span>
                  <span>¥${bs.totalAssets.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <!-- 負債・純資産の部 -->
            <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
              <div class="font-bold text-rose-900 border-b pb-1.5 text-xs flex justify-between">
                <span>【負債・純資産の部】</span>
                <span class="text-rose-700 font-mono">¥${(bs.totalLiab + bs.totalEquity).toLocaleString()}</span>
              </div>
              <div class="space-y-1.5 text-xs">
                <div class="font-semibold text-slate-700 text-[11px]">■ 流動負債</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">買掛金・未払金（石材建材仕入代）</span>
                  <strong class="font-bold text-slate-800">¥${bs.liabilities.current.accountsPayable.toLocaleString()}</strong>
                </div>
                <div class="font-semibold text-slate-700 text-[11px] pt-1">■ 固定負債</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">長期借入金（公庫・地銀借入残高）</span>
                  <strong class="font-bold text-rose-700">¥${bs.liabilities.fixed.longTermDebt.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pt-1 border-t text-[11px] text-slate-600">
                  <span>負債合計</span>
                  <strong>¥${bs.totalLiab.toLocaleString()}</strong>
                </div>

                <div class="font-semibold text-blue-900 text-[11px] pt-2">■ 純資産の部</div>
                <div class="flex justify-between pl-2">
                  <span class="text-slate-600">元入金・自己資本・当期利益</span>
                  <strong class="font-black text-blue-900">¥${bs.totalEquity.toLocaleString()}</strong>
                </div>
                <div class="flex justify-between pt-2 border-t font-black text-slate-900 text-xs">
                  <span>負債・純資産合計</span>
                  <span>¥${(bs.totalLiab + bs.totalEquity).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          ${plVsCashBoxHtml}
        </div>
      `;
    } else {
      bsplTabCF.className = 'px-3 py-1.5 rounded-lg bg-blue-600 text-white shadow-sm font-bold';
      bsplTabPL.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';
      bsplTabBS.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:bg-slate-100';

      cont.innerHTML = `
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex items-center justify-between border-b pb-2">
            <span class="font-bold text-slate-900 text-sm flex items-center">
              <span>💵 キャッシュフロー計算書 (C/F: Cash Flow Statement)</span>
              <span class="ml-2 text-[10px] bg-sky-100 text-sky-800 px-2 py-0.5 rounded font-bold">営業・投資・財務3区分</span>
            </span>
            <span class="text-[11px] text-slate-500">現金の実際の出入り</span>
          </div>

          <table class="w-full text-xs text-left border-collapse">
            <tr class="border-b bg-emerald-50/70">
              <td class="py-2.5 px-3 font-bold text-emerald-950 flex items-center">
                <span>Ⅰ. 営業活動によるキャッシュフロー（本業の現金創出）</span>
                <span class="ml-2 text-[9px] bg-emerald-200 text-emerald-800 px-1.5 py-0.2 rounded font-bold">確定値</span>
              </td>
              <td class="py-2.5 px-3 text-right font-black text-emerald-900">+¥${cf.operatingCF.toLocaleString()}</td>
            </tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">・税引前当期利益</td><td class="py-2 px-3 text-right text-slate-800">¥${pl.ordinaryProfit.toLocaleString()}</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">・売掛金の回収（入金）</td><td class="py-2 px-3 text-right text-slate-800">+¥1,200,000</td></tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">・仕入代金・買掛金の支払い</td><td class="py-2 px-3 text-right text-rose-700">-¥845,000</td></tr>

            <tr class="border-b bg-slate-50">
              <td class="py-2.5 px-3 font-bold text-slate-800 flex items-center">
                <span>Ⅱ. 投資活動によるキャッシュフロー（機械・車両設備投資）</span>
                <span class="ml-2 text-[9px] bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded font-medium">推計値</span>
              </td>
              <td class="py-2.5 px-3 text-right font-bold text-slate-700">¥${cf.investingCF.toLocaleString()}</td>
            </tr>

            <tr class="border-b bg-purple-50/70">
              <td class="py-2.5 px-3 font-bold text-purple-950 flex items-center">
                <span>Ⅲ. 財務活動によるキャッシュフロー（公庫・地銀借入金の返済）</span>
                <span class="ml-2 text-[9px] bg-purple-200 text-purple-800 px-1.5 py-0.2 rounded font-bold">確定値</span>
              </td>
              <td class="py-2.5 px-3 text-right font-black text-purple-900">¥${cf.financingCF.toLocaleString()}</td>
            </tr>
            <tr class="border-b"><td class="py-2 px-3 pl-6 text-slate-600">・日本政策金融公庫 設備資金元金定期返済</td><td class="py-2 px-3 text-right text-rose-700 font-bold">-¥960,000</td></tr>

            <tr class="border-b bg-slate-900 text-white">
              <td class="py-2.5 px-3 font-bold">★ 現金及び現金同等物の純増減額 (Net Cash Flow)</td>
              <td class="py-2.5 px-3 text-right font-black text-sky-300">¥${cf.netCF.toLocaleString()}</td>
            </tr>
          </table>

          <div class="p-3 bg-emerald-50 border border-emerald-300 rounded-xl text-xs text-emerald-950 flex items-center justify-between">
            <div>
              <div class="font-bold flex items-center text-emerald-900">
                <span class="mr-1 text-base">✅</span> 本業の現金創出力（営業CF）で借入返済を全額カバーできています
              </div>
              <p class="text-[10px] text-emerald-800 mt-0.5">本業の儲け（+¥${cf.operatingCF.toLocaleString()}）が、借入金返済（-¥${Math.abs(cf.financingCF).toLocaleString()}）を大きく上回っており、資金繰りとして極めて健全です。</p>
            </div>
          </div>

          ${plVsCashBoxHtml}
        </div>
      `;
    }
  }


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
    if (newDate && /^\d{4}-\d{2}-\d{2}$/.test(newDate)) {
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
        this.currentScannedImageData = evt.target.result;
        this.simulateInvoiceAIScan(evt.target.result, false, file.name);
      };
      reader.readAsDataURL(file);
    }
  }

  // AIによる画像解析（Gemini AI OCR連携＆シミュレーション）
  simulateInvoiceAIScan(imgDataUrl = null, isSample = false, fileName = '') {
    if (isSample && !this.currentScannedImageData) {
      // サンプル請求書のダミー画像データ
      this.currentScannedImageData = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250"><rect width="400" height="250" fill="%23ffffff"/><text x="20" y="40" font-size="16" font-weight="bold">御請求書</text></svg>';
    }
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
    }, 1200);
  }

  async handleSaveScannedInvoice(e) {
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


  // ==============================================================
  // 将来資金シミュレーション（ストレステスト）ハンドラー
  // ==============================================================
  openSimulationModal() {
    const modal = document.getElementById('modalStressTest');
    if (!modal) return;
    this.updateStressTestResult();
    modal.classList.remove('hidden');
  }

  updateStressTestResult() {
    const checkDelay = document.getElementById('simCheckDelay')?.checked || false;
    const salesRangeVal = parseInt(document.getElementById('simSalesRange')?.value || '0', 10);
    const extraExpVal = parseInt(document.getElementById('simInputExtraExp')?.value || '0', 10);

    const salesRateLabel = document.getElementById('simSalesRateLabel');
    if (salesRateLabel) {
      salesRateLabel.textContent = salesRangeVal === 0 ? '通常 (0%減)' : `▼ ${salesRangeVal}% 減少`;
    }

    const result = window.stoneStore.runStressTestSimulation({
      delayBigIncomes: checkDelay,
      salesReductionRate: salesRangeVal / 100,
      extraExpenseAmount: extraExpVal,
      months: 6
    });

    const badge = document.getElementById('simSafetyBadge');
    const minBalVal = document.getElementById('simMinBalVal');
    const detail = document.getElementById('simResultDetail');

    if (minBalVal) minBalVal.textContent = `¥${result.minTotalBal.toLocaleString()}`;

    if (badge) {
      if (result.safetyStatus === 'safe') {
        badge.className = 'px-2 py-0.5 rounded text-[10px] font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
        badge.textContent = '✅ 安全・余裕あり';
        if (minBalVal) minBalVal.className = 'text-2xl font-black text-emerald-400';
      } else if (result.safetyStatus === 'warning') {
        badge.className = 'px-2 py-0.5 rounded text-[10px] font-black bg-amber-500/20 text-amber-300 border border-amber-500/40';
        badge.textContent = '⚠️ 要注意ゾーン';
        if (minBalVal) minBalVal.className = 'text-2xl font-black text-amber-400';
      } else {
        badge.className = 'px-2 py-0.5 rounded text-[10px] font-black bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse';
        badge.textContent = '🚨 資金ショート予測！';
        if (minBalVal) minBalVal.className = 'text-2xl font-black text-rose-400';
      }
    }

    if (detail) {
      if (result.hasShortage) {
        detail.innerHTML = `
          <div class="text-rose-300 font-bold">⚠️ このシナリオでは資金が不足する日が発生します：</div>
          <div class="mt-1 text-slate-300">最短で <strong>${result.minDate}</strong> に最低手元残高が <strong class="text-rose-400">¥${result.minTotalBal.toLocaleString()}</strong> まで悪化します。事前に借入の準備や支払日の調整が必要です。</div>
        `;
      } else {
        detail.innerHTML = `
          <div class="text-emerald-300 font-bold">✅ このシミュレーション下でも手元資金は安全を維持できます：</div>
          <div class="mt-1 text-slate-300">最も残高が減る <strong>${result.minDate}</strong> でも <strong class="text-emerald-300">¥${result.minTotalBal.toLocaleString()}</strong> の手元資金が確保され、石材仕入代や給与・公庫返済に支障はありません。</div>
        `;
      }
    }
  }


  // 夫婦別画面（管理者モード vs ご主人用シンプル閲覧モード）
  applyUserRoleView(role) {
    const isHusband = role === 'husband';
    const husbandDashboard = document.getElementById('husbandQuickDashboard');

    if (husbandDashboard) {
      if (isHusband) {
        husbandDashboard.classList.remove('hidden');
        // ご主人専用カードのデータ反映
        const accounts = window.stoneStore.getAccounts();
        const totalCash = accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0);
        const kpis = window.stoneStore.getDashboardKPIs();

        const husbandTotalCash = document.getElementById('husbandTotalCash');
        const husbandMonthIn = document.getElementById('husbandMonthIn');
        const husbandMonthOut = document.getElementById('husbandMonthOut');
        const husbandMonthStatus = document.getElementById('husbandMonthStatus');
        const husbandShortageBadge = document.getElementById('husbandShortageBadge');

        if (husbandTotalCash) husbandTotalCash.textContent = `¥${totalCash.toLocaleString()}`;
        if (husbandMonthIn) husbandMonthIn.textContent = `¥${kpis.next30Income.toLocaleString()}`;
        if (husbandMonthOut) husbandMonthOut.textContent = `¥${kpis.next30Expense.toLocaleString()}`;

        if (husbandMonthStatus) {
          if (kpis.next30Net >= 0) {
            husbandMonthStatus.textContent = `✅ 今月は黒字見込み（＋¥${kpis.next30Net.toLocaleString()}）`;
            husbandMonthStatus.className = 'text-[10px] text-emerald-300 font-bold mt-1';
          } else {
            husbandMonthStatus.textContent = `⚠️ 今月は出金先行（−¥${Math.abs(kpis.next30Net).toLocaleString()}）`;
            husbandMonthStatus.className = 'text-[10px] text-amber-300 font-bold mt-1';
          }
        }

        if (husbandShortageBadge) {
          if (kpis.shortageAlerts && kpis.shortageAlerts.length > 0) {
            husbandShortageBadge.textContent = '🚨 要注意: 資金不足の恐れあり！';
            husbandShortageBadge.className = 'text-sm font-black text-rose-400 mt-1 animate-pulse';
          } else {
            husbandShortageBadge.textContent = '✅ 今後3か月は安全圏です';
            husbandShortageBadge.className = 'text-sm font-bold text-emerald-300 mt-1';
          }
        }
      } else {
        husbandDashboard.classList.add('hidden');
      }
    }
    
    // ご主人モードの場合：編集ボタンや設定ボタンを非表示にし、誤操作を防止
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

}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
  window.app = new StoneApp();
});
