use anyhow::{Error, anyhow, bail};
use archi_client::protocol::ClientMessage;
use poise::{CreateReply, Modal};
use poise_error::UserError;
use utils::checks::has_active_room;
use utils::common::ApplicationContext;
use utils::fetchers::fetch_room_id;

#[derive(Debug, Modal)]
#[name = "Debug Packet Sender"]
struct DebugModal {
    #[name = "Packet Body"]
    #[placeholder = "{'cmd': 'INPUT', 'data': []}"]
    #[paragraph]
    packet_body: String,
}

/// DEBUG: Send an arbitrary packet.
#[poise::command(
    slash_command,
    guild_only,
    owners_only,
    rename = "send_packet",
    check = "has_active_room"
)]
pub async fn send_packet(ctx: ApplicationContext<'_>) -> Result<(), Error> {
    let db = &ctx.data().db.conn;
    let pool = &ctx.data().ap_clients;
    let room_id = fetch_room_id(ctx.channel_id(), db).await?;

    match DebugModal::execute(ctx).await? {
        Some(v) => {
            let msg: ClientMessage = serde_json::from_str(&v.packet_body).unwrap();
            ctx.send(
                CreateReply::default().content(format!("Sending Packet: `{}`", &v.packet_body)),
            )
            .await?;
            pool.send(room_id.to_owned(), msg).await?;
            match pool.recv(room_id).await {
                Ok(Some(srv_msg)) => {
                    ctx.send(CreateReply::default().content(format!(
                        "```{}```",
                        serde_json::to_string(&srv_msg).unwrap()
                    )))
                    .await?;
                    Ok(())
                }
                _ => bail!("Did not recieve a packet."),
            }
        }
        _ => bail!(UserError(anyhow!("No packet given! Aborting.."))),
    }
}
