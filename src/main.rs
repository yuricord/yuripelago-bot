#![warn(clippy::str_to_string)]

mod commands;
mod utils;

use anyhow::Error;
use poise::serenity_prelude as serenity;
use poise_error::on_error;
use sea_orm::{ConnectOptions, Database, DatabaseConnection};
use std::time::Duration;
use tracing::info;

use migration::{Migrator, MigratorTrait};
use utils::{client_pool::ClientPool, settings::Settings};

// Types used by all command functions
type Context<'a> = poise::Context<'a, Data, Error>;
type ApplicationContext<'a> = poise::ApplicationContext<'a, Data, Error>;

pub struct DatabaseService {
    pub conn: DatabaseConnection,
}

impl DatabaseService {
    pub async fn init(url: String) -> Self {
        let mut connection_options = ConnectOptions::new(url);
        connection_options
            .max_connections(100)
            .min_connections(5)
            .connect_timeout(Duration::from_secs(8))
            .acquire_timeout(Duration::from_secs(8))
            .idle_timeout(Duration::from_secs(8))
            .max_lifetime(Duration::from_secs(8))
            .sqlx_logging(false);

        // test connection
        #[allow(clippy::expect_used)]
        let conn = Database::connect(connection_options)
            .await
            .expect("Can't connect to database");

        Self { conn }
    }
}

pub struct Data {
    db: DatabaseService,
    #[allow(dead_code)]
    config: Settings,
    #[allow(dead_code)]
    ap_clients: ClientPool,
}

// Custom user data passed to all command functions
#[tokio::main]
async fn main() {
    // Start `tracing`
    tracing_subscriber::fmt()
        .with_env_filter(
            "info,\
            archi_bot=debug,\
            sea_orm=debug,\
            archi_client=debug,\
            poise_error=debug,",
        )
        .init();

    // Load Configuration
    let settings = Settings::new().unwrap();
    let token = settings.discord_token.to_owned();

    let db = DatabaseService::init(settings.database_url.to_owned()).await;

    // Run Pending database migrations at startup
    info!("Running migrations!");
    Migrator::up(&db.conn, None).await.unwrap();

    // FrameworkOptions contains all of poise's configuration option in one struct
    // Every option can be omitted to use its default value
    let options = poise::FrameworkOptions {
        commands: vec![commands::game::parent(), commands::slots::parent()],

        // Enforce command checks even for owners (enforced by default)
        // Set to true to bypass checks, which is useful for testing
        skip_checks_for_owners: false,

        on_error,
        // Set all other arguments to default
        ..Default::default()
    };

    let framework = poise::Framework::builder()
        .setup(move |ctx, _ready, framework| {
            Box::pin(async move {
                info!("Logged in as {}", _ready.user.name);
                poise::builtins::register_globally(ctx, &framework.options().commands).await?;
                Ok(Data {
                    db,
                    config: settings,
                    ap_clients: ClientPool::new(),
                })
            })
        })
        .options(options)
        .build();

    let intents = serenity::GatewayIntents::non_privileged();

    let client = serenity::ClientBuilder::new(token, intents)
        .framework(framework)
        .await;

    client.unwrap().start().await.unwrap()
}
