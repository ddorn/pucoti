.PHONY: all run mkdist zip linux check_git_status poetry_patch poetry_minor poetry_major commit_version_bump publish patch minor major clean distclean

END=\033[0m
GREEN=\033[34m

# all: zip

run:
	@uv run pucoti

# mkdist:
# 	@mkdir -p dist

# zip: mkdist
# 	@echo -e "$(GREEN)Updating zip...$(END)"
# 	@git ls-files | zip --filesync -r --names-stdin dist/pucoti.zip

# linux: mkdist
# 	@echo -e "$(GREEN)Building for linux...$(END)"
# 	poetry run pyinstaller --noconsole --add-data assets/:assets --onefile pucoti.py

# For this to work on linux, I needed to download the python 32-bit installer and run it with wine
# Then I had to install the deps (wine pip install .) and pyinstaller (wine pip install pyinstaller)
# And make windows worked!

# windows: mkdist
# 	@echo -e "$(GREEN)Building for windows...$(END)"
# 	WINEDEBUG=-all wine pyinstaller.exe --noconsole --add-data assets\;assets --onefile pucoti.py

version_patch:
	hatch version patch

version_minor:
	hatch version minor

version_major:
	hatch version major

commit_version_bump:
	@echo "Bumped version to $$(hatch version)"
	git add src/pucoti/version.py
	git commit -m "chore: bump version to $$(hatch version)"
	git tag -a "v$$(hatch version)" -m "v$$(hatch version)"

check_git_status:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Git working directory is not clean. Please commit or stash your changes."; \
		read -p "Continue anyway? [y/N] " CONTINUE; \
		if [ "$$CONTINUE" != "y" ]; then \
			exit 1; \
		fi; \
	fi


wheel:
	hatch build -t wheel

patch: check_git_status version_patch commit_version_bump wheel
minor: check_git_status version_minor commit_version_bump wheel
major: check_git_status version_major commit_version_bump wheel

publish:
	hatch publish

clean:
	rm -r build
	rm -r **/__pycache__ __pycache__

distclean: clean
	rm -r dist


deploy:
	# Push files by ssh to hyperion in ./pucoti
	git ls-files | rsync -avz --files-from=- . hyperion:pucoti
	# Restart the service
	ssh hyperion "systemctl --user restart pucoti"

server:
	poetry run uvicorn pucoti.server:app --reload --port 9123
