# SteamDBScraper
1. Edit config.json and customers.json in files directory.
2. Run "docker build --platform linux/amd64 -t steamdb-img ."
3. Run "docker run --rm -v /path/to/host/directory/files:/steamdb_scrape/files steamdb-img"
