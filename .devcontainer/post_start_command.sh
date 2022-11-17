sudo cp .devcontainer/first-run-notice.txt /usr/local/etc/vscode-dev-containers/first-run-notice.txt

export $(cat .env |grep -v '#')
