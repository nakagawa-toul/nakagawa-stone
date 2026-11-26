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
# 1. 口座マスター（弥生会計と完全一致）
# -----------------------------------------------------------------------------
# 弥生科目: 北國銀行（18277）, 北国銀行（199439）, 北國銀行, JAバンク, はくさん信用金庫, 手許現金
yayoi_accounts = [
    ("E", "北國銀行（18277）", 16),
    ("F", "北国銀行（199439）", 16),
    ("G", "北國銀行", 14),
    ("H", "JAバンク", 14),
    ("I", "はくさん信用金庫", 16),
    ("J", "手許現金", 13),
    ("K", "クレジット・他", 13),
    ("L", "備考・お客様名", 25)
]

# -----------------------------------------------------------------------------
# 2. シート列定義
# -----------------------------------------------------------------------------
# メインシート
main_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "総合残高", 15),
    ("E", "前年同日残高", 14),
    ("F", "昨対差額", 13),
    ("G", "入金合計", 14),
    ("H", "本社（売上）", 14),
    ("I", "借入入金", 12),
    ("J", "出金合計", 14),
    ("K", "社員給与", 13),
    ("L", "出金（一般）", 14),
    ("M", "借入返済", 13),
    ("N", "源泉・住民税", 13),
    ("O", "消費・法人税", 13),
    ("P", "その他", 12),
    ("Q", "備考", 22)
]

# 本社シート（入金）
income_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "入金合計", 14),
] + yayoi_accounts

# 出金シート（ご要望：石材のなどなしで商品仕入などに）
expense_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "出金合計", 14),
    ("E", "商品仕入", 14),         # 修正：石材のなどなし
    ("F", "外注工賃", 14),
    ("G", "社員給与", 14),
    ("H", "車両費・燃料費", 14),
    ("I", "光熱費", 13),
    ("J", "通信費", 13),
    ("K", "地代家賃", 13),
    ("L", "法人カード", 14),
    ("M", "源泉税・住民税", 13),
    ("N", "消耗品費", 13),
    ("O", "その他経費", 13),
    ("P", "備考・支払先", 25)
]

# 返済シート
repay_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "返済合計", 14),
    ("E", "日本政策金融公庫", 15),
    ("F", "はくさん信用金庫", 15),
    ("G", "北國銀行", 14),
    ("H", "その他借入", 13),
    ("I", "利息合計", 13),
    ("J", "返済備考", 22)
]

# タイトルと見出し描画
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
# 3. 日付と完全エラーフリーの数式埋め込み
# -----------------------------------------------------------------------------
# 2026年11月1日〜2027年3月31日（151日間）
start_date = datetime.date(2026, 11, 1)
total_days = 151

# 弥生確定残高の合計（¥2,416,828 ＋ 金庫現金 ¥207,705 ＝ ¥2,624,533）
initial_balance = 2624533

for i in range(total_days):
    row = 5 + i
    cur_date = start_date + datetime.timedelta(days=i)
    w_idx = cur_date.weekday()

    # --- 日付と曜日（CHOOSE + WEEKDAYでGoogleスプレッドシートでも100%エラーなく日本語曜日表示） ---
    for ws in [ws_main, ws_income, ws_expense, ws_repay]:
        if i == 0:
            ws[f"B{row}"] = f'=DATE(2026,11,1)'
        else:
            ws[f"B{row}"] = f'=B{row-1}+1'
        ws[f"B{row}"].number_format = "yyyy/mm/dd"
        ws[f"B{row}"].alignment = Alignment(horizontal="center", vertical="center")
        ws[f"B{row}"].font = font_body
        ws[f"B{row}"].border = border_cell

        # 曜日数式: Googleスプレッドシート・Excel双方で完璧動作
        ws[f"C{row}"] = f'=CHOOSE(WEEKDAY(B{row}, 2), "月", "火", "水", "木", "金", "土", "日")'
        ws[f"C{row}"].alignment = Alignment(horizontal="center", vertical="center")
        ws[f"C{row}"].font = font_body
        ws[f"C{row}"].border = border_cell
        if w_idx == 5:
            ws[f"C{row}"].fill = fill_sat
        elif w_idx == 6:
            ws[f"C{row}"].fill = fill_sun

    # --- 本社（入金）シート ---
    # D列: 入金合計 = SUM(E:K) （数値以外の空白があってもエラーにならないSUM）
    ws_income[f"D{row}"] = f"=SUM(E{row}:K{row})"
    ws_income[f"D{row}"].fill = fill_light_green
    ws_income[f"D{row}"].font = font_bold
    for col_l in ["D","E","F","G","H","I","J","K"]:
        c = ws_income[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
    ws_income[f"L{row}"].border = border_cell
    ws_income[f"L{row}"].font = font_body

    # --- 出金シート ---
    # D列: 出金合計 = SUM(E:O)
    ws_expense[f"D{row}"] = f"=SUM(E{row}:O{row})"
    ws_expense[f"D{row}"].fill = fill_light_red
    ws_expense[f"D{row}"].font = font_bold
    for col_l in ["D","E","F","G","H","I","J","K","L","M","N","O"]:
        c = ws_expense[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
    ws_expense[f"P{row}"].border = border_cell
    ws_expense[f"P{row}"].font = font_body

    # --- 返済シート ---
    # D列: 返済合計 = SUM(E:H)
    ws_repay[f"D{row}"] = f"=SUM(E{row}:H{row})"
    ws_repay[f"D{row}"].fill = fill_light_yellow
    ws_repay[f"D{row}"].font = font_bold
    for col_l in ["D","E","F","G","H","I"]:
        c = ws_repay[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
    ws_repay[f"J{row}"].border = border_cell
    ws_repay[f"J{row}"].font = font_body

    # --- 資金繰表（メイン）シート ---
    # G列: 入金合計 = SUM(H:I)
    ws_main[f"G{row}"] = f"=SUM(H{row}:I{row})"
    # H列: 本社売上 = 本社シートのD列
    ws_main[f"H{row}"] = f"='本社'!D{row}"

    # J列: 出金合計 = SUM(K:P)
    ws_main[f"J{row}"] = f"=SUM(K{row}:P{row})"
    # K列: 社員給与 = 出金シートのG列
    ws_main[f"K{row}"] = f"=IF('出金'!G{row}=\"\",0,'出金'!G{row})"
    # L列: 出金（一般・仕入） = 出金合計 - 給与 - 税金 (SUMとIFで#VALUE!エラーを完全防止)
    ws_main[f"L{row}"] = f"='出金'!D{row}-SUM(K{row},N{row})"
    # M列: 借入返済 = 返済シートのD列
    ws_main[f"M{row}"] = f"=IF('返済'!D{row}=\"\",0,'返済'!D{row})"
    # N列: 源泉・住民税 = 出金シートのM列
    ws_main[f"N{row}"] = f"=IF('出金'!M{row}=\"\",0,'出金'!M{row})"

    # D列: 総合残高
    if i == 0:
        ws_main[f"D{row}"] = f"={initial_balance}+G{row}-J{row}"
    else:
        ws_main[f"D{row}"] = f"=D{row-1}+G{row}-J{row}"

    # F列: 昨対差額 = IF(E{row}="","",D{row}-E{row})
    ws_main[f"F{row}"] = f'=IF(E{row}="","",D{row}-E{row})'

    for col_l in ["D","E","F","G","H","I","J","K","L","M","N","O","P"]:
        c = ws_main[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
    ws_main[f"Q{row}"].border = border_cell
    ws_main[f"Q{row}"].font = font_body

    ws_main[f"D{row}"].fill = fill_light_blue
    ws_main[f"D{row}"].font = font_blue_bold
    ws_main[f"G{row}"].fill = fill_light_green
    ws_main[f"J{row}"].fill = fill_light_red

# -----------------------------------------------------------------------------
# 4. サンプル実データ投入（弥生口座＆商品仕入に合わせたもの）
# -----------------------------------------------------------------------------
# 11/5 能美農協 165,000 (北國銀行18277) -> row 9
ws_income["E9"] = 165000
ws_income["L9"] = "能美農協 麹谷様 墓石解体工事"

# 11/10 森造形センター 330,000 (北國銀行) -> row 14
ws_income["G14"] = 330000
ws_income["L14"] = "森造形センター モニュメント台座"

# 11/15 河上様 88,000 (JAバンク) -> row 19
ws_income["H19"] = 88000
ws_income["L19"] = "河上様 墓石クリーニング"

# 11/20 南様 120,000 (はくさん信金) -> row 24
ws_income["I24"] = 120000
ws_income["L24"] = "南様 納骨堂改修工事"

# 11/25 辻様 500,000 (手許現金) -> row 29
ws_income["J29"] = 500000
ws_income["L29"] = "金沢東山 辻様 墓石新築前受金"

# 出金サンプル（E列: 商品仕入）
ws_expense["E9"] = 450000
ws_expense["P9"] = "商品仕入（墓石・部材）"

ws_expense["F14"] = 180000
ws_expense["P14"] = "外注工賃（字彫り・据付）"

ws_expense["H19"] = 65000
ws_expense["P19"] = "車両費・リース代"

ws_expense["H24"] = 42000
ws_expense["P24"] = "燃料費・ガソリン代"

ws_expense["G29"] = 380000
ws_expense["P29"] = "11月度スタッフ給与"

ws_expense["I31"] = 35000
ws_expense["P31"] = "工場・事務所光熱費"

# 返済サンプル
ws_repay["E34"] = 110000
ws_repay["J34"] = "公庫設備資金返済"

# 保存
out_path = "/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/中川石材_資金繰り表_弥生口座完全準拠版.xlsx"
wb.save(out_path)
print("Spreadsheet successfully built:", out_path)
