use anyhow::{Error, anyhow, bail};
use catppuccin::PALETTE as CTP;
use entity::{discord_slot_link, discord_slot_link::Entity as DiscordSlotLink};
use itertools::Itertools;
use poise::CreateReply;
use poise::serenity_prelude::{Colour as SerenityColor, CreateEmbed};
use poise_error::UserError;
use sea_orm::{ActiveModelTrait, EntityTrait, Set};
use utils::autocomplete::{autocomplete_player_slots, autocomplete_slot_names};
use utils::checks::has_active_room;
use utils::common::ApplicationContext;
use utils::fetchers::{
    fetch_discord_user, fetch_player_slot_names, fetch_rando_game, fetch_room_id,
    fetch_single_slot_by_name,
};

/// Top-level Game command
#[poise::command(
    slash_command,
    guild_only,
    subcommands("register_slot", "unregister_slot", "list_slots"),
    rename = "slot"
)]
#[allow(unused_variables)]
pub async fn parent(ctx: ApplicationContext<'_>, arg: String) -> Result<(), Error> {
    Ok(())
}

/// Register a new slot for the game in the current channel.
#[poise::command(
    slash_command,
    guild_only,
    rename = "register",
    check = "has_active_room"
)]
pub async fn register_slot(
    ctx: ApplicationContext<'_>,
    #[description = "Slot name to register"]
    #[autocomplete = "autocomplete_slot_names"]
    slot: String,
) -> Result<(), Error> {
    let db = &ctx.data().db.conn;
    let room_id = fetch_room_id(ctx.channel_id(), db).await?;

    // Get the discord user database entry
    let user = fetch_discord_user(ctx.author().id, db).await?;

    // Get the slot's database entry
    let slot = match fetch_single_slot_by_name(room_id.to_owned(), &slot, db).await {
        Ok(val) => val,
        _ => bail!(UserError(anyhow!(
            "No slot with name {} found in this channel's game! Please try again.",
            &slot
        ))),
    };

    match DiscordSlotLink::find_by_id((slot.global_id, user.id))
        .one(db)
        .await
    {
        Ok(Some(_v)) => {
            bail!(UserError(anyhow!(
                "You're already registered for slot {} in this game!",
                &slot.name
            )))
        }
        Ok(None) => {
            let to_insert = discord_slot_link::ActiveModel {
                discord_id: Set(user.id),
                slot_id: Set(slot.global_id),
            };
            to_insert.insert(db).await?;
            ctx.send(
                CreateReply::default().content(format!("Registered you for slot {}!", slot.name)),
            )
            .await?;
        }
        _ => {
            bail!("Database Error! Please try again.")
        }
    }

    Ok(())
}

#[poise::command(
    slash_command,
    guild_only,
    rename = "unregister",
    check = "has_active_room"
)]
pub async fn unregister_slot(
    ctx: ApplicationContext<'_>,
    #[description = "Slot name to unregister"]
    #[autocomplete = "autocomplete_player_slots"]
    slot: String,
) -> Result<(), Error> {
    // Set up our variables
    let db = &ctx.data().db.conn;
    let room_id = fetch_room_id(ctx.channel_id(), db).await?;
    let user = fetch_discord_user(ctx.author().id, db).await?;

    // Get the slot or bail
    let slot = match fetch_single_slot_by_name(room_id.to_owned(), &slot, db).await {
        Ok(val) => val,
        _ => bail!(UserError(anyhow!(
            "No slot with name {} found in this channel's game! Please try again.",
            &slot
        ))),
    };

    match DiscordSlotLink::find_by_id((slot.global_id, user.id))
        .one(db)
        .await
    {
        Ok(None) => {
            bail!(UserError(anyhow!(
                "You're not registered for slot {} in this game!",
                &slot.name
            )))
        }
        Ok(Some(link)) => {
            let to_delete: discord_slot_link::ActiveModel = link.into();
            to_delete.delete(db).await?;
            ctx.send(
                CreateReply::default()
                    .content(format!("Unregistered you from slot {}!", slot.name)),
            )
            .await?;
        }
        _ => {
            bail!("Database Error! Please try again.")
        }
    }

    Ok(())
}

/// List all your slots in this channel's game.
#[poise::command(slash_command, guild_only, rename = "list", check = "has_active_room")]
pub async fn list_slots(ctx: ApplicationContext<'_>) -> Result<(), Error> {
    let db = &ctx.data().db.conn;
    let room_id = fetch_room_id(ctx.channel_id(), db).await?;
    let user_id = i64::try_from(ctx.author().id)?;
    let rando_game = fetch_rando_game(ctx.channel_id(), db, None, Some(true))
        .await?
        .unwrap();

    let description = fetch_player_slot_names(room_id, db, user_id, None)
        .await
        .into_iter()
        .collect_vec()
        .join("\n");

    let purple = CTP.mocha.colors.mauve.rgb;
    let embed = CreateEmbed::new()
        .title(format!(
            "{}'s slots for {}",
            ctx.author_member().await.unwrap().display_name(),
            rando_game.display_name
        ))
        .description(description)
        .color(SerenityColor::from_rgb(purple.r, purple.g, purple.b));

    ctx.send(CreateReply::default().embed(embed)).await?;

    Ok(())
}
