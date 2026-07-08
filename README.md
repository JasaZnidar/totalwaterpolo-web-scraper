# Total Waterpolo Web Scraper

Python scraper that collects water polo **match and player statistics** from [total-waterpolo.com](https://total-waterpolo.com/), the leading digital water polo platform. Built as the data-collection component of my B.Sc. thesis *"Predicting the outcome of a water polo match using machine learning"* (University of Ljubljana, Faculty of Computer and Information Science, 2026).

The collected dataset is used by the companion repository [waterpolo-match-prediction](https://github.com/JasaZnidar/waterpolo-match-prediction) to train and benchmark machine-learning models.

## What it does

- Scrapes **player pages** (`/tw_player/{id}`): date of birth, height, weight, position, dominant hand, and the list of matches the player appeared in
- Scrapes **match pages** (`/tw_match/{id}`): lineups, team names, final result, and the full per-quarter event log (goals, shots, exclusions, penalties, sprints, saves, ...)
- Discovers match IDs automatically from the players' match histories
- Stores everything in a single structured **JSON** file:

```
{
  "last checked": ...,
  "matches": {
    "{match id}": {
      "competition id": ...,
      "date": ...,
      "lineup":  { "home": [...], "away": [...] },
      "name":    { "home": ...,   "away": ... },
      "plays":   [ ...event list... ],
      "result":  { "home": ...,   "away": ... }
    }
  },
  "players": { "{player id}": { ...player data... } }
}
```

Each event in `plays` contains: event name, details, position, player number, assisting player number, target, team, and timestamp.

## Tech stack

- **Python 3**
- **Selenium** — total-waterpolo.com loads most of its data via JavaScript, so a real browser driver is required
- **BeautifulSoup** — HTML parsing of the loaded pages

## Usage

```bash
pip install -r requirements.txt

# TODO: adjust to the actual entry point / arguments of the repo
python scraper.py
```

## Notes

- Please scrape responsibly: keep request rates low and respect the site's terms of use.
- Match data is entered by clubs during games; optional fields (e.g. sprints, saves) are not always recorded, so downstream users should expect missing values.

## License

GPL-3.0 — see [LICENSE](LICENSE).

## Author

Jaša Žnidar — B.Sc. thesis, University of Ljubljana, Faculty of Computer and Information Science (mentor: doc. dr. Blaž Meden)
