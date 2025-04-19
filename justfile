gen-entities:
    sea-orm-cli generate entity -o entity/src --with-serde=both

migrate:
    sea-orm-cli migrate
