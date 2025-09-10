setup:
	python3 -m venv .venv
	
deps: setup
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/python3 otravez/
