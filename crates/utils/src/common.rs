use crate::client_pool::ClientPool;
use crate::settings::Settings;
use anyhow::Error;
use poise;
use sea_orm::{ConnectOptions, Database, DatabaseConnection};
use std::time::Duration;

// Types used by all command functions
pub type Context<'a> = poise::Context<'a, Data, Error>;
pub type ApplicationContext<'a> = poise::ApplicationContext<'a, Data, Error>;

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
    pub db: DatabaseService,
    #[allow(dead_code)]
    pub config: Settings,
    #[allow(dead_code)]
    pub ap_clients: ClientPool,
}
