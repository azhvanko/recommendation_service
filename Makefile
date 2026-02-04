# custom variables
SHELL = /bin/bash
COMPOSE_CMD = docker compose -f ./docker-compose.yml

# shortcuts
up:
	$(COMPOSE_CMD) up --build -d

down:
	$(COMPOSE_CMD) down --remove-orphans

clear:
	$(COMPOSE_CMD) down --remove-orphans -v

insert_user_events:
	$(COMPOSE_CMD) exec -it api bash -c "python manage.py insert_user_events"

.PHONY: up down clear insert_user_events
