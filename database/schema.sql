-- CS2 Match Explorer. SQLite schema for the 2026-11-11 snapshot.

CREATE TABLE events (
    event_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL CHECK (end_date >= start_date),
    prize_pool INTEGER CHECK (prize_pool >= 0),
    event_mode TEXT NOT NULL CHECK (event_mode IN ('lan', 'mixed')),
    location TEXT NOT NULL,
    source_url TEXT NOT NULL
);

CREATE TABLE stages (
    stage_id INTEGER PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(event_id),
    name TEXT NOT NULL,
    format TEXT NOT NULL CHECK (format IN ('swiss', 'single_elimination', 'double_elimination', 'gsl', 'round_robin')),
    display_order INTEGER NOT NULL CHECK (display_order > 0),
    source_section TEXT NOT NULL,
    source_url TEXT NOT NULL,
    UNIQUE (event_id, display_order),
    UNIQUE (event_id, name)
);

CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    country_or_region TEXT
);

CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    nickname TEXT NOT NULL,
    country_or_region TEXT,
    current_team_id INTEGER REFERENCES teams(team_id),
    last_observed_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    last_observed_date TEXT NOT NULL
);

CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    hltv_match_id INTEGER UNIQUE,
    stage_id INTEGER NOT NULL REFERENCES stages(stage_id),
    team1_id INTEGER NOT NULL REFERENCES teams(team_id),
    team2_id INTEGER NOT NULL REFERENCES teams(team_id),
    match_date TEXT NOT NULL,
    scheduled_at TEXT,
    best_of INTEGER CHECK (best_of IN (1, 3, 5)),
    status TEXT NOT NULL CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    round_no INTEGER CHECK (round_no > 0),
    bracket_label TEXT,
    reported_team1_score INTEGER CHECK (reported_team1_score >= 0),
    reported_team2_score INTEGER CHECK (reported_team2_score >= 0),
    reported_score_unit TEXT CHECK (reported_score_unit IN ('maps', 'rounds')),
    stage_assignment TEXT NOT NULL CHECK (stage_assignment IN ('source_section', 'date_boundary', 'published_result')),
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    CHECK (team1_id <> team2_id),
    CHECK (status <> 'completed' OR (
        reported_team1_score IS NOT NULL AND reported_team2_score IS NOT NULL
        AND reported_team1_score <> reported_team2_score AND reported_score_unit IS NOT NULL
    ))
);

CREATE TABLE maps (
    map_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE
);

CREATE TABLE match_maps (
    match_id INTEGER NOT NULL REFERENCES matches(match_id),
    map_id INTEGER NOT NULL REFERENCES maps(map_id),
    map_order INTEGER NOT NULL CHECK (map_order > 0),
    team1_rounds INTEGER NOT NULL CHECK (team1_rounds >= 0),
    team2_rounds INTEGER NOT NULL CHECK (team2_rounds >= 0),
    replay_filename TEXT,
    source_url TEXT NOT NULL,
    PRIMARY KEY (match_id, map_id),
    UNIQUE (match_id, map_order),
    CHECK (team1_rounds <> team2_rounds)
);

CREATE TABLE player_map_stats (
    match_id INTEGER NOT NULL,
    map_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    team_id INTEGER NOT NULL REFERENCES teams(team_id),
    kills INTEGER NOT NULL CHECK (kills >= 0),
    deaths INTEGER NOT NULL CHECK (deaths >= 0),
    assists INTEGER CHECK (assists >= 0),
    total_damage INTEGER CHECK (total_damage >= 0),
    rounds_played INTEGER NOT NULL CHECK (rounds_played > 0),
    headshot_kills INTEGER NOT NULL CHECK (headshot_kills BETWEEN 0 AND kills),
    opening_kills INTEGER NOT NULL CHECK (opening_kills BETWEEN 0 AND kills),
    opening_deaths INTEGER NOT NULL CHECK (opening_deaths BETWEEN 0 AND deaths),
    grenades_thrown INTEGER CHECK (grenades_thrown >= 0),
    reported_adr REAL CHECK (reported_adr >= 0),
    kast_pct REAL CHECK (kast_pct BETWEEN 0 AND 100),
    rating_3 REAL CHECK (rating_3 >= 0),
    flash_assists INTEGER CHECK (flash_assists BETWEEN 0 AND assists),
    stats_source TEXT NOT NULL CHECK (stats_source IN ('replay', 'hltv')),
    source_url TEXT NOT NULL,
    grenades_source_url TEXT,
    PRIMARY KEY (match_id, map_id, player_id),
    FOREIGN KEY (match_id, map_id) REFERENCES match_maps(match_id, map_id)
);

CREATE INDEX matches_stage_date_idx ON matches(stage_id, match_date);
CREATE INDEX matches_team1_date_idx ON matches(team1_id, match_date);
CREATE INDEX matches_team2_date_idx ON matches(team2_id, match_date);
CREATE INDEX match_maps_map_idx ON match_maps(map_id, match_id);
CREATE INDEX player_map_stats_player_idx ON player_map_stats(player_id, match_id);

-- A reported series score can remain available when replay/map coverage is incomplete.
CREATE VIEW match_results AS
WITH map_totals AS (
    SELECT match_id, COUNT(*) AS maps_recorded,
           SUM(team1_rounds > team2_rounds) AS observed_team1_map_wins,
           SUM(team2_rounds > team1_rounds) AS observed_team2_map_wins
    FROM match_maps
    GROUP BY match_id
)
SELECT m.match_id, s.event_id, m.stage_id, m.match_date, m.best_of, m.status,
       m.team1_id, m.team2_id,
       CASE WHEN m.reported_score_unit = 'rounds' THEN m.reported_team1_score > m.reported_team2_score
            ELSE m.reported_team1_score END AS team1_map_wins,
       CASE WHEN m.reported_score_unit = 'rounds' THEN m.reported_team2_score > m.reported_team1_score
            ELSE m.reported_team2_score END AS team2_map_wins,
       CASE WHEN m.status <> 'completed' THEN NULL
            WHEN m.reported_team1_score > m.reported_team2_score THEN m.team1_id
            ELSE m.team2_id END AS winner_team_id,
       COALESCE(mt.maps_recorded, 0) AS maps_recorded,
       COALESCE(mt.observed_team1_map_wins, 0) AS observed_team1_map_wins,
       COALESCE(mt.observed_team2_map_wins, 0) AS observed_team2_map_wins,
       CASE WHEN m.status <> 'completed' THEN NULL
            WHEN m.reported_score_unit = 'rounds' THEN 1
            ELSE m.reported_team1_score + m.reported_team2_score END AS expected_maps,
       CASE WHEN m.status <> 'completed' THEN 'not_completed'
            WHEN mt.maps_recorded IS NULL THEN 'missing'
            WHEN m.reported_score_unit = 'rounds' AND mt.maps_recorded = 1
                 AND mm.team1_rounds = m.reported_team1_score
                 AND mm.team2_rounds = m.reported_team2_score THEN 'complete'
            WHEN m.reported_score_unit = 'maps'
                 AND mt.observed_team1_map_wins = m.reported_team1_score
                 AND mt.observed_team2_map_wins = m.reported_team2_score THEN 'complete'
            WHEN m.reported_score_unit = 'maps'
                 AND mt.observed_team1_map_wins <= m.reported_team1_score
                 AND mt.observed_team2_map_wins <= m.reported_team2_score THEN 'partial'
            ELSE 'conflict' END AS map_coverage
FROM matches AS m
JOIN stages AS s ON s.stage_id = m.stage_id
LEFT JOIN map_totals AS mt ON mt.match_id = m.match_id
LEFT JOIN match_maps AS mm ON mm.match_id = m.match_id AND mm.map_order = 1;

CREATE VIEW event_coverage AS
WITH series AS (
    SELECT event_id, COUNT(*) AS series_recorded,
           SUM(map_coverage = 'complete') AS series_with_all_maps,
           SUM(expected_maps) AS expected_maps_for_recorded_series,
           SUM(maps_recorded) AS maps_recorded
    FROM match_results
    GROUP BY event_id
), stats_by_map AS (
    SELECT s.event_id, p.match_id, p.map_id, COUNT(*) AS player_rows,
           SUM(p.total_damage IS NOT NULL) AS damage_rows,
           SUM(p.reported_adr IS NOT NULL) AS reported_adr_rows
    FROM player_map_stats AS p
    JOIN matches AS m ON m.match_id = p.match_id
    JOIN stages AS s ON s.stage_id = m.stage_id
    GROUP BY s.event_id, p.match_id, p.map_id
), stats AS (
    SELECT event_id, COUNT(*) AS maps_with_player_stats,
           SUM(player_rows) AS player_rows, SUM(damage_rows) AS damage_rows,
           SUM(reported_adr_rows) AS reported_adr_rows
    FROM stats_by_map
    GROUP BY event_id
)
SELECT e.event_id, e.name,
       COALESCE(series.series_recorded, 0) AS series_recorded,
       COALESCE(series.series_with_all_maps, 0) AS series_with_all_maps,
       COALESCE(series.expected_maps_for_recorded_series, 0) AS expected_maps_for_recorded_series,
       COALESCE(series.maps_recorded, 0) AS maps_recorded,
       COALESCE(stats.maps_with_player_stats, 0) AS maps_with_player_stats,
       COALESCE(stats.player_rows, 0) AS player_rows,
       COALESCE(stats.damage_rows, 0) AS damage_rows,
       COALESCE(stats.reported_adr_rows, 0) AS reported_adr_rows
FROM events AS e
LEFT JOIN series ON series.event_id = e.event_id
LEFT JOIN stats ON stats.event_id = e.event_id;

-- Latest observed map lineup for each team in this snapshot.
CREATE VIEW latest_observed_lineups AS
WITH ranked AS (
    SELECT p.team_id, p.player_id, p.match_id, p.map_id, m.match_date,
           DENSE_RANK() OVER (
               PARTITION BY p.team_id
               ORDER BY m.match_date DESC, m.match_id DESC, mm.map_order DESC
           ) AS position
    FROM player_map_stats AS p
    JOIN matches AS m ON m.match_id = p.match_id
    JOIN match_maps AS mm ON mm.match_id = p.match_id AND mm.map_id = p.map_id
)
SELECT r.team_id, r.player_id, p.nickname, r.match_id, r.map_id, r.match_date
FROM ranked AS r
JOIN players AS p ON p.player_id = r.player_id
WHERE r.position = 1;
