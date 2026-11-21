import re

store_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js'

with open(store_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update INITIAL_DATA to include yayoiData
yayoi_init_def = """  // 弥生データ管理（CSV取り込み・財務三表）
  yayoiData: {
    lastImportedAt: null,
    importedFileName: null,
    importedCount: 0,
    importedKeys: [],
    errors: [],
    // 財務三表（基準データ）
    pl: {
      sales: 24500000, // 工事売上高
      cogs: 10290000,  // 売上原価（石材・生コン建材・外注加工・重機）
      grossProfit: 14210000, // 売上総利益（限界利益 58.0%）
      sga: 10800000,   // 販管費（人件費・車両費・消耗品・保険・通信光熱）
      operatingProfit: 3410000, // 営業利益
      nonOperatingExpense: 72000, // 借入金利息
      ordinaryProfit: 3338000 // 経常利益
    },
    bs: {
      assets: {
        current: {
          cashAndDeposits: 5000000, // 5口座＋手許現金
          accountsReceivable: 2105000, // 売掛金（未回収請求書）
          inventory: 2800000 // 展示墓石・石材部材在庫
        },
        fixed: {
          tangible: 4500000 // 車両・カニクレーン・切削機械
        }
      },
      liabilities: {
        current: {
          accountsPayable: 1045000 // 買掛金・未払金（石材建材仕入）
        },
        fixed: {
          longTermDebt: 4200000 // 公庫・地銀借入残高
        }
      },
      equity: {
        capital: 9160000 // 元入金・当期純利益
      }
    },
    cf: {
      operatingCF: 4890000, // 営業活動によるCF（確定値）
      investingCF: 0,       // 投資活動によるCF（推計値）
      financingCF: -960000, // 財務活動によるCF（借入元金返済、確定値）
      netCF: 3930000        // 純増減
    }
  },
"""

if "yayoiData:" not in code:
    code = code.replace("  // 1. 口座残高（基準日付き手入力）", yayoi_init_def + "  // 1. 口座残高（基準日付き手入力）")

# 2. Add Yayoi parsing and financial statements methods to StoneAppStore
yayoi_store_methods = """
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

  // やよいの青色申告オンライン CSVパーサー
  // 仕訳日記帳CSVおよび残高試算表CSVを自動判別してパース・重複防止
  importYayoiCSV(csvText, fileName = '弥生仕訳データ.csv') {
    const lines = csvText.split(/\\r?\\n/).filter(line => line.trim().length > 0);
    if (lines.length < 2) {
      throw new Error('CSVファイルの中身が空、または行数が不足しています。');
    }

    const accounts = this.getAccounts();
    const importedKeys = this.data.yayoiData?.importedKeys ? [...this.data.yayoiData.importedKeys] : [];
    const errors = [];
    let parsedCount = 0;
    let duplicateCount = 0;
    let newTransactions = [];

    // 口座残高加算用
    const accountBalances = {};
    accounts.forEach(a => { accountBalances[a.id] = Number(a.baseBalance) || 0; });

    let isHeaderFound = false;
    let headerCols = [];

    for (let i = 0; i < lines.length; i++) {
      const rawLine = lines[i];
      // CSV行の分割（カンマ区切り、クォーテーション考慮）
      const cols = rawLine.split(',').map(c => c.trim().replace(/^[\"']|[\"']$/g, ''));

      // ヘッダー行判定（弥生仕訳日記帳、または標準形式）
      if (!isHeaderFound) {
        if (cols.includes('取引日') || cols.includes('日付') || cols.includes('借方勘定科目') || cols.includes('借方科目')) {
          isHeaderFound = true;
          headerCols = cols;
          continue;
        }
        // ヘッダーがない弥生エクスポート（先頭が識別フラグ2000や日付）
        if (/^\\d{4}[\\/\\-]\\d{1,2}[\\/\\-]\\d{1,2}/.test(cols[0]) || /^[0-9]{4}$/.test(cols[0])) {
          isHeaderFound = true;
          headerCols = ['日付', '借方科目', '借方補助科目', '借方金額', '貸方科目', '貸方補助科目', '貸方金額', '摘要'];
          // 1行目からデータとして処理
        } else {
          continue;
        }
      }

      // 列インデックスの特定
      let dateIdx = headerCols.findIndex(c => c.includes('日'));
      let debitSubjectIdx = headerCols.findIndex(c => c.includes('借方科目') || c.includes('借方勘定科目'));
      let debitSubIdx = headerCols.findIndex(c => c.includes('借方補助科目'));
      let debitAmountIdx = headerCols.findIndex(c => c.includes('借方金額'));
      let creditSubjectIdx = headerCols.findIndex(c => c.includes('貸方科目') || c.includes('貸方勘定科目'));
      let creditSubIdx = headerCols.findIndex(c => c.includes('貸方補助科目'));
      let creditAmountIdx = headerCols.findIndex(c => c.includes('貸方金額'));
      let descIdx = headerCols.findIndex(c => c.includes('摘要') || c.includes('備考'));

      // デフォルトインデックスフォールバック
      if (dateIdx === -1) dateIdx = 0;
      if (debitSubjectIdx === -1) debitSubjectIdx = 1;
      if (debitSubIdx === -1) debitSubIdx = 2;
      if (debitAmountIdx === -1) debitAmountIdx = 4;
      if (creditSubjectIdx === -1) creditSubjectIdx = 6;
      if (creditSubIdx === -1) creditSubIdx = 7;
      if (creditAmountIdx === -1) creditAmountIdx = 9;
      if (descIdx === -1) descIdx = cols.length - 1;

      const dateStr = cols[dateIdx] || '';
      const debitSubj = cols[debitSubjectIdx] || '';
      const debitSub = cols[debitSubIdx] || '';
      const debitAmt = parseInt((cols[debitAmountIdx] || '0').replace(/[^0-9\\-]/g, ''), 10) || 0;
      const creditSubj = cols[creditSubjectIdx] || '';
      const creditSub = cols[creditSubIdx] || '';
      const creditAmt = parseInt((cols[creditAmountIdx] || '0').replace(/[^0-9\\-]/g, ''), 10) || debitAmt;
      const desc = cols[descIdx] || '';

      if (!dateStr || (debitAmt === 0 && creditAmt === 0)) continue;

      // 日付の正規化 (YYYY-MM-DD)
      const cleanDate = dateStr.replace(/\\//g, '-').replace(/^(\\d{4}-\\d{1})-(\\d)/, '$1-0$2');

      // 重複防止用ハッシュキー生成（日付_借方_貸方_金額_摘要）
      const entryKey = `${cleanDate}_${debitSubj}_${creditSubj}_${debitAmt}_${desc.slice(0, 15)}`;
      if (importedKeys.includes(entryKey)) {
        duplicateCount++;
        continue;
      }
      importedKeys.push(entryKey);

      // 口座マッピング判定（借方・貸方の科目および補助科目・摘要から5口座＋現金を特定）
      const matchAccount = (subj, sub, text) => {
        const full = `${subj} ${sub} ${text}`;
        if (full.includes('中京') || (subj.includes('当座') && !full.includes('十六'))) return 'bank-1';
        if (full.includes('十六')) return 'bank-2';
        if (full.includes('ゆうちょ') || full.includes('郵便')) return 'bank-3';
        if (full.includes('大垣') || full.includes('OKB')) return 'bank-4';
        if (full.includes('JA') || full.includes('農協')) return 'bank-5';
        if (subj.includes('現金')) return 'cash';
        if (subj.includes('普通預金') || subj.includes('当座預金')) return 'bank-1'; // デフォルト主口座
        return null;
      };

      const debitAcc = matchAccount(debitSubj, debitSub, desc);
      const creditAcc = matchAccount(creditSubj, creditSub, desc);

      // 取引（入出金）として抽出
      if (debitAcc && !creditAcc) {
        // 預金・現金が増加（入金仕訳）
        newTransactions.push({
          id: 'yayoi-' + Date.now() + '-' + parsedCount,
          date: cleanDate,
          type: 'income',
          partner: desc || debitSub || '弥生売上入金',
          category: creditSubj.includes('売上') ? '墓石新設代' : 'その他収入',
          amount: debitAmt,
          accountId: debitAcc,
          projectId: null,
          isActual: true, // 弥生実績
          note: `弥生仕訳: [${debitSubj}] ← [${creditSubj}] ${desc}`
        });
        parsedCount++;
      } else if (!debitAcc && creditAcc) {
        // 預金・現金が減少（支払仕訳）
        newTransactions.push({
          id: 'yayoi-' + Date.now() + '-' + parsedCount,
          date: cleanDate,
          type: 'expense',
          partner: desc || creditSub || '弥生支払経費',
          category: debitSubj.includes('仕入') ? '石材仕入' : (debitSubj.includes('給料') ? '給与手当' : 'その他経費'),
          amount: creditAmt,
          accountId: creditAcc,
          projectId: null,
          isActual: true, // 弥生実績
          note: `弥生仕訳: [${debitSubj}] → [${creditSubj}] ${desc}`
        });
        parsedCount++;
      } else if (debitAcc && creditAcc && debitAcc !== creditAcc) {
        // 口座間振替仕訳
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
          note: `弥生振替仕訳: ${desc}`
        });
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

    // 新規取引を追加（既存データにマージ）
    if (newTransactions.length > 0) {
      this.data.transactions = [...this.data.transactions, ...newTransactions];
    }

    this.saveData();
    return {
      success: true,
      parsedCount,
      duplicateCount,
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
"""

if "importYayoiCSV" not in code:
    code = code.replace("  // ユーザー・権限制御\n  getCurrentUser() {", yayoi_store_methods + "\n  // ユーザー・権限制御\n  getCurrentUser() {")

with open(store_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated store.js with Yayoi CSV import parser and financial statements.")
