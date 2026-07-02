echo "[input_text]" | wc -w   # word count for text string
pbpaste | wc -w   # word count from macOS clipboard
wc -w [path_filename]   # word count for a file
token-count --text "your text"   # token count for text string
token-count --file [path_filename]   # token count for a file

# ============================================================
# Prerequisites:
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"   # install Homebrew (if not already)
# brew install python   # install Python (if not already)
# pip install token-count   # install package if not already
# ============================================================