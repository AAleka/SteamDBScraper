# SteamDBScraper
1. Create drivers directory and save your web drivers there.
2. Create out directory for games.json files.
3. Create config directory with config.json and customers.json.
4. Run "docker build --platform linux/amd64 -t steamdb_selenium-img ."
5. Run "docker run -it -d -v data:/steam_scrape/data --name steamdb-script steamdb_selenium-img"
6. Run "docker exec -it steamdb-script /bin/bash"
