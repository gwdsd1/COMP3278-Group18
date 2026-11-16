"""Offline CS2 Match Explorer. Run with Python 3.10 or later."""

import argparse
from contextlib import closing
from datetime import date
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import sqlite3
from urllib.parse import parse_qs, urlsplit


APP = Path(__file__).resolve().parent
DATABASE = APP.parent / "database" / "app.db"
SQL_BLOCKS = re.split(
    r"(?m)^-- (Q[1-9]|event_detail|match_detail):[^\n]*\n",
    (APP / "queries.sql").read_text(encoding="utf-8"),
)
QUERIES = dict(zip(SQL_BLOCKS[1::2], SQL_BLOCKS[2::2]))

FEATURES = [
    ("Find events", "Browse events by date range and minimum prize pool.", ("from_date", "to_date", "min_prize")),
    ("Team lineup", "See the latest lineup recorded in this dataset.", ("team_id",)),
    ("Event schedule", "Find series, start times, stages, and results for an event.", ("event_id", "from_date", "to_date")),
    ("Map results", "See the scores and winners for each map in a series.", ("match_id",)),
    ("Head to head", "Compare completed series and win rates for two teams.", ("team_a", "team_b", "from_date", "to_date")),
    ("Team map performance", "Compare map win rates for one team.", ("team_id", "from_date", "to_date", "min_maps")),
    ("Player leaderboard", "Compare K/D, assists, weighted ADR, and estimated total damage.", ("event_id", "min_maps")),
    ("Teams without map records", "Find teams with no recorded games on a map during the selected dates.", ("map_id", "from_date", "to_date")),
    ("Map scoreboard", "Choose a series, then open any played map to see both teams' player stats.", ("match_id",)),
]

FIELDS = {
    "from_date": ("From date", "date"),
    "to_date": ("To date", "date"),
    "min_prize": ("Minimum prize pool (USD)", "number"),
    "min_maps": ("Minimum maps", "number"),
    "team_id": ("Team", "team"),
    "team_a": ("Team A", "team"),
    "team_b": ("Team B", "team"),
    "event_id": ("Event", "event"),
    "match_id": ("Series", "match"),
    "map_id": ("Map", "map"),
}

OPTIONS = {
    "team": "SELECT team_id, name FROM teams ORDER BY name",
    "event": "SELECT event_id, name FROM events ORDER BY end_date DESC, event_id DESC",
    "map": "SELECT map_id, name FROM maps ORDER BY name",
    "match": """
        SELECT m.match_id, m.match_date || ' | ' || a.name || ' vs ' || b.name || ' | ' || e.name
        FROM matches m
        JOIN teams a ON a.team_id = m.team1_id JOIN teams b ON b.team_id = m.team2_id
        JOIN stages s ON s.stage_id = m.stage_id JOIN events e ON e.event_id = s.event_id
        ORDER BY COALESCE(datetime(m.scheduled_at), datetime(m.match_date)) DESC, m.match_id DESC
    """,
}

COLUMN_NAMES = {
    "scheduled_at": "Scheduled start",
    "prize_pool": "Prize pool (USD)",
    "map_win_pct": "Map win %",
    "team_a_win_pct": "Team A win %",
    "team_b_win_pct": "Team B win %",
    "kd": "K/D",
    "maps_with_reported_adr": "Maps with ADR",
    "sampled_adr": "Weighted ADR",
    "sampled_assists": "Assists",
    "estimated_total_damage": "Estimated total damage",
    "match_id": "Match",
    "adr": "ADR",
    "kast_pct": "KAST %",
    "rating_3": "Rating 3.0",
}

NOTES = {
    2: "Lineups reflect the most recent match recorded for this team.",
    3: "Start times include the Central European UTC offset. Dates are inclusive.",
    7: "Estimated total damage sums ADR × rounds played across maps with published ADR.",
    8: "Includes teams with no matches during the selected dates.",
}


def connect():
    db = sqlite3.connect(f"{DATABASE.as_uri()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db


def load_form(db, keys):
    options = {
        kind: db.execute(OPTIONS[kind]).fetchall()
        for kind in {FIELDS[key][1] for key in keys} & OPTIONS.keys()
    }
    first_date, last_date = db.execute("SELECT MIN(start_date), MAX(end_date) FROM events").fetchone()
    team_a, team_b = db.execute("""
        SELECT team1_id, team2_id FROM matches
        ORDER BY COALESCE(datetime(scheduled_at), datetime(match_date)) DESC, match_id DESC LIMIT 1
    """).fetchone()
    defaults = {
        "from_date": first_date, "to_date": last_date, "min_prize": 0, "min_maps": 1,
        "team_id": team_a, "team_a": team_a, "team_b": team_b,
    }
    for key in keys:
        if key not in defaults:
            defaults[key] = options[FIELDS[key][1]][0][0]
    return options, {key: str(defaults[key]) for key in keys}


def parse_filters(values, options):
    params = {}
    for key, value in values.items():
        label, kind = FIELDS[key]
        if kind == "date":
            try:
                params[key] = date.fromisoformat(value).isoformat()
            except ValueError:
                raise ValueError(f"{label} must be a valid date.") from None
        elif kind == "number":
            minimum = 1 if key == "min_maps" else 0
            if not re.fullmatch(r"[0-9]{1,18}", value) or int(value) < minimum:
                raise ValueError(f"{label} must be a whole number of at least {minimum}.")
            params[key] = int(value)
        else:
            if not any(value == str(option[0]) for option in options[kind]):
                raise ValueError(f"Choose a valid value for {label}.")
            params[key] = int(value)
    if "from_date" in params and params["from_date"] > params["to_date"]:
        raise ValueError("From date must be on or before To date.")
    if "team_a" in params and params["team_a"] == params["team_b"]:
        raise ValueError("Choose two different teams.")
    return params


def form_html(number, values, options):
    fields = []
    for key, value in values.items():
        label, kind = FIELDS[key]
        if kind in options:
            choices = []
            for option_id, name in options[kind]:
                selected = " selected" if str(option_id) == value else ""
                choices.append(f'<option value="{option_id}"{selected}>{escape(name)}</option>')
            control = f'<select id="{key}" name="{key}" required>{"".join(choices)}</select>'
        else:
            limit = f' min="{1 if key == "min_maps" else 0}" step="1"' if kind == "number" else ""
            control = f'<input id="{key}" name="{key}" type="{kind}" value="{escape(value)}"{limit} required>'
        fields.append(f'<div class="field"><label for="{key}">{label}</label>{control}</div>')
    action_label = "Open series" if number == 9 else "Run query"
    return (
        f'<form class="filters" method="get" action="/q{number}">'
        f'<input type="hidden" name="run" value="1">{"".join(fields)}'
        f'<button type="submit">{action_label}</button></form>'
    )


def table_html(columns, rows, *, links=None, label="Query results"):
    if not rows:
        return '<p class="feedback" role="status">No results for these filters.</p>'
    links = links or {}
    match_list = "match_id" in links
    if match_list:
        leading = ("match_id", "team1", "team2")
        columns = [*leading, *(name for name in columns if name not in leading)]
    table_class = ' class="match-list"' if match_list else ""
    headings = "".join(
        f'<th scope="col">{COLUMN_NAMES.get(name, name.replace("_", " ").capitalize())}</th>'
        for name in columns
    )
    body = []
    for row in rows:
        cells = []
        for name in columns:
            value = row[name]
            content = links[name](row) if name in links else ("—" if value is None else escape(str(value)))
            cells.append(f"<td>{content}</td>")
        body.append(f'<tr>{"".join(cells)}</tr>')
    return (
        f'<p class="row-count" role="status">{len(rows):,} {"result" if len(rows) == 1 else "results"}</p>'
        f'<div class="results" role="region" aria-label="{escape(label)}" tabindex="0">'
        f'<table{table_class}><thead><tr>{headings}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'
    )


def result_html(cursor, *, links=None, hidden=(), label="Query results"):
    columns = [name for name, *_ in cursor.description if name not in hidden]
    return table_html(columns, cursor.fetchall(), links=links, label=label)


def event_link(row):
    return f'<a href="/events/{row["event_id"]}">{escape(row["name"])}</a>'


def match_link(row):
    matchup = escape(f'{row["team1"]} vs {row["team2"]}, {row["match_date"]}')
    return f'<a class="match-action" href="/matches/{row["match_id"]}" aria-label="View match: {matchup}">View match</a>'


def map_link(row, match_id, selected_map=None):
    current = ' aria-current="true"' if row["map_id"] == selected_map else ""
    return f'<a href="/matches/{match_id}/maps/{row["map_id"]}#scoreboard"{current}>{escape(row["map"])}</a>'


def page(title, content, number=None):
    links = []
    for i, (name, _, _) in enumerate(FEATURES, 1):
        current = ' aria-current="page"' if i == number else ""
        links.append(f'<a href="/q{i}"{current}><span>Q{i}</span> {name}</a>')
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | CS2 Match Explorer</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <header><a href="/">CS2 <strong>Match Explorer</strong></a><span>COMP3278</span></header>
  <div class="layout">
    <nav aria-label="Queries">{"".join(links)}</nav>
    <main>{content}</main>
  </div>
</body>
</html>"""


def homepage(db):
    counts = db.execute("""
        SELECT (SELECT COUNT(*) FROM events), (SELECT COUNT(*) FROM matches),
               (SELECT COUNT(*) FROM match_maps), (SELECT COUNT(*) FROM player_map_stats)
    """).fetchone()
    labels = ("Events", "Series", "Maps", "Player-map records")
    stats = "".join(f"<div><dt>{label}</dt><dd>{count:,}</dd></div>" for label, count in zip(labels, counts))
    cards = "".join(
        f'<a href="/q{i}" class="card"><span class="query-id">Q{i}</span><h2>{name}</h2><p>{about}</p></a>'
        for i, (name, about, _) in enumerate(FEATURES, 1)
    )
    return page("Queries", f'<h1>CS2 Match Explorer</h1><dl class="stats">{stats}</dl><div class="cards">{cards}</div>')


def not_found(message="Page not found"):
    return 404, page("Not found", f"<h1>{message}</h1>")


def event_page(db, event_id):
    event = db.execute(QUERIES["event_detail"], {"event_id": event_id}).fetchone()
    if event is None:
        return not_found("Event not found")
    schedule = db.execute(QUERIES["Q3"], {
        "event_id": event_id, "from_date": event["start_date"], "to_date": event["end_date"],
    })
    games = result_html(schedule, links={"match_id": match_link}, label="Event matches")
    stats = db.execute(QUERIES["Q7"], {"event_id": event_id, "min_maps": 1})
    leaderboard = result_html(stats, label="Event player leaderboard")
    name = event["name"]
    dates = f'{event["start_date"]} to {event["end_date"]}'
    prize = f' · ${event["prize_pool"]:,} prize pool' if event["prize_pool"] is not None else ""
    content = (
        f'<p class="breadcrumb"><a href="/q1">Find events</a></p><h1>{escape(name)}</h1>'
        f'<p class="intro">{escape(dates)} · {escape(event["location"])}{escape(prize)}</p>'
        '<div class="section-links"><a href="#matches">Matches</a><a href="#players">Player leaderboard</a></div>'
        f'<section id="matches"><h2>Matches</h2>{games}</section>'
        f'<section id="players"><h2>Player leaderboard</h2><p class="note">{NOTES[7]}</p>{leaderboard}</section>'
    )
    return 200, page(name, content, 1)


def match_page(db, match_id, map_id=None):
    match = db.execute(QUERIES["match_detail"], {"match_id": match_id}).fetchone()
    if match is None:
        return not_found("Match not found")
    maps = db.execute(QUERIES["Q4"], {"match_id": match_id}).fetchall()
    if map_id is None:
        selected = maps[0] if maps else None
    else:
        selected = next((row for row in maps if row["map_id"] == map_id), None)
        if selected is None:
            return not_found("Map not found in this match")

    title = f'{match["team1"]} vs {match["team2"]}'
    details = [
        match["scheduled_at"], match["stage"],
        f'BO{match["best_of"]}' if match["best_of"] else None, match["status"].capitalize(),
    ]
    score = ""
    if match["team1_map_wins"] is not None and match["team2_map_wins"] is not None:
        score = f'<p class="series-score">{match["team1_map_wins"]}–{match["team2_map_wins"]} <span>Series score</span></p>'
    content = [
        f'<p class="breadcrumb"><a href="/events/{match["event_id"]}#matches">{escape(match["event_name"])}</a></p>',
        f'<h1>{escape(title)}</h1><p class="intro">{escape(" · ".join(filter(None, details)))}</p>',
        score,
        '<section><h2>Played maps</h2>',
    ]
    if selected is None:
        content.append('<p class="feedback">No map results recorded for this series.</p></section>')
        return 200, page(title, "".join(content), 9)

    columns = [name for name in selected.keys() if name != "map_id"]
    content.append(table_html(
        columns, maps,
        links={"map": lambda row: map_link(row, match_id, selected["map_id"])}, label="Played maps",
    ))
    content.append("</section>")
    board = db.execute(QUERIES["Q9"], {"match_id": match_id, "map_id": selected["map_id"]})
    rows = board.fetchall()
    columns = [name for name, *_ in board.description if name != "team"]
    content.append(f'<section id="scoreboard"><h2>{escape(selected["map"])} player scoreboard</h2>')
    for team in (match["team1"], match["team2"]):
        team_rows = [row for row in rows if row["team"] == team]
        content.append(f'<h3>{escape(team)}</h3>{table_html(columns, team_rows, label=f"{team} player stats")}')
    content.append("</section>")
    return 200, page(title, "".join(content), 9)


def feature_page(db, number, request):
    title, about, keys = FEATURES[number - 1]
    options, values = load_form(db, keys)
    content = [f'<span class="query-id">Q{number}</span><h1>{title}</h1><p class="intro">{about}</p>']
    results = ""
    status = 200
    if request.get("run") == ["1"]:
        values = {key: request.get(key, [""])[0] for key in keys}
        try:
            params = parse_filters(values, options)
        except ValueError as error:
            results = f'<p class="feedback error" role="alert">{escape(str(error))}</p>'
            status = 400
        else:
            if number == 9:
                return match_page(db, params["match_id"])
            links = {1: {"name": event_link}, 3: {"match_id": match_link}}
            if number == 4:
                links[4] = {"map": lambda row: map_link(row, params["match_id"])}
            results = result_html(
                db.execute(QUERIES[f"Q{number}"], params),
                links=links.get(number), hidden=("map_id",) if number == 4 else (),
            )
    content.append(form_html(number, values, options))
    if number in NOTES:
        content.append(f'<p class="note">{NOTES[number]}</p>')
    content.append(results)
    return status, page(title, "".join(content), number)


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, content_type, content):
        data = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/style.css":
            self.respond(200, "text/css", (APP / "style.css").read_text(encoding="utf-8"))
            return
        feature = re.fullmatch(r"/q([1-9])", url.path)
        event = re.fullmatch(r"/events/([0-9]{1,18})", url.path)
        series = re.fullmatch(r"/matches/([0-9]{1,18})(?:/maps/([0-9]{1,18}))?", url.path)
        if url.path != "/" and not (feature or event or series):
            status, markup = not_found()
            self.respond(status, "text/html", markup)
            return
        try:
            request = parse_qs(url.query, keep_blank_values=True, max_num_fields=20)
        except ValueError:
            self.respond(400, "text/html", page("Invalid query", "<h1>Invalid query parameters</h1>"))
            return
        try:
            with closing(connect()) as db:
                if feature:
                    status, markup = feature_page(db, int(feature[1]), request)
                elif event:
                    status, markup = event_page(db, int(event[1]))
                elif series:
                    status, markup = match_page(db, int(series[1]), int(series[2]) if series[2] else None)
                else:
                    status, markup = 200, homepage(db)
        except sqlite3.Error as error:
            self.log_error("Query failed: %s", error)
            status, markup = 500, page("Database error", "<h1>Could not read the database</h1>")
        self.respond(status, "text/html", markup)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000, help="Local port (default: 8000)")
    args = parser.parse_args()
    if not DATABASE.is_file():
        parser.exit(1, f"Database file not found: {DATABASE}\n")
    try:
        with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
            print(f"CS2 Match Explorer · http://127.0.0.1:{server.server_port}/", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    except OSError as error:
        parser.exit(1, f"Could not start local server: {error}\n")


if __name__ == "__main__":
    main()
