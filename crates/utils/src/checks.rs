use crate::common::Context;
use crate::fetchers::fetch_room_id;
use anyhow::{Error, bail};

pub async fn has_active_room(ctx: Context<'_>) -> Result<bool, Error> {
    let db = &ctx.data().db.conn;
    return match fetch_room_id(ctx.channel_id(), db).await {
        Ok(_v) => Ok(true),
        _ => {
            bail!("No active room found in this channel!")
        }
    };
}
