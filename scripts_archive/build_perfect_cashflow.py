import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import datetime

wb = openpyxl.Workbook()
# デフォルトシートをリネーム
ws_main = wb.active
ws_main.title = "資金繰表（メイン）"

ws_income = wb.create_sheet(title="本社（入金）")
ws_expense = wb.create_sheet(title="出金")
ws_repay = wb.create_sheet(title="返済")

for ws in [ws_main, ws_income, ws_expense, ws_repay]:
    ws.views.sheetView[0].showGridLines = True

# スタイル定義
font_title = Font(name="Yu Gothic", size=13, bold=True, color="1F2937")
font_head_main = Font(name="Yu Gothic", size=10, bold=True, color="FFFFFF")
font_head_sub = Font(name="Yu Gothic", size=9, bold=True, color="1F2937")
font_body = Font(name="Yu Gothic", size=9, color="1F2937")
font_body_bold = Font(name="Yu Gothic", size=9, bold=True, color="1F2937")
font_num_bold = Font(name="Yu Gothic", size=9, bold=True, color="1E3A8A")

fill_dark_blue = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # メイン見出し
fill_emerald = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")   # 入金見出し
fill_rose = PatternFill(start_color="9F1239", end_color="9F1239", fill_type="solid")      # 出金見出し
fill_amber = PatternFill(start_color="92400E", end_color="92400E", fill_type="solid")     # 返済見出し

fill_sub_gray = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
fill_light_blue = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
fill_light_green = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
fill_light_red = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
fill_light_yellow = PatternFill(start_color="FEFCE8", end_color="FEFCE8", fill_type="solid")

fill_sat = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid") # 土曜
fill_sun = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid") # 日曜

thin_border = Side(style='thin', color='D1D5DB')
border_cell = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
thick_bottom = Border(left=thin_border, right=thin_border, top=thin_border, bottom=Side(style='medium', color='1F2937'))

# 日付リスト（2026年11月1日〜2027年3月31日：151日間）
start_date = datetime.date(2026, 11, 1)
total_days = 151
weekday_kanji = ["月", "火", "水", "木", "金", "土", "日"]

# -----------------------------------------------------------------------------
# 1. 資金繰表（メイン）の作成
# -----------------------------------------------------------------------------
ws_main["B1"] = "中川石材店　日別資金繰り管理表（メイン）"
ws_main["B1"].font = font_title
ws_main["B2"] = "※各シート（本社・出金・返済）と完全に1行対1行で連動しています。"
ws_main["B2"].font = Font(name="Yu Gothic", size=9, color="4B5563", italic=True)

main_cols = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "総合残高", 15),
    ("E", "前年同日残高", 14),
    ("F", "昨対差額", 13),
    ("G", "入金合計", 14),
    ("H", "本社売上", 13),
    ("I", "借入入金", 12),
    ("J", "出金合計", 14),
    ("K", "社員給与", 13),
    ("L", "一般出金・仕入", 14),
    ("M", "借入返済", 13),
    ("N", "源泉・住民税", 13),
    ("O", "消費・法人税", 13),
    ("P", "その他出金", 13),
    ("Q", "備考・特記事項", 24)
]

for col_l, title, width in main_cols:
    cell = ws_main[f"{col_l}4"]
    cell.value = title
    cell.font = font_head_main
    cell.fill = fill_dark_blue
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = border_cell
    ws_main.column_dimensions[col_l].width = width

# 初期総合残高（2026/11/1 時点の現預金合計: 北國 2,824,641 + ゆうちょ 3,986,877 + 金信 1,533,036 + 現金 207,705 = 8,552,259）
initial_balance = 8552259

# -----------------------------------------------------------------------------
# 2. 本社（入金）シートの作成
# -----------------------------------------------------------------------------
ws_income["B1"] = "中川石材店　日別売上・入金内訳表（本社）"
ws_income["B1"].font = font_title

income_cols = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "入金合計", 14),
    ("E", "北國銀行", 14),
    ("F", "ゆうちょ銀行", 14),
    ("G", "金沢信用金庫", 14),
    ("H", "手許現金(店頭)", 14),
    ("I", "クレジットカード", 14),
    ("J", "PayPay/電子", 13),
    ("K", "その他入金", 13),
    ("L", "入金先・お客様備考", 25)
]

for col_l, title, width in income_cols:
    cell = ws_income[f"{col_l}4"]
    cell.value = title
    cell.font = font_head_main
    cell.fill = fill_emerald
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = border_cell
    ws_income.column_dimensions[col_l].width = width

# -----------------------------------------------------------------------------
# 3. 出金シートの作成
# -----------------------------------------------------------------------------
ws_expense["B1"] = "中川石材店　日別出金・仕入・経費内訳表"
ws_expense["B1"].font = font_title

expense_cols = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "出金合計", 14),
    ("E", "石材・商品仕入", 14),
    ("F", "外注工賃・職人", 14),
    ("G", "給与・人件費", 14),
    ("H", "車両リース・燃料", 14),
    ("I", "光熱費・水道", 13),
    ("J", "通信費・ネット", 13),
    ("K", "地代家賃・維持", 13),
    ("L", "法人カード決済", 14),
    ("M", "源泉税・住民税", 13),
    ("N", "消耗品・事務用品", 13),
    ("O", "その他経費", 13),
    ("P", "支払先・内容備考", 25)
]

for col_l, title, width in expense_cols:
    cell = ws_expense[f"{col_l}4"]
    cell.value = title
    cell.font = font_head_main
    cell.fill = fill_rose
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = border_cell
    ws_expense.column_dimensions[col_l].width = width

# -----------------------------------------------------------------------------
# 4. 返済シートの作成
# -----------------------------------------------------------------------------
ws_repay["B1"] = "中川石材店　日別借入金返済内訳表"
ws_repay["B1"].font = font_title

repay_cols = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "返済合計", 14),
    ("E", "日本政策金融公庫", 15),
    ("F", "北國銀行", 14),
    ("G", "金沢信用金庫", 14),
    ("H", "商工中金", 14),
    ("I", "その他借入", 13),
    ("J", "利息合計", 13),
    ("K", "返済メモ", 22)
]

for col_l, title, width in repay_cols:
    cell = ws_repay[f"{col_l}4"]
    cell.value = title
    cell.font = font_head_main
    cell.fill = fill_amber
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = border_cell
    ws_repay.column_dimensions[col_l].width = width

# -----------------------------------------------------------------------------
# 日別データの生成＆完全行連動数式の埋め込み
# -----------------------------------------------------------------------------
for i in range(total_days):
    row = 5 + i
    cur_date = start_date + datetime.timedelta(days=i)
    w_idx = cur_date.weekday()
    w_str = weekday_kanji[w_idx]
    date_str = cur_date.strftime("%Y/%m/%d")

    # 全シート共通の日付・曜日設定
    for ws, cols in [(ws_main, main_cols), (ws_income, income_cols), (ws_expense, expense_cols), (ws_repay, repay_cols)]:
        ws[f"B{row}"] = date_str
        ws[f"C{row}"] = f'=TEXT(B{row},"aaa")'
        ws[f"B{row}"].alignment = Alignment(horizontal="center", vertical="center")
        ws[f"C{row}"].alignment = Alignment(horizontal="center", vertical="center")
        ws[f"B{row}"].font = font_body
        ws[f"C{row}"].font = font_body
        ws[f"B{row}"].border = border_cell
        ws[f"C{row}"].border = border_cell
        if w_idx == 5:
            ws[f"C{row}"].fill = fill_sat
        elif w_idx == 6:
            ws[f"C{row}"].fill = fill_sun

    # --- 1. 本社（入金）シート ---
    # D列: 入金合計 = SUM(E{row}:K{row})
    ws_income[f"D{row}"] = f"=SUM(E{row}:K{row})"
    ws_income[f"D{row}"].fill = fill_light_green
    ws_income[f"D{row}"].font = font_body_bold
    for col_l in ["D","E","F","G","H","I","J","K"]:
        c = ws_income[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
    ws_income[f"L{row}"].border = border_cell
    ws_income[f"L{row}"].font = font_body

    # --- 2. 出金シート ---
    # D列: 出金合計 = SUM(E{row}:O{row})
    ws_expense[f"D{row}"] = f"=SUM(E{row}:O{row})"
    ws_expense[f"D{row}"].fill = fill_light_red
    ws_expense[f"D{row}"].font = font_body_bold
    for col_l in ["D","E","F","G","H","I","J","K","L","M","N","O"]:
        c = ws_expense[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
    ws_expense[f"P{row}"].border = border_cell
    ws_expense[f"P{row}"].font = font_body

    # --- 3. 返済シート ---
    # D列: 返済合計 = SUM(E{row}:I{row})
    ws_repay[f"D{row}"] = f"=SUM(E{row}:I{row})"
    ws_repay[f"D{row}"].fill = fill_light_yellow
    ws_repay[f"D{row}"].font = font_body_bold
    for col_l in ["D","E","F","G","H","I","J"]:
        c = ws_repay[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
    ws_repay[f"K{row}"].border = border_cell
    ws_repay[f"K{row}"].font = font_body

    # --- 4. 資金繰表（メイン）シート ---
    # G列: 入金合計 = 本社売上(H) + 借入入金(I)
    ws_main[f"G{row}"] = f"=SUM(H{row}:I{row})"
    # H列: 本社売上 = '本社（入金）'!D{row}
    ws_main[f"H{row}"] = f"='本社（入金）'!D{row}"

    # J列: 出金合計 = SUM(K{row}:P{row})
    ws_main[f"J{row}"] = f"=SUM(K{row}:P{row})"
    # K列: 社員給与 = '出金'!G{row}
    ws_main[f"K{row}"] = f"='出金'!G{row}"
    # L列: 一般出金・仕入 = '出金'!D{row} - '出金'!G{row} - '出金'!M{row} (給与と税金を除いた一般出金)
    ws_main[f"L{row}"] = f"='出金'!D{row}-'出金'!G{row}-'出金'!M{row}"
    # M列: 借入返済 = '返済'!D{row}
    ws_main[f"M{row}"] = f"='返済'!D{row}"
    # N列: 源泉・住民税 = '出金'!M{row}
    ws_main[f"N{row}"] = f"='出金'!M{row}"

    # D列: 総合残高
    if i == 0:
        # 初日は 初期残高 + 当日入金 - 当日出金
        ws_main[f"D{row}"] = f"={initial_balance}+G{row}-J{row}"
    else:
        prev = row - 1
        # 翌日以降は 前日残高(D{prev}) + 当日入金(G{row}) - 当日出金(J{row})
        ws_main[f"D{row}"] = f"=D{prev}+G{row}-J{row}"

    # F列: 昨対差額 = D{row} - E{row}
    ws_main[f"F{row}"] = f'=IF(E{row}="","",D{row}-E{row})'

    # スタイルと書式
    for col_l in ["D","E","F","G","H","I","J","K","L","M","N","O","P"]:
        c = ws_main[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
    ws_main[f"Q{row}"].border = border_cell
    ws_main[f"Q{row}"].font = font_body

    # 残高列を薄青で強調
    ws_main[f"D{row}"].fill = fill_light_blue
    ws_main[f"D{row}"].font = font_num_bold

    # 入金合計を薄緑、出金合計を薄赤
    ws_main[f"G{row}"].fill = fill_light_green
    ws_main[f"J{row}"].fill = fill_light_red

# -----------------------------------------------------------------------------
# サンプル実データの投入（11月分のMisoca確定入金＆定例出金）
# -----------------------------------------------------------------------------
# 入金サンプル（本社シート）
# 11/5 能美農協 165,000 (北國) -> row 9
ws_income["E9"] = 165000
ws_income["L9"] = "能美農協 麹谷様 墓石解体工事"

# 11/10 森造形センター 330,000 (北國) -> row 14
ws_income["E14"] = 330000
ws_income["L14"] = "森造形センター モニュメント台座"

# 11/15 河上様 88,000 (ゆうちょ) -> row 19
ws_income["F19"] = 88000
ws_income["L19"] = "河上様 墓石クリーニング"

# 11/20 南様 120,000 (北國) -> row 24
ws_income["E24"] = 120000
ws_income["L24"] = "南様 納骨堂改修工事"

# 11/25 辻様 500,000 (金信) -> row 29
ws_income["G29"] = 500000
ws_income["L29"] = "金沢東山 辻様 墓石新築前受金"

# 出金サンプル（出金シート）
# 11/5 石材仕入 450,000 -> row 9
ws_expense["E9"] = 450000
ws_expense["P9"] = "石材・原石定期仕入"

# 11/10 外注工賃 180,000 -> row 14
ws_expense["F14"] = 180000
ws_expense["P14"] = "文字彫り・現場据付応援"

# 11/15 車両リース 65,000 -> row 19
ws_expense["H19"] = 65000
ws_expense["P19"] = "トラック・重機リース代"

# 11/20 燃料費 42,000 -> row 24
ws_expense["H24"] = 42000
ws_expense["P24"] = "デュトロ燃料代（法人カード）"

# 11/25 給与 380,000 -> row 29
ws_expense["G29"] = 380000
ws_expense["P29"] = "11月度スタッフ給与"

# 11/27 光熱費 35,000 -> row 31
ws_expense["I31"] = 35000
ws_expense["P31"] = "工場・事務所電気代"

# 返済サンプル（返済シート）
# 11/30 日本政策金融公庫 110,000 -> row 34
ws_repay["E34"] = 110000
ws_repay["K34"] = "公庫設備資金返済（元金＋利息）"

# 保存
out_path = "/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/中川石材_資金繰り表_完全連動版.xlsx"
wb.save(out_path)
print("Perfect cashflow spreadsheet generated:", out_path)
