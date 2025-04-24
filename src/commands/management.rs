use crate::utils::fetchers::fetch_rando_game;
use crate::utils::writers::{write_all_game_packages, write_players, write_room_info, write_slots};
use crate::{ApplicationContext, Error};
use ::entity::{rando_game, rando_game::Entity as RandoGame};
use archi_client::client::ArchipelagoClient;
use poise::{CreateReply, Modal};
use sea_orm::ActiveValue::Set;
use sea_orm::{ActiveModelTrait, ColumnTrait, EntityTrait, QueryFilter};

fn get_room_id(url: &String) -> String {
    let room_pieces: Vec<&str> = url.split("/").collect();
    return String::from(room_pieces[4]);
}

/// Top-level Game command
#[poise::command(
    slash_command,
    guild_only,
    required_permissions = "MANAGE_THREADS",
    subcommands("create_game", "deactivate_game",)
)]
#[allow(unused_variables)]
pub async fn parent(ctx: ApplicationContext<'_>, arg: String) -> Result<(), Error> {
    Ok(())
}

/// Register a game with Archi-Bot
#[poise::command(
    slash_command,
    guild_only,
    required_permissions = "MANAGE_THREADS",
    rename = "create"
)]
pub async fn create_game(
    ctx: ApplicationContext<'_>,
    #[description = "Server-provided port number for your game"] port: i32,
    #[description = "The server's tracker URL for your room, which is the `Multiworld Tracker` link on your room's page."]
    tracker_url: String,
    #[description = "The room URL for your game, where you get the `tracker_url` from."]
    room_url: String,
    #[description = "The pretty name to display for this game in logs and commands."]
    display_name: String,
    #[description = "(optional) if True, will display traps in commands that return items. Defaults to True."]
    spoil_traps: Option<bool>,
    #[description = "(optional) The server that the game is hosted on. Defaults to `archipelago.gg`."]
    server_url: Option<String>,
    #[description = "(optional) The slot the bot uses to connect to the game. Defaults to `ArchiBot`."]
    bot_slot: Option<String>,
) -> Result<(), Error> {
    let db = &ctx.data().db.connection;
    // Check for a registered, active game in this channel.
    // There can only be one active game at a time in any channel.
    match RandoGame::find()
        .filter(rando_game::Column::GameChannel.eq(ctx.channel_id().get()))
        .filter(rando_game::Column::Active.eq(true))
        .one(db)
        .await?
    {
        Some(val) => {
            ctx.send(
                CreateReply::default()
                    .content(
                        format!(
                            "Game {} is already registered for this channel! Please deactivate the game if you wish to start a new game in this channel.",
                            val.display_name
                        )
                    )
                    .ephemeral(true),
            ).await?;
            return Ok(());
        }
        None => (),
    };
    // Check for a registered game with the same tracker URL.
    // If it is, print it along with the channel.
    // This is a separate check because a room may have been registered before in a different channel.
    match RandoGame::find()
        .filter(rando_game::Column::TrackerUrl.eq(&tracker_url))
        .one(&ctx.data().db.connection)
        .await?
    {
        Some(val) => {
            ctx.send(
                CreateReply::default()
                    .content(format!(
                        "A game with the same tracker URL has been registered at <#{}>!",
                        val.game_channel
                    ))
                    .ephemeral(true),
            )
            .await?;
            return Ok(());
        }
        None => (),
    };

    // Defer initial response if it doesn't pass the above conditions.
    ctx.defer_ephemeral().await?;

    // Construct a connection URL
    let client_connection_url = &format!(
        "{}:{}",
        server_url.clone().unwrap_or(String::from("archipelago.gg")),
        &port
    );

    // Start archi client
    let mut archi_client =
        ArchipelagoClient::with_data_package(client_connection_url, None).await?;

    // Get room id from room url
    let room_id = get_room_id(&room_url);

    // write room info to database
    match write_room_info(archi_client.room_info(), db, &room_id).await {
        Err(_e) => {
            ctx.send(
                CreateReply::default()
                    .content("Error: Room already exists in database")
                    .ephemeral(true),
            )
            .await?;
        }
        _ => (),
    };

    // Write all game data packages to database.
    write_all_game_packages(archi_client.data_package().unwrap(), db).await?;

    // Create the rando game and insert it
    rando_game::ActiveModel {
        display_name: Set(String::from(&display_name)),
        server_url: Set(server_url.unwrap_or(String::from("archipelago.gg"))),
        port: Set(port),
        bot_slot: Set(bot_slot
            .to_owned()
            .unwrap_or(String::from("ArchiBot"))
            .to_string()),
        game_channel: Set(ctx.channel_id().get() as i64),
        tracker_url: Set(tracker_url),
        room_url: Set(room_url),
        spoil_traps: Set(spoil_traps.unwrap_or(true)),
        room_id: Set(String::from(&room_id)),
        active: Set(true),
        ..Default::default()
    }
    .save(db)
    .await?;

    let slot = bot_slot.unwrap_or(String::from("ArchiBot"));
    // Fetch slots by connecting to our slot
    match archi_client
        .connect(
            "Archipelago",
            slot.as_str(),
            None,
            Some(0i32),
            vec![String::from("Tracker"), String::from("DeathLink")],
        )
        .await
    {
        Ok(res) => {
            write_slots(res.slot_info, &room_id, db).await?;
            write_players(res.players, &room_id, db).await?;
            ()
        }
        _ => (),
    };

    // Final response
    ctx.send(
        CreateReply::default()
            .content(format!(
                "Registered new game {} for this channel!",
                display_name
            ))
            .ephemeral(true),
    )
    .await?;

    Ok(())
}

#[derive(Debug, Modal)]
#[name = "Deactivate Game Confirmation"]
struct DeactivateModel {
    #[name = "Confirmation"]
    #[placeholder = "Type exactly the string `CONFIRM` here to confirm deactivation of this game."]
    #[min_length = 7]
    #[max_length = 7]
    confirmation: String,
}

#[poise::command(
    slash_command,
    guild_only,
    required_permissions = "MANAGE_THREADS",
    rename = "deactivate"
)]
pub async fn deactivate_game(ctx: ApplicationContext<'_>) -> Result<(), Error> {
    let db = &ctx.data().db.connection;
    #[allow(unused_must_use)]
    match DeactivateModel::execute(ctx).await? {
        Some(v) => match v.confirmation.as_str() {
            "CONFIRM" => match fetch_rando_game(&ctx.channel_id(), db).await {
                Ok(Some(model)) => {
                    let message = ctx
                        .send(
                            CreateReply::default()
                                .content(format!("Deactivating game {}...", &model.display_name)),
                        )
                        .await?;
                    let mut to_update: rando_game::ActiveModel = model.into();
                    to_update.active = Set(false);
                    let to_update = to_update.update(db).await?;
                    message
                        .edit(
                            poise::Context::Application(ctx),
                            CreateReply::default()
                                .content(format!("Deactivated game {}", to_update.display_name)),
                        )
                        .await?;
                    Ok(())
                }
                Ok(None) => {
                    ctx.send(
                        CreateReply::default()
                            .content("Error: No game registered in this channel.")
                            .ephemeral(true),
                    )
                    .await?;
                    Ok(())
                }
                _ => Ok(()),
            },
            _ => {
                ctx.send(
                    CreateReply::default()
                        .content("Error: Confirmation string was not correct. Please try again."),
                )
                .await?;
                Err(String::from("bad"))
            }
        },
        _ => Ok(()),
    };

    Ok(())
}
