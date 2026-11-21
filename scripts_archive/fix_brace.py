with open('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace extra closing brace before initialization
target = """    }
  }

}
}

// アプリケーション初期化"""

replacement = """    }
  }

}

// アプリケーション初期化"""

if target in text:
    text = text.replace(target, replacement)
    with open('/Users/nakagawaminorutsuru/.gemini/antigravity/scratch/nakagawa-stone-app/js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed extra brace successfully.")
else:
    print("Target not found directly, checking...")
