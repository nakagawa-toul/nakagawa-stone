#!/bin/bash
# 中川石材 業務管理システム - かんたん起動スクリプト

cd "$(dirname "$0")"

PORT=8080
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")

echo "=========================================================="
echo "  中川石材 業務管理Webアプリ（試作版）"
echo "=========================================================="
echo ""
echo "パソコンのブラウザで直接開く場合:"
echo "  http://localhost:${PORT}"
echo ""
echo "同じWi-Fiに接続したスマートフォンから開く場合:"
echo "  http://${IP}:${PORT}"
echo ""
echo "※ 終了するときはキーボードで [Control] + [C] を押してください。"
echo "=========================================================="

# Macのブラウザを自動で開く
(sleep 1 && open "http://localhost:${PORT}") &

# Python3 または Ruby でWebサーバー起動
if command -v python3 >/dev/null 2>&1; then
  python3 -m http.server ${PORT}
elif command -v ruby >/dev/null 2>&1; then
  ruby -run -e httpd . -p ${PORT}
else
  open index.html
fi
