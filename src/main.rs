#![warn(clippy::str_to_string)]

use poise::serenity_prelude as serenity;
use poise_error::on_error;
use tracing::info;

use migration::{Migrator, MigratorTrait};
use utils::common::{Data, DatabaseService};
use utils::startup::start_ap_clients;
use utils::{client_pool::ClientPool, settings::Settings};

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
        commands: vec![
            commands::game::parent(),
            commands::slots::parent(),
            commands::debug::send_packet(),
        ],

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
                let client_pool = ClientPool::new();
                start_ap_clients(&client_pool, &db.conn).await?;
                Ok(Data {
                    db,
                    config: settings,
                    ap_clients: client_pool,
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
