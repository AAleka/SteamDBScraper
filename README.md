# SteamDBScraper
1. Add config.json and customers.json to config directory.
2. Run "docker build --platform linux/amd64 -t steamdb_selenium-img ."
3. Run "docker run --rm -v /path/to/host/directory/out:/steam_scrape/out steamdb_selenium-img"
