use anyhow::Result;
use archi_client::protocol::{
    DataPackageObject, GameData, NetworkPlayer, NetworkSlot, RoomInfo, SlotType,
};
use entity::{
    archi_player, archi_room, archi_slot, game_data_package,
    prelude::{ArchiPlayer, ArchiRoom, ArchiSlot, GameDataPackage},
};
use sea_orm::{ActiveModelTrait, ActiveValue::NotSet, DatabaseConnection, EntityTrait, Set};
use std::{collections::HashMap, iter::IntoIterator};

pub async fn write_room_info(
    info: &RoomInfo,
    db: &DatabaseConnection,
    room_id: &String,
) -> Result<()> {
    let to_insert = archi_room::ActiveModel {
        id: Set(room_id.to_owned()),
        password: Set(info.password_required),
        hint_cost: Set(info.hint_cost),
        location_check_points: Set(info.location_check_points),
    };
    ArchiRoom::insert(to_insert).exec(db).await?;

    Ok(())
}

/// Write a single game data package to the database.
pub async fn write_single_game_package(
    package: &GameData,
    name: &String,
    db: &DatabaseConnection,
) -> Result<()> {
    // Check if there's already a game with the same name and checksum
    // If the name is the same but checksum is different, update the checksum and return
    // If there is no game with the same name, this is a new game, so it should be inserted

    #[allow(unused_must_use)]
    match GameDataPackage::find_by_id(name.to_owned()).one(db).await {
        Ok(Some(model)) => match model.checksum == package.checksum {
            true => Err(String::from("already inserted")),
            false => {
                let mut model: game_data_package::ActiveModel = model.into();
                model.checksum = Set(package.checksum.to_owned());
                model.update(db).await?;
                Ok(())
            }
        },
        Err(_e) => Err(String::from("database error")),
        _ => Ok(()),
    };

    // Create new game data package and insert it
    let to_insert = game_data_package::ActiveModel {
        name: Set(name.to_owned()),
        checksum: Set(package.checksum.to_owned()),
    };

    GameDataPackage::insert(to_insert).exec(db).await?;

    Ok(())
}

/// Write a list of game packages to the database.
pub async fn write_all_game_packages(
    data: &DataPackageObject,
    db: &DatabaseConnection,
) -> Result<()> {
    for (k, v) in data.to_owned().games.into_iter() {
        write_single_game_package(&v, &k, db).await?;
    }
    Ok(())
}

/// Write all slots for a specific room to the database.
pub async fn write_slots(
    slots: HashMap<i32, NetworkSlot>,
    room_id: &String,
    db: &DatabaseConnection,
) -> Result<()> {
    for (id, data) in slots.iter() {
        let slot_type = match data.r#type {
            SlotType::Player => 1i32,
            SlotType::Group => 2i32,
            _ => 0i32,
        };
        let slot = archi_slot::ActiveModel {
            global_id: NotSet,
            id: Set(id.to_owned()),
            name: Set(String::from(&data.name)),
            game: Set(String::from(&data.game)),
            r#type: Set(slot_type),
            room_id: Set(room_id.to_owned()),
            ..Default::default()
        };
        ArchiSlot::insert(slot).exec(db).await?;
    }
    Ok(())
}

/// Write all players for a specific room to the database.
pub async fn write_players(
    players: Vec<NetworkPlayer>,
    room_id: &String,
    db: &DatabaseConnection,
) -> Result<()> {
    for player in players.iter() {
        let player = archi_player::ActiveModel {
            team: Set(player.team),
            slot: Set(player.slot),
            name: Set(String::from(&player.name)),
            room_id: Set(room_id.to_owned()),
            ..Default::default()
        };
        ArchiPlayer::insert(player).exec(db).await?;
    }
    Ok(())
}
