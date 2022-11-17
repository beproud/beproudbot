# setup procedure from /README.md

# env.sample をコピペして .env というファイルを作成
cp -n env.sample .env || true

# install python libraries
pip install -r src/requirements.txt

# prepare docker. ログ出力がターミナルではないため、壊れないようにplainを指定
BUILDKIT_PROGRESS=plain docker compose pull
# bot用containerがubuntu-16ベースでエラーになるためコメントアウト
# BUILDKIT_PROGRESS=plain docker compose build
