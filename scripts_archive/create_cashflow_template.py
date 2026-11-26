import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import datetime

wb = openpyxl.Workbook()

# スタイル定義
font_title = Font(name="Yu Gothic", size=14, bold=True, color="1F2937")
font_header = Font(name="Yu Gothic", size=10, bold=True, color="FFFFFF")
font_sub = Font(name="Yu Gothic", size=9, bold=True, color="374151")
font_body = Font(name="Yu Gothic", size=10, color="1F2937")
font_bold = Font(name="Yu Gothic", size=10, bold=True, color="1F2937")
font_alert = Font(name="Yu Gothic", size=10, bold=True, color="DC2626")

fill_main_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # 濃紺
fill_income_header = PatternFill(start_color="047857", end_color="047857", fill_type="solid") # 緑
fill_expense_header = PatternFill(start_color="B91C1C", end_color="B91C1C", fill_type="solid") # 赤
fill_bank_header = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid") # 青
fill_sub_header = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
fill_yellow = PatternFill(start_color="FEF08A", end_color="FEF08A", fill_type="solid")
fill_light_blue = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
fill_light_green = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
fill_light_red = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
fill_sat = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
fill_sun = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

thin_border_side = Side(style='thin', color='D1D5DB')
border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
thick_top = Border(top=Side(style='medium', color='1F2937'), bottom=Side(style='double', color='1F2937'))

# ==============================================================
# シート1: 資金繰表（メイン）
# ==============================================================
ws_main = wb.active
ws_main.title = "資金繰表（メイン）"
ws_main.views.sheetView[0].showGridLines = True

ws_main["A1"] = "中川石材店　日別資金繰り管理表（総合メイン）"
ws_main["A1"].font = font_title

headers_main = [
    ("A3", "日付", 12),
    ("B3", "曜日", 6),
    ("C3", "総合残高", 15),
    ("D3", "入金合計", 14),
    ("E3", "出金合計", 14),
    ("F3", "当日収支", 13),
    ("G3", "北國銀行", 14),
    ("H3", "ゆうちょ銀行", 14),
    ("I3", "金沢信用金庫", 14),
    ("J3", "手許現金(金庫)", 14),
    ("K3", "備考・主要予定", 25)
]

for pos, text, width in headers_main:
    cell = ws_main[pos]
    cell.value = text
    cell.font = font_header
    cell.fill = fill_main_header
    cell.alignment = Alignment(horizontal="center", vertical="center")
    col_letter = pos[0]
    ws_main.column_dimensions[col_letter].width = width

# 2026年11月1日〜12月31日の日別行を生成（61日間）
start_date = datetime.date(2026, 11, 1)
days = 61
weekday_kanji = ["月", "火", "水", "木", "金", "土", "日"]

for i in range(days):
    row = 4 + i
    cur_date = start_date + datetime.timedelta(days=i)
    w_idx = cur_date.weekday()
    w_str = weekday_kanji[w_idx]
    
    ws_main[f"A{row}"] = cur_date.strftime("%Y/%m/%d")
    ws_main[f"B{row}"] = w_str
    
    # 総合残高 = 北國 + ゆうちょ + 金沢信金 + 手許現金
    ws_main[f"C{row}"] = f"=G{row}+H{row}+I{row}+J{row}"
    
    # 入金合計 = 各行の入金合計（口座別残高シートから集計または売上予定シートから集計）
    # 当日収支 = 入金合計 - 出金合計
    ws_main[f"F{row}"] = f"=D{row}-E{row}"
    
    # 各口座残高は「口座別残高」シートを参照
    ws_main[f"G{row}"] = f"='口座別残高'!C{row}"
    ws_main[f"H{row}"] = f"='口座別残高'!D{row}"
    ws_main[f"I{row}"] = f"='口座別残高'!E{row}"
    ws_main[f"J{row}"] = f"='口座別残高'!F{row}"
    
    # 入金合計・出金合計も口座別シートから参照
    ws_main[f"D{row}"] = f"='口座別残高'!G{row}"
    ws_main[f"E{row}"] = f"='口座別残高'!H{row}"
    
    # スタイル
    for col_l in ["A","B","C","D","E","F","G","H","I","J","K"]:
        c = ws_main[f"{col_l}{row}"]
        c.font = font_body
        c.border = border_cell
        if col_l in ["C","D","E","F","G","H","I","J"]:
            c.number_format = "#,##0"
            c.alignment = Alignment(horizontal="right", vertical="center")
        else:
            c.alignment = Alignment(horizontal="center", vertical="center")
            
    if w_idx == 5: # 土
        ws_main[f"B{row}"].fill = fill_sat
    elif w_idx == 6: # 日
        ws_main[f"B{row}"].fill = fill_sun
        
    # 残高列を薄い青で強調
    ws_main[f"C{row}"].fill = fill_light_blue
    ws_main[f"C{row}"].font = font_bold

# ==============================================================
# シート2: 口座別残高
# ==============================================================
ws_bank = wb.create_sheet(title="口座別残高")
ws_bank.views.sheetView[0].showGridLines = True

ws_bank["A1"] = "中川石材店　口座別・日別残高推移"
ws_bank["A1"].font = font_title

headers_bank = [
    ("A3", "日付", 12),
    ("B3", "曜日", 6),
    ("C3", "北國銀行", 15),
    ("D3", "ゆうちょ銀行", 15),
    ("E3", "金沢信用金庫", 15),
    ("F3", "手許現金(金庫)", 15),
    ("G3", "当日入金計", 13),
    ("H3", "当日出金計", 13),
    ("I3", "メモ・移動など", 25)
]

for pos, text, width in headers_bank:
    cell = ws_bank[pos]
    cell.value = text
    cell.font = font_header
    cell.fill = fill_bank_header
    cell.alignment = Alignment(horizontal="center", vertical="center")
    col_letter = pos[0]
    ws_bank.column_dimensions[col_letter].width = width

# 初期残高（4行目: 11/1）
ws_bank["A4"] = "2026/11/01"
ws_bank["B4"] = "日"
ws_bank["C4"] = 2824641  # 北國
ws_bank["D4"] = 3986877  # ゆうちょ
ws_bank["E4"] = 1533036  # 金沢信金
ws_bank["F4"] = 207705   # 手許現金

for i in range(days):
    row = 4 + i
    cur_date = start_date + datetime.timedelta(days=i)
    w_idx = cur_date.weekday()
    w_str = weekday_kanji[w_idx]
    
    ws_bank[f"A{row}"] = cur_date.strftime("%Y/%m/%d")
    ws_bank[f"B{row}"] = w_str
    
    if i > 0:
        prev = row - 1
        # 翌日以降: 前日残高 + 当日入金 - 当日出金 (SUMIFSで各シートから自動集計)
        # 北國
        ws_bank[f"C{row}"] = f"=C{prev}+SUMIFS('売上・入金予定'!$D$4:$D$100,'売上・入金予定'!$A$4:$A$100,A{row},'売上・入金予定'!$E$4:$E$100,\"北國銀行\")-SUMIFS('仕入・支払予定'!$D$4:$D$100,'仕入・支払予定'!$A$4:$A$100,A{row},'仕入・支払予定'!$E$4:$E$100,\"北國銀行\")"
        # ゆうちょ
        ws_bank[f"D{row}"] = f"=D{prev}+SUMIFS('売上・入金予定'!$D$4:$D$100,'売上・入金予定'!$A$4:$A$100,A{row},'売上・入金予定'!$E$4:$E$100,\"ゆうちょ銀行\")-SUMIFS('仕入・支払予定'!$D$4:$D$100,'仕入・支払予定'!$A$4:$A$100,A{row},'仕入・支払予定'!$E$4:$E$100,\"ゆうちょ銀行\")"
        # 金沢信金
        ws_bank[f"E{row}"] = f"=E{prev}+SUMIFS('売上・入金予定'!$D$4:$D$100,'売上・入金予定'!$A$4:$A$100,A{row},'売上・入金予定'!$E$4:$E$100,\"金沢信用金庫\")-SUMIFS('仕入・支払予定'!$D$4:$D$100,'仕入・支払予定'!$A$4:$A$100,A{row},'仕入・支払予定'!$E$4:$E$100,\"金沢信用金庫\")"
        # 手許現金
        ws_bank[f"F{row}"] = f"=F{prev}+SUMIFS('売上・入金予定'!$D$4:$D$100,'売上・入金予定'!$A$4:$A$100,A{row},'売上・入金予定'!$E$4:$E$100,\"現金\")-SUMIFS('仕入・支払予定'!$D$4:$D$100,'仕入・支払予定'!$A$4:$A$100,A{row},'仕入・支払予定'!$E$4:$E$100,\"現金\")"
    
    # 当日入金計 = 売上・入金予定シートの当日の全入金
    ws_bank[f"G{row}"] = f"=SUMIFS('売上・入金予定'!$D$4:$D$100,'売上・入金予定'!$A$4:$A$100,A{row})"
    # 当日出金計 = 仕入・支払予定シートの当日の全出金
    ws_bank[f"H{row}"] = f"=SUMIFS('仕入・支払予定'!$D$4:$D$100,'仕入・支払予定'!$A$4:$A$100,A{row})"
    
    for col_l in ["A","B","C","D","E","F","G","H","I"]:
        c = ws_bank[f"{col_l}{row}"]
        c.font = font_body
        c.border = border_cell
        if col_l in ["C","D","E","F","G","H"]:
            c.number_format = "#,##0"
            c.alignment = Alignment(horizontal="right", vertical="center")
        else:
            c.alignment = Alignment(horizontal="center", vertical="center")
            
    if w_idx == 5:
        ws_bank[f"B{row}"].fill = fill_sat
    elif w_idx == 6:
        ws_bank[f"B{row}"].fill = fill_sun

# ==============================================================
# シート3: 売上・入金予定
# ==============================================================
ws_income = wb.create_sheet(title="売上・入金予定")
ws_income.views.sheetView[0].showGridLines = True

ws_income["A1"] = "中川石材店　売上・入金予定明細"
ws_income["A1"].font = font_title

headers_income = [
    ("A3", "入金予定日", 13),
    ("B3", "お客様・取引先名", 24),
    ("C3", "工事・案件名（内容）", 26),
    ("D3", "入金額", 15),
    ("E3", "入金先口座", 15),
    ("F3", "状況 (予定/確定)", 14),
    ("G3", "請求書No / 備考", 20)
]

for pos, text, width in headers_income:
    cell = ws_income[pos]
    cell.value = text
    cell.font = font_header
    cell.fill = fill_income_header
    cell.alignment = Alignment(horizontal="center", vertical="center")
    col_letter = pos[0]
    ws_income.column_dimensions[col_letter].width = width

# 実データをサンプルとして投入（Misoca確定データ）
income_samples = [
    ("2026/11/05", "能美農業協同組合", "宮竹町 麹谷様 墓石解体工事", 165000, "北國銀行", "確定", "Misoca-001"),
    ("2026/11/10", "株式会社 森造形センター", "モニュメント台座据付工事", 330000, "北國銀行", "確定", "Misoca-002"),
    ("2026/11/15", "河上様", "寺井町 墓石クリーニング・文字彫刻", 88000, "ゆうちょ銀行", "確定", "Misoca-003"),
    ("2026/11/20", "南様", "辰口町 納骨堂改修工事", 120000, "北國銀行", "確定", "Misoca-004"),
    ("2026/11/25", "金沢東山 辻様", "墓石新築工事（前受金）", 500000, "金沢信用金庫", "予定", "M-toul契約"),
    ("2026/11/30", "末寺町 新出様", "墓地新築工事", 450000, "北國銀行", "予定", "M-toul見積"),
    ("2026/12/10", "粟生町 太田様", "墓石新築工事", 600000, "ゆうちょ銀行", "予定", "M-toul見積"),
    ("2026/12/20", "元山様", "墓石新築工事", 350000, "北國銀行", "予定", "M-toul契約")
]

for idx, item in enumerate(income_samples):
    r = 4 + idx
    for c_idx, val in enumerate(item):
        col_letter = get_column_letter(c_idx + 1)
        cell = ws_income[f"{col_letter}{r}"]
        cell.value = val
        cell.font = font_body
        cell.border = border_cell
        if c_idx == 3: # 金額
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.fill = fill_light_green
        elif c_idx in [0, 4, 5]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")

# ==============================================================
# シート4: 仕入・支払予定
# ==============================================================
ws_expense = wb.create_sheet(title="仕入・支払予定")
ws_expense.views.sheetView[0].showGridLines = True

ws_expense["A1"] = "中川石材店　仕入・経費・支払予定明細"
ws_expense["A1"].font = font_title

headers_expense = [
    ("A3", "支払予定日", 13),
    ("B3", "支払先・相手先", 24),
    ("C3", "費目・支払内容", 26),
    ("D3", "支払額", 15),
    ("E3", "支払元口座", 15),
    ("F3", "状況 (予定/済)", 14),
    ("G3", "備考 / 引落日", 20)
]

for pos, text, width in headers_expense:
    cell = ws_expense[pos]
    cell.value = text
    cell.font = font_header
    cell.fill = fill_expense_header
    cell.alignment = Alignment(horizontal="center", vertical="center")
    col_letter = pos[0]
    ws_expense.column_dimensions[col_letter].width = width

# 支払サンプル投入（中川石材様の実情に合わせたもの）
expense_samples = [
    ("2026/11/05", "石材仕入先各社", "墓石・外柵・原石仕入", 450000, "北國銀行", "確定", "定期仕入"),
    ("2026/11/10", "外注加工・職人様", "文字彫り・現場据付応援費", 180000, "北國銀行", "確定", "外注工賃"),
    ("2026/11/15", "トラック・リース会社", "車両リース料・重機維持費", 65000, "北國銀行", "確定", "自動引落"),
    ("2026/11/20", "ガソリンスタンド", "車両燃料代（デュトロ等）", 42000, "北國銀行", "確定", "カード決済"),
    ("2026/11/25", "スタッフ給与", "11月度人件費", 380000, "ゆうちょ銀行", "予定", "給与振込"),
    ("2026/11/27", "電気・水道・通信費", "工場・事務所光熱費", 35000, "北國銀行", "予定", "自動引落"),
    ("2026/11/30", "日本政策金融公庫", "設備資金借入返済", 110000, "北國銀行", "予定", "約定返済"),
    ("2026/12/05", "石材仕入先各社", "墓石材追加仕入", 350000, "北國銀行", "予定", "仕入代"),
    ("2026/12/10", "外注工事費", "基礎工事応援費", 150000, "北國銀行", "予定", "外注工賃")
]

for idx, item in enumerate(expense_samples):
    r = 4 + idx
    for c_idx, val in enumerate(item):
        col_letter = get_column_letter(c_idx + 1)
        cell = ws_expense[f"{col_letter}{r}"]
        cell.value = val
        cell.font = font_body
        cell.border = border_cell
        if c_idx == 3: # 金額
            cell.number_format = "#,##0"
            cell.alignment = Alignment(horizontal="right", vertical="center")
            cell.fill = fill_light_red
        elif c_idx in [0, 4, 5]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
        else:
            cell.alignment = Alignment(horizontal="left", vertical="center")

# 保存
out_path = "/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/中川石材_日別資金繰り管理表_テンプレート.xlsx"
wb.save(out_path)
print("Template created successfully:", out_path)
