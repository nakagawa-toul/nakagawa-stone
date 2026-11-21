app_path = '/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js'

with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

old_card = """          <div class="bg-slate-800/90 hover:bg-slate-800 p-2.5 rounded-xl border border-slate-700 transition cursor-pointer" onclick="app.switchView('funds'); app.switchFundsSubtab('cashflow');">
            <div class="flex items-center justify-between text-[10px]">
              <span class="font-bold truncate text-slate-300 flex items-center">
                <span class="w-2 h-2 rounded-full mr-1.5 flex-shrink-0" style="background-color: ${acc.color};"></span>
                ${acc.shortName}
              </span>
              <span class="text-[9px] px-1 py-0.2 rounded bg-slate-700 text-slate-400 font-mono">${acc.type === 'cash' ? '現金' : '口座'}</span>
            </div>
            <div class="text-sm sm:text-base font-extrabold mt-1 tracking-tight ${isShortage ? 'text-rose-400 font-black' : 'text-white'}">
              ¥${acc.currentBalance.toLocaleString()}
            </div>
            <div class="text-[9px] text-slate-400 mt-0.5 truncate">基準日: ${acc.baseDate || '10/31'}</div>
          </div>"""

new_card = """          <div class="bg-white hover:bg-slate-50 text-slate-800 p-3 rounded-xl border border-slate-300 shadow-sm transition cursor-pointer group" onclick="app.switchView('funds'); app.switchFundsSubtab('cashflow');">
            <div class="flex items-center justify-between text-xs">
              <span class="font-extrabold truncate text-slate-800 flex items-center group-hover:text-blue-600">
                <span class="w-2.5 h-2.5 rounded-full mr-1.5 flex-shrink-0" style="background-color: ${acc.color};"></span>
                ${acc.shortName}
              </span>
              <span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-bold">${acc.type === 'cash' ? '現金' : '口座'}</span>
            </div>
            <div class="text-base sm:text-lg font-black mt-1.5 tracking-tight ${isShortage ? 'text-rose-600 font-black' : 'text-slate-900'}">
              ¥${acc.currentBalance.toLocaleString()}
            </div>
            <div class="text-[10px] text-slate-400 mt-0.5 truncate">基準日: ${acc.baseDate || '10/31'}</div>
          </div>"""

if old_card in code:
    code = code.replace(old_card, new_card)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Improved account cards contrast successfully.")
else:
    print("old_card not found directly.")
