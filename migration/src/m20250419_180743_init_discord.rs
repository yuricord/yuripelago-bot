use sea_orm_migration::{prelude::*, schema::*};

use crate::m20250418_210821_init_archi_base::ArchiSlot;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(DiscordUser::Table)
                    .if_not_exists()
                    .col(big_unsigned(DiscordUser::Id).primary_key().not_null())
                    .to_owned(),
            )
            .await?;

        manager
            .create_table(
                Table::create()
                    .table(DiscordSlotLink::Table)
                    .if_not_exists()
                    .col(integer(DiscordSlotLink::SlotId).not_null())
                    .col(big_unsigned(DiscordSlotLink::DiscordId).not_null())
                    .primary_key(
                        Index::create()
                            .col(DiscordSlotLink::SlotId)
                            .col(DiscordSlotLink::DiscordId),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-discord_slot_link-slot_id")
                            .from(DiscordSlotLink::Table, DiscordSlotLink::SlotId)
                            .to(ArchiSlot::Table, ArchiSlot::GlobalId)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-discord_slot_link-discord_id")
                            .from(DiscordSlotLink::Table, DiscordSlotLink::DiscordId)
                            .to(DiscordUser::Table, DiscordUser::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Tables
        manager
            .drop_table(Table::drop().table(DiscordSlotLink::Table).to_owned())
            .await?;

        manager
            .drop_table(Table::drop().table(DiscordUser::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(DeriveIden)]
enum DiscordUser {
    Table,
    Id,
}

#[derive(DeriveIden)]
enum DiscordSlotLink {
    Table,
    SlotId,
    DiscordId,
}
