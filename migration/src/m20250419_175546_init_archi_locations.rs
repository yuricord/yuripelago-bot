use super::m20250419_170728_init_archi_games::GameDataPackage;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(LocationGroup::Table)
                    .if_not_exists()
                    .col(string(LocationGroup::Name).not_null())
                    .col(string(LocationGroup::Game).not_null())
                    .primary_key(
                        Index::create()
                            .col(LocationGroup::Name)
                            .col(LocationGroup::Game),
                    )
                    .to_owned(),
            )
            .await?;

        manager
            .create_table(
                Table::create()
                    .table(Location::Table)
                    .if_not_exists()
                    .col(big_integer(Location::Id).not_null())
                    .col(string(Location::Game).not_null())
                    .col(string(Location::Name).not_null())
                    .col(string(Location::Group).null())
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-location-game")
                            .from(Location::Table, Location::Game)
                            .to(GameDataPackage::Table, GameDataPackage::Name)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-location-group")
                            .from(Location::Table, Location::Group)
                            .to(LocationGroup::Table, LocationGroup::Name)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .primary_key(Index::create().col(Location::Id).col(Location::Game))
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Location::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(LocationGroup::Table).to_owned())
            .await?;

        Ok(())
    }
}

#[derive(DeriveIden)]
enum Location {
    Table,
    Id,
    Game,
    Name,
    Group,
}

#[derive(DeriveIden)]
enum LocationGroup {
    Table,
    Name,
    Game,
}
