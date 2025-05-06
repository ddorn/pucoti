# Set uv to either /root/.local/bin/uv or uv depending on which one exists
UV := $(shell command -v uv >/dev/null 2>&1 && echo "uv" || echo "/root/.local/bin/uv")

deploy:
	rsync -avz --delete vue/dist uv.lock pyproject.toml server.py pucoti.service Makefile pine:/srv/pucoti-vue
	rsync -avz pucoti.service pine:/etc/systemd/system/
	ssh pine "systemctl daemon-reload && systemctl restart pucoti"

run:
	$(UV) run uvicorn server:app --port 9123
