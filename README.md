# SteamDBScraper
1. Add config.json and customers.json to config directory.
2. Run "docker build --platform linux/amd64 -t steamdb_selenium-img ."
3. Run "docker run -it -d -v data:/steam_scrape/data --name steamdb-script steamdb_selenium-img"
4. Run "docker exec -it steamdb-script /bin/bash"
