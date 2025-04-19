use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(GameDataPackage::Table)
                    .if_not_exists()
                    .col(string(GameDataPackage::Name).primary_key().not_null())
                    .col(string(GameDataPackage::PackageChecksum).not_null())
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(GameDataPackage::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
pub enum GameDataPackage {
    Table,
    Name,
    PackageChecksum,
}
