import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import datetime

wb = openpyxl.Workbook()

# シート構成
ws_main = wb.active
ws_main.title = "資金繰表（メイン）"
ws_income = wb.create_sheet(title="本社")
ws_expense = wb.create_sheet(title="出金")
ws_repay = wb.create_sheet(title="返済")

for ws in [ws_main, ws_income, ws_expense, ws_repay]:
    ws.views.sheetView[0].showGridLines = True

# スタイル
font_title = Font(name="Yu Gothic", size=13, bold=True, color="1F2937")
font_head = Font(name="Yu Gothic", size=9, bold=True, color="FFFFFF")
font_body = Font(name="Yu Gothic", size=9, color="1F2937")
font_bold = Font(name="Yu Gothic", size=9, bold=True, color="1F2937")
font_blue_bold = Font(name="Yu Gothic", size=9, bold=True, color="1D4ED8")

fill_main = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")     # 紺
fill_income = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")   # 深緑
fill_expense = PatternFill(start_color="991B1B", end_color="991B1B", fill_type="solid")  # 深赤
fill_repay = PatternFill(start_color="92400E", end_color="92400E", fill_type="solid")    # 茶

fill_light_blue = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
fill_light_green = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
fill_light_red = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
fill_light_yellow = PatternFill(start_color="FEFCE8", end_color="FEFCE8", fill_type="solid")

fill_sat = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
fill_sun = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

thin_border = Side(style='thin', color='D1D5DB')
border_cell = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)

# -----------------------------------------------------------------------------
# 列ヘッダー定義（備考を曜日のすぐ横「D列」に配置）
# -----------------------------------------------------------------------------
# 1. 資金繰表（メイン）
main_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "備考・主要予定", 24),     # 曜日の横に移動
    ("E", "総合残高", 15),
    ("F", "前年同日残高", 14),
    ("G", "昨対差額", 13),
    ("H", "入金合計", 14),
    ("I", "本社（売上）", 14),
    ("J", "借入入金", 12),
    ("K", "出金合計", 14),
    ("L", "社員給与", 13),
    ("M", "出金（一般）", 14),
    ("N", "借入返済", 13),
    ("O", "源泉・住民税", 13),
    ("P", "消費・法人税", 13),
    ("Q", "その他出金", 12)
]

# 2. 本社（入金）
income_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "備考・お客様名", 24),     # 曜日の横に移動
    ("E", "入金合計", 14),
    ("F", "北國銀行（18277）", 16),
    ("G", "北国銀行（199439）", 16),
    ("H", "北國銀行", 14),
    ("I", "JAバンク", 14),
    ("J", "はくさん信用金庫", 16),
    ("K", "手許現金", 13),
    ("L", "クレジット・他", 13)
]

# 3. 出金
expense_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "備考・支払先", 24),       # 曜日の横に移動
    ("E", "出金合計", 14),
    ("F", "商品仕入", 14),
    ("G", "外注工賃", 14),
    ("H", "社員給与", 14),
    ("I", "車両費・燃料費", 14),
    ("J", "光熱費", 13),
    ("K", "通信費", 13),
    ("L", "地代家賃", 13),
    ("M", "法人カード", 14),
    ("N", "源泉税・住民税", 13),
    ("O", "消耗品費", 13),
    ("P", "その他経費", 13)
]

# 4. 返済（ご指定：はくさん信用金庫2本＋国民生活金融公庫の計3本）
repay_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "返済備考", 24),           # 曜日の横に移動
    ("E", "返済合計", 14),
    ("F", "国民生活金融公庫", 16),   # 国民生活金融公庫（公庫）
    ("G", "はくさん信用金庫①", 16), # はくさん信金1本目
    ("H", "はくさん信用金庫②", 16), # はくさん信金2本目
    ("I", "その他借入", 13),
    ("J", "利息合計", 13)
]

# タイトル
ws_main["B1"] = "中川石材　日別資金繰り管理表（メイン）"
ws_main["B1"].font = font_title
ws_income["B1"] = "中川石材　日別入金明細表（本社）"
ws_income["B1"].font = font_title
ws_expense["B1"] = "中川石材　日別出金明細表"
ws_expense["B1"].font = font_title
ws_repay["B1"] = "中川石材　日別借入金返済明細表"
ws_repay["B1"].font = font_title

for col_l, t, w in main_headers:
    c = ws_main[f"{col_l}4"]
    c.value = t
    c.font = font_head
    c.fill = fill_main
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = border_cell
    ws_main.column_dimensions[col_l].width = w

for col_l, t, w in income_headers:
    c = ws_income[f"{col_l}4"]
    c.value = t
    c.font = font_head
    c.fill = fill_income
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = border_cell
    ws_income.column_dimensions[col_l].width = w

for col_l, t, w in expense_headers:
    c = ws_expense[f"{col_l}4"]
    c.value = t
    c.font = font_head
    c.fill = fill_expense
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = border_cell
    ws_expense.column_dimensions[col_l].width = w

for col_l, t, w in repay_headers:
    c = ws_repay[f"{col_l}4"]
    c.value = t
    c.font = font_head
    c.fill = fill_repay
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = border_cell
    ws_repay.column_dimensions[col_l].width = w

# -----------------------------------------------------------------------------
# 日別データの生成＆完全行連動数式
# -----------------------------------------------------------------------------
start_date = datetime.date(2026, 11, 1)
total_days = 151
initial_balance = 2624533

for i in range(total_days):
    row = 5 + i
    cur_date = start_date + datetime.timedelta(days=i)
    w_idx = cur_date.weekday()

    # 日付・曜日・備考（全シート共通）
    for ws in [ws_main, ws_income, ws_expense, ws_repay]:
        if i == 0:
            ws[f"B{row}"] = '=DATE(2026,11,1)'
        else:
            ws[f"B{row}"] = f'=B{row-1}+1'
        ws[f"B{row}"].number_format = "yyyy/mm/dd"
        ws[f"B{row}"].alignment = Alignment(horizontal="center", vertical="center")
        ws[f"B{row}"].font = font_body
        ws[f"B{row}"].border = border_cell

        ws[f"C{row}"] = f'=CHOOSE(WEEKDAY(B{row}, 2), "月", "火", "水", "木", "金", "土", "日")'
        ws[f"C{row}"].alignment = Alignment(horizontal="center", vertical="center")
        ws[f"C{row}"].font = font_body
        ws[f"C{row}"].border = border_cell
        if w_idx == 5:
            ws[f"C{row}"].fill = fill_sat
        elif w_idx == 6:
            ws[f"C{row}"].fill = fill_sun

        # D列: 備考
        ws[f"D{row}"].font = font_body
        ws[f"D{row}"].border = border_cell
        ws[f"D{row}"].alignment = Alignment(horizontal="left", vertical="center")

    # --- 1. 本社（入金）シート ---
    # E列: 入金合計 = SUM(F:L)
    ws_income[f"E{row}"] = f"=SUM(F{row}:L{row})"
    ws_income[f"E{row}"].fill = fill_light_green
    ws_income[f"E{row}"].font = font_bold
    for col_l in ["E","F","G","H","I","J","K","L"]:
        c = ws_income[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")

    # --- 2. 出金シート ---
    # E列: 出金合計 = SUM(F:P)
    ws_expense[f"E{row}"] = f"=SUM(F{row}:P{row})"
    ws_expense[f"E{row}"].fill = fill_light_red
    ws_expense[f"E{row}"].font = font_bold
    for col_l in ["E","F","G","H","I","J","K","L","M","N","O","P"]:
        c = ws_expense[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")

    # --- 3. 返済シート ---
    # E列: 返済合計 = SUM(F:I) (公庫 + はくさん① + はくさん② + その他)
    ws_repay[f"E{row}"] = f"=SUM(F{row}:I{row})"
    ws_repay[f"E{row}"].fill = fill_light_yellow
    ws_repay[f"E{row}"].font = font_bold
    for col_l in ["E","F","G","H","I","J"]:
        c = ws_repay[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")

    # --- 4. 資金繰表（メイン）シート ---
    # H列: 入金合計 = SUM(I:J)
    ws_main[f"H{row}"] = f"=SUM(I{row}:J{row})"
    # I列: 本社（売上） = '本社'!E{row}
    ws_main[f"I{row}"] = f"='本社'!E{row}"

    # K列: 出金合計 = SUM(L:Q)
    ws_main[f"K{row}"] = f"=SUM(L{row}:Q{row})"
    # L列: 社員給与 = '出金'!H{row}
    ws_main[f"L{row}"] = f"=IF('出金'!H{row}=\"\",0,'出金'!H{row})"
    # M列: 出金（一般） = '出金'!E{row} - 社員給与(L) - 源泉税(O)
    ws_main[f"M{row}"] = f"='出金'!E{row}-SUM(L{row},O{row})"
    # N列: 借入返済 = '返済'!E{row}
    ws_main[f"N{row}"] = f"=IF('返済'!E{row}=\"\",0,'返済'!E{row})"
    # O列: 源泉・住民税 = '出金'!N{row}
    ws_main[f"O{row}"] = f"=IF('出金'!N{row}=\"\",0,'出金'!N{row})"

    # E列: 総合残高
    if i == 0:
        ws_main[f"E{row}"] = f"={initial_balance}+H{row}-K{row}"
    else:
        ws_main[f"E{row}"] = f"=E{row-1}+H{row}-K{row}"

    # G列: 昨対差額
    ws_main[f"G{row}"] = f'=IF(F{row}="","",E{row}-F{row})'

    for col_l in ["E","F","G","H","I","J","K","L","M","N","O","P","Q"]:
        c = ws_main[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")

    ws_main[f"E{row}"].fill = fill_light_blue
    ws_main[f"E{row}"].font = font_blue_bold
    ws_main[f"H{row}"].fill = fill_light_green
    ws_main[f"K{row}"].fill = fill_light_red

# -----------------------------------------------------------------------------
# 実例データの投入（新レイアウト）
# -----------------------------------------------------------------------------
# 本社（入金）: D列に備考、F〜K列に口座
ws_income["D9"] = "能美農協 麹谷様 墓石解体工事"
ws_income["F9"] = 165000 # 北國(18277)

ws_income["D14"] = "森造形センター モニュメント台座"
ws_income["H14"] = 330000 # 北國銀行

ws_income["D19"] = "河上様 墓石クリーニング"
ws_income["I19"] = 88000 # JAバンク

ws_income["D24"] = "南様 納骨堂改修工事"
ws_income["J24"] = 120000 # はくさん信金

ws_income["D29"] = "金沢東山 辻様 墓石新築前受金"
ws_income["K29"] = 500000 # 手許現金

# 出金: D列に備考、F列に商品仕入
ws_expense["D9"] = "商品仕入（墓石材・部材）"
ws_expense["F9"] = 450000

ws_expense["D14"] = "外注工賃（字彫り・据付）"
ws_expense["G14"] = 180000

ws_expense["D19"] = "車両費・リース料"
ws_expense["I19"] = 65000

ws_expense["D24"] = "燃料費・ガソリン代"
ws_expense["I24"] = 42000

ws_expense["D29"] = "11月度スタッフ給与"
ws_expense["H29"] = 380000

ws_expense["D31"] = "工場・事務所電気代"
ws_expense["J31"] = 35000

# 返済: D列に備考、F列に公庫、G列にはくさん①、H列にはくさん②
ws_repay["D34"] = "11月末日 定例返済"
ws_repay["F34"] = 110000 # 国民生活金融公庫
ws_repay["G34"] = 50000  # はくさん信用金庫①
ws_repay["H34"] = 35000  # はくさん信用金庫②

# メインシートの備考
ws_main["D9"] = "能美農協入金／仕入支払"
ws_main["D14"] = "森造形センター入金／外注工賃"
ws_main["D29"] = "辻様前受金／給与支払日"
ws_main["D34"] = "公庫・信金 借入返済日"

out_path = "/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/中川石材_資金繰り表_確定版.xlsx"
wb.save(out_path)
print("Updated spreadsheet saved successfully:", out_path)
