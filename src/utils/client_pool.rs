use anyhow::Result;
use archi_client::{
    client::{ArchipelagoClient, ArchipelagoError},
    protocol::Retrieved,
};
use dashmap::DashMap;

/// Pool of Archipelago clients that are currently active.
pub struct ClientPool {
    clients: DashMap<String, ArchipelagoClient>,
}

impl ClientPool {
    pub fn new() -> ClientPool {
        ClientPool {
            clients: DashMap::new(),
        }
    }

    /// Add a client to the client pool
    pub fn insert(&self, id: String, client: ArchipelagoClient) -> Result<()> {
        self.clients.insert(id, client);
        Ok(())
    }

    /// Remove a client from the client pool
    pub fn remove(&self, id: String) -> Result<()> {
        self.clients.remove(&id);
        Ok(())
    }

    /// Wrapper around ArchipelagoClient::get
    pub async fn get(&self, id: String, keys: Vec<String>) -> Result<Retrieved, ArchipelagoError> {
        let mut client = self.clients.get_mut(&id).unwrap();

        let res = client.get(keys).await;

        return res;
    }
}
