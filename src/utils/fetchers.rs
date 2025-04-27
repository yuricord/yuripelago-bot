use anyhow::Result;
use entity::archi_room::Entity as ArchiRoom;
use entity::archi_slot::{self, Entity as ArchiSlot};
use entity::discord_slot_link;
use entity::prelude::DiscordSlotLink;
use entity::rando_game::{self, Entity as RandoGame};
use poise::serenity_prelude::ChannelId;
use sea_orm::{
    ColumnTrait, DatabaseConnection, DerivePartialModel, EntityTrait, FromQueryResult, ModelTrait,
    QueryFilter, QuerySelect,
};
use serde::Serialize;

/// A rando game that only has the game's name
#[derive(DerivePartialModel, FromQueryResult)]
#[sea_orm(entity = "RandoGame")]
struct NameOnlyRandoGame {
    pub display_name: String,
}

/// A slot that only has the name column
#[derive(DerivePartialModel, FromQueryResult)]
#[sea_orm(entity = "ArchiSlot")]
struct NameOnlySlot {
    pub name: String,
}

/// A DiscordSlotLink slot that also contains the slot name
#[derive(Debug, FromQueryResult, Serialize)]
pub struct SlotLinkWithName {
    pub discord_id: i64,
    pub slot_id: i32,
    pub slot_name: String,
}

/// Fetch the last rando game from the specified channel
pub async fn fetch_rando_game(
    channel: ChannelId,
    db: &DatabaseConnection,
    name: Option<String>,
    active_check: Option<bool>,
) -> Result<Option<rando_game::Model>, ()> {
    #[allow(unused_must_use)]
    let mut select = RandoGame::find().filter(rando_game::Column::GameChannel.eq(channel.get()));
    select = match name {
        Some(n) => select.filter(rando_game::Column::DisplayName.eq(n)),
        None => select,
    };
    select = match active_check {
        Some(val) => select.filter(rando_game::Column::Active.eq(val)),
        None => select,
    };
    return match select.one(db).await {
        Ok(Some(model)) => Ok(Some(model)),
        Ok(None) => Ok(None),
        _ => Err(()),
    };
}

/// Fetch the active room id for a channel
pub async fn fetch_room_id(channel: ChannelId, db: &DatabaseConnection) -> Result<String, ()> {
    return match fetch_rando_game(channel, db, None, Some(true)).await {
        Ok(Some(game)) => match game.find_related(ArchiRoom).one(db).await {
            Ok(Some(room)) => Ok(room.id),
            _ => Err(()),
        },
        _ => Err(()),
    };
}

/// Fetch all slots for the current game
pub async fn fetch_slots(room_id: String, db: &DatabaseConnection) -> Vec<String> {
    let slots = ArchiSlot::find()
        .select_only()
        .column(archi_slot::Column::Name)
        .filter(archi_slot::Column::RoomId.eq(room_id))
        .into_partial_model::<NameOnlySlot>()
        .all(db)
        .await
        .unwrap_or(vec![]);
    slots.iter().map(|s| String::from(&s.name)).collect()
}

/// Fetch all of a player's slots for a game
pub async fn fetch_player_slots(
    room_id: String,
    db: &DatabaseConnection,
    user_id: i64,
    query: Option<&str>,
) -> Vec<String> {
    let mut select = DiscordSlotLink::find()
        .left_join(ArchiSlot)
        .filter(discord_slot_link::Column::DiscordId.eq(user_id))
        .filter(archi_slot::Column::RoomId.eq(room_id))
        .column_as(archi_slot::Column::Name, "slot_name");

    select = match query {
        Some(v) => select.filter(archi_slot::Column::Name.contains(v)),
        _ => select,
    };

    match select.into_model::<SlotLinkWithName>().all(db).await {
        Ok(slots) => slots.iter().map(|s| String::from(&s.slot_name)).collect(),
        _ => vec![],
    }
}

pub async fn fetch_single_slot_by_name(
    room_id: String,
    name: &str,
    db: &DatabaseConnection,
) -> Result<archi_slot::Model, ()> {
    match ArchiSlot::find()
        .filter(archi_slot::Column::RoomId.eq(room_id))
        .filter(archi_slot::Column::Name.eq(name))
        .one(db)
        .await
    {
        Ok(Some(slot)) => Ok(slot),
        _ => Err(()),
    }
}

pub async fn fetch_games_for_channel(
    channel: ChannelId,
    db: &DatabaseConnection,
) -> Result<Vec<String>> {
    let games = RandoGame::find()
        .select_only()
        .column(rando_game::Column::DisplayName)
        .filter(rando_game::Column::GameChannel.eq(channel.get()))
        .into_partial_model::<NameOnlyRandoGame>()
        .all(db)
        .await?;

    Ok(games
        .iter()
        .map(|g| String::from(&g.display_name))
        .collect())
}
