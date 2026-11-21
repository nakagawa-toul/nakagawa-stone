import re

store_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js'

with open(store_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace INITIAL_DATA.transactions with accountId enriched transactions
# We will match the transactions array in INITIAL_DATA
tx_replacement = """  transactions: [
    // 10月度取引（過去実績）
    {
      id: 'tx-1',
      date: '2026-10-30',
      type: 'expense',
      partner: '(株)東日本石材',
      category: '石材仕入',
      amount: 680000,
      accountId: 'bank-1', // 中京銀行
      projectId: 'proj-1',
      isActual: false,
      note: '佐藤家 インド産黒御影部材'
    },
    {
      id: 'tx-101',
      date: '2026-10-25',
      type: 'expense',
      partner: 'ENEOS石材町給油所',
      category: '車両・燃料',
      amount: 32000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: true,
      note: 'トラック2台 軽油代'
    },
    {
      id: 'tx-102',
      date: '2026-10-25',
      type: 'expense',
      partner: '専従者給与・従業員給与',
      category: '給与手当',
      amount: 450000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: true,
      note: '10月分給与振込'
    },
    {
      id: 'tx-103',
      date: '2026-10-27',
      type: 'expense',
      partner: '日本政策金融公庫',
      category: '借入返済',
      amount: 80000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: true,
      note: '設備資金借入元利返済'
    },

    // 11月度取引
    {
      id: 'tx-2',
      date: '2026-11-05',
      type: 'income',
      partner: '佐藤 正雄 様',
      category: '墓石新設代',
      amount: 850000,
      accountId: 'bank-1', // 中京銀行
      projectId: 'proj-1',
      isActual: false,
      note: '墓所新設 着工時内金（契約金額の半金）'
    },
    {
      id: 'tx-3',
      date: '2026-11-10',
      type: 'expense',
      partner: '中川建材(株)',
      category: '建材仕入',
      amount: 145000,
      accountId: 'bank-1', // 中京銀行
      projectId: 'proj-1',
      isActual: false,
      note: '砕石、生コン、セメント等'
    },
    {
      id: 'tx-4',
      date: '2026-11-15',
      type: 'expense',
      partner: 'オリエント重機リース',
      category: '重機リース',
      amount: 220000,
      accountId: 'bank-1', // 中京銀行
      projectId: 'proj-1',
      isActual: false,
      note: '小型カニクレーン・運搬車 3日間'
    },
    {
      id: 'tx-104',
      date: '2026-11-18',
      type: 'expense',
      partner: '東京ダイヤモンド工具',
      category: '消耗品・工具',
      amount: 28000,
      accountId: 'cash', // 手許現金
      projectId: null,
      isActual: false,
      note: '切削砥石ブレード・墓誌彫刻用ゴムシート'
    },
    {
      id: 'tx-5',
      date: '2026-11-20',
      type: 'income',
      partner: '高橋 健一 様',
      category: '戒名彫刻・納骨',
      amount: 55000,
      accountId: 'bank-3', // ゆうちょ銀行
      projectId: 'proj-3',
      isActual: false,
      note: '戒名追加彫刻および納骨立会料'
    },
    // 【重要サンプル】口座間振替（中京銀行から十六銀行へ給与・公庫資金移動、合計残高では二重計上なし）
    {
      id: 'tx-tr-1',
      date: '2026-11-22',
      type: 'transfer',
      partner: '中京銀行 ➔ 十六銀行',
      category: '口座間振替',
      amount: 500000,
      fromAccountId: 'bank-1',
      toAccountId: 'bank-2',
      projectId: null,
      isActual: false,
      note: '給料・公庫返済に備えた口座間資金移動'
    },
    // 【重要サンプル】支払口座未定の支払い（警告表示＆口座別未配分額として管理）
    {
      id: 'tx-unassigned-1',
      date: '2026-11-24',
      type: 'expense',
      partner: '中部石材加工所',
      category: '外注加工',
      amount: 180000,
      accountId: 'unassigned', // 支払口座未定！
      projectId: 'proj-1',
      isActual: false,
      note: '大型記念碑の特殊字彫り加工（出金口座未定）'
    },
    {
      id: 'tx-6',
      date: '2026-11-25',
      type: 'expense',
      partner: '専従者給与・従業員給与',
      category: '給与手当',
      amount: 450000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: false,
      note: '11月分給与振込'
    },
    {
      id: 'tx-105',
      date: '2026-11-25',
      type: 'expense',
      partner: 'ENEOS石材町給油所',
      category: '車両・燃料',
      amount: 35000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: false,
      note: '現場トラック燃料代'
    },
    {
      id: 'tx-106',
      date: '2026-11-27',
      type: 'expense',
      partner: '日本政策金融公庫',
      category: '借入返済',
      amount: 80000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: false,
      note: '設備資金借入元利返済'
    },
    {
      id: 'tx-7',
      date: '2026-11-30',
      type: 'income',
      partner: '宗教法人 田中寺',
      category: '改修・補修代',
      amount: 1200000,
      accountId: 'bank-1', // 中京銀行
      projectId: 'proj-2',
      isActual: false,
      note: '住職墓補修・参道補修 一式完工分'
    },

    // 12月度取引
    {
      id: 'tx-8',
      date: '2026-12-10',
      type: 'expense',
      partner: '中川建材(株)',
      category: '建材仕入',
      amount: 85000,
      accountId: 'bank-1', // 中京銀行
      projectId: 'proj-2',
      isActual: false,
      note: '補修用モルタル・御影板石'
    },
    {
      id: 'tx-9',
      date: '2026-12-15',
      type: 'income',
      partner: '佐藤 正雄 様',
      category: '墓石新設代',
      amount: 850000,
      accountId: 'bank-1', // 中京銀行
      projectId: 'proj-1',
      isActual: false,
      note: '墓所新設 完工時残金（お引き渡し時）'
    },
    {
      id: 'tx-10',
      date: '2026-12-25',
      type: 'expense',
      partner: '専従者給与・従業員給与',
      category: '給与手当',
      amount: 550000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: false,
      note: '12月分給与＋年末一時金'
    },
    {
      id: 'tx-11',
      date: '2026-12-27',
      type: 'expense',
      partner: '日本政策金融公庫',
      category: '借入返済',
      amount: 80000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: false,
      note: '設備資金借入元利返済'
    },

    // 1月度取引
    {
      id: 'tx-12',
      date: '2027-01-15',
      type: 'expense',
      partner: '損害保険ジャパン',
      category: '損害保険料',
      amount: 110000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: false,
      note: '工事賠償責任保険 年払い'
    },
    {
      id: 'tx-13',
      date: '2027-01-20',
      type: 'income',
      partner: '渡辺 浩司 様',
      category: '墓じまい代',
      amount: 450000,
      accountId: 'bank-1', // 中京銀行
      projectId: null,
      isActual: false,
      note: '市営霊園 墓所撤去・更地返還工事代'
    },
    {
      id: 'tx-14',
      date: '2027-01-25',
      type: 'expense',
      partner: '専従者給与・従業員給与',
      category: '給与手当',
      amount: 450000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: false,
      note: '1月分給与振込'
    },
    {
      id: 'tx-15',
      date: '2027-01-27',
      type: 'expense',
      partner: '日本政策金融公庫',
      category: '借入返済',
      amount: 80000,
      accountId: 'bank-2', // 十六銀行
      projectId: null,
      isActual: false,
      note: '設備資金借入元利返済'
    }
  ],"""

pattern = r'  transactions:\s*\[.*?\n  \],'
text = re.sub(pattern, tx_replacement, text, flags=re.DOTALL)

with open(store_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated INITIAL_DATA transactions with accountId, transfer, and unassigned sample.")
