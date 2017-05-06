configure:
	@echo "--> Setting up virtualenv"
	scripts/venv_installed.sh
	@echo ""

install:
	@echo "--> Installing Dependencies"
	python3 -m pip install -r requirements.txt
	@echo ""

clean:
	@echo "--> Removing virtualenv"
	rm -rf ${PWD}/venv/
	@echo ""

.PHONY: install clean
