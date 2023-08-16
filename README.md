# SteamDBScraper
1. Edit config.json and customers.json in files directory.
2. Move files directory anywhere you want.
3. Run "docker build --platform linux/amd64 -t steamdb_selenium-img ."
4. Run "docker run --rm -v /path/to/host/directory/files:/steamdb_scrape/files steamdb_selenium-img"
