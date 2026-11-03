run:
	npx tsc
	flask --app src/mptcp_reaserch_dashboard/__init__ run --debug