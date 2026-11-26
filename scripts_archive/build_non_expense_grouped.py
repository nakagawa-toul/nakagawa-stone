import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import datetime

wb = openpyxl.Workbook()

# シート構成
ws_main = wb.active
ws_main.title = "資金繰表（メイン）"
ws_income = wb.create_sheet(title="入金")
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

# 見出し塗りつぶし
fill_main_def = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")     # 濃紺
fill_income_head = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid") # 深緑
fill_expense_head = PatternFill(start_color="991B1B", end_color="991B1B", fill_type="solid")# 深赤
fill_repay_head = PatternFill(start_color="92400E", end_color="92400E", fill_type="solid")  # 茶

# 「事業の経費とならないもの」3つ統一カラー（事業主消費、源泉・所得税、消費税・法人税）
# 琥珀・テラコッタ系で美しく統一
fill_non_expense_head = PatternFill(start_color="B45309", end_color="B45309", fill_type="solid") # 琥珀色
fill_non_expense_body = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # 薄黄色
font_non_expense = Font(name="Yu Gothic", size=9, bold=True, color="92400E")

# 通常データ色
fill_light_blue = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
fill_light_green = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
fill_light_red = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
fill_light_yellow = PatternFill(start_color="FEFCE8", end_color="FEFCE8", fill_type="solid")

fill_sat = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
fill_sun = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

thin_border = Side(style='thin', color='D1D5DB')
border_cell = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)

# -----------------------------------------------------------------------------
# 列ヘッダー定義（3つを経費外グループとしてそのたの直前にまとめて移動）
# -----------------------------------------------------------------------------
# 1. 資金繰表（メイン）
main_headers = [
    ("B", "日付", 12, fill_main_def),
    ("C", "曜日", 5, fill_main_def),
    ("D", "備考・主要予定", 24, fill_main_def),
    ("E", "総合残高", 15, fill_main_def),
    ("F", "前年同日残高", 14, fill_main_def),
    ("G", "昨対差額", 13, fill_main_def),
    ("H", "入金合計", 14, fill_main_def),
    ("I", "売上入金", 14, fill_main_def),
    ("J", "借入入金", 12, fill_main_def),
    ("K", "出金合計", 14, fill_main_def),
    ("L", "洋外注費", 13, fill_main_def),
    ("M", "外注費", 14, fill_main_def),
    ("N", "商品仕入", 14, fill_main_def),
    ("O", "一般経費", 14, fill_main_def),
    ("P", "借入返済", 13, fill_main_def),
    # --- ここから経費外グループ3つ（そのたの直前・同色！） ---
    ("Q", "事業主消費", 14, fill_non_expense_head),
    ("R", "源泉・所得税", 13, fill_non_expense_head),
    ("S", "消費税・法人税", 13, fill_non_expense_head),
    # --- 右端 ---
    ("T", "その他出金", 12, fill_main_def)
]

# 2. 入金
income_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "備考・お客様名", 24),
    ("E", "入金合計", 14),
    ("F", "北國銀行（18277）", 16),
    ("G", "北国銀行（199439）", 16),
    ("H", "北國銀行", 14),
    ("I", "JAバンク", 14),
    ("J", "はくさん信用金庫", 16),
    ("K", "手許現金", 13),
    ("L", "クレジット・他", 13)
]

# 3. 出金（経費外3つを右端「その他経費」の直前に移動 ＆ 同色統一）
expense_headers = [
    ("B", "日付", 12, fill_expense_head),
    ("C", "曜日", 5, fill_expense_head),
    ("D", "備考・支払先", 24, fill_expense_head),
    ("E", "出金合計", 14, fill_expense_head),
    ("F", "商品仕入", 14, fill_expense_head),
    ("G", "外注費", 14, fill_expense_head),
    ("H", "洋外注費", 14, fill_expense_head),
    ("I", "車両費・燃料費", 14, fill_expense_head),
    ("J", "光熱費", 13, fill_expense_head),
    ("K", "通信費", 13, fill_expense_head),
    ("L", "地代家賃", 13, fill_expense_head),
    ("M", "法人カード", 14, fill_expense_head),
    ("N", "消耗品費", 13, fill_expense_head),
    # --- ここから経費外グループ3つ（そのたの直前・同色！） ---
    ("O", "事業主消費", 14, fill_non_expense_head),
    ("P", "源泉・所得税", 13, fill_non_expense_head),
    ("Q", "消費税・法人税", 13, fill_non_expense_head),
    # --- 右端 ---
    ("R", "その他経費", 13, fill_expense_head)
]

# 4. 返済
repay_headers = [
    ("B", "日付", 12),
    ("C", "曜日", 5),
    ("D", "返済備考", 24),
    ("E", "返済合計", 14),
    ("F", "国民生活金融公庫", 16),
    ("G", "はくさん信用金庫①", 16),
    ("H", "はくさん信用金庫②", 16),
    ("I", "その他借入", 13),
    ("J", "利息合計", 13)
]

# タイトル
ws_main["B1"] = "中川石材　日別資金繰り管理表（メイン）"
ws_main["B1"].font = font_title
ws_income["B1"] = "中川石材　日別売上・入金明細表"
ws_income["B1"].font = font_title
ws_expense["B1"] = "中川石材　日別出金明細表"
ws_expense["B1"].font = font_title
ws_repay["B1"] = "中川石材　日別借入金返済明細表"
ws_repay["B1"].font = font_title

for col_l, t, w, fill_c in main_headers:
    c = ws_main[f"{col_l}4"]
    c.value = t
    c.font = font_head
    c.fill = fill_c
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = border_cell
    ws_main.column_dimensions[col_l].width = w

for col_l, t, w in income_headers:
    c = ws_income[f"{col_l}4"]
    c.value = t
    c.font = font_head
    c.fill = fill_income_head
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = border_cell
    ws_income.column_dimensions[col_l].width = w

for col_l, t, w, fill_c in expense_headers:
    c = ws_expense[f"{col_l}4"]
    c.value = t
    c.font = font_head
    c.fill = fill_c
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border = border_cell
    ws_expense.column_dimensions[col_l].width = w

for col_l, t, w in repay_headers:
    c = ws_repay[f"{col_l}4"]
    c.value = t
    c.font = font_head
    c.fill = fill_repay_head
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

    # --- 1. 入金シート ---
    ws_income[f"E{row}"] = f"=SUM(F{row}:L{row})"
    ws_income[f"E{row}"].fill = fill_light_green
    ws_income[f"E{row}"].font = font_bold
    for col_l in ["E","F","G","H","I","J","K","L"]:
        c = ws_income[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")

    # --- 2. 出金シート ---
    # E列: 出金合計 = SUM(F:R)
    ws_expense[f"E{row}"] = f"=SUM(F{row}:R{row})"
    ws_expense[f"E{row}"].fill = fill_light_red
    ws_expense[f"E{row}"].font = font_bold
    for col_l in ["E","F","G","H","I","J","K","L","M","N","O","P","Q","R"]:
        c = ws_expense[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
        if col_l in ["O", "P", "Q"]: # 経費外3つ（同色統一）
            c.fill = fill_non_expense_body
            c.font = font_non_expense

    # --- 3. 返済シート ---
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
    # I列: 売上入金 = '入金'!E{row}
    ws_main[f"I{row}"] = f"='入金'!E{row}"

    # K列: 出金合計 = SUM(L:T)
    ws_main[f"K{row}"] = f"=SUM(L{row}:T{row})"
    # L列: 洋外注費 = '出金'!H{row}
    ws_main[f"L{row}"] = f"=IF('出金'!H{row}=\"\",0,'出金'!H{row})"
    # M列: 外注費 = '出金'!G{row}
    ws_main[f"M{row}"] = f"=IF('出金'!G{row}=\"\",0,'出金'!G{row})"
    # N列: 商品仕入 = '出金'!F{row}
    ws_main[f"N{row}"] = f"=IF('出金'!F{row}=\"\",0,'出金'!F{row})"
    # O列: 一般経費 = 出金合計 - (洋外注 + 外注 + 仕入 + 経費外3つ + その他出金)
    ws_main[f"O{row}"] = f"='出金'!E{row}-SUM(L{row},M{row},N{row},Q{row},R{row},S{row},T{row})"
    # P列: 借入返済 = '返済'!E{row}
    ws_main[f"P{row}"] = f"=IF('返済'!E{row}=\"\",0,'返済'!E{row})"

    # Q列: 事業主消費 = '出金'!O{row} (経費外①)
    ws_main[f"Q{row}"] = f"=IF('出金'!O{row}=\"\",0,'出金'!O{row})"
    # R列: 源泉・所得税 = '出金'!P{row} (経費外②)
    ws_main[f"R{row}"] = f"=IF('出金'!P{row}=\"\",0,'出金'!P{row})"
    # S列: 消費税・法人税 = '出金'!Q{row} (経費外③)
    ws_main[f"S{row}"] = f"=IF('出金'!Q{row}=\"\",0,'出金'!Q{row})"

    # T列: その他出金 = '出金'!R{row}
    ws_main[f"T{row}"] = f"=IF('出金'!R{row}=\"\",0,'出金'!R{row})"

    # E列: 総合残高
    if i == 0:
        ws_main[f"E{row}"] = f"={initial_balance}+H{row}-K{row}"
    else:
        ws_main[f"E{row}"] = f"=E{row-1}+H{row}-K{row}"

    # G列: 昨対差額
    ws_main[f"G{row}"] = f'=IF(F{row}="","",E{row}-F{row})'

    for col_l in ["E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T"]:
        c = ws_main[f"{col_l}{row}"]
        c.number_format = "#,##0"
        c.border = border_cell
        c.alignment = Alignment(horizontal="right", vertical="center")
        if col_l in ["Q", "R", "S"]: # 経費外3つ（同色統一）
            c.fill = fill_non_expense_body
            c.font = font_non_expense

    ws_main[f"E{row}"].fill = fill_light_blue
    ws_main[f"E{row}"].font = font_blue_bold
    ws_main[f"H{row}"].fill = fill_light_green
    ws_main[f"K{row}"].fill = fill_light_red

# 実例データ投入
ws_income["D9"] = "能美農協 麹谷様 墓石解体工事"
ws_income["F9"] = 165000

ws_income["D14"] = "森造形センター モニュメント台座"
ws_income["H14"] = 330000

ws_income["D19"] = "河上様 墓石クリーニング"
ws_income["I19"] = 88000

ws_income["D24"] = "南様 納骨堂改修工事"
ws_income["J24"] = 120000

ws_income["D29"] = "金沢東山 辻様 墓石新築前受金"
ws_income["K29"] = 500000

# 出金実例（F:仕入, G:外注, H:洋外注, I:車両, J:光熱, O:事業主消費, P:源泉, Q:消費税, R:その他）
ws_expense["D9"] = "商品仕入（墓石材・部材）"
ws_expense["F9"] = 450000

ws_expense["D14"] = "外注費（据付応援）"
ws_expense["G14"] = 180000

ws_expense["D19"] = "車両費・リース料"
ws_expense["I19"] = 65000

ws_expense["D20"] = "事業主消費（生活費引出）"
ws_expense["O20"] = 150000 # 事業主消費

ws_expense["D24"] = "燃料費・ガソリン代"
ws_expense["I24"] = 42000

ws_expense["D25"] = "源泉徴収税 納付"
ws_expense["P25"] = 35000  # 源泉・所得税

ws_expense["D29"] = "洋外注費（字彫り・加工工賃）"
ws_expense["H29"] = 380000 # 洋外注費

ws_expense["D31"] = "工場・事務所光熱費"
ws_expense["J31"] = 35000

# 返済実例
ws_repay["D34"] = "11月末日 定例返済"
ws_repay["F34"] = 110000
ws_repay["G34"] = 50000
ws_repay["H34"] = 35000

# メイン備考
ws_main["D9"] = "能美農協入金／商品仕入"
ws_main["D14"] = "森造形センター入金／外注費"
ws_main["D20"] = "事業主消費（生活費引出）"
ws_main["D25"] = "源泉・所得税 納付"
ws_main["D29"] = "辻様前受金／洋外注費"
ws_main["D34"] = "公庫・信金 借入返済日"

out_path = "/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/中川石材_資金繰り表_経費外配置統一版.xlsx"
wb.save(out_path)
print("Saved successfully:", out_path)
