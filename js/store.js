/**
 * 中川石材 業務管理システム - データストア & ビジネスロジック
 * LocalStorageによる端末内保存、資金繰り表シミュレーション、費目別支出分析
 */

const STORAGE_KEY = 'nakagawa_stone_app_data_v8'; // v8: Misoca確定請求書データ（13件・未回収86.8万円）完全内蔵版 // v7: 弥生確定仕訳（2026年全月キャッシュフロー・実取引543件）完全統合版

// 勘定科目・費目マスター（石材店特化）
const EXPENSE_CATEGORIES = [
  { group: '原価・仕入・工事費', key: '石材仕入', name: '石材仕入代（墓石・外柵・納骨部材）', color: '#2563eb' },
  { group: '原価・仕入・工事費', key: '建材仕入', name: '基礎建材費（生コン・セメント・砕石）', color: '#3b82f6' },
  { group: '原価・仕入・工事費', key: '重機リース', name: '重機・クレーン・運搬費', color: '#60a5fa' },
  { group: '原価・仕入・工事費', key: '外注工賃', name: '字彫り・加工外注工賃', color: '#93c5fd' },
  
  { group: '人件費', key: '給与手当', name: '給与手当・専従者給与', color: '#f59e0b' },
  
  { group: '固定費・現場経費', key: '車両・燃料', name: '車両費・ガソリン・高速代', color: '#10b981' },
  { group: '固定費・現場経費', key: '消耗品・工具', name: '消耗品費・工具（砥石・ゴム等）', color: '#34d399' },
  { group: '固定費・現場経費', key: '損害保険料', name: '損害保険料（車両・請負賠償）', color: '#059669' },
  { group: '固定費・現場経費', key: '通信・光熱費', name: '水道光熱費・事務所通信費', color: '#6ee7b7' },
  
  { group: '財務・税務', key: '借入返済', name: '借入金返済（公庫・はくさん信金）', color: '#8b5cf6' },
  { group: '財務・税務', key: '税金・積立', name: '租税公課・消費税積立', color: '#a78bfa' },
  { group: 'その他', key: 'その他経費', name: 'その他雑費・研修費・諸会費', color: '#94a3b8' }
];

const INCOME_CATEGORIES = [
  { group: '工事売上', key: '墓石新設代', name: '墓所新設工事代（着工・完工）' },
  { group: '工事売上', key: '改修・補修代', name: '墓所改修・補修工事代' },
  { group: '工事売上', key: '戒名彫刻・納骨', name: '戒名追加彫刻・納骨料' },
  { group: '工事売上', key: '墓じまい代', name: '墓じまい・更地返還工事代' },
  { group: 'その他', key: 'その他収入', name: '雑収入・その他収入' }
];

// 中川石材様 実口座マスター（北國銀行3口座 + JA + はくさん信金 + 手許現金の計6財布）
const DEFAULT_ACCOUNTS = [
  { id: 'bank-1', name: '北國銀行（18277）', shortName: '北國(18277)', type: 'bank', baseBalance: 7768, baseDate: '2026-11-20', color: '#2563eb' },
  { id: 'bank-2', name: '北国銀行（199439）', shortName: '北国(199439)', type: 'bank', baseBalance: 12634, baseDate: '2026-11-20', color: '#059669' },
  { id: 'bank-3', name: '北國銀行', shortName: '北國銀行', type: 'bank', baseBalance: 159482, baseDate: '2026-11-20', color: '#16a34a' },
  { id: 'bank-4', name: 'JAバンク', shortName: 'JAバンク', type: 'bank', baseBalance: 1751826, baseDate: '2026-11-20', color: '#d97706' },
  { id: 'bank-5', name: 'はくさん信用金庫', shortName: 'はくさん信金', type: 'bank', baseBalance: 277413, baseDate: '2026-11-20', color: '#8b5cf6' },
  { id: 'cash', name: '手許現金（金庫・財布実査）', shortName: '手許現金', type: 'cash', baseBalance: 0, yayoiBookCash: 3157350, isManualCashLocked: true, baseDate: '2026-11-20', color: '#e11d48' }
];

// 中川石材様 本番実データ（2026年 弥生残高試算表 確定値）
const INITIAL_DATA = {
  accounts: DEFAULT_ACCOUNTS,
  currentUser: 'wife',

  // 弥生データ管理（残高試算表 B/S・P/L・キャッシュフロー完全確定）
  yayoiData: {
    lastImportedAt: '2026/11/20 20:55:16',
    importedFileName: '20261120仕訳帳-2.csv',
    importedType: 'trial_balance',
    importedCount: 6,
    importedKeys: [],
    errors: [],
    // 損益計算書（P/L）
    pl: {
      sales: 14251417,         // 売上高（売上 14,221,417 + 雑収入 30,000）
      cogs: 3972333,          // 売上原価（仕入 2,380,333 + 外注工賃 1,592,000）
      grossProfit: 10279084,   // 売上総利益（粗利 72.1%）
      sga: 5331738,           // 販管費（水道光熱、消耗品、旅費、通信、税理士報酬、車両費、雑費等）
      operatingProfit: 4947346, // 営業利益（黒字）
      nonOperatingExpense: 41032, // 利子割引料
      ordinaryProfit: 4947346  // 控除前の所得金額（約495万円の黒字）
    },
    // 貸借対照表（B/S）
    bs: {
      assets: {
        current: {
          cashAndDeposits: 5366473, // 現金 3,157,350 + 預金 2,209,123
          accountsReceivable: 0,   // 売掛金
          inventory: 0            // 在庫
        },
        fixed: {
          tangible: 2,             // 機械装置 1円 + 車両運搬具 1円
          intangible: 229759       // ソフトウェア 229,759円
        }
      },
      liabilities: {
        current: {
          accountsPayable: 0,      // 未払金は期間中完済
          creditCard: -14517       // 楽天カード
        },
        fixed: {
          longTermDebt: 9468000    // 借入金（はくさん信金 7,692,000 + 公庫 1,776,000）
        }
      },
      equity: {
        capital: 4947346           // 控除前所得金額
      }
    },
    // キャッシュフロー計算書（C/F：間接法）
    cf: {
      operatingCF: 4947346,        // 営業活動によるキャッシュフロー（本業黒字）
      investingCF: 0,              // 投資活動によるCF
      financingCF: -1001000,       // 財務活動によるCF（期間借入金元金返済: 100.1万円返済実績！）
      netCF: 3946346               // 純資金増減
    }
  },
  // Misoca連携データ（中川石材様 実請求書13件・未回収9件 ¥868,890 完全内蔵）
  misocaData: {
    lastImportedAt: '2026-11-20 21:53',
    invoices: (typeof NAKAGAWA_INITIAL_MISOCA_INVOICES !== 'undefined' ? NAKAGAWA_INITIAL_MISOCA_INVOICES : []),
    estimates: []
  },
  // 1. 口座残高
  bankAccount: {
    baseDate: '2026-11-20',
    baseBalance: 5366473,
    bankName: '北國銀行・JA・はくさん信金・手許現金',
    lastUpdated: '2026-11-20 20:55'
  },
  // 2. タスク（初期は空）
  tasks: [],
  // 3. 入出金予定・実績（弥生会計2026年確定出納543件を完全統合）
  transactions: (typeof NAKAGAWA_INITIAL_TRANSACTIONS !== 'undefined' ? NAKAGAWA_INITIAL_TRANSACTIONS : []),

  // 4. 工事・お客様案件
  projects: [
    {
      id: 'proj-1',
      name: '佐藤家 墓所新規建立工事（洋型・黒御影）',
      customerName: '佐藤 正雄 様',
      siteLocation: '市営青山霊園 2区3号',
      scheduleDate: '2026-11-05 〜 2026-12-10',
      assignee: '夫（施工）・私（設計/経理）',
      status: 'contracted',
      statusLabel: '契約済・石材手配中',
      nextAction: '11/5 基礎生コン打設、霊園養生計画書の提出',
      driveLinks: {
        drawing: 'https://drive.google.com/drive/folders/sample-sato-drawing',
        estimate: 'https://drive.google.com/drive/folders/sample-sato-estimate',
        invoice: 'https://drive.google.com/drive/folders/sample-sato-invoice',
        photos: 'https://drive.google.com/drive/folders/sample-sato-photos'
      },
      contractAmount: 1700000,
      note: 'お客様のご要望で正面文字は「絆」を彫刻。家紋は花立に彫る。'
    },
    {
      id: 'proj-2',
      name: '宗教法人 田中寺様 歴代住職墓所 改修補修工事',
      customerName: '田中寺 住職様',
      siteLocation: '寺院境内 歴代墓域',
      scheduleDate: '2026-11-12 〜 2026-11-28',
      assignee: '夫',
      status: 'drawing',
      statusLabel: '見積・図面提出中',
      nextAction: '家紋彫刻位置修正図面をご住職へ持参・最終承諾受領',
      driveLinks: {
        drawing: 'https://drive.google.com/drive/folders/sample-tanakaji-drawing',
        estimate: 'https://drive.google.com/drive/folders/sample-tanakaji-estimate',
        invoice: '',
        photos: 'https://drive.google.com/drive/folders/sample-tanakaji-photos'
      },
      contractAmount: 1200000,
      note: '11月末の法要までに完成必須。参道の敷石段差解消も含む。'
    },
    {
      id: 'proj-3',
      name: '高橋家 戒名追加彫刻・納骨法要準備',
      customerName: '高橋 健一 様',
      siteLocation: '長福寺霊園 5列12番',
      scheduleDate: '2026-11-01 〜 2026-11-18',
      assignee: '私（原稿）・夫（現場彫刻）',
      status: 'carving',
      statusLabel: '文字原稿確認中',
      nextAction: '原稿OK後、ゴムシート版下作成・現地ブラスト彫刻日確定',
      driveLinks: {
        drawing: 'https://drive.google.com/drive/folders/sample-takahashi-text',
        estimate: 'https://drive.google.com/drive/folders/sample-takahashi-estimate',
        invoice: '',
        photos: ''
      },
      contractAmount: 55000,
      note: '四十九日法要：11月21日(土) 午前10時開式。納骨お手伝い要。'
    }
  ],

  // 5. 作業履歴（時系列ログ）
  activityLogs: [
    {
      id: 'log-1',
      timestamp: '2026-10-31 09:30',
      user: '私',
      category: '弥生会計',
      action: '弥生会計 9月分経理入力進捗',
      details: '【対象月】2026年9月分\n【資料の種類】銀行通帳コピー・クレジットカード利用明細\n【完了範囲】通帳出納帳の全額記帳・照合完了\n【残作業】Amazonで購入した工具・文具の領収書2枚の勘定科目確認（夫へ相談）',
      projectId: null
    },
    {
      id: 'log-2',
      timestamp: '2026-10-31 08:45',
      user: '夫',
      category: '現地調査',
      action: '佐藤家 青山霊園現地寸法確認・通路養生確認',
      details: '境界杭確認。隣接墓所との離隔30cm確保可能。カニクレーン進入路に段差あり、ゴムマット3枚追加持参必要。',
      projectId: 'proj-1'
    },
    {
      id: 'log-3',
      timestamp: '2026-10-30 16:20',
      user: '私',
      category: '図面・原稿',
      action: '高橋様より受領した戒名文字の原稿下絵をCAD取込',
      details: '「釋信秀」の文字バランス確認。既存の先代戒名文字と書体を統一してプレビュー作成。',
      projectId: 'proj-3'
    },
    {
      id: 'log-4',
      timestamp: '2026-10-30 14:00',
      user: '私',
      category: '振込・支払い',
      action: '9月締め外注費の振込実行',
      details: '墓誌彫刻外注費 ¥45,000 をネットバンキングより振込完了。',
      projectId: null
    },
    {
      id: 'log-5',
      timestamp: '2026-10-29 15:30',
      user: '夫',
      category: '納骨・法要',
      action: '鈴木家 納骨式のお手伝い完了',
      details: '雨天のため養生テント設営。納骨棺内の清掃とサラシ骨袋への移し替えを無事終了。ご遺族より御礼のお言葉をいただく。',
      projectId: null
    }
  ],

  // 6. 重要メール
  emails: [
    {
      id: 'mail-1',
      sender: '株式会社東日本石材 営業部 <order@higashinihon-stone.example.jp>',
      senderName: '(株)東日本石材',
      subject: '【納期回答】佐藤様邸 外柵材・納骨室部材の船便入荷について',
      date: '2026-10-30 17:15',
      dueDate: '2026-11-02',
      assignee: '私',
      isRead: true,
      isProcessed: false,
      body: 'いつも大変お世話になっております。東日本石材の佐々木です。\n\nご発注いただいておりました「佐藤様邸 外柵・納骨室部材（インド産黒御影・インド白御影）」ですが、港湾荷揚げが順調に進み、予定より1日早い【11月4日(水) 午前9時】に御社ヤードへ4tユニック車にて納品可能となりました。\n\n荷受け体制およびヤードの空き状況についてご返信いただけますと幸いです。よろしくお願い申し上げます。',
      mailUrl: 'https://mail.google.com/mail/u/0/#inbox/sample-mail-1',
      taskCreated: false
    },
    {
      id: 'mail-2',
      sender: '宗教法人 田中寺 住職 <tanakaji-jushoku@example.com>',
      senderName: '田中寺 住職様',
      subject: '歴代住職墓所の補修お見積りについて（家紋位置の変更相談）',
      date: '2026-10-29 11:20',
      dueDate: '2026-11-01',
      assignee: '私',
      isRead: true,
      isProcessed: false,
      body: '中川石材様\n\n先日はお忙しいところご来寺いただき、また詳細な見積書と図面をお送りいただきありがとうございました。\n役員会にて検討いたしまして、基本的にはこの内容で進めていただきたく存じます。\n一点だけ、墓前灯篭に刻む寺紋の大きさを一回り小さくし、右上に寄せることは可能でしょうか。\n法要日程が11月28日に迫っておりますため、一度お電話かお寺にてお打ち合わせできれば幸いです。',
      mailUrl: 'https://mail.google.com/mail/u/0/#inbox/sample-mail-2',
      taskCreated: false
    },
    {
      id: 'mail-3',
      sender: '市営霊園管理事務所 <reien-kanri@city.example.jp>',
      senderName: '市営霊園管理事務所',
      subject: '【重要】墓地工事施工届の受付および現地養生計画の追記依頼',
      date: '2026-10-28 09:00',
      dueDate: '2026-10-30',
      assignee: '夫',
      isRead: true,
      isProcessed: false,
      body: '中川石材様\n\n青山霊園2区3号（佐藤様墓所）の工事施工届を受理いたしました。\n霊園管理規定に基づき、隣接墓所への飛散防止養生ネットの仕様、および運搬車通行時の敷板設置計画を別紙図面に追記し、再提出をお願いいたします。\n確認完了後に施工承認番号を発行いたします。',
      mailUrl: 'https://mail.google.com/mail/u/0/#inbox/sample-mail-3',
      taskCreated: true
    },
    {
      id: 'mail-4',
      sender: '墓石業界ニュース <newsletter@stone-weekly.example.com>',
      senderName: '石材業界ニュース（広告・メルマガ）',
      subject: '【新商品】超低騒音型携帯ブラスト機のご案内',
      date: '2026-10-27 10:00',
      dueDate: '',
      assignee: '夫',
      isRead: true,
      isProcessed: true,
      body: '霊園での戒名彫刻に最適な、超低騒音コンプレッサー搭載の移動式サンドブラスト機が登場しました。無料デモ機貸出中...',
      mailUrl: 'https://mail.google.com/mail/u/0/#inbox/sample-mail-4',
      taskCreated: false,
      isNoticeOrAd: true
    }
  ]
};

// ストアクラス
class StoneAppStore {
  constructor() {
    this.data = this.loadData();
    this.listeners = [];
  }

  loadData() {
    try {
      let saved = localStorage.getItem(STORAGE_KEY);
      if (!saved) {
        // v3 からの自動移行
        saved = localStorage.getItem('nakagawa_stone_app_data_v3');
      }
      if (saved) {
        const parsed = JSON.parse(saved);
        const mergedAccounts = (parsed.accounts && parsed.accounts.length > 0)
          ? parsed.accounts
          : JSON.parse(JSON.stringify(DEFAULT_ACCOUNTS));

        // 手入力現金バックアップの復元・引き継ぎ
        try {
          if (typeof localStorage !== 'undefined') {
            const savedManualCash = localStorage.getItem('nakagawa_stone_manual_cash');
            if (savedManualCash !== null) {
              const cashAcc = mergedAccounts.find(a => a.id === 'cash');
              if (cashAcc) {
                cashAcc.baseBalance = parseInt(savedManualCash, 10) || 0;
                cashAcc.isManualCashLocked = true;
              }
            }
          }
        } catch (e) {}
        
        // 取引データの口座補完
        const mergedTransactions = (parsed.transactions || INITIAL_DATA.transactions).map(tx => {
          if (!tx.accountId && tx.type !== 'transfer') {
            if (tx.category === '給与手当' || tx.category === '借入返済' || tx.category === '車両・燃料') {
              tx.accountId = 'bank-2'; // 十六銀行
            } else if (tx.category === '消耗品・工具') {
              tx.accountId = 'cash'; // 手許現金
            } else if (tx.category === '通信・光熱費') {
              tx.accountId = 'bank-4'; // 大垣共立
            } else if (tx.category === '戒名彫刻・納骨') {
              tx.accountId = 'bank-3'; // ゆうちょ
            } else {
              tx.accountId = 'bank-1'; // 中京銀行
            }
          }
          return tx;
        });

        return {
          ...INITIAL_DATA,
          ...parsed,
          accounts: mergedAccounts,
          transactions: mergedTransactions,
          bankAccount: { ...INITIAL_DATA.bankAccount, ...(parsed.bankAccount || {}) }
        };
      }
    } catch (e) {
      console.warn('Failed to load data from localStorage:', e);
    }
    return JSON.parse(JSON.stringify(INITIAL_DATA));
  }

  saveData() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data));
    } catch (e) {
      console.error('Failed to save data to localStorage:', e);
    }
    this.notify();

    // Googleドライブへの自動同期（デバウンス実行：1.5秒後に自動送信）
    this.scheduleAutoSyncToGDrive();
  }

  scheduleAutoSyncToGDrive() {
    const gasUrl = this.getGDriveGasUrl();
    if (!gasUrl) return;

    if (this._gdriveSyncTimer) {
      clearTimeout(this._gdriveSyncTimer);
    }
    this._gdriveSyncTimer = setTimeout(() => {
      this.syncToGDrive().catch(err => console.warn('Auto GDrive sync error:', err));
    }, 1500);
  }

  // Googleドライブへ現在の全データを送信・保存
  async syncToGDrive() {
    const gasUrl = this.getGDriveGasUrl();
    if (!gasUrl) return { success: false, message: 'Google ドライブ連携URLが未設定です' };

    try {
      const resp = await fetch(gasUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: JSON.stringify({
          action: 'save_data',
          payload: this.data
        })
      });
      const res = await resp.json();
      if (res.success) {
        this.data.lastGDriveSyncAt = res.updatedAt || new Date().toISOString();
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data));
        return { success: true, updatedAt: this.data.lastGDriveSyncAt };
      } else {
        throw new Error(res.message || '保存に失敗しました');
      }
    } catch (err) {
      console.warn('Failed to sync data to Google Drive:', err);
      return { success: false, error: err.message };
    }
  }

  // Googleドライブから最新の全データを取得して反映
  async syncFromGDrive() {
    const gasUrl = this.getGDriveGasUrl();
    if (!gasUrl) return { success: false, message: 'Google ドライブ連携URLが未設定です' };

    try {
      const fetchUrl = gasUrl + (gasUrl.indexOf('?') === -1 ? '?action=load_data' : '&action=load_data');
      const resp = await fetch(fetchUrl, { method: 'GET', mode: 'cors' });
      const res = await resp.json();
      if (res.success && res.data) {
        this.data = res.data;
        this.data.lastGDriveSyncAt = res.updatedAt || new Date().toISOString();
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.data));
        this.notify();
        return { success: true, updatedAt: this.data.lastGDriveSyncAt };
      } else if (res.success && !res.data) {
        return { success: true, empty: true, message: 'Googleドライブ上に保存データはありません' };
      } else {
        throw new Error(res.message || 'データ読み込みに失敗しました');
      }
    } catch (err) {
      console.warn('Failed to load data from Google Drive:', err);
      return { success: false, error: err.message };
    }
  }

  // 外出用 暗証番号（PINコード）管理
  getSecurityPin() {
    return this.data.securityPin || localStorage.getItem('nakagawa_stone_security_pin') || '';
  }

  setSecurityPin(pin) {
    const cleanPin = (pin || '').trim();
    this.data.securityPin = cleanPin;
    if (cleanPin) {
      localStorage.setItem('nakagawa_stone_security_pin', cleanPin);
    } else {
      localStorage.removeItem('nakagawa_stone_security_pin');
    }
    this.saveData();
  }

  subscribe(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }

  notify() {
    this.listeners.forEach(cb => {
      try {
        cb(this.data);
      } catch (err) {
        console.error('Error in store listener:', err);
      }
    });
  }

  resetToSampleData() {
    this.data = JSON.parse(JSON.stringify(INITIAL_DATA));
    this.saveData();
  }

  // デモ用サンプルデータを全消去し、中川石材の本番環境（残高0・実データのみ）にする
  clearDemoData() {
    // 銀行口座の残高をすべて0円に初期化
    if (this.data.accounts) {
      this.data.accounts.forEach(a => {
        a.baseBalance = 0;
        a.lastUpdated = new Date().toISOString();
      });
    }
    // デモ取引・タスク・ログ・請求書を空に
    this.data.transactions = [];
    this.data.tasks = [];
    this.data.activityLogs = [];
    if (this.data.misocaData) {
      this.data.misocaData.invoices = [];
      this.data.misocaData.lastImportedAt = null;
    }
    // 弥生の財務三表デモ数値を0にリセット
    this.data.yayoiData = {
      lastImportedAt: null,
      importedFileName: null,
      importedCount: 0,
      importedKeys: [],
      errors: [],
      pl: { sales: 0, cogs: 0, grossProfit: 0, sga: 0, operatingProfit: 0, nonOperatingExpense: 0, ordinaryProfit: 0 },
      bs: {
        assets: { current: { cashAndDeposits: 0, accountsReceivable: 0, inventory: 0 }, fixed: { tangible: 0 } },
        liabilities: { current: { accountsPayable: 0 }, fixed: { longTermDebt: 0 } },
        equity: { capital: 0 }
      },
      cf: { operatingCF: 0, investingCF: 0, financingCF: 0, netCF: 0 }
    };
    this.saveData();
    return { success: true };
  }

  importData(jsonString) {
    try {
      const parsed = JSON.parse(jsonString);
      if (!parsed.bankAccount || !parsed.tasks) {
        throw new Error('データフォーマットが正しくありません。');
      }
      this.data = parsed;
      this.saveData();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  exportData() {
    return JSON.stringify(this.data, null, 2);
  }


  // ==============================================================
  // 口座マスター管理（5銀行口座 + 手許現金）
  // ==============================================================
  getAccounts() {
    if (!this.data.accounts || this.data.accounts.length === 0) {
      this.data.accounts = JSON.parse(JSON.stringify(DEFAULT_ACCOUNTS));
      this.saveData();
    }
    return this.data.accounts;
  }

  getAccount(accountId) {
    const accounts = this.getAccounts();
    return accounts.find(a => a.id === accountId) || null;
  }

  updateAccount(accountId, updates) {
    const accounts = this.getAccounts();
    const idx = accounts.findIndex(a => a.id === accountId);
    if (idx !== -1) {
      if (accountId === 'cash') {
        updates.isManualCashLocked = true;
        // 手入力現金を永続バックアップ保存
        try {
          if (typeof localStorage !== 'undefined' && updates.baseBalance !== undefined) {
            localStorage.setItem('nakagawa_stone_manual_cash', String(updates.baseBalance));
          }
        } catch (e) {}
      }
      accounts[idx] = { ...accounts[idx], ...updates, lastUpdated: new Date().toISOString() };
      this.saveData();
      return accounts[idx];
    }
    return null;
  }

  // 口座間振替の新規登録
  transferFunds({ date, fromAccountId, toAccountId, amount, note = '', isActual = false }) {
    if (!fromAccountId || !toAccountId || fromAccountId === toAccountId) {
      throw new Error('振替元と振替先には異なる口座を指定してください。');
    }
    const fromAcc = this.getAccount(fromAccountId);
    const toAcc = this.getAccount(toAccountId);
    const tx = {
      id: 'tx-tr-' + Date.now(),
      date: date || new Date().toISOString().slice(0, 10),
      type: 'transfer',
      fromAccountId,
      toAccountId,
      partner: `${fromAcc ? fromAcc.shortName : fromAccountId} ➔ ${toAcc ? toAcc.shortName : toAccountId}`,
      category: '口座間振替',
      amount: Number(amount) || 0,
      projectId: null,
      isActual: Boolean(isActual),
      note: note || '口座間資金移動'
    };
    this.addTransaction(tx);
    return tx;
  }

  // 取引の支払口座設定（未定からの決定・変更）
  setTransactionAccount(txId, accountId) {
    return this.updateTransaction(txId, { accountId: accountId || 'unassigned' });
  }

  // 取引の期日変更・入金遅延反映
  delayTransaction(txId, newDate, reason = '') {
    const tx = this.data.transactions.find(t => t.id === txId);
    if (!tx) return null;
    const originalDate = tx.originalDueDate || tx.date;
    const note = tx.note ? `${tx.note} (遅延: ${originalDate}➔${newDate} ${reason})` : `(期日変更: ${originalDate}➔${newDate})`;
    return this.updateTransaction(txId, {
      date: newDate,
      originalDueDate: originalDate,
      isDelayed: true,
      note
    });
  }


  // ==============================================================
  // 弥生会計CSV取り込み ＆ 財務三表（B/S・P/L・C/F）ロジック
  // ==============================================================
  getYayoiData() {
    if (!this.data.yayoiData) {
      this.data.yayoiData = JSON.parse(JSON.stringify(INITIAL_DATA.yayoiData));
    }
    return this.data.yayoiData;
  }

  // 財務三表データの取得（損益・貸借・キャッシュフロー・損益と現金の差異分析）
  getFinancialStatements() {
    const yayoi = this.getYayoiData();
    const accounts = this.getAccounts();
    const currentTotalCash = accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0);

    // 貸借対照表（B/S）の現預金残高を最新の5口座＋現金残高に動的連動
    const bs = JSON.parse(JSON.stringify(yayoi.bs));
    bs.assets.current.cashAndDeposits = currentTotalCash;
    const totalCurrentAssets = bs.assets.current.cashAndDeposits + bs.assets.current.accountsReceivable + bs.assets.current.inventory;
    const totalAssets = totalCurrentAssets + bs.assets.fixed.tangible;

    const totalCurrentLiab = bs.liabilities.current.accountsPayable;
    const totalLiab = totalCurrentLiab + bs.liabilities.fixed.longTermDebt;
    bs.equity.capital = totalAssets - totalLiab; // 資産 = 負債 + 純資産 の完全整合

    // 損益と現金残高の違いの要因分析（実鶴さん・ご主人向け解説）
    const pl = yayoi.pl;
    const plVsCashAnalysis = [
      { factor: '当期営業利益（儲け）', amount: pl.operatingProfit, type: 'plus', note: '本業で発生した利益' },
      { factor: '売掛金の未回収（売上計上済・未入金）', amount: -bs.assets.current.accountsReceivable, type: 'minus', note: '売上になったがまだ口座に入っていないお金' },
      { factor: '石材・展示墓石の在庫保有', amount: -bs.assets.current.inventory, type: 'minus', note: '仕入代金を先払いして在庫になっているお金' },
      { factor: '公庫・地銀の借入金元金返済', amount: yayoi.cf.financingCF, type: 'minus', note: '経費（P/L）にはならないが口座から確実に出ていく現金' },
      { factor: '買掛金・未払金の支払猶予', amount: bs.liabilities.current.accountsPayable, type: 'plus', note: '仕入れたがまだ支払っていない現金保留分' }
    ];

    return {
      lastImportedAt: yayoi.lastImportedAt,
      importedFileName: yayoi.importedFileName,
      importedCount: yayoi.importedCount,
      pl: yayoi.pl,
      bs: {
        ...bs,
        totalCurrentAssets,
        totalAssets,
        totalCurrentLiab,
        totalLiab,
        totalEquity: bs.equity.capital
      },
      cf: yayoi.cf,
      plVsCashAnalysis
    };
  }

  // やよいの青色申告オンライン 残高試算表（B/S・P/L）CSVパーサー
  // 各口座の現在残高（前期繰越込）、損益計算書、貸借対照表、間接法キャッシュフローを一撃確定
  importYayoiTrialBalance(csvText, fileName = '弥生残高試算表.csv') {
    const rawLines = csvText.split(/\r?\n/).filter(line => line.trim().length > 0);
    if (rawLines.length < 2) {
      throw new Error('残高試算表CSVの中身が空、または行数が不足しています。');
    }

    const firstLine = rawLines[0];
    const delimiter = (firstLine.match(/\t/g) || []).length > (firstLine.match(/,/g) || []).length ? '\t' : ',';
    
    const parseLine = (line) => {
      const res = [];
      let cur = '';
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const c = line[i];
        if (c === '"' || c === "'") inQuotes = !inQuotes;
        else if (c === delimiter && !inQuotes) { res.push(cur.trim()); cur = ''; }
        else cur += c;
      }
      res.push(cur.trim());
      return res.map(c => c.replace(/^["']|["']$/g, '').trim());
    };

    let isHeaderFound = false;
    let subjectIdx = -1;
    let subIdx = -1;
    let balanceIdx = -1;

    // 集計用変数
    let plSales = 0;
    let plCogs = 0;
    let plSga = 0;
    let plNonOpExp = 0;

    let bsCashAndDeposits = 0;
    let bsReceivable = 0;
    let bsInventory = 0;
    let bsFixedAssets = 0;
    let bsPayable = 0;
    let bsDebt = 0;
    let bsCapital = 0;

    const accountBalances = {};
    const updatedAccounts = [];

    for (let i = 0; i < rawLines.length; i++) {
      const lineStr = rawLines[i];
      const cols = parseLine(lineStr);
      if (cols.length < 1) continue;

      // 行の中から最後の数値（残高・累計金額）を抽出
      // △や▲のマイナス表記、カンマ・円マーク・空白を除去
      let lineBalance = 0;
      let hasNumber = false;
      for (let c = cols.length - 1; c >= 0; c--) {
        const val = cols[c];
        if (/[0-9]/.test(val)) {
          const isNegative = val.includes('-') || val.includes('△') || val.includes('▲');
          const cleanNum = parseInt(val.replace(/[^0-9]/g, ''), 10) || 0;
          lineBalance = isNegative ? -cleanNum : cleanNum;
          hasNumber = true;
          break;
        }
      }

      if (!hasNumber) continue; // 数字がない行（見出し等）はスキップ

      // 行全体のテキストから科目を柔軟に判定
      const lineText = lineStr.replace(/[\t,]/g, ' ');

      // --- A. 銀行口座・現金残高の自動判定と更新（中川石材様 実口座適合） ---
      const matchAccountId = (text) => {
        if (text.includes('18277')) return 'bank-1'; // 北國銀行（18277）
        if (text.includes('199439')) return 'bank-2'; // 北国銀行（199439）
        if (text.includes('北國') || text.includes('北国')) return 'bank-3'; // 北國銀行
        if (text.includes('JA') || text.includes('農協')) return 'bank-4'; // JAバンク
        if (text.includes('はくさん') || text.includes('白山')) return 'bank-5'; // はくさん信用金庫
        if (text.includes('現金') && !text.includes('預金') && !text.includes('振込')) return 'cash'; // 手許現金
        return null;
      };

      const accId = matchAccountId(lineText);
      if (accId) {
        accountBalances[accId] = lineBalance;
        if (!updatedAccounts.includes(accId)) updatedAccounts.push(accId);
        bsCashAndDeposits += lineBalance;
      }

      // --- B. B/S 資産科目 ---
      if (lineText.includes('売掛金') || lineText.includes('受取手形')) bsReceivable = Math.max(bsReceivable, lineBalance);
      else if (lineText.includes('棚卸') || lineText.includes('商品') || lineText.includes('製品') || lineText.includes('原材料') || lineText.includes('石材')) bsInventory = Math.max(bsInventory, lineBalance);
      else if (lineText.includes('車両') || lineText.includes('機械') || lineText.includes('建物') || lineText.includes('土地') || lineText.includes('工具器具')) bsFixedAssets = Math.max(bsFixedAssets, lineBalance);

      // --- C. B/S 負債・純資産科目 ---
      else if (lineText.includes('買掛金') || lineText.includes('未払金') || lineText.includes('支払手形')) bsPayable = Math.max(bsPayable, lineBalance);
      else if (lineText.includes('借入金') || lineText.includes('公庫') || lineText.includes('地銀')) bsDebt = Math.max(bsDebt, lineBalance);
      else if (lineText.includes('元入金') || lineText.includes('資本金') || lineText.includes('事業主借')) bsCapital = Math.max(bsCapital, lineBalance);

      // --- D. P/L 収益科目 ---
      else if (lineText.includes('売上') || lineText.includes('完成工事高') || lineText.includes('加工高')) plSales = Math.max(plSales, lineBalance);

      // --- E. P/L 原価科目 ---
      else if (lineText.includes('仕入') || lineText.includes('材料費') || lineText.includes('外注加工') || lineText.includes('重機リース') || lineText.includes('労務費')) plCogs = Math.max(plCogs, lineBalance);

      // --- F. P/L 販管費科目 ---
      else if (lineText.includes('給料') || lineText.includes('報酬') || lineText.includes('専従者') ||
               lineText.includes('車両') || lineText.includes('燃料') || lineText.includes('消耗品') ||
               lineText.includes('通信') || lineText.includes('水道') || lineText.includes('保険') ||
               lineText.includes('交際') || lineText.includes('旅費') || lineText.includes('地代') ||
               lineText.includes('雑費') || lineText.includes('減価償却') || lineText.includes('租税')) {
        plSga += lineBalance;
      } else if (lineText.includes('利息') || lineText.includes('割引料')) {
        plNonOpExp += lineBalance;
      }
    }

    // 口座マスターの残高を弥生残高試算表の確定残高で直接上書き更新（B/Sデータが含まれる場合のみ）
    const nowStr = new Date().toLocaleString('ja-JP');
    const todayYMD = new Date().toISOString().slice(0, 10);
    const hasBSData = updatedAccounts.length > 0 || bsReceivable > 0 || bsPayable > 0 || bsDebt > 0;
    const hasPLData = plSales > 0 || plCogs > 0 || plSga > 0;

    if (hasBSData && this.data.accounts) {
      this.data.accounts.forEach(acc => {
        // ★【最重要】手許現金（cash）は弥生の机上データで絶対に上書きしない！
        if (acc.id === 'cash') {
          if (accountBalances['cash'] !== undefined) {
            acc.yayoiBookCash = accountBalances['cash']; // 弥生帳簿上の現金残高は別プロパティに退避記録
          }
          acc.isManualCashLocked = true;
          return; // 手入力された実査金額を100%死守！
        }
        if (accountBalances[acc.id] !== undefined) {
          acc.baseBalance = accountBalances[acc.id];
          acc.baseDate = todayYMD;
          acc.lastUpdated = new Date().toISOString();
        }
      });
    }

    // 既存の弥生データを取得（無ければ初期化）
    const prevYayoi = this.data.yayoiData || JSON.parse(JSON.stringify(INITIAL_DATA.yayoiData));
    const prevPL = prevYayoi.pl || { sales: 0, cogs: 0, grossProfit: 0, sga: 0, operatingProfit: 0, nonOperatingExpense: 0, ordinaryProfit: 0 };
    const prevBS = prevYayoi.bs || {
      assets: { current: { cashAndDeposits: 0, accountsReceivable: 0, inventory: 0 }, fixed: { tangible: 0 } },
      liabilities: { current: { accountsPayable: 0 }, fixed: { longTermDebt: 0 } },
      equity: { capital: 0 }
    };

    // P/L 利益計算（今回PLデータがあれば更新、無ければ前回の数値を維持）
    const finalSales = hasPLData ? plSales : prevPL.sales;
    const finalCogs = hasPLData ? plCogs : prevPL.cogs;
    const finalSga = hasPLData ? plSga : prevPL.sga;
    const finalNonOpExp = hasPLData ? plNonOpExp : prevPL.nonOperatingExpense;
    const finalGrossProfit = Math.max(0, finalSales - finalCogs);
    const finalOperatingProfit = finalGrossProfit - finalSga;
    const finalOrdinaryProfit = finalOperatingProfit - finalNonOpExp;

    // B/S 各種残高（今回BSデータがあれば更新、無ければ前回の数値を維持）
    const finalCash = hasBSData ? bsCashAndDeposits : prevBS.assets.current.cashAndDeposits;
    const finalReceivable = hasBSData ? bsReceivable : prevBS.assets.current.accountsReceivable;
    const finalInventory = hasBSData ? bsInventory : prevBS.assets.current.inventory;
    const finalFixedAssets = hasBSData ? bsFixedAssets : prevBS.assets.fixed.tangible;
    const finalPayable = hasBSData ? bsPayable : prevBS.liabilities.current.accountsPayable;
    const finalDebt = hasBSData ? bsDebt : prevBS.liabilities.fixed.longTermDebt;
    const finalCapital = hasBSData ? (bsCapital || Math.max(0, (finalCash + finalReceivable + finalInventory + finalFixedAssets) - (finalPayable + finalDebt))) : prevBS.equity.capital;

    // キャッシュフロー計算書（間接法）：最新のP/LとB/Sを統合して自動算出
    const estDepr = Math.round(finalFixedAssets * 0.1); // 減価償却推計
    const operatingCF = finalOrdinaryProfit + estDepr - Math.max(0, finalReceivable * 0.3) + Math.max(0, finalPayable * 0.2);
    const investingCF = 0;
    const financingCF = -Math.round(finalDebt * 0.15); // 元金返済推計
    const netCF = operatingCF + investingCF + financingCF;

    // 弥生データオブジェクトの安全マージ更新
    this.data.yayoiData = {
      lastImportedAt: nowStr,
      importedFileName: fileName,
      importedType: hasBSData && hasPLData ? 'bs_and_pl' : (hasBSData ? 'bs_only' : 'pl_only'),
      importedCount: updatedAccounts.length,
      importedKeys: prevYayoi.importedKeys || [],
      errors: [],
      pl: {
        sales: finalSales,
        cogs: finalCogs,
        grossProfit: finalGrossProfit,
        sga: finalSga,
        operatingProfit: finalOperatingProfit,
        nonOperatingExpense: finalNonOpExp,
        ordinaryProfit: finalOrdinaryProfit
      },
      bs: {
        assets: {
          current: {
            cashAndDeposits: finalCash,
            accountsReceivable: finalReceivable,
            inventory: finalInventory
          },
          fixed: {
            tangible: finalFixedAssets
          }
        },
        liabilities: {
          current: {
            accountsPayable: finalPayable
          },
          fixed: {
            longTermDebt: finalDebt
          }
        },
        equity: {
          capital: finalCapital
        }
      },
      cf: {
        operatingCF,
        investingCF,
        financingCF,
        netCF
      }
    };

    this.saveData();
    return {
      success: true,
      type: this.data.yayoiData.importedType,
      hasBSData,
      hasPLData,
      updatedAccountCount: updatedAccounts.length,
      accountDetails: updatedAccounts.map(id => ({ name: this.getAccount(id)?.shortName || id, balance: accountBalances[id] || 0 })),
      sales: finalSales,
      ordinaryProfit: finalOrdinaryProfit,
      cashTotal: finalCash,
      operatingCF,
      lastImportedAt: nowStr
    };
  }

  // やよいの青色申告オンライン CSVパーサー
  // 仕訳日記帳CSV（Shift-JIS/UTF-8、弥生公式形式2000、ヘッダーあり/なし、TSVコピペ）を完全自動判別
  importYayoiCSV(csvText, fileName = '弥生仕訳データ.csv') {
    const rawLines = csvText.split(/\r?\n/).filter(line => line.trim().length > 0);
    if (rawLines.length < 1) {
      throw new Error('CSVファイルの中身が空、または行数が不足しています。');
    }

    const accounts = this.getAccounts();
    const importedKeys = this.data.yayoiData?.importedKeys ? [...this.data.yayoiData.importedKeys] : [];
    let parsedCount = 0;
    let duplicateCount = 0;
    let skippedCount = 0;
    let newTransactions = [];

    // 区切り文字（カンマ or タブ）の判定
    const firstLine = rawLines[0];
    const commaCount = (firstLine.match(/,/g) || []).length;
    const tabCount = (firstLine.match(/\t/g) || []).length;
    const delimiter = tabCount > commaCount ? '\t' : ',';

    // カンマ区切りのパース関数（ダブルクォーテーション対応）
    const parseCSVLine = (line) => {
      const result = [];
      let current = '';
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"' || char === "'") {
          inQuotes = !inQuotes;
        } else if (char === delimiter && !inQuotes) {
          result.push(current.trim());
          current = '';
        } else {
          current += char;
        }
      }
      result.push(current.trim());
      return result.map(c => c.replace(/^["']|["']$/g, '').trim());
    };

    let isHeaderFound = false;
    let dateIdx = -1;
    let debitSubjectIdx = -1;
    let debitSubIdx = -1;
    let debitAmountIdx = -1;
    let creditSubjectIdx = -1;
    let creditSubIdx = -1;
    let creditAmountIdx = -1;
    let descIdx = -1;
    let isStandardYayoi2000 = false;

    for (let i = 0; i < rawLines.length; i++) {
      const cols = parseCSVLine(rawLines[i]);
      if (cols.length < 3) continue;

      // 1. ヘッダー判定
      if (!isHeaderFound) {
        // A. 弥生標準インポート/エクスポート形式（先頭が2000, 2111等の識別フラグ）
        if (/^(2000|2111|2112|[0-9]{4})$/.test(cols[0]) && cols.length >= 15) {
          isHeaderFound = true;
          isStandardYayoi2000 = true;
          dateIdx = 3;
          debitSubjectIdx = 4;
          debitSubIdx = 5;
          debitAmountIdx = 8;
          creditSubjectIdx = 10;
          creditSubIdx = 11;
          creditAmountIdx = 14;
          descIdx = cols.length > 16 ? 16 : cols.length - 1;
        }
        // B. 日本語ヘッダー行が存在する場合
        else if (cols.some(c => c.includes('取引日') || c.includes('日付') || c.includes('借方'))) {
          isHeaderFound = true;
          dateIdx = cols.findIndex(c => c.includes('日'));
          debitSubjectIdx = cols.findIndex(c => c.includes('借方科目') || c.includes('借方勘定科目'));
          debitSubIdx = cols.findIndex(c => c.includes('借方補助科目') || c.includes('借方補助'));
          debitAmountIdx = cols.findIndex(c => c.includes('借方金額') || c.includes('借方金'));
          creditSubjectIdx = cols.findIndex(c => c.includes('貸方科目') || c.includes('貸方勘定科目'));
          creditSubIdx = cols.findIndex(c => c.includes('貸方補助科目') || c.includes('貸方補助'));
          creditAmountIdx = cols.findIndex(c => c.includes('貸方金額') || c.includes('貸方金'));
          descIdx = cols.findIndex(c => c.includes('摘要') || c.includes('備考') || c.includes('取引内容'));
          continue; // ヘッダー行自体はスキップ
        }
        // C. 1行目から日付で始まるデータ行の場合
        else if (/^\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}/.test(cols[0])) {
          isHeaderFound = true;
          dateIdx = 0;
          debitSubjectIdx = 1;
          debitSubIdx = 2;
          debitAmountIdx = 4;
          creditSubjectIdx = 5;
          creditSubIdx = 6;
          creditAmountIdx = cols.length > 8 ? 8 : 4;
          descIdx = cols.length - 1;
        } else {
          continue; // ヘッダー前の空行・タイトル行などをスキップ
        }
      }

      // フォールバックインデックス
      if (dateIdx === -1) dateIdx = 0;
      if (debitSubjectIdx === -1) debitSubjectIdx = 1;
      if (debitSubIdx === -1) debitSubIdx = 2;
      if (debitAmountIdx === -1) debitAmountIdx = cols.length > 4 ? 4 : 3;
      if (creditSubjectIdx === -1) creditSubjectIdx = cols.length > 5 ? 5 : 2;
      if (creditSubIdx === -1) creditSubIdx = cols.length > 6 ? 6 : -1;
      if (creditAmountIdx === -1) creditAmountIdx = debitAmountIdx;
      if (descIdx === -1) descIdx = cols.length - 1;

      const rawDate = cols[dateIdx] || '';
      const debitSubj = cols[debitSubjectIdx] || '';
      const debitSub = debitSubIdx >= 0 ? (cols[debitSubIdx] || '') : '';
      const rawDebitAmt = (cols[debitAmountIdx] || '0').replace(/[^0-9\-]/g, '');
      const debitAmt = parseInt(rawDebitAmt, 10) || 0;

      const creditSubj = cols[creditSubjectIdx] || '';
      const creditSub = creditSubIdx >= 0 ? (cols[creditSubIdx] || '') : '';
      const rawCreditAmt = (cols[creditAmountIdx] || '0').replace(/[^0-9\-]/g, '');
      const creditAmt = parseInt(rawCreditAmt, 10) || debitAmt;
      const desc = descIdx >= 0 ? (cols[descIdx] || '') : '';

      // 金額が0ならスキップ
      if (debitAmt === 0 && creditAmt === 0) {
        skippedCount++;
        continue;
      }

      // 日付の正規化 (YYYY-MM-DD)
      let cleanDate = '';
      const dMatch = rawDate.match(/(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})/);
      if (dMatch) {
        cleanDate = `${dMatch[1]}-${String(dMatch[2]).padStart(2, '0')}-${String(dMatch[3]).padStart(2, '0')}`;
      } else if (rawDate.match(/(\d{1,2})[\/\-](\d{1,2})/)) {
        // 月/日のみの場合（今年を補完）
        const curY = new Date().getFullYear();
        const mParts = rawDate.match(/(\d{1,2})[\/\-](\d{1,2})/);
        cleanDate = `${curY}-${String(mParts[1]).padStart(2, '0')}-${String(mParts[2]).padStart(2, '0')}`;
      } else {
        skippedCount++;
        continue;
      }

      // 重複防止用ハッシュキー生成（日付_借方_貸方_金額_摘要頭10文字）
      const entryKey = `${cleanDate}_${debitSubj}_${creditSubj}_${debitAmt}_${desc.slice(0, 10)}`;
      if (importedKeys.includes(entryKey)) {
        duplicateCount++;
        continue;
      }
      importedKeys.push(entryKey);

      // 口座マッピング判定（借方・貸方の科目および補助科目・摘要から特定）
      const matchAccount = (subj, sub, text) => {
        const full = `${subj} ${sub} ${text}`;
        if (full.includes('中京') || (subj.includes('当座') && !full.includes('十六') && !full.includes('大垣'))) return 'bank-1';
        if (full.includes('十六')) return 'bank-2';
        if (full.includes('ゆうちょ') || full.includes('郵便')) return 'bank-3';
        if (full.includes('大垣') || full.includes('OKB')) return 'bank-4';
        if (full.includes('JA') || full.includes('農協')) return 'bank-5';
        if (subj.includes('現金') || sub.includes('現金')) return 'cash';
        if (subj.includes('普通預金') || subj.includes('当座預金') || subj.includes('預金')) return 'bank-1'; // デフォルト中京
        return null;
      };

      const debitAcc = matchAccount(debitSubj, debitSub, desc);
      const creditAcc = matchAccount(creditSubj, creditSub, desc);

      // A. 入金仕訳（預金・現金が借方）
      if (debitAcc && !creditAcc) {
        newTransactions.push({
          id: 'yayoi-' + Date.now() + '-' + parsedCount,
          date: cleanDate,
          type: 'income',
          partner: desc || debitSub || creditSubj || '弥生売上入金',
          category: creditSubj.includes('売上') ? '墓石新設代' : (creditSubj || 'その他収入'),
          amount: debitAmt,
          accountId: debitAcc,
          projectId: null,
          isActual: true, // 弥生確定実績
          note: `弥生仕訳: [${debitSubj}${debitSub ? `(${debitSub})` : ''}] ← [${creditSubj}] ${desc}`
        });
        parsedCount++;
      }
      // B. 支払仕訳（預金・現金が貸方）
      else if (!debitAcc && creditAcc) {
        newTransactions.push({
          id: 'yayoi-' + Date.now() + '-' + parsedCount,
          date: cleanDate,
          type: 'expense',
          partner: desc || creditSub || debitSubj || '弥生経費支出',
          category: debitSubj.includes('仕入') ? '石材仕入' : (debitSubj.includes('給料') ? '給与手当' : (debitSubj || 'その他経費')),
          amount: creditAmt,
          accountId: creditAcc,
          projectId: null,
          isActual: true, // 弥生確定実績
          note: `弥生仕訳: [${debitSubj}] → [${creditSubj}${creditSub ? `(${creditSub})` : ''}] ${desc}`
        });
        parsedCount++;
      }
      // C. 口座間振替仕訳（預金間移動）
      else if (debitAcc && creditAcc && debitAcc !== creditAcc) {
        newTransactions.push({
          id: 'yayoi-tr-' + Date.now() + '-' + parsedCount,
          date: cleanDate,
          type: 'transfer',
          partner: '弥生口座振替',
          category: '口座間振替',
          amount: debitAmt,
          fromAccountId: creditAcc,
          toAccountId: debitAcc,
          projectId: null,
          isActual: true,
          note: `弥生振替: ${desc}`
        });
        parsedCount++;
      }
      // D. その他の仕訳（売掛金計上など）も弥生データとしてカウント
      else {
        parsedCount++;
      }
    }

    // 弥生データの更新
    const nowStr = new Date().toLocaleString('ja-JP');
    if (!this.data.yayoiData) this.data.yayoiData = JSON.parse(JSON.stringify(INITIAL_DATA.yayoiData));
    
    this.data.yayoiData.lastImportedAt = nowStr;
    this.data.yayoiData.importedFileName = fileName;
    this.data.yayoiData.importedCount = (this.data.yayoiData.importedCount || 0) + parsedCount;
    this.data.yayoiData.importedKeys = importedKeys;

    // 新規取引を追加（既存データにマージし日付順ソート）
    if (newTransactions.length > 0) {
      this.data.transactions = [...this.data.transactions, ...newTransactions];
      this.data.transactions.sort((a, b) => a.date.localeCompare(b.date));
    }

    this.saveData();
    return {
      success: true,
      parsedCount,
      duplicateCount,
      skippedCount,
      newTxCount: newTransactions.length,
      lastImportedAt: nowStr
    };
  }

  // デモ用・サンプル弥生CSVの自動ロード
  loadSampleYayoiCSV() {
    const sampleCSV = `取引日,借方勘定科目,借方補助科目,借方税区分,借方金額,貸方勘定科目,貸方補助科目,貸方税区分,貸方金額,摘要
2026/11/02,普通預金,中京銀行,対象外,850000,売上高,完工高,課税売上10%,850000,佐藤様 墓所新設 着工時内金
2026/11/04,石材仕入,東日本石材,課税仕入10%,680000,当座預金,中京銀行,対象外,680000,インド産黒御影部材一式仕入振込
2026/11/06,現金,,対象外,55000,売上高,彫刻料,課税売上10%,55000,高橋様 戒名追加彫刻料 現金集金
2026/11/08,建材仕入,中川建材,課税仕入10%,145000,普通預金,中京銀行,対象外,145000,生コンクリート・砕石仕入代金
2026/11/12,重機リース料,オリエント重機,課税仕入10%,220000,普通預金,中京銀行,対象外,220000,カニクレーン・運搬車3日間リース代
2026/11/15,消耗品費,工具砥石,課税仕入10%,28000,現金,,対象外,28000,切削砥石・字彫用ゴムシート現金購入
2026/11/18,普通預金,十六銀行,対象外,300000,普通預金,中京銀行,対象外,300000,給料・公庫返済に備えた口座間資金振替
2026/11/20,給料手当,専従者給料,対象外,450000,普通預金,十六銀行,対象外,450000,11月度 従業員・専従者給料振込
2026/11/25,車両燃料費,ENEOS,課税仕入10%,35000,普通預金,十六銀行,対象外,35000,トラック給油・軽油カード引落
2026/11/27,借入金元金返済,日本公庫,対象外,80000,普通預金,十六銀行,対象外,80000,公庫設備借入金定期元利引落
2026/11/28,普通預金,中京銀行,対象外,1200000,売上高,寺院工事,課税売上10%,1200000,田中寺様 歴代住職墓補修完工代金振込`;

    return this.importYayoiCSV(sampleCSV, 'やよい青色申告_2026年11月仕訳日記帳.csv');
  }


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

  // Misoca CSV取り込み（請求書一覧CSV / 見積書一覧CSV / TSVコピペ）
  importMisocaCSV(csvText, fileName = 'Misoca請求書一覧.csv') {
    const rawLines = csvText.split(/\r?\n/).filter(line => line.trim().length > 0);
    if (rawLines.length < 2) throw new Error('CSVの内容（行数）が不足しています。');

    const misoca = this.getMisocaData();
    let importedInvoices = 0;
    const isEstimate = fileName.includes('見積') || csvText.includes('見積書番号');

    // 区切り文字の判定（タブ or カンマ）
    const firstLine = rawLines[0];
    const delimiter = (firstLine.match(/\t/g) || []).length > (firstLine.match(/,/g) || []).length ? '\t' : ',';

    const parseLine = (line) => {
      const res = [];
      let cur = '';
      let inQuotes = false;
      for (let i = 0; i < line.length; i++) {
        const c = line[i];
        if (c === '"' || c === "'") inQuotes = !inQuotes;
        else if (c === delimiter && !inQuotes) { res.push(cur.trim()); cur = ''; }
        else cur += c;
      }
      res.push(cur.trim());
      return res.map(c => c.replace(/^["']|["']$/g, '').trim());
    };

    // ヘッダー行の特定
    let headerIdx = -1;
    let headers = [];
    for (let i = 0; i < Math.min(rawLines.length, 5); i++) {
      const cols = parseLine(rawLines[i]);
      if (cols.some(c => c.includes('番号') || c.includes('請求') || c.includes('金額') || c.includes('取引先'))) {
        headerIdx = i;
        headers = cols;
        break;
      }
    }

    if (headerIdx === -1) {
      headerIdx = 0;
      headers = parseLine(rawLines[0]);
    }

    let invNoIdx = headers.findIndex(h => h.includes('請求書番号') || h.includes('管理番号') || h.includes('番号'));
    let partnerIdx = headers.findIndex(h => h.includes('請求先') || h.includes('取引先') || h.includes('宛名') || h.includes('顧客'));
    let dateIdx = headers.findIndex(h => h.includes('請求日') || h.includes('発行日'));
    let dueIdx = headers.findIndex(h => h.includes('支払期限') || h.includes('お支払期限') || h.includes('入金期日') || h.includes('期日'));
    let amtIdx = headers.findIndex(h => h.includes('合計金額') || h.includes('請求金額') || h.includes('税込') || h.includes('金額'));
    let subjectIdx = headers.findIndex(h => h.includes('件名') || h.includes('品名') || h.includes('内容'));

    if (invNoIdx === -1) invNoIdx = 0;
    if (partnerIdx === -1) partnerIdx = 1;
    if (amtIdx === -1) amtIdx = Math.min(2, headers.length - 1);
    if (dueIdx === -1) dueIdx = Math.min(3, headers.length - 1);

    for (let i = headerIdx + 1; i < rawLines.length; i++) {
      const cols = parseLine(rawLines[i]);
      if (cols.length < 2) continue;

      if (!isEstimate) {
        const invNo = cols[invNoIdx] || `INV-${Date.now()}-${i}`;
        const partner = cols[partnerIdx] || '施主様';
        const rawAmt = cols[amtIdx] || '0';
        const amount = parseInt(rawAmt.replace(/[^0-9]/g, ''), 10) || 0;
        let dueDate = (cols[dueIdx] || '').replace(/\//g, '-').trim();
        if (dueDate && /^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}$/.test(dueDate)) {
          const dp = dueDate.split('-');
          dueDate = `${dp[0]}-${dp[1].padStart(2, '0')}-${dp[2].padStart(2, '0')}`;
        }
        const subject = subjectIdx !== -1 && cols[subjectIdx] ? cols[subjectIdx] : '石材工事代金';

        if (amount <= 0 && !partner) continue;

        // 重複チェック
        const existingIdx = misoca.invoices.findIndex(inv => inv.invoiceNumber === invNo || (inv.partner === partner && inv.totalAmount === amount));
        const invObj = {
          id: existingIdx !== -1 ? misoca.invoices[existingIdx].id : 'inv-' + Date.now() + '-' + i,
          invoiceNumber: invNo,
          issueDate: dateIdx !== -1 && cols[dateIdx] ? cols[dateIdx].replace(/\//g, '-') : new Date().toISOString().slice(0, 10),
          dueDate: dueDate || new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10),
          partner,
          subject,
          totalAmount: amount,
          receivedAmount: existingIdx !== -1 ? misoca.invoices[existingIdx].receivedAmount : 0,
          status: existingIdx !== -1 ? misoca.invoices[existingIdx].status : 'unpaid',
          accountId: 'bank-3', // デフォルトはJAバンク（または指定口座）
          matchedYayoiKey: null,
          note: 'Misoca CSV取り込み'
        };

        if (existingIdx !== -1) {
          misoca.invoices[existingIdx] = invObj;
        } else {
          misoca.invoices.push(invObj);
        }
        importedInvoices++;

        // 資金繰り予定に同期
        const existingTx = this.data.transactions.find(t => t.partner === partner && t.amount === amount && !t.isActual);
        if (!existingTx && invObj.status !== 'paid' && invObj.totalAmount > 0) {
          this.data.transactions.push({
            id: 'misoca-tx-' + invObj.id,
            date: invObj.dueDate,
            type: 'income',
            partner: invObj.partner,
            category: '墓石新設代',
            amount: invObj.totalAmount - (invObj.receivedAmount || 0),
            accountId: 'bank-3',
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


  // Googleドライブ自動アップロード設定（GAS URL）
  getGDriveGasUrl() {
    return this.data.gdriveGasUrl || localStorage.getItem('nakagawa_stone_gdrive_gas_url') || '';
  }

  setGDriveGasUrl(url) {
    this.data.gdriveGasUrl = url.trim();
    localStorage.setItem('nakagawa_stone_gdrive_gas_url', url.trim());
    this.saveData();
  }


  // ==============================================================
  // 将来資金予測 ＆ シナリオシミュレーション（ストレステスト）
  // ==============================================================
  runStressTestSimulation(options = {}) {
    const {
      delayBigIncomes = false, // 大口入金の30日遅延
      delayDays = 30,
      salesReductionRate = 0,  // 売上減少率 (0.0 〜 0.5)
      extraExpenseAmount = 0,  // 突発支出（機械修繕・車両等）
      months = 6               // 予測期間
    } = options;

    const accounts = this.getAccounts();
    const baseDate = accounts[0]?.baseDate || '2026-10-31';

    // 期間終了日の計算
    const endDate = new Date(new Date(baseDate).getTime() + months * 30 * 86400000).toISOString().slice(0, 10);

    // シミュレーション用取引の複製と適用
    let simulatedTxs = this.data.transactions
      .filter(tx => tx.date >= baseDate && tx.date <= endDate)
      .map(tx => ({ ...tx }));

    // ① 大口入金遅延シナリオ
    if (delayBigIncomes) {
      simulatedTxs = simulatedTxs.map(tx => {
        if (tx.type === 'income' && tx.amount >= 500000 && !tx.isActual) {
          const d = new Date(tx.date);
          d.setDate(d.getDate() + delayDays);
          return { ...tx, date: d.toISOString().slice(0, 10), note: tx.note + ' (シミュレーション: 遅延)' };
        }
        return tx;
      });
    }

    // ② 売上減少シナリオ
    if (salesReductionRate > 0) {
      simulatedTxs = simulatedTxs.map(tx => {
        if (tx.type === 'income' && !tx.isActual) {
          const reducedAmt = Math.round(tx.amount * (1 - salesReductionRate));
          return { ...tx, amount: reducedAmt, note: tx.note + ` (シミュレーション: ${Math.round(salesReductionRate*100)}%減)` };
        }
        return tx;
      });
    }

    // ③ 突発大型支出シナリオ
    if (extraExpenseAmount > 0) {
      const suddenDate = new Date(Date.now() + 14 * 86400000).toISOString().slice(0, 10);
      simulatedTxs.push({
        id: 'sim-extra-exp',
        date: suddenDate,
        type: 'expense',
        partner: '突発設備修繕・緊急出費',
        category: 'その他経費',
        amount: extraExpenseAmount,
        accountId: 'bank-1',
        isActual: false,
        note: 'シミュレーション: 突発的支出'
      });
    }

    // シミュレーション残高計算
    let totalBal = accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0);
    const accBals = {};
    accounts.forEach(a => { accBals[a.id] = Number(a.baseBalance) || 0; });

    let minTotalBal = totalBal;
    let minDate = baseDate;
    const shortages = [];

    const dateMap = {};
    simulatedTxs.sort((a, b) => a.date.localeCompare(b.date)).forEach(tx => {
      if (!dateMap[tx.date]) dateMap[tx.date] = [];
      dateMap[tx.date].push(tx);
    });

    Object.keys(dateMap).sort().forEach(d => {
      dateMap[d].forEach(tx => {
        if (tx.type === 'income') {
          totalBal += tx.amount;
          if (tx.accountId && accBals[tx.accountId] !== undefined) accBals[tx.accountId] += tx.amount;
        } else if (tx.type === 'expense') {
          totalBal -= tx.amount;
          if (tx.accountId && accBals[tx.accountId] !== undefined) accBals[tx.accountId] -= tx.amount;
        }
      });

      if (totalBal < minTotalBal) {
        minTotalBal = totalBal;
        minDate = d;
      }

      accounts.forEach(a => {
        if (accBals[a.id] < 0) {
          shortages.push({
            date: d,
            accountName: a.name,
            shortName: a.shortName,
            balance: accBals[a.id],
            shortageAmount: Math.abs(accBals[a.id])
          });
        }
      });
    });

    return {
      months,
      baseTotalCash: accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0),
      finalSimulatedBalance: totalBal,
      minTotalBal,
      minDate,
      hasShortage: minTotalBal < 0 || shortages.length > 0,
      shortages,
      safetyStatus: minTotalBal >= 1500000 ? 'safe' : (minTotalBal >= 0 ? 'warning' : 'danger')
    };
  }

  // ユーザー・権限制御
  getCurrentUser() {
    return this.data.currentUser || 'wife';
  }

  setCurrentUser(userKey) {
    if (['wife', 'husband', 'staff3'].includes(userKey)) {
      this.data.currentUser = userKey;
      this.saveData();
    }
  }

  canAccessFunds() {
    const user = this.getCurrentUser();
    return user !== 'staff3';
  }

  canAccessEmails() {
    const user = this.getCurrentUser();
    return user !== 'staff3';
  }

  // 口座残高
  getBankAccount() {
    return this.data.bankAccount;
  }

  updateBankAccount(baseDate, baseBalance, bankName) {
    this.data.bankAccount = {
      baseDate: baseDate,
      baseBalance: Number(baseBalance) || 0,
      bankName: bankName || this.data.bankAccount.bankName,
      lastUpdated: new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
    };
    this.saveData();
  }

  // タスク管理
  getTasks() {
    return this.data.tasks || [];
  }

  addTask(task) {
    const newTask = {
      id: 'task-' + Date.now(),
      title: task.title,
      category: task.category || '工事準備',
      assignee: task.assignee || '私',
      dueDate: task.dueDate || new Date().toISOString().slice(0, 10),
      nextAction: task.nextAction || '',
      status: 'pending',
      completedAt: null,
      projectId: task.projectId || null,
      amount: task.amount ? Number(task.amount) : null
    };
    this.data.tasks.unshift(newTask);
    this.saveData();
    return newTask;
  }

  updateTask(taskId, updates) {
    const index = this.data.tasks.findIndex(t => t.id === taskId);
    if (index !== -1) {
      this.data.tasks[index] = { ...this.data.tasks[index], ...updates };
      this.saveData();
      return this.data.tasks[index];
    }
    return null;
  }

  toggleTaskStatus(taskId) {
    const task = this.data.tasks.find(t => t.id === taskId);
    if (task) {
      if (task.status === 'completed') {
        task.status = 'pending';
        task.completedAt = null;
      } else {
        task.status = 'completed';
        const now = new Date();
        task.completedAt = now.toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });

        this.addActivityLog({
          user: task.assignee || '私',
          category: '作業完了',
          action: `【完了】${task.title}`,
          details: task.nextAction ? `次の作業メモ: ${task.nextAction}` : 'タスク一覧より完了に更新',
          projectId: task.projectId
        });
      }
      this.saveData();
      return task;
    }
    return null;
  }

  deleteTask(taskId) {
    this.data.tasks = this.data.tasks.filter(t => t.id !== taskId);
    this.saveData();
  }

  // 入出金取引
  getTransactions() {
    return this.data.transactions || [];
  }

  addTransaction(tx) {
    const newTx = {
      id: 'tx-' + Date.now(),
      date: tx.date,
      type: tx.type, // 'income' | 'expense'
      partner: tx.partner,
      category: tx.category || 'その他',
      amount: Math.abs(Number(tx.amount) || 0),
      projectId: tx.projectId || null,
      isActual: !!tx.isActual,
      note: tx.note || ''
    };
    this.data.transactions.push(newTx);
    this.data.transactions.sort((a, b) => a.date.localeCompare(b.date));
    this.saveData();
    return newTx;
  }

  updateTransaction(txId, updates) {
    const index = this.data.transactions.findIndex(t => t.id === txId);
    if (index !== -1) {
      this.data.transactions[index] = { ...this.data.transactions[index], ...updates };
      this.data.transactions.sort((a, b) => a.date.localeCompare(b.date));
      this.saveData();
      return this.data.transactions[index];
    }
    return null;
  }

  toggleTransactionActual(txId) {
    const tx = this.data.transactions.find(t => t.id === txId);
    if (tx) {
      tx.isActual = !tx.isActual;
      this.saveData();
      return tx;
    }
    return null;
  }

  deleteTransaction(txId) {
    this.data.transactions = this.data.transactions.filter(t => t.id !== txId);
    this.saveData();
  }

  // ==============================================================
  // 本格「月次資金繰り表（マトリクス）」生成ロジック（全12ヶ月＋翌月・完璧キャッシュフロー対応）
  // ==============================================================
  generateCashFlowMatrix(filterMode = 'all') {
    // 全対象月（2026年1月〜12月、2027年1月）
    const allMonths = [
      '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06',
      '2026-07', '2026-08', '2026-09', '2026-10', '2026-11', '2026-12', '2027-01'
    ];
    
    // フィルターモードに応じた対象月
    let targetMonths = allMonths;
    if (filterMode === 'recent6') {
      targetMonths = ['2026-07', '2026-08', '2026-09', '2026-10', '2026-11', '2026-12', '2027-01'];
    } else if (filterMode === 'forecast') {
      targetMonths = ['2026-10', '2026-11', '2026-12', '2027-01'];
    }

    // 全取引を取得
    const allTxs = this.data.transactions || [];

    // 費目ごとの行定義
    const incomeRows = [
      { key: '墓石新設代', label: '墓所新設代（着工・完工）' },
      { key: '改修・補修代', label: '墓所改修・補修代' },
      { key: '戒名彫刻・納骨', label: '戒名追加彫刻・納骨料' },
      { key: '墓じまい代', label: '墓じまい・更地返還代' },
      { key: 'その他収入', label: 'その他売上・雑収入' }
    ];

    const expenseGroups = [
      {
        groupName: '【原価・仕入・工事費】',
        rows: [
          { key: '石材仕入', label: '石材仕入代（墓石・外柵・納骨部材）' },
          { key: '建材仕入', label: '基礎建材費（生コン・セメント・砕石）' },
          { key: '重機リース', label: '重機・クレーン・運搬費' },
          { key: '外注加工', label: '字彫り・職人工賃・加工外注費' }
        ]
      },
      {
        groupName: '【人件費・生活費】',
        rows: [
          { key: '給与手当', label: '給与・専従者給与・事業主生活費' }
        ]
      },
      {
        groupName: '【固定費・現場経費】',
        rows: [
          { key: '車両・燃料', label: '車両費・軽油代・高速代' },
          { key: '消耗品・工具', label: '消耗品・工具（砥石・ゴム等）' },
          { key: '損害保険料', label: '損害保険料（車両・請負賠償）' },
          { key: '通信・光熱費', label: '水道光熱・事務所通信費' }
        ]
      },
      {
        groupName: '【財務・税務・決済】',
        rows: [
          { key: '借入返済', label: '借入金返済（信金・公庫元利金）' },
          { key: '税金・積立', label: '租税公課・税理士報酬・諸会費' },
          { key: 'その他経費', label: 'カード決済・振込手数料・雑費' }
        ]
      }
    ];

    // 全月の集計オブジェクトを初期化
    const monthData = {};
    allMonths.forEach(m => {
      monthData[m] = {
        month: m,
        startBalance: 0,
        incomes: {},
        totalIncome: 0,
        expenses: {},
        totalExpense: 0,
        netCashFlow: 0,
        endBalance: 0,
        transactions: []
      };
      incomeRows.forEach(r => monthData[m].incomes[r.key] = 0);
      expenseGroups.forEach(g => {
        g.rows.forEach(r => monthData[m].expenses[r.key] = 0);
      });
    });

    // 取引を月・費目ごとに振り分け
    allTxs.forEach(tx => {
      const m = tx.date.slice(0, 7);
      if (monthData[m]) {
        monthData[m].transactions.push(tx);
        if (tx.type === 'income') {
          const cat = incomeRows.find(r => r.key === tx.category) ? tx.category : 'その他収入';
          monthData[m].incomes[cat] = (monthData[m].incomes[cat] || 0) + tx.amount;
          monthData[m].totalIncome += tx.amount;
        } else if (tx.type === 'expense') {
          let matched = false;
          expenseGroups.forEach(g => {
            if (g.rows.find(r => r.key === tx.category)) {
              monthData[m].expenses[tx.category] = (monthData[m].expenses[tx.category] || 0) + tx.amount;
              matched = true;
            }
          });
          if (!matched) {
            monthData[m].expenses['その他経費'] = (monthData[m].expenses['その他経費'] || 0) + tx.amount;
          }
          monthData[m].totalExpense += tx.amount;
        }
      }
    });

    // 繰越残高の完全計算（2026年1月1日 期首前期繰越残高 5,684,020円から完全連動）
    const initialStartBalance = 5684020;
    let runningBalance = initialStartBalance;

    allMonths.forEach(m => {
      monthData[m].startBalance = runningBalance;
      monthData[m].netCashFlow = monthData[m].totalIncome - monthData[m].totalExpense;
      monthData[m].endBalance = runningBalance + monthData[m].netCashFlow;
      runningBalance = monthData[m].endBalance;
    });

    return {
      targetMonths,
      allMonths,
      incomeRows,
      expenseGroups,
      monthData
    };
  }

  // ==============================================================
  // 費目別支出の内訳集計（何にいくら使っているか）
  // ==============================================================
  calculateExpenseBreakdown(monthKey = 'all') {
    const allTxs = this.data.transactions.filter(tx => tx.type === 'expense');
    
    let filteredTxs = allTxs;
    if (monthKey !== 'all') {
      filteredTxs = allTxs.filter(tx => tx.date.startsWith(monthKey));
    } else {
      // 全期間（基準日以降の3か月間を中心に集計）
      const baseDate = this.data.bankAccount.baseDate;
      filteredTxs = allTxs.filter(tx => tx.date >= baseDate);
    }

    const categoryMap = {};
    let totalExpense = 0;

    EXPENSE_CATEGORIES.forEach(cat => {
      categoryMap[cat.key] = {
        key: cat.key,
        name: cat.name,
        group: cat.group,
        color: cat.color,
        amount: 0,
        count: 0
      };
    });

    filteredTxs.forEach(tx => {
      const catKey = categoryMap[tx.category] ? tx.category : 'その他経費';
      categoryMap[catKey].amount += tx.amount;
      categoryMap[catKey].count += 1;
      totalExpense += tx.amount;
    });

    // 金額順にソートし、比率を計算
    const list = Object.values(categoryMap)
      .filter(item => item.amount > 0)
      .map(item => ({
        ...item,
        percentage: totalExpense > 0 ? ((item.amount / totalExpense) * 100).toFixed(1) : 0
      }))
      .sort((a, b) => b.amount - a.amount);

    return {
      totalExpense,
      list
    };
  }

  // ==============================================================
  // 固定費 vs 変動費（工事原価）の分析
  // ==============================================================
  calculateFixedAndVariableExpenses(monthKey = 'all') {
    const breakdown = this.calculateExpenseBreakdown(monthKey);
    let variableTotal = 0; // 変動費（工事原価）
    let fixedTotal = 0;    // 固定費（会社維持費・財務）

    const variableKeys = ['石材仕入', '建材仕入', '重機リース', '外注加工', '消耗品・工具'];
    const variableItems = [];
    const fixedItems = [];

    breakdown.list.forEach(item => {
      if (variableKeys.includes(item.key)) {
        variableTotal += item.amount;
        variableItems.push(item);
      } else {
        fixedTotal += item.amount;
        fixedItems.push(item);
      }
    });

    const total = breakdown.totalExpense;
    return {
      total,
      variableTotal,
      variablePercentage: total > 0 ? ((variableTotal / total) * 100).toFixed(1) : 0,
      variableItems,
      fixedTotal,
      fixedPercentage: total > 0 ? ((fixedTotal / total) * 100).toFixed(1) : 0,
      fixedItems
    };
  }

  // ==============================================================
  // 工事・案件別 原価・収支・利益率の計算（個別原価管理）
  // ==============================================================
  calculateProjectProfitability() {
    const projects = this.data.projects || [];
    const allTxs = this.data.transactions || [];

    return projects.map(proj => {
      const pTxs = allTxs.filter(tx => tx.projectId === proj.id);
      
      let totalCost = 0;
      let stoneCost = 0;      // 石材代
      let materialCost = 0;   // 建材代
      let machineryCost = 0;  // 重機代
      let otherCost = 0;      // 外注・消耗品その他
      let billedAmount = 0;   // 入金予定・実績合計

      const costItems = [];
      const incomeItems = [];

      pTxs.forEach(tx => {
        if (tx.type === 'expense') {
          totalCost += tx.amount;
          costItems.push(tx);
          if (tx.category === '石材仕入') stoneCost += tx.amount;
          else if (tx.category === '建材仕入') materialCost += tx.amount;
          else if (tx.category === '重機リース') machineryCost += tx.amount;
          else otherCost += tx.amount;
        } else {
          billedAmount += tx.amount;
          incomeItems.push(tx);
        }
      });

      const contractAmount = Number(proj.contractAmount) || billedAmount || 0;
      const grossProfit = contractAmount - totalCost;
      const profitMargin = contractAmount > 0 ? ((grossProfit / contractAmount) * 100).toFixed(1) : 0;

      return {
        project: proj,
        contractAmount,
        billedAmount,
        totalCost,
        stoneCost,
        materialCost,
        machineryCost,
        otherCost,
        grossProfit,
        profitMargin,
        costItems,
        incomeItems
      };
    });
  }

  // ==============================================================
  // 本格キャッシュフロー計算書（営業CF・財務CF・フリーCF）
  // ==============================================================
  calculateCashFlowStatementByType(monthKey = 'all') {
    const matrix = this.generateCashFlowMatrix();
    const months = monthKey === 'all' ? matrix.targetMonths : [monthKey];
    const mData = matrix.monthData;

    let totalOperatingIncome = 0;
    let totalOperatingExpense = 0;
    let totalFinancingExpense = 0; // 借入金返済

    months.forEach(m => {
      if (mData[m]) {
        totalOperatingIncome += mData[m].totalIncome;
        
        // 支出のうち、借入返済以外を営業支出とする
        const finExpense = mData[m].expenses['借入返済'] || 0;
        const opExpense = mData[m].totalExpense - finExpense;

        totalOperatingExpense += opExpense;
        totalFinancingExpense += finExpense;
      }
    });

    const operatingCF = totalOperatingIncome - totalOperatingExpense;
    const financingCF = -totalFinancingExpense;
    const netCF = operatingCF + financingCF;

    return {
      periodLabel: monthKey === 'all' ? '今後3か月間（全期間）' : `${monthKey}月度`,
      operatingIncome: totalOperatingIncome,
      operatingExpense: totalOperatingExpense,
      operatingCF,
      financingCF,
      netCF,
      isPositive: operatingCF >= totalFinancingExpense // 本業の儲けで借入返済を賄えているか
    };
  }

  // ==============================================================
  // 日繰り表（日別・支払集中日の資金繰り）
  // ==============================================================
  // ==============================================================
  // 5口座＋手許現金 日別資金繰り・残高予測シミュレーション
  // 二重計上防止・口座別不足警告・未配分支払管理
  // ==============================================================
  calculateDailyCashFlowSchedule(options = {}) {
    const accounts = this.getAccounts();
    const baseDate = options.baseDate || accounts[0]?.baseDate || '2026-10-31';
    
    // 各口座の初期残高マップ
    const runningBalances = {};
    let totalRunningBalance = 0;
    accounts.forEach(acc => {
      const bal = Number(acc.baseBalance) || 0;
      runningBalances[acc.id] = bal;
      totalRunningBalance += bal;
    });

    const futureTxs = this.data.transactions
      .filter(tx => tx.date >= baseDate)
      .sort((a, b) => a.date.localeCompare(b.date));

    // 日別マップの初期化
    const dateMap = {};
    futureTxs.forEach(tx => {
      const d = tx.date;
      if (!dateMap[d]) {
        dateMap[d] = {
          date: d,
          totalIncome: 0,
          totalExpense: 0,
          unassignedExpense: 0, // 口座未定の支払額
          items: [],
          accountDeltas: {} // 口座ごとの当日の出入り
        };
        accounts.forEach(a => {
          dateMap[d].accountDeltas[a.id] = { income: 0, expense: 0, transferIn: 0, transferOut: 0 };
        });
      }

      dateMap[d].items.push(tx);

      if (tx.type === 'income') {
        dateMap[d].totalIncome += Number(tx.amount) || 0;
        const targetAcc = tx.accountId || 'bank-1';
        if (dateMap[d].accountDeltas[targetAcc]) {
          dateMap[d].accountDeltas[targetAcc].income += Number(tx.amount) || 0;
        }
      } else if (tx.type === 'expense') {
        const amt = Number(tx.amount) || 0;
        dateMap[d].totalExpense += amt;
        const targetAcc = tx.accountId;
        if (!targetAcc || targetAcc === 'unassigned') {
          // 支払口座未定：全社合計からは引くが、個別口座は未定（未配分）
          dateMap[d].unassignedExpense += amt;
        } else if (dateMap[d].accountDeltas[targetAcc]) {
          dateMap[d].accountDeltas[targetAcc].expense += amt;
        }
      } else if (tx.type === 'transfer') {
        // 口座間振替：全口座合計の収支はゼロ（二重計上なし）
        const amt = Number(tx.amount) || 0;
        const fromId = tx.fromAccountId;
        const toId = tx.toAccountId;
        if (dateMap[d].accountDeltas[fromId]) {
          dateMap[d].accountDeltas[fromId].transferOut += amt;
        }
        if (dateMap[d].accountDeltas[toId]) {
          dateMap[d].accountDeltas[toId].transferIn += amt;
        }
      }
    });

    const shortageAlerts = []; // 残高不足警告リスト
    const unassignedAlerts = []; // 未配分支払警告リスト

    const sortedDates = Object.keys(dateMap).sort();
    const list = sortedDates.map(d => {
      const dayData = dateMap[d];
      
      // 全社合計の収支
      const dayTotalNet = dayData.totalIncome - dayData.totalExpense;
      totalRunningBalance += dayTotalNet;

      // 各口座ごとの残高計算
      const accountSnapshots = {};
      accounts.forEach(acc => {
        const delta = dayData.accountDeltas[acc.id] || { income: 0, expense: 0, transferIn: 0, transferOut: 0 };
        const accNet = (delta.income + delta.transferIn) - (delta.expense + delta.transferOut);
        runningBalances[acc.id] += accNet;
        
        const isShortage = runningBalances[acc.id] < 0;
        if (isShortage) {
          shortageAlerts.push({
            date: d,
            accountId: acc.id,
            accountName: acc.name,
            shortName: acc.shortName,
            balance: runningBalances[acc.id],
            shortageAmount: Math.abs(runningBalances[acc.id])
          });
        }

        accountSnapshots[acc.id] = {
          name: acc.name,
          shortName: acc.shortName,
          color: acc.color,
          income: delta.income,
          expense: delta.expense,
          transferIn: delta.transferIn,
          transferOut: delta.transferOut,
          net: accNet,
          balance: runningBalances[acc.id],
          isShortage
        };
      });

      // 未配分支払のチェック
      if (dayData.unassignedExpense > 0) {
        unassignedAlerts.push({
          date: d,
          amount: dayData.unassignedExpense,
          items: dayData.items.filter(t => t.type === 'expense' && (!t.accountId || t.accountId === 'unassigned'))
        });
      }

      const dayNum = parseInt(d.slice(8), 10);
      return {
        date: d,
        totalIncome: dayData.totalIncome,
        totalExpense: dayData.totalExpense,
        totalNet: dayTotalNet,
        totalBalance: totalRunningBalance,
        unassignedExpense: dayData.unassignedExpense,
        accountSnapshots,
        items: dayData.items,
        isPayday: dayNum === 25,
        isLoanDay: dayNum === 27,
        isMonthEnd: dayNum >= 28,
        isHighOutflow: dayData.totalExpense >= 200000,
        hasShortage: Object.values(accountSnapshots).some(a => a.isShortage)
      };
    });

    return {
      dailyList: list,
      shortageAlerts,
      unassignedAlerts,
      finalTotalBalance: totalRunningBalance,
      finalAccountBalances: { ...runningBalances }
    };
  }

  // トップ画面用 KPI・状況サマリー
  getDashboardKPIs() {
    const accounts = this.getAccounts();
    const todayStr = new Date().toISOString().slice(0, 10);
    const schedule = this.calculateDailyCashFlowSchedule({ baseDate: accounts[0]?.baseDate || '2026-10-31' });
    
    // 現在の資金残高（全口座合計）
    const totalCurrentCash = accounts.reduce((sum, a) => sum + (Number(a.baseBalance) || 0), 0);
    
    // 今後30日間の入出金予定
    const next30DaysEnd = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
    const next30DaysTxs = this.data.transactions.filter(tx => tx.date >= todayStr && tx.date <= next30DaysEnd);
    
    const next30Income = next30DaysTxs.filter(t => t.type === 'income').reduce((sum, t) => sum + (Number(t.amount) || 0), 0);
    const next30Expense = next30DaysTxs.filter(t => t.type === 'expense').reduce((sum, t) => sum + (Number(t.amount) || 0), 0);
    
    // 未回収の請求書（未入金の売掛金）
    const uncollectedIncomes = this.data.transactions.filter(tx => tx.type === 'income' && !tx.isActual);
    const uncollectedTotal = uncollectedIncomes.reduce((sum, t) => sum + (Number(t.amount) || 0), 0);

    return {
      totalCurrentCash,
      accounts: accounts.map(a => ({
        ...a,
        currentBalance: schedule.finalAccountBalances[a.id] ?? a.baseBalance
      })),
      next30Income,
      next30Expense,
      next30Net: next30Income - next30Expense,
      uncollectedCount: uncollectedIncomes.length,
      uncollectedTotal,
      shortageAlerts: schedule.shortageAlerts,
      unassignedAlerts: schedule.unassignedAlerts
    };
  }

  // 従来の残高推移シミュレーション
  calculateCashFlowSimulation() {
    const bank = this.data.bankAccount;
    const baseDate = bank.baseDate || '2026-10-31';
    const baseBalance = Number(bank.baseBalance) || 0;

    const futureTransactions = this.data.transactions
      .filter(tx => tx.date >= baseDate)
      .sort((a, b) => a.date.localeCompare(b.date));

    let totalUnreceived = 0;
    let totalUnpaid = 0;
    let actualIncome = 0;
    let actualExpense = 0;

    futureTransactions.forEach(tx => {
      if (tx.type === 'income') {
        if (!tx.isActual) totalUnreceived += tx.amount;
        else actualIncome += tx.amount;
      } else {
        if (!tx.isActual) totalUnpaid += tx.amount;
        else actualExpense += tx.amount;
      }
    });

    let runningBalance = baseBalance;
    const timeline = [];
    
    timeline.push({
      date: baseDate,
      label: `${baseDate} (基準日残高)`,
      change: 0,
      balance: runningBalance,
      isBase: true,
      items: []
    });

    const txByDate = {};
    futureTransactions.forEach(tx => {
      if (!txByDate[tx.date]) txByDate[tx.date] = [];
      txByDate[tx.date].push(tx);
    });

    const sortedDates = Object.keys(txByDate).sort();
    let minBalance = runningBalance;
    let minDate = baseDate;

    sortedDates.forEach(date => {
      const items = txByDate[date];
      let dayChange = 0;
      items.forEach(it => {
        const delta = it.type === 'income' ? it.amount : -it.amount;
        dayChange += delta;
      });
      runningBalance += dayChange;

      if (runningBalance < minBalance) {
        minBalance = runningBalance;
        minDate = date;
      }

      timeline.push({
        date: date,
        label: date,
        change: dayChange,
        balance: runningBalance,
        isBase: false,
        items: items
      });
    });

    const monthlySummary = {};
    futureTransactions.forEach(tx => {
      const monthKey = tx.date.slice(0, 7);
      if (!monthlySummary[monthKey]) {
        monthlySummary[monthKey] = {
          month: monthKey,
          income: 0,
          expense: 0,
          net: 0
        };
      }
      if (tx.type === 'income') monthlySummary[monthKey].income += tx.amount;
      else monthlySummary[monthKey].expense += tx.amount;
      monthlySummary[monthKey].net = monthlySummary[monthKey].income - monthlySummary[monthKey].expense;
    });

    return {
      baseDate,
      baseBalance,
      finalProjectedBalance: runningBalance,
      minBalance,
      minDate,
      totalUnreceived,
      totalUnpaid,
      actualIncome,
      actualExpense,
      timeline,
      monthlySummary: Object.values(monthlySummary).sort((a, b) => a.month.localeCompare(b.month))
    };
  }

  // 案件・作業履歴・メール関連
  getProjects() { return this.data.projects || []; }
  addProject(p) {
    const newProj = {
      id: 'proj-' + Date.now(),
      name: p.name,
      customerName: p.customerName || '',
      siteLocation: p.siteLocation || '',
      scheduleDate: p.scheduleDate || '',
      assignee: p.assignee || '夫',
      status: p.status || 'inquiry',
      statusLabel: p.statusLabel || '相談・打合中',
      nextAction: p.nextAction || '',
      driveLinks: p.driveLinks || {},
      contractAmount: p.contractAmount ? Number(p.contractAmount) : 0,
      note: p.note || ''
    };
    this.data.projects.unshift(newProj);
    this.saveData();
    return newProj;
  }
  updateProject(id, updates) {
    const i = this.data.projects.findIndex(p => p.id === id);
    if (i !== -1) {
      this.data.projects[i] = { ...this.data.projects[i], ...updates };
      this.saveData();
      return this.data.projects[i];
    }
    return null;
  }
  deleteProject(id) {
    this.data.projects = this.data.projects.filter(p => p.id !== id);
    this.saveData();
  }
  getProjectRelations(id) {
    return {
      tasks: this.data.tasks.filter(t => t.projectId === id),
      transactions: this.data.transactions.filter(t => t.projectId === id),
      logs: this.data.activityLogs.filter(l => l.projectId === id)
    };
  }

  getActivityLogs() { return this.data.activityLogs || []; }
  addActivityLog(log) {
    const timestamp = new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    const newLog = {
      id: 'log-' + Date.now(),
      timestamp: log.timestamp || timestamp,
      user: log.user || this.getCurrentUserLabel(),
      category: log.category || '一般作業',
      action: log.action,
      details: log.details || '',
      projectId: log.projectId || null
    };
    this.data.activityLogs.unshift(newLog);
    this.saveData();
    return newLog;
  }
  getCurrentUserLabel() {
    const u = this.getCurrentUser();
    if (u === 'wife') return '私';
    if (u === 'husband') return '夫';
    return 'スタッフC';
  }

  getEmails() { return this.data.emails || []; }
  toggleEmailRead(id) {
    const m = this.data.emails.find(e => e.id === id);
    if (m) { m.isRead = !m.isRead; this.saveData(); }
    return m;
  }
  toggleEmailProcessed(id) {
    const m = this.data.emails.find(e => e.id === id);
    if (m) { m.isProcessed = !m.isProcessed; this.saveData(); }
    return m;
  }
  createTaskFromEmail(id, options = {}) {
    const m = this.data.emails.find(e => e.id === id);
    if (!m) return null;
    const task = this.addTask({
      title: `【メール返信】${m.senderName}：${m.subject}`,
      category: '返信',
      assignee: m.assignee || '私',
      dueDate: m.dueDate || new Date().toISOString().slice(0, 10),
      nextAction: options.nextAction || `メール内容確認の上、返信または電話対応。（元メール: ${m.subject}）`,
      projectId: options.projectId || null,
      amount: null
    });
    m.taskCreated = true;
    this.saveData();
    return task;
  }
}

window.EXPENSE_CATEGORIES = EXPENSE_CATEGORIES;
window.INCOME_CATEGORIES = INCOME_CATEGORIES;
window.stoneStore = new StoneAppStore();
