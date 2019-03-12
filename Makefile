.PHONY: help build deploy mirations migrate\
       test down destroy clean\

DC := docker-compose

MYSQL_EXPOSE_PORT := 33061

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  build           to build docker images."
	@echo "  deploy          to deploy bot"
	@echo "  clean           to remove all docker containers, images"
	@echo "  destroy         to remove all docker containers, images, and all volumes"
	@echo "  down            to down all docker containers, images"
	@echo "  test            to excute all tests."
	@echo "  migrations      to generate alembic migration files."
	@echo "  migrate         to apply alembic migration."
	@echo "  help            to show this help messages"

clean:
	docker system prune
	${DC} down --remove-orphans --rmi all

destroy:
	docker system prune
	${DC} down --volume --remove-orphans --rmi all

down:
	${DC} down

build:
	${DC} build

deploy: build
	${DC} up -d
	sh scripts/start_logging.sh
	${DC} exec bot sh scripts/wait_for_mysql.sh honcho start migrate
	${DC} restart bot

test:
	${DC} exec bot tox -e py36

migrations:
	${DC} exec bot honcho start makemigrations

migrate:
	${DC} exec bot honcho start migrate
