use crate::utils::autocomplete::{autocomplete_player_slots, autocomplete_slot_names};
use crate::utils::checks::has_active_room;
use crate::utils::fetchers::fetch_room_id;
use crate::{ApplicationContext, utils::fetchers::fetch_single_slot_by_name};
use anyhow::{Error, anyhow, bail};
use entity::{
    discord_slot_link, discord_slot_link::Entity as DiscordSlotLink, discord_user,
    discord_user::Entity as DiscordUser,
};
use poise::CreateReply;
use poise_error::UserError;
use sea_orm::{ActiveModelTrait, EntityTrait, Set};

/// Top-level Game command
#[poise::command(
    slash_command,
    guild_only,
    subcommands("register_slot"),
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
    let room_id = match fetch_room_id(ctx.channel_id(), db).await {
        Ok(val) => val,
        // This is included to satisfy the compiler, but it should never be called
        // because of the `has_active_room` check.
        _ => {
            bail!("No active room found in this channel!")
        }
    };

    // Get the discord user database entry
    let user = match DiscordUser::find_by_id(i64::try_from(ctx.author().id)?)
        .one(db)
        .await
    {
        // Already in the database, skip this
        Ok(Some(u)) => u,
        _ => {
            let new_user = discord_user::ActiveModel {
                id: Set(i64::try_from(ctx.author().id)?),
            };
            new_user.insert(db).await?
        }
    };

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
    Ok(())
}
