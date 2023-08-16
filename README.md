# SteamDBScraper
1. Add config.json and customers.json to config directory.
2. Run "docker build --platform linux/amd64 -t steamdb_selenium-img ."
3. Run "docker run --rm -v /path/to/host/directory/files:/steam_scrape/files steamdb_selenium-img"
