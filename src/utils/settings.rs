use config::{Config, ConfigError, Environment, File};
use serde::Deserialize;

#[derive(Debug, Deserialize)]
#[allow(unused)]
pub(crate) struct Settings {
    pub discord_token: String,
    pub database_url: String,
}

impl Settings {
    pub(crate) fn new() -> Result<Self, ConfigError> {
        let s = Config::builder()
            // Start off by merging in the "default" configuration file
            .add_source(File::with_name("config").required(false))
            // Add in settings from the environment (with a prefix of ARCHIBOT)
            // Eg.. `ARCHIBOT_DEBUG=1 archi-bot` would set the `debug` key
            .add_source(Environment::with_prefix("archibot"))
            .set_default("database_url", "sqlite://archi-bot.db?mode=rwc")?
            .build()?;

        s.try_deserialize()
    }
}
