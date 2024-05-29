.SECONDARY:
# prevents deletion of intermediate targets in chained rules

.DELETE_ON_ERROR:
# delete targets if a rule fails

default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -_]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

flask: # Runs a flask app on developement server using flask export
	export FLASK_APP=flask_app/flask_app; export FLASK_ENV=development; flask run --port 6262 --debug --no-reload

setup: requirements.txt # Sets up the environment
	pip install -r requirements.txt
