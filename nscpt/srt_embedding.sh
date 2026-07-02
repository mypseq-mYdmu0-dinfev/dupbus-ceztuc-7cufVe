ffmpeg -i [input_path_filename] -i [srt_path_filename] -c copy -c:s mov_text [output_path_filename]

# ============================================================
# Pre-requisites:
# 1. Install Homebrew:
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# 2. Install FFmpeg using Homebrew:
# brew install ffmpeg
# 3. Verify Installation:
# ffmpeg
# ============================================================