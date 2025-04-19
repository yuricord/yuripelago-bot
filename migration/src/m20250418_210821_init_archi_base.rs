use super::m20250419_170728_init_archi_games::GameDataPackage;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Archi Player
        manager
            .create_table(
                Table::create()
                    .table(ArchiPlayer::Table)
                    .if_not_exists()
                    .col(integer(ArchiPlayer::Team).not_null())
                    .col(integer(ArchiPlayer::Slot).not_null())
                    .col(string(ArchiPlayer::Name).not_null())
                    .col(string(ArchiPlayer::RoomId).not_null())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-archi_player-room_id")
                            .from(ArchiPlayer::Table, ArchiPlayer::RoomId)
                            .to(ArchiRoom::Table, ArchiRoom::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .primary_key(
                        Index::create()
                            .col(ArchiPlayer::Team)
                            .col(ArchiPlayer::Slot)
                            .col(ArchiPlayer::RoomId),
                    )
                    .to_owned(),
            )
            .await?;

        // Archi Room
        manager
            .create_table(
                Table::create()
                    .table(ArchiRoom::Table)
                    .if_not_exists()
                    .col(string(ArchiRoom::Id).not_null().primary_key())
                    .col(boolean(ArchiRoom::Password).not_null())
                    .col(integer(ArchiRoom::HintCost).not_null())
                    .col(integer(ArchiRoom::LocationCheckPoints).not_null())
                    .to_owned(),
            )
            .await?;

        // Archi Slots
        manager
            .create_table(
                Table::create()
                    .table(ArchiSlot::Table)
                    .if_not_exists()
                    .col(
                        integer(ArchiSlot::GlobalId)
                            .not_null()
                            .auto_increment()
                            .primary_key(),
                    )
                    .col(integer(ArchiSlot::Id).not_null())
                    .col(string(ArchiSlot::Name).not_null())
                    .col(string(ArchiSlot::Game).not_null())
                    .col(integer(ArchiSlot::Type).not_null())
                    .col(json_null(ArchiSlot::GroupMembers))
                    .col(string(ArchiSlot::RoomId).not_null())
                    .col(integer(ArchiSlot::Deaths).default(0i32))
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-archi_slot-room_id")
                            .from(ArchiSlot::Table, ArchiSlot::RoomId)
                            .to(ArchiRoom::Table, ArchiRoom::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-archi_slot-game")
                            .from(ArchiSlot::Table, ArchiSlot::Game)
                            .to(GameDataPackage::Table, GameDataPackage::Name),
                    )
                    .to_owned(),
            )
            .await?;
        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(ArchiPlayer::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(ArchiRoom::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(ArchiSlot::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(DeriveIden)]
enum ArchiPlayer {
    Table,
    Team,
    Slot,
    Name,
    RoomId,
}

#[derive(DeriveIden)]
pub enum ArchiRoom {
    Table,
    Id,
    Password,
    HintCost,
    LocationCheckPoints,
}

#[derive(DeriveIden)]
pub enum ArchiSlot {
    Table,
    GlobalId,
    Id,
    Name,
    Game,
    Type,
    GroupMembers,
    RoomId,
    Deaths,
}
