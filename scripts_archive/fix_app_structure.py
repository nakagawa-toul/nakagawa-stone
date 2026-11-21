with open('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the initialization block
init_block = """// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
  window.app = new StoneApp();
});"""

# Split before the initialization block
parts = text.split(init_block)
if len(parts) == 2:
    class_part = parts[0].strip()
    after_part = parts[1].strip()
    
    # Check if class_part ends with '}'
    if class_part.endswith('}'):
        # Remove the trailing '}' of the class
        class_part = class_part[:-1].rstrip()
    
    # Put after_part (the methods) INSIDE the class, then close the class, then add init_block
    fixed_code = class_part + "\n\n" + after_part + "\n}\n\n" + init_block + "\n"
    
    with open('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js', 'w', encoding='utf-8') as f:
        f.write(fixed_code)
    print("Fixed app.js structure successfully.")
else:
    print("Could not find init_block split.")
