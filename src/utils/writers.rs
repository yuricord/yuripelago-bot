use anyhow::{Error, Result, bail};
use archi_client::protocol::{
    DataPackageObject, GameData, NetworkPlayer, NetworkSlot, RoomInfo, SlotType,
};
use entity::{
    archi_player, archi_room, archi_slot, game_data_package, item, location,
    prelude::GameDataPackage,
};
use sea_orm::{
    ActiveModelTrait, ActiveValue::NotSet, DatabaseConnection, EntityTrait, Set, TransactionTrait,
};
use std::{collections::HashMap, iter::IntoIterator};

pub async fn write_room_info(
    info: &RoomInfo,
    db: &DatabaseConnection,
    room_id: &String,
) -> Result<()> {
    archi_room::ActiveModel {
        id: Set(room_id.to_owned()),
        password: Set(info.password_required),
        hint_cost: Set(info.hint_cost),
        location_check_points: Set(info.location_check_points),
    }
    .save(db)
    .await?;

    Ok(())
}

/// Write a single game data package to the database.
pub async fn write_single_game_package(
    package: &GameData,
    name: &String,
    db: &DatabaseConnection,
) -> Result<(), Error> {
    // Check if there's already a game with the same name and checksum
    // If the name is the same but checksum is different, update the checksum and return
    // If there is no game with the same name, this is a new game, so it should be inserted

    #[allow(unused_must_use)]
    match GameDataPackage::find_by_id(name.to_owned()).one(db).await {
        Ok(Some(existing)) => match existing.checksum == package.checksum {
            true => bail!("Already inserted."),
            false => {
                let old_model: game_data_package::ActiveModel = existing.into();
                old_model.delete(db).await?;

                game_data_package::ActiveModel {
                    name: Set(name.to_owned()),
                    checksum: Set(package.checksum.to_owned()),
                }
                .save(db)
                .await;
                write_items(package.item_name_to_id.to_owned(), name, db);
                write_locations(package.location_name_to_id.to_owned(), name, db);
            }
        },
        // No existing package
        Ok(None) => {
            game_data_package::ActiveModel {
                name: Set(name.to_owned()),
                checksum: Set(package.checksum.to_owned()),
            }
            .save(db)
            .await?;
        }

        // Database error
        Err(_e) => bail!("Database Error"),
    };
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
    let txn = db.begin().await?;
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
        slot.insert(&txn).await?;
    }
    txn.commit().await?;
    Ok(())
}

/// Write all players for a specific room to the database.
pub async fn write_players(
    players: Vec<NetworkPlayer>,
    room_id: &String,
    db: &DatabaseConnection,
) -> Result<()> {
    let txn = db.begin().await?;
    for player in players.iter() {
        let player = archi_player::ActiveModel {
            team: Set(player.team),
            slot: Set(player.slot),
            name: Set(String::from(&player.name)),
            room_id: Set(room_id.to_owned()),
            ..Default::default()
        };
        player.insert(&txn).await?;
    }
    txn.commit().await?;
    Ok(())
}

// Write all items from a GameData hashmap to the database
pub async fn write_items(
    items: HashMap<String, i32>,
    game: &String,
    db: &DatabaseConnection,
) -> Result<(), Error> {
    let txn = db.begin().await?;
    for (name, id) in items.iter() {
        item::ActiveModel {
            game: Set(game.to_owned()),
            id: Set(i64::from(id.to_owned())),
            name: Set(name.to_owned()),
            ..Default::default()
        }
        .save(&txn)
        .await?;
    }
    txn.commit().await?;
    Ok(())
}

// Write all items from a GameData hashmap to the database
pub async fn write_locations(
    locations: HashMap<String, i32>,
    game: &String,
    db: &DatabaseConnection,
) -> Result<(), Error> {
    let txn = db.begin().await?;
    for (name, id) in locations.iter() {
        location::ActiveModel {
            game: Set(game.to_owned()),
            id: Set(i64::from(id.to_owned())),
            name: Set(name.to_owned()),
            ..Default::default()
        }
        .save(&txn)
        .await?;
    }
    txn.commit().await?;
    Ok(())
}
