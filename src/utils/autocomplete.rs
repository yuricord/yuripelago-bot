use super::fetchers::{fetch_games_for_channel, fetch_player_slots, fetch_slots};
use crate::{Context, utils::fetchers::fetch_room_id};

/// Complete slot names from the current game in the channel using a string to search.
pub async fn autocomplete_slot_names<'a>(ctx: Context<'_>, partial: &'a str) -> Vec<String> {
    let db = &ctx.data().db.conn;
    let room_id = fetch_room_id(ctx.channel_id(), db).await;
    return match room_id {
        Ok(id) => fetch_slots(id, db)
            .await
            .into_iter()
            .filter(move |name| name.contains(partial))
            .collect(),
        _ => vec![],
    };
}

/// Complete the player's slots in the current game
pub async fn autocomplete_player_slots<'a>(ctx: Context<'_>, partial: &'a str) -> Vec<String> {
    let db = &ctx.data().db.conn;
    let user_id = i64::try_from(ctx.author().id)?;
    return match fetch_room_id(ctx.channel_id(), db).await {
        Ok(id) => fetch_player_slots(id, db, user_id),
    };
}

/// Complete rando games in the current channel
pub async fn autocomplete_rando_games<'a>(ctx: Context<'_>, partial: &'a str) -> Vec<String> {
    let db = &ctx.data().db.conn;
    let games = fetch_games_for_channel(ctx.channel_id(), db).await;
    return match games {
        Ok(games) => games
            .into_iter()
            .filter(move |name| name.contains(partial))
            .collect(),
        _ => vec![],
    };
}
