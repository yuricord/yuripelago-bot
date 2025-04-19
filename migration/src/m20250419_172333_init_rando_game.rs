use sea_orm_migration::{prelude::*, schema::*};

use crate::m20250418_210821_init_archi_base::ArchiRoom;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(RandoGame::Table)
                    .if_not_exists()
                    .col(
                        integer(RandoGame::Id)
                            .primary_key()
                            .auto_increment()
                            .not_null(),
                    )
                    .col(string(RandoGame::DisplayName).null())
                    .col(string(RandoGame::RoomId).not_null())
                    .col(
                        string(RandoGame::ServerUrl)
                            .not_null()
                            .default("archipelago.gg"),
                    )
                    .col(small_unsigned(RandoGame::Port).not_null())
                    .col(string(RandoGame::BotSlot).not_null().default("ArchiBot"))
                    .col(big_unsigned(RandoGame::GameChannel).not_null())
                    .col(string(RandoGame::TrackerUrl).not_null())
                    .col(string(RandoGame::RoomUrl).not_null())
                    .col(boolean(RandoGame::SpoilTraps).not_null())
                    .col(boolean(RandoGame::Active).not_null())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-rando_game-room_id")
                            .from(RandoGame::Table, RandoGame::RoomId)
                            .to(ArchiRoom::Table, ArchiRoom::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(RandoGame::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum RandoGame {
    Table,
    Id,
    DisplayName,
    RoomId,
    ServerUrl,
    Port,
    BotSlot,
    GameChannel,
    TrackerUrl,
    RoomUrl,
    SpoilTraps,
    Active,
}
