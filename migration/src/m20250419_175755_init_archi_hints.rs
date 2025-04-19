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
                    .table(Hint::Table)
                    .if_not_exists()
                    .col(pk_auto(Hint::Id))
                    .col(integer(Hint::ReceivingPlayer).not_null())
                    .col(integer(Hint::FindingPlayer).not_null())
                    .col(big_integer(Hint::Location).not_null())
                    .col(big_integer(Hint::Item).not_null())
                    .col(boolean(Hint::Found).not_null())
                    .col(string(Hint::Entrance).not_null().default(""))
                    .col(integer(Hint::ItemFlags).not_null())
                    .col(string(Hint::RoomId).not_null())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-hint-room_id")
                            .from(Hint::Table, Hint::RoomId)
                            .to(ArchiRoom::Table, ArchiRoom::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Hint::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Hint {
    Table,
    Id,
    ReceivingPlayer,
    FindingPlayer,
    Location,
    Item,
    Found,
    Entrance,
    ItemFlags,
    RoomId,
}
