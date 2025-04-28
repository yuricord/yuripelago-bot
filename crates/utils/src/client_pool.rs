use anyhow::Result;
use archi_client::{
    client::{ArchipelagoClient, ArchipelagoError},
    protocol::{ClientMessage, Retrieved, ServerMessage},
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

        return client.get(keys).await;
    }

    /// Send a message to the client with id `id`
    pub async fn send(&self, id: String, msg: ClientMessage) -> Result<(), ArchipelagoError> {
        let mut client = self.clients.get_mut(&id).unwrap();

        return client.send(msg).await;
    }

    /// Recieve a message from the specified client.
    pub async fn recv(&self, id: String) -> Result<Option<ServerMessage>, ArchipelagoError> {
        let mut client = self.clients.get_mut(&id).unwrap();

        return client.recv().await;
    }
}
