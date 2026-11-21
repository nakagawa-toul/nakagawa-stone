import re

store_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js'

with open(store_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update STORAGE_KEY
content = content.replace("const STORAGE_KEY = 'nakagawa_stone_app_data_v3';", "const STORAGE_KEY = 'nakagawa_stone_app_data_v4';")

# 2. Add DEFAULT_ACCOUNTS definition right before INITIAL_DATA
accounts_def = """// 5つの銀行口座 + 手許現金マスター（計6財布の個別管理）
const DEFAULT_ACCOUNTS = [
  { id: 'bank-1', name: '中京銀行（当座預金 / 主口座）', shortName: '中京銀行', type: 'bank', baseBalance: 2450000, baseDate: '2026-10-31', color: '#2563eb' },
  { id: 'bank-2', name: '十六銀行（普通預金）', shortName: '十六銀行', type: 'bank', baseBalance: 1200000, baseDate: '2026-10-31', color: '#059669' },
  { id: 'bank-3', name: 'ゆうちょ銀行', shortName: 'ゆうちょ', type: 'bank', baseBalance: 650000, baseDate: '2026-10-31', color: '#16a34a' },
  { id: 'bank-4', name: '大垣共立銀行（普通預金）', shortName: '大垣共立', type: 'bank', baseBalance: 350000, baseDate: '2026-10-31', color: '#4f46e5' },
  { id: 'bank-5', name: 'JAバンク（普通預金）', shortName: 'JAバンク', type: 'bank', baseBalance: 200000, baseDate: '2026-10-31', color: '#d97706' },
  { id: 'cash', name: '手許現金', shortName: '手許現金', type: 'cash', baseBalance: 150000, baseDate: '2026-10-31', color: '#e11d48' }
];

"""

if "const DEFAULT_ACCOUNTS =" not in content:
    content = content.replace("// 初期架空データ\nconst INITIAL_DATA = {", accounts_def + "// 初期架空データ\nconst INITIAL_DATA = {\n  accounts: DEFAULT_ACCOUNTS,")

with open(store_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated DEFAULT_ACCOUNTS and STORAGE_KEY successfully.")
