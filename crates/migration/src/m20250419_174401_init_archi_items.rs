use sea_orm_migration::{prelude::*, schema::*};

use crate::m20250419_170728_init_archi_games::GameDataPackage;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(ItemGroup::Table)
                    .if_not_exists()
                    .col(string(ItemGroup::Name).not_null())
                    .col(string(ItemGroup::Game).not_null())
                    .primary_key(Index::create().col(ItemGroup::Name).col(ItemGroup::Game))
                    .to_owned(),
            )
            .await?;

        manager
            .create_table(
                Table::create()
                    .table(Item::Table)
                    .if_not_exists()
                    .col(big_integer(Item::Id).not_null())
                    .col(string(Item::Game).not_null())
                    .col(string(Item::Name).not_null())
                    .col(string(Item::Group).null())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-item-game")
                            .from(Item::Table, Item::Game)
                            .to(GameDataPackage::Table, GameDataPackage::Name)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-item-group")
                            .from(Item::Table, Item::Group)
                            .to(ItemGroup::Table, ItemGroup::Name)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .primary_key(Index::create().col(Item::Id).col(Item::Game))
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Item::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(ItemGroup::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(DeriveIden)]
enum Item {
    Table,
    Id,
    Game,
    Name,
    Group,
}

#[derive(DeriveIden)]
enum ItemGroup {
    Table,
    Name,
    Game,
}
