import openpyxl, datetime, json

wb = openpyxl.load_workbook('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/中川石材_資金繰り表_経費外配置統一版.xlsx', data_only=False)

ws_main = wb['資金繰表（メイン）']
ws_income = wb['入金']
ws_expense = wb['出金']
ws_repay = wb['返済']

start_date = datetime.date(2026, 11, 1)
total_days = 151
initial_balance = 2624533
weekday_kanji = ["月", "火", "水", "木", "金", "土", "日"]

running_balance = initial_balance
daily_schedule = []

for i in range(total_days):
    row = 5 + i
    cur_date = start_date + datetime.timedelta(days=i)
    w_str = weekday_kanji[cur_date.weekday()]
    date_str = cur_date.strftime("%Y-%m-%d")

    # 入金シートから各口座の入金を取得
    # F:北國(18277), G:北国(199439), H:北國, I:JA, J:はくさん, K:現金, L:クレジット
    bank_income = {
        'hokkoku18277': ws_income.cell(row, 6).value or 0,
        'hokkoku199439': ws_income.cell(row, 7).value or 0,
        'hokkoku': ws_income.cell(row, 8).value or 0,
        'ja': ws_income.cell(row, 9).value or 0,
        'hakusan': ws_income.cell(row, 10).value or 0,
        'cash': ws_income.cell(row, 11).value or 0,
        'other': ws_income.cell(row, 12).value or 0
    }
    income_remarks = str(ws_income.cell(row, 4).value or '').strip()
    sales_income = sum(v for v in bank_income.values() if isinstance(v, (int, float)))

    # 出金シートから各費目を取得
    # F:商品仕入, G:外注費, H:洋外注費, I:車両費・燃料費, J:光熱費, K:通信費, L:地代家賃, M:法人カード, N:消耗品費, O:事業主消費, P:源泉・所得税, Q:消費税・法人税, R:その他経費
    cogs = ws_expense.cell(row, 6).value or 0
    subcontract = ws_expense.cell(row, 7).value or 0
    yo_subcontract = ws_expense.cell(row, 8).value or 0
    vehicle = ws_expense.cell(row, 9).value or 0
    utilities = ws_expense.cell(row, 10).value or 0
    communication = ws_expense.cell(row, 11).value or 0
    rent = ws_expense.cell(row, 12).value or 0
    card = ws_expense.cell(row, 13).value or 0
    supplies = ws_expense.cell(row, 14).value or 0
    owner_expense = ws_expense.cell(row, 15).value or 0
    withholding_tax = ws_expense.cell(row, 16).value or 0
    consumption_tax = ws_expense.cell(row, 17).value or 0
    other_expense = ws_expense.cell(row, 18).value or 0
    expense_remarks = str(ws_expense.cell(row, 4).value or '').strip()

    def to_num(val):
        return int(val) if isinstance(val, (int, float)) else 0

    cogs_num = to_num(cogs)
    subcontract_num = to_num(subcontract)
    yo_subcontract_num = to_num(yo_subcontract)
    owner_expense_num = to_num(owner_expense)
    withholding_tax_num = to_num(withholding_tax)
    consumption_tax_num = to_num(consumption_tax)
    other_expense_num = to_num(other_expense)
    gen_expense_num = to_num(vehicle) + to_num(utilities) + to_num(communication) + to_num(rent) + to_num(card) + to_num(supplies)

    # 返済シートから返済額を取得
    # F:公庫, G:はくさん①, H:はくさん②, I:その他, J:利息
    kouko = to_num(ws_repay.cell(row, 6).value)
    hakusan1 = to_num(ws_repay.cell(row, 7).value)
    hakusan2 = to_num(ws_repay.cell(row, 8).value)
    other_loan = to_num(ws_repay.cell(row, 9).value)
    loan_repay = kouko + hakusan1 + hakusan2 + other_loan
    repay_remarks = str(ws_repay.cell(row, 4).value or '').strip()

    income_total = sales_income # 借入入金なしの場合
    expense_total = yo_subcontract_num + subcontract_num + cogs_num + gen_expense_num + loan_repay + owner_expense_num + withholding_tax_num + consumption_tax_num + other_expense_num

    running_balance = running_balance + income_total - expense_total

    # メイン備考の合成
    remarks_list = []
    main_rem = str(ws_main.cell(row, 4).value or '').strip()
    if main_rem:
        remarks_list.append(main_rem)
    elif income_remarks or expense_remarks or repay_remarks:
        if income_remarks: remarks_list.append(income_remarks)
        if expense_remarks: remarks_list.append(expense_remarks)
        if repay_remarks: remarks_list.append(repay_remarks)
    combined_remarks = ' / '.join(remarks_list)

    daily_schedule.append({
        'date': date_str,
        'weekday': w_str,
        'remarks': combined_remarks,
        'balance': running_balance,
        'incomeTotal': income_total,
        'salesIncome': sales_income,
        'loanIncome': 0,
        'expenseTotal': expense_total,
        'yoSubcontract': yo_subcontract_num,
        'subcontract': subcontract_num,
        'cogs': cogs_num,
        'genExpense': gen_expense_num,
        'loanRepay': loan_repay,
        'loanRepayDetails': {
            'kouko': kouko,
            'hakusan1': hakusan1,
            'hakusan2': hakusan2
        },
        'ownerExpense': owner_expense_num,
        'withholdingTax': withholding_tax_num,
        'consumptionTax': consumption_tax_num,
        'otherExpense': other_expense_num,
        'bankIncome': {k: to_num(v) for k, v in bank_income.items()}
    })

print(f'Generated {len(daily_schedule)} days.')
# 出力
with open('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/nakagawa_cashflow_daily.json', 'w', encoding='utf-8') as f:
    json.dump(daily_schedule, f, ensure_ascii=False, indent=2)

print('Saved to js/nakagawa_cashflow_daily.json successfully!')
