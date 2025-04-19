//! `SeaORM` Entity, @generated by sea-orm-codegen 1.1.8

use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, DeriveEntityModel, Eq, Serialize, Deserialize)]
#[sea_orm(table_name = "location")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = false)]
    pub id: i64,
    #[sea_orm(primary_key, auto_increment = false)]
    pub game: String,
    pub name: String,
    pub group: String,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::game_data_package::Entity",
        from = "Column::Game",
        to = "super::game_data_package::Column::Name",
        on_update = "Cascade",
        on_delete = "Cascade"
    )]
    GameDataPackage,
    #[sea_orm(
        belongs_to = "super::location_group::Entity",
        from = "Column::Group",
        to = "super::location_group::Column::Name",
        on_update = "Cascade",
        on_delete = "Cascade"
    )]
    LocationGroup,
}

impl Related<super::game_data_package::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::GameDataPackage.def()
    }
}

impl Related<super::location_group::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::LocationGroup.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
