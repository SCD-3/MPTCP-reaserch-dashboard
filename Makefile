build:
	npx tsc

run:
	make build
	flask --app src/mptcp_reaserch_dashboard/__init__ run --debug

db:
	sudo systemctl start mongodb