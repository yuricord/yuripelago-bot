use crate::ApplicationContext;
use crate::Error;
use crate::utils::autocomplete::autocomplete_slot_names;
use crate::utils::fetchers::fetch_room_id;

/// Register a new slot for the game in the current channel.
///
/// Slot name is autocompleted.
#[poise::command(slash_command, guild_only)]
pub async fn register(
    ctx: ApplicationContext<'_>,
    #[description = "Slot name to register"]
    #[autocomplete = "autocomplete_slot_names"]
    slot: String,
) -> Result<(), Error> {
    let db = &ctx.data().db.connection;
    let room_id = fetch_room_id(ctx.channel_id(), db);

    Ok(())
}
