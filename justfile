gen-entities:
    sea-orm-cli generate entity -o entity/src --with-serde=both -l

migrate:
    sea-orm-cli migrate

docs:
    cargo doc --open --no-deps \
        -p archi-bot -p anyhow -p archi_client -p dotenvy -p entity \
        -p migration -p poise -p sea-orm -p thiserror@2 -p tokio \
        -p tracing -p tracing-subscriber -p poise_error -p dashmap@6
