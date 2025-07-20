up:
	docker compose up -d
down:
	docker compose down

build:
	make down
	docker compose up --build

sh:
	docker compose exec web sh