use crate::{Context, utils::fetchers::fetch_room_id};

use super::fetchers::fetch_slots_by_name;

#[allow(dead_code)]
/// Complete slot names from the current game in the channel using a string to search.
/// Rustc complains it's unused, but we use it in commands::slots so ignore that.
pub async fn autocomplete_slot_names<'a>(ctx: Context<'_>, partial: &'a str) -> Vec<String> {
    let db = &ctx.data().db.connection;
    let room_id = fetch_room_id(ctx.channel_id(), db).await;
    match room_id {
        Ok(id) => {
            return fetch_slots_by_name(id, partial, db).await.unwrap();
        }
        _ => return vec![],
    }
}
