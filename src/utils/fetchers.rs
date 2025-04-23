use anyhow::Result;
use entity::archi_room::Entity as ArchiRoom;
use entity::archi_slot::{self, Entity as ArchiSlot};
use entity::rando_game::{self, Entity as RandoGame};
use poise::serenity_prelude::ChannelId;
use sea_orm::{
    ColumnTrait, DatabaseConnection, DerivePartialModel, EntityTrait, FromQueryResult, ModelTrait,
    QueryFilter, QuerySelect,
};

pub async fn fetch_rando_game(
    channel: &ChannelId,
    db: &DatabaseConnection,
) -> Result<Option<rando_game::Model>, ()> {
    #[allow(unused_must_use)]
    match RandoGame::find()
        .filter(rando_game::Column::GameChannel.eq(channel.get()))
        .filter(rando_game::Column::Active.eq(true))
        .one(db)
        .await
    {
        Ok(Some(model)) => Ok(Some(model)),
        Ok(None) => Ok(None),
        _ => Err(()),
    };

    Err(())
}

pub async fn fetch_room_id(channel: ChannelId, db: &DatabaseConnection) -> Result<String, ()> {
    return match fetch_rando_game(&channel, db).await {
        Ok(Some(game)) => match game.find_related(ArchiRoom).one(db).await {
            Ok(Some(room)) => Ok(room.id),
            _ => Err(()),
        },
        _ => Err(()),
    };
}

#[derive(DerivePartialModel, FromQueryResult)]
#[sea_orm(entity = "ArchiSlot")]
struct NameOnlySlot {
    pub name: String,
}

#[allow(dead_code)]
pub async fn fetch_slots(room_id: String, db: &DatabaseConnection) -> Result<Vec<String>> {
    let slots = ArchiSlot::find()
        .select_only()
        .column(archi_slot::Column::Name)
        .filter(archi_slot::Column::RoomId.eq(room_id))
        .into_partial_model::<NameOnlySlot>()
        .all(db)
        .await?;
    Ok(slots.iter().map(|s| String::from(&s.name)).collect())
}

#[allow(dead_code)]
pub async fn fetch_slots_by_name(
    room_id: String,
    query: &str,
    db: &DatabaseConnection,
) -> Result<Vec<String>> {
    match ArchiSlot::find()
        .select_only()
        .column(archi_slot::Column::Name)
        .filter(archi_slot::Column::RoomId.eq(room_id))
        .filter(archi_slot::Column::Name.contains(query))
        .into_partial_model::<NameOnlySlot>()
        .all(db)
        .await
    {
        Ok(slots) => Ok(slots.iter().map(|s| String::from(&s.name)).collect()),
        _ => Ok(vec![]),
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
