gen-entities:
    sea-orm-cli generate entity -o entity/src --with-serde=both -l

migrate:
    sea-orm-cli migrate
