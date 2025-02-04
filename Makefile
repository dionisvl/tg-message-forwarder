up:
	docker compose up
down:
	docker compose down

build:
	make down
	docker compose up --build