-- Q1: Event search / 赛事查询
SELECT event_id, name, start_date, end_date, prize_pool, event_mode
FROM events
WHERE start_date <= :to_date AND end_date >= :from_date AND prize_pool >= :min_prize
ORDER BY start_date, event_id;

-- Q2: Latest observed lineup / 最近一次录得阵容
SELECT nickname, match_date, match_id
FROM latest_observed_lineups
WHERE team_id = :team_id
ORDER BY nickname;

-- Q3: Series by event and date / 赛事对阵与赛果
SELECT r.match_date, m.scheduled_at,
       CASE WHEN m.round_no IS NOT NULL THEN s.name || ' · Round ' || m.round_no
            WHEN m.bracket_label IS NOT NULL THEN s.name || ' · ' || m.bracket_label
            ELSE s.name END AS stage,
       a.name AS team1, b.name AS team2,
       r.best_of, r.status, r.team1_map_wins, r.team2_map_wins, r.map_coverage, r.match_id
FROM match_results r
JOIN matches m ON m.match_id = r.match_id
JOIN stages s ON s.stage_id = r.stage_id
JOIN teams a ON a.team_id = r.team1_id
JOIN teams b ON b.team_id = r.team2_id
WHERE r.event_id = :event_id AND r.match_date BETWEEN :from_date AND :to_date
ORDER BY COALESCE(datetime(m.scheduled_at), datetime(r.match_date)), r.match_id;

-- Q4: Played maps and winners / 逐图比分及胜者
SELECT mm.map_order, mp.name AS map, a.name AS team1, b.name AS team2,
       mm.team1_rounds, mm.team2_rounds,
       CASE WHEN mm.team1_rounds > mm.team2_rounds THEN a.name ELSE b.name END AS winner,
       mm.map_id
FROM match_maps mm
JOIN maps mp USING (map_id)
JOIN matches m USING (match_id)
JOIN teams a ON a.team_id = m.team1_id
JOIN teams b ON b.team_id = m.team2_id
WHERE mm.match_id = :match_id
ORDER BY mm.map_order;

-- Q5: Head-to-head series totals / 历史交手，按系列赛计数
SELECT a.name AS team_a, b.name AS team_b, COUNT(r.match_id) AS series_played,
       COALESCE(SUM(r.winner_team_id = a.team_id), 0) AS team_a_wins,
       COALESCE(SUM(r.winner_team_id = b.team_id), 0) AS team_b_wins,
       ROUND(100.0 * SUM(r.winner_team_id = a.team_id) / NULLIF(COUNT(r.match_id), 0), 1) AS team_a_win_pct,
       ROUND(100.0 * SUM(r.winner_team_id = b.team_id) / NULLIF(COUNT(r.match_id), 0), 1) AS team_b_win_pct
FROM teams a JOIN teams b ON b.team_id = :team_b AND a.team_id <> b.team_id
LEFT JOIN match_results r ON r.status = 'completed' AND r.match_date BETWEEN :from_date AND :to_date
 AND ((r.team1_id = a.team_id AND r.team2_id = b.team_id)
   OR (r.team1_id = b.team_id AND r.team2_id = a.team_id))
WHERE a.team_id = :team_a
GROUP BY a.team_id, a.name, b.team_id, b.name;

-- Q6: Team map performance / 战队地图表现
WITH observed AS (
    SELECT mp.map_id, mp.name,
           CASE WHEN m.team1_id = :team_id THEN mm.team1_rounds > mm.team2_rounds
                ELSE mm.team2_rounds > mm.team1_rounds END AS won
    FROM match_maps mm JOIN matches m USING (match_id) JOIN maps mp USING (map_id)
    WHERE m.status = 'completed' AND m.match_date BETWEEN :from_date AND :to_date
      AND :team_id IN (m.team1_id, m.team2_id)
)
SELECT name, COUNT(*) AS maps_played, SUM(won) AS map_wins,
       ROUND(100.0 * SUM(won) / COUNT(*), 1) AS map_win_pct
FROM observed GROUP BY map_id, name HAVING COUNT(*) >= :min_maps
ORDER BY map_win_pct DESC, maps_played DESC, name;

-- Q7: Sampled player leaderboard / 选手样本榜
SELECT p.nickname, COUNT(*) AS maps_with_stats, SUM(ps.kills) AS kills,
       SUM(ps.deaths) AS deaths, ROUND(1.0 * SUM(ps.kills) / NULLIF(SUM(ps.deaths), 0), 2) AS kd,
       SUM(ps.headshot_kills) AS headshot_kills, SUM(ps.opening_kills) AS opening_kills,
       COUNT(ps.reported_adr) AS maps_with_reported_adr,
       CAST(ROUND(ROUND(SUM(ps.reported_adr * ps.rounds_played), 1)) AS INTEGER) AS estimated_total_damage,
       -- Round the weighted ADR in tenths to avoid floating-point errors at half steps.
       ROUND(ROUND(SUM(ps.reported_adr * ps.rounds_played) * 10) /
           NULLIF(SUM(CASE WHEN ps.reported_adr IS NOT NULL THEN ps.rounds_played END), 0)) / 10.0 AS sampled_adr,
       COUNT(ps.assists) AS maps_with_assists, SUM(ps.assists) AS sampled_assists
FROM player_map_stats ps
JOIN players p USING (player_id)
JOIN matches m USING (match_id)
JOIN stages s USING (stage_id)
WHERE s.event_id = :event_id
GROUP BY p.player_id, p.nickname HAVING COUNT(*) >= :min_maps
ORDER BY kd DESC, maps_with_stats DESC, p.player_id;

-- Q8: Teams without an observed map / 所选期间没有该地图记录的战队
SELECT t.team_id, t.name
FROM teams t
WHERE NOT EXISTS (
    SELECT 1 FROM match_maps mm JOIN matches m USING (match_id)
    WHERE mm.map_id = :map_id AND m.status = 'completed'
      AND m.match_date BETWEEN :from_date AND :to_date
      AND t.team_id IN (m.team1_id, m.team2_id)
)
ORDER BY t.name;

-- Q9: Player scoreboard for one map in a series / 比赛逐图选手计分板
SELECT t.name AS team, p.nickname, ps.kills, ps.deaths, ps.assists,
       ps.headshot_kills, ps.opening_kills, ps.reported_adr AS adr, ps.kast_pct, ps.rating_3
FROM player_map_stats ps
JOIN players p USING (player_id)
JOIN teams t USING (team_id)
JOIN matches m USING (match_id)
WHERE ps.match_id = :match_id AND ps.map_id = :map_id
ORDER BY ps.team_id <> m.team1_id, ps.kills DESC, p.nickname, p.player_id;

-- event_detail: Header and date range for an event
SELECT name, start_date, end_date, location, prize_pool
FROM events
WHERE event_id = :event_id;

-- match_detail: Header for a series
SELECT r.event_id, e.name AS event_name, a.name AS team1, b.name AS team2, m.scheduled_at,
       CASE WHEN m.round_no IS NOT NULL THEN s.name || ' · Round ' || m.round_no
            WHEN m.bracket_label IS NOT NULL THEN s.name || ' · ' || m.bracket_label
            ELSE s.name END AS stage,
       r.best_of, r.status, r.team1_map_wins, r.team2_map_wins
FROM match_results r
JOIN matches m USING (match_id)
JOIN stages s ON s.stage_id = r.stage_id
JOIN events e ON e.event_id = r.event_id
JOIN teams a ON a.team_id = r.team1_id
JOIN teams b ON b.team_id = r.team2_id
WHERE r.match_id = :match_id;
