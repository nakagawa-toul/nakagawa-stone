import re, json

with open('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/index.html') as f:
    html = f.read()

# 全要素のIDとタグ名を抽出
elements = re.findall(r'<([a-zA-Z0-9]+)[^>]*\sid=["\']([^"\']+)["\']', html)
print(f"Extracted {len(elements)} elements with ID.")

# JSC用のDOMモックスクリプトを生成
mock_js = """
var window = this;
var localStorageData = {};
var localStorage = {
  getItem: function(k) { return localStorageData[k] || null; },
  setItem: function(k, v) { localStorageData[k] = v; },
  removeItem: function(k) { delete localStorageData[k]; }
};

var elementsMap = {};
function createElement(tag, id) {
  return {
    id: id,
    tagName: tag.toUpperCase(),
    classList: {
      add: function(){},
      remove: function(){},
      toggle: function(){},
      contains: function(){ return false; }
    },
    style: {},
    dataset: {},
    addEventListener: function(evt, handler){},
    querySelectorAll: function(){ return []; },
    querySelector: function(){ return null; },
    focus: function(){},
    value: '',
    textContent: '',
    innerHTML: '',
    checked: false
  };
}

"""

for tag, elem_id in elements:
    mock_js += f"elementsMap['{elem_id}'] = createElement('{tag}', '{elem_id}');\n"

mock_js += """
var document = {
  getElementById: function(id) {
    return elementsMap[id] || null;
  },
  querySelectorAll: function(sel) {
    return [];
  },
  querySelector: function(sel) {
    return null;
  },
  addEventListener: function(evt, handler) {
    if (evt === 'DOMContentLoaded') {
      handler();
    }
  }
};
window.document = document;
window.addEventListener = function(){};
var Chart = function(){ return { update: function(){}, destroy: function(){} }; };

try {
  load('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/initial_transactions.js');
  load('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/store.js');
  load('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js');
  print('App instantiated successfully with real DOM mock!');
} catch (e) {
  print('RUNTIME ERROR CAUGHT: ' + e + '\\nStack: ' + e.stack);
}
"""

with open('/tmp/test_runner.js', 'w') as f:
    f.write(mock_js)

