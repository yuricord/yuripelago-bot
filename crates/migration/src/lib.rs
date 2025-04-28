pub use sea_orm_migration::prelude::*;

pub struct Migrator;
mod m20250418_210821_init_archi_base;
mod m20250419_170728_init_archi_games;
mod m20250419_172333_init_rando_game;
mod m20250419_174401_init_archi_items;
mod m20250419_175546_init_archi_locations;
mod m20250419_175755_init_archi_hints;
mod m20250419_180743_init_discord;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            Box::new(m20250418_210821_init_archi_base::Migration),
            Box::new(m20250419_170728_init_archi_games::Migration),
            Box::new(m20250419_172333_init_rando_game::Migration),
            Box::new(m20250419_174401_init_archi_items::Migration),
            Box::new(m20250419_175546_init_archi_locations::Migration),
            Box::new(m20250419_175755_init_archi_hints::Migration),
            Box::new(m20250419_180743_init_discord::Migration),
        ]
    }
}
