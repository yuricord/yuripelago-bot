- [ ] Migrate player/game data storage from json+csv -> sqlite database

  - [x] Connection Info Storage
  - [x] Room Info Storage
  - [x] Player/Slot Info from Archi Server
  - [x] Discord -> Archi Slot Registrations
    - Migrated initial registrations, have to move all the lookups though
  - [ ] Item Queue
  - [ ] Death Queue

- [ ] Runtime configuration(So I don't have to start/stop the bot when games are finished or the port changes)
- [ ] Add more useful commands(suggestions wanted!)
  - Removed clearreg, added `unregister` to remove slot registration
- [ ] Update README
- [x] All uses of string concatenation -> f-strings
  - I think this is done
