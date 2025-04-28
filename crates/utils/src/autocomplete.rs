use super::fetchers::{fetch_game_names_for_channel, fetch_player_slot_names, fetch_slots};
use crate::{common::Context, fetchers::fetch_room_id};

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
    let user_id = match i64::try_from(ctx.author().id) {
        Ok(val) => val,
        _ => return vec![],
    };
    return match fetch_room_id(ctx.channel_id(), db).await {
        Ok(id) => fetch_player_slot_names(id, db, user_id, Some(partial)).await,
        _ => vec![],
    };
}

/// Complete rando games in the current channel
pub async fn autocomplete_rando_games<'a>(ctx: Context<'_>, partial: &'a str) -> Vec<String> {
    let db = &ctx.data().db.conn;
    let games = fetch_game_names_for_channel(ctx.channel_id(), db).await;
    return match games {
        Ok(games) => games
            .into_iter()
            .filter(move |name| name.contains(partial))
            .collect(),
        _ => vec![],
    };
}
