# Webhook2RSS
Small webserver that listens to webhook invokations and logs them to RSS feed. Useful since many applications provide webhook, discord, slack etc. support for various notifications but no RSS feed.

## Usage
Run from command-line using python3
```
python src/main.py
```
OR

Run using docker-compose
```
docker-compose -f docker-compose.yml.example up
```

This creates an SQLite database file in `/data` directory and runs a server on port 8000.
Any path can be POST'ed to by Webhooks and same path can be read using GET method.

### Example use-case
Running [watchtower](https://github.com/containrrr/watchtower) and specifing `WATCHTOWER_NOTIFICATION_URL` to POST update info to this application and then using RSS feed reader to find out about updates that watchtower made.