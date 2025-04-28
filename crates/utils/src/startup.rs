use crate::client_pool::ClientPool;
use anyhow::{Error, Result};
use archi_client::client::ArchipelagoClient;
use entity::rando_game::{self, Entity as RandoGame};
use sea_orm::{
    ColumnTrait, DatabaseConnection, DerivePartialModel, EntityTrait, FromQueryResult, QueryFilter,
    QuerySelect,
};
use tracing::{info, warn};

/// A rando game containing all the info we need to start a client.
#[derive(DerivePartialModel, FromQueryResult)]
#[sea_orm(entity = "RandoGame")]
struct EssentialGameInfo {
    pub server_url: String,
    pub port: i32,
    pub room_id: String,
    pub bot_slot: String,
}

pub async fn start_ap_clients(pool: &ClientPool, db: &DatabaseConnection) -> Result<(), Error> {
    let clients = RandoGame::find()
        .select_only()
        .columns([
            rando_game::Column::Port,
            rando_game::Column::ServerUrl,
            rando_game::Column::RoomId,
            rando_game::Column::BotSlot,
        ])
        .filter(rando_game::Column::Active.eq(true))
        .into_partial_model::<EssentialGameInfo>()
        .all(db)
        .await?;

    for c in clients.into_iter() {
        let url = format!("{}:{}", c.server_url, c.port);

        match ArchipelagoClient::new(&url).await {
            Ok(mut cli) => {
                cli.connect(
                    "Archipelago",
                    &c.bot_slot,
                    None,
                    Some(0i32),
                    vec![String::from("Tracker"), String::from("DeathLink")],
                )
                .await?;
                match pool.insert(c.room_id.to_owned(), cli) {
                    _ => (),
                };
                info!(
                    "Started Archipelago client with id {}",
                    c.room_id.to_owned()
                );
                ()
            }
            Err(e) => warn!(
                "Could not start Archipelago client with id {}. Reason is {}",
                c.room_id.to_owned(),
                e
            ),
        }
    }
    Ok(())
}
