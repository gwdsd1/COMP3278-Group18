# CS2 Match Explorer 数据手册 / Data Guide

**2026-11-11 快照 / Snapshot as of 2026-11-11** · COMP3278 · 三人组 / Three-person team

## 1. 离线开发 / Offline development

把整个 `database/` 文件夹复制到解压后的课程 starter kit 根目录。应用继续从 `database/app.db` 读取 **SQLite**。表名、字段名和赛事名称使用英文。SQLite 本身支持 UTF-8，保留 `Kraków` 等原始拼写。

Copy the complete `database/` folder into the extracted starter kit. The app reads the **SQLite** file at `database/app.db`. Table names, field names and event names are in English, with original spellings such as `Kraków` preserved.

| 文件 / File | 用途 / Purpose |
|---|---|
| [`database/app.db`](./database/app.db) | 可直接打开、无需联网的数据快照 / Ready-to-use offline snapshot |
| [`database/schema.sql`](./database/schema.sql) | 8 张表、索引和 3 个查询视图 / Eight tables, indexes and three query views |
| [`database/seed.sql`](./database/seed.sql) | 真实比赛数据及来源链接 / Match data and provenance |
| [`database/build.sql`](./database/build.sql) | starter kit 原始构建脚本 / Original starter-kit build script |

需要重建时，在包含 `database/` 的目录运行课程命令。Windows PowerShell 使用本目录的 `sqlite3.exe` 时，把 `sqlite3` 写为 `./sqlite3.exe`。

To rebuild, run the course command from the directory containing `database/`. In Windows PowerShell, use `./sqlite3.exe` if the CLI executable is in the current directory.

```sh
sqlite3 -bail :memory: ".read database/build.sql"
```

已用课程原版 `build.sql` 和官方 SQLite 命令行工具在独立目录重建，并与交付快照逐行比对。数据库完整性和外键检查通过。

The snapshot was rebuilt in a separate directory with the original course script and official SQLite CLI. The rebuilt data matched the delivered file. Integrity, foreign keys and all eight reference queries passed local checks.

## 2. 赛事范围与覆盖 / Scope and coverage

只纳入指定的 17 届 2026 年赛事。Bounty S1/S2 的正赛线上阶段和线下决赛各合为一届。IEM Kraków 包含 Stage 1。科隆 Major 包含 Stage 1、2、3 和淘汰赛。EPL S23 只纳入线下 Finals。各赛事的独立预选赛不在范围内。

The snapshot covers only the 17 requested 2026 events. Each Bounty season groups its main online bracket with its LAN finals. Kraków includes Stage 1 and Cologne includes all three Swiss stages and playoffs. EPL S23 is LAN finals only. Separate qualifiers are out of scope.

比分对账覆盖 HLTV 的 22 个赛事分区，对应指定的 17 届赛事。每条 Results 赛果已入库，所有系列赛的逐图结果均与发布比分一致。每张有选手统计的地图均有双方共 10 行。

The reconciliation covers all listed HLTV Results across 22 source sections for the 17 requested events. Every recorded series has map results that reconcile with its published score. Each map with player data has ten rows.

| 赛事 / Event | 系列赛 / Series | 地图 / Maps | 有选手统计 / With players | 有 ADR 和助攻 / With ADR & assists | 缺全部选手统计 / No player data | 缺 ADR 或助攻 / Missing ADR or assists |
|---|---:|---:|---:|---:|---:|---:|
| [BLAST Bounty 2026 Season 1](https://www.hltv.org/events/8876) | 31 | 76 | 76 | 76 | 0 | 0 |
| [IEM Kraków 2026](https://www.hltv.org/events/8240) | 50 | 122 | 122 | 122 | 0 | 0 |
| [PGL Cluj-Napoca 2026](https://www.hltv.org/events/8047) | 41 | 102 | 102 | 102 | 0 | 0 |
| [ESL Pro League Season 23 Finals](https://www.hltv.org/events/8413) | 8 | 23 | 23 | 23 | 0 | 0 |
| [BLAST Open Rotterdam 2026](https://www.hltv.org/events/8248) | 29 | 70 | 70 | 70 | 0 | 0 |
| [IEM Rio 2026](https://www.hltv.org/events/8242) | 30 | 70 | 70 | 70 | 0 | 0 |
| [BLAST Rivals 2026 Season 1](https://www.hltv.org/events/8250) | 13 | 32 | 32 | 32 | 0 | 0 |
| [PGL Astana 2026](https://www.hltv.org/events/8049) | 41 | 96 | 96 | 96 | 0 | 0 |
| [IEM Atlanta 2026](https://www.hltv.org/events/8243) | 30 | 73 | 73 | 73 | 0 | 0 |
| [IEM Cologne Major 2026](https://www.hltv.org/events/8301) | 106 | 202 | 202 | 202 | 0 | 0 |
| [BLAST Bounty 2026 Season 2](https://www.hltv.org/events/9154) | 31 | 81 | 81 | 81 | 0 | 0 |
| [Esports World Cup 2026](https://www.hltv.org/events/8261) | 56 | 115 | 115 | 115 | 0 | 0 |
| [BLAST Open Porto 2026](https://www.hltv.org/events/8249) | 29 | 68 | 68 | 68 | 0 | 0 |
| [ESL Pro League Season 24](https://www.hltv.org/events/8244) | 41 | 99 | 99 | 99 | 0 | 0 |
| [Thunderpick World Championship 2026](https://www.hltv.org/events/8932) | 14 | 37 | 37 | 37 | 0 | 0 |
| [PGL Masters Bucharest 2026](https://www.hltv.org/events/8050) | 41 | 97 | 97 | 97 | 0 | 0 |
| [IEM Beijing 2026](https://www.hltv.org/events/8245) | 30 | 74 | 74 | 74 | 0 | 0 |
| **合计 / Total** | **621** | **1,437** | **1,437** | **1,437** | **0** | **0** |

本轮根据用户提供的 HLTV 截图补齐最后 **3 张**地图。共有 14,370 条选手逐图记录，其中 14,370 条同时有 ADR 和助攻。比赛与逐图比分沿用此前已对账的 621 场和 1,437 张图。

The last **3** HLTV map scoreboards were transcribed from user-provided screenshots. The snapshot has 14,370 player-map rows, including 14,370 with both ADR and assists. It retains the previously reconciled 621 series and 1,437 map scores.

| 优先范围 / Priority scope | 已补齐系列赛 / Complete series | 已补齐地图 / Complete maps | 缺图 / Missing maps |
|---|---:|---:|---:|
| 总决赛 / Grand finals | 17/17 | 60/60 | 0 |
| 淘汰赛含决赛和季军赛 / Playoffs including finals and third-place matches | 120/120 | 311/311 | 0 |

### 逐张图查缺口 / List the missing map scorecards

全部 1,437 张地图均有双方各 5 人的 ADR 和助攻。下方的离线查询用于检查缺口，当前快照返回零行。

All 1,437 maps have ADR and assists for five players on each team. The offline query below checks for gaps and returns zero rows for this snapshot.

```sqlite
SELECT e.name AS event, m.match_date, m.match_id, m.hltv_match_id,
       t1.name AS team1, t2.name AS team2, mm.map_order, mp.name AS map,
       COUNT(ps.player_id) AS player_rows, COUNT(ps.reported_adr) AS adr_rows,
       COUNT(ps.assists) AS assist_rows
FROM match_maps mm
JOIN matches m USING (match_id)
JOIN stages s USING (stage_id)
JOIN events e USING (event_id)
JOIN maps mp USING (map_id)
JOIN teams t1 ON t1.team_id = m.team1_id
JOIN teams t2 ON t2.team_id = m.team2_id
LEFT JOIN player_map_stats ps USING (match_id, map_id)
GROUP BY m.match_id, mm.map_id
HAVING COUNT(ps.player_id) < 10 OR COUNT(ps.reported_adr) < 10 OR COUNT(ps.assists) < 10
ORDER BY e.start_date, m.match_date, m.match_id, mm.map_order;
```

### 决赛缺口 / Missing grand-final maps

全部补齐。 / All complete.

### 其他淘汰赛缺口 / Missing maps from other playoff rounds

统计口径为 HLTV 的 Playoffs 结果及对阵页确认的其他四分之一决赛和季军赛。BLAST Rivals S1 的两场小组赛（2393335、2393336）在库里沿用按日期分配的阶段，在本清单中列入其他阶段。

The playoff scope combines HLTV’s Playoffs results with additional quarterfinal and third-place matches verified on their match pages. BLAST Rivals S1 group matches 2393335 and 2393336 retain their date-based stage in SQLite and appear under other stages in this list.

全部补齐。 / All complete.

### 其他阶段缺口 / Missing maps from other stages

全部补齐。 / All complete.

## 3. HLTV 的查询路径 / Where to find the metrics on HLTV

| 页面 / Page | 中文说明 | English |
|---|---|---|
| [Results](https://www.hltv.org/results?event=8244&playoffMatchType=PLAYOFFS) | 在 `Event` 选赛事，在 `Match type` 选 `Grand final` 或 `Playoffs`。部分季军赛和淘汰赛可从赛事对阵页找到 | Select an event and `Grand final` or `Playoffs` under `Match type`. Check the event bracket for additional rounds |
| [Stats → Matches](https://www.hltv.org/stats/matches) | 用 CS2、日期、地图和比赛类型定位单图，结果列表中的一行对应一张已打地图 | Filter played maps by CS2, date, map and match type. Each row represents one played map |
| [Stats](https://www.hltv.org/stats?csVersion=CS2) | 选择 CS2。在 `Add to context` 添加赛事、队伍或选手，配合时间、地图、赛事类型、最低地图数等筛选 | Choose CS2 and add event, team or player context. Combine it with date, map, event type and minimum-map filters |
| [选手比赛记录 / Player match history](https://www.hltv.org/stats/players/matches/11893/zywoo?csVersion=CS2&teamId=9565) | 按选手、时间与地图定位具体场次。该页用于定位和核对，逐图 ADR 和助攻取自对应单图计分板 | Locate a player’s map by date and map filter. Read ADR and assists from the linked map scoreboard |
| [单图计分板 / Map scoreboard](https://www.hltv.org/stats/matches/mapstatsid/243883/the-mongolz-vs-mouz) | 从比赛详情点具体地图的 `STATS`，读取该图 `Both sides` 的 `K (hs)`、`D (t)`、`A (f)`、`Op.K-D`、ADR、KAST、Rating。CT 和 T 是同一张地图的分边表 | Open `STATS` for a particular map and use its `Both sides` scoreboard. CT and T split the same map |
| [Opening](https://www.hltv.org/stats/players/opening) | 选手筛选样本中的每回合开局击杀与死亡率，如 OpKPR、OpDPR | Filtered player rates such as opening kills and deaths per round |
| [Grenades](https://www.hltv.org/stats/players/grenades?country=United+States) | 烟、火、HE 每回合投掷量、投掷物伤害等。该页的筛选样本汇总不等同于某一张图的投掷总数 | Per-round smoke, molotov and HE rates and grenade damage. Filtered aggregates have a different grain from a map's throw count |

从系列赛页点开缺失地图旁的 `STATS`，使用 `Side → Both` 下双方各五人的总计。助攻取 `A (f)` 主值，写入 `assists`。括号里的闪光助攻写入 `flash_assists`，ADR 原样写入 `reported_adr`。

Open `STATS` beside the missing map and read the five players per team under `Side → Both`. The main number in `A (f)` goes in `assists`, the bracketed value goes in `flash_assists`, and the displayed ADR goes in `reported_adr`. [Kraków grand final · Inferno](https://www.hltv.org/stats/matches/mapstatsid/218565/furia-vs-vitality)

### 来源与口径 / Provenance and definitions

- 最后 3 张地图的 30 行来自用户提供的 HLTV `Players → Side: Both` 截图。MIBR 对 B8 的 Nuke 补齐既有录像行，G2 对 PARIVISION 的 Inferno 和 Team Spirit 对 M80 的 Cache 新增选手行。 / The final 30 rows were transcribed from user-provided HLTV `Players → Side: Both` screenshots. The MIBR–B8 Nuke enriched existing replay rows, and the G2–PARIVISION Inferno and Team Spirit–M80 Cache added player rows. [MIBR–B8 · Nuke](https://www.hltv.org/stats/matches/mapstatsid/231112/b8-vs-mibr) · [G2–PARIVISION · Inferno](https://www.hltv.org/stats/matches/mapstatsid/240807/g2-vs-parivision) · [Team Spirit–M80 · Cache](https://www.hltv.org/stats/matches/mapstatsid/240965/m80-vs-spirit)
- BLAST Bounty S2 四分之一决赛 FaZe 对 The MongolZ 第 3 图 Ancient 的 10 行来自用户提供的 HLTV `Players → Side: Both` 截图。 / The ten rows for map 3, Ancient, in the BLAST Bounty S2 quarter-final between FaZe and The MongolZ were transcribed from a user-provided HLTV screenshot. [HLTV Ancient](https://www.hltv.org/stats/matches/mapstatsid/234071/the-mongolz-vs-faze)
- IEM Atlanta 决赛第 3 图 Nuke 的 10 行来自用户提供的 HLTV `Players → Side: Both` 截图。 / The ten rows for map 3, Nuke, in the IEM Atlanta grand final were transcribed from the user-provided HLTV screenshot. [HLTV Nuke](https://www.hltv.org/stats/matches/mapstatsid/229180/natus-vincere-vs-gamerlegion)
- IEM Atlanta 决赛第 2 图 Anubis 的 10 行来自用户提供的 HLTV `Players → Side: Both` 截图。 / The ten rows for map 2, Anubis, in the IEM Atlanta grand final were transcribed from a user-provided screenshot of HLTV’s `Players → Side: Both` tables. [HLTV Anubis](https://www.hltv.org/stats/matches/mapstatsid/229170/natus-vincere-vs-gamerlegion)
- **HLTV** 提供赛事资料、补录系列赛和逐图计分板。`stats_source = 'hltv'` 仅指该行的基础计分板值。部分页面在采集期间返回过 HTTP 429，相关计分板后来通过 HLTV 页面或截图补齐。 / HLTV supplies event metadata, supplementary series results and published map scoreboards. Some pages returned HTTP 429 during collection. The affected scoreboards were later completed from HLTV pages or screenshots. [HLTV Terms](https://www.hltv.org/terms)
- **CS2dave** 提供公开比赛索引及部分地图的录像事件。录像统计使用对应地图的事件，先校验重建回合比分和双方阵容。`grenades_thrown` 是录像导出中可辨认的投掷事件数。 / CS2dave supplies the public match index and some replay events. Replay scoreboards are accepted after checking round scores and both lineups. `grenades_thrown` counts throw events recognized in the replay export. [CS2dave](https://cs2dave.com/)
- `source_url` 记录主要来源。`grenades_source_url` 单独记录投掷物来源。已补录计分板的行优先使用 HLTV 的击杀、死亡和开局数。 / `source_url` records the primary source. Grenade provenance is stored separately. The selected HLTV rows use the published scoreboard values.
- **缺失为 `NULL`，真实零才写 `0`**。`reported_adr` 保留站点显示的精度。精确字段 `total_damage` 当前为 `NULL`。Q7 在查询时用 `reported_adr × rounds_played` 计算估算总伤害。没有 HLTV 计分板的录像样本通常没有助攻、KAST 和 Rating。 / `NULL` is missing. A zero is an observed value. `reported_adr` keeps the published precision. The exact `total_damage` field is currently `NULL`. Q7 calculates estimated damage from `reported_adr × rounds_played` at query time. Replay-only samples generally lack assists, KAST and Rating.

## 4. 表、键与字段约定 / Tables, keys and field semantics

| 表 / Table | 行粒度与键 / Grain and keys | 行数 / Rows |
|---|---|---:|
| `events` | 每届赛事 / One event. PK `event_id` | 17 |
| `stages` | 每届赛事的一个阶段 / One stage. PK `stage_id`, FK `event_id` | 36 |
| `teams` | 规范化后的战队 / One canonical team. PK `team_id` | 65 |
| `players` | 按已观测身份合并的选手 / One observed player identity. PK `player_id` | 343 |
| `matches` | 一场系列赛 / One series. PK `match_id`, FK `stage_id`, `team1_id`, `team2_id` | 621 |
| `maps` | 一张地图的定义 / One map. PK `map_id`, unique `code` | 8 |
| `match_maps` | 一场系列赛中已打的一张图 / One played map. PK `(match_id, map_id)`, unique `(match_id, map_order)` | 1,437 |
| `player_map_stats` | 一名选手在某场比赛某张图的统计 / One player on one played map. PK `(match_id, map_id, player_id)` | 14,370 |

- `best_of` 从正常完成的赛果推断为 1、3 或 5，或来自已核对的比赛页。`reported_score_unit` 区分赢图数与 BO1 的回合比分。推荐通过 `match_results` 读取统一的系列赛比分和胜者。 / `best_of` comes from normal results or a verified match page. `reported_score_unit` distinguishes maps from BO1 rounds. Use `match_results` for normalized series scores and winner.
- `match_date` 采用 HLTV Results 显示的比赛日期。`scheduled_at`、`round_no` 等字段在未核实时保留空值。部分阶段按赛事公布的日期边界归类，见 `stage_assignment`。`match_id` 保留本地已分配的主键，`hltv_match_id` 保存 HLTV 的比赛 ID。 / `match_date` follows the HLTV Results date. Unverified times and round numbers remain nullable. See `stage_assignment` for date-based phase attribution. Existing local keys are preserved as `match_id`; the published ID is stored in `hltv_match_id`.
- `current_team_id` 按有证据的 HLTV 当前阵容补录。开发时将 `latest_observed_lineups` 标为“最近一次录得阵容”，显示样本日期。`player_map_stats.team_id` 是当时代表队。 / Current team membership was filled from verifiable published lineups. Label `latest_observed_lineups` as the latest observed lineup and display its date. Historical team membership is `player_map_stats.team_id`.
- `match_results.map_coverage` 对比本库逐图比分与已记录系列赛结果。`event_coverage` 提供逐赛事汇总。二者都只覆盖已录入的系列赛。 / `match_results.map_coverage` reconciles map rows against recorded results. `event_coverage` summarizes the same recorded series by event.

- `V$M` 和 `vsm` 沿用历史选手 ID `27` 与 `246`。汇总该选手时可同时选取这两个 ID。 / The same player appears under legacy IDs `27` (`V$M`) and `246` (`vsm`). Include both IDs when aggregating his results.

### 字段缺失统计 / Field completeness

| 字段 / Field | 含义 / Meaning | 本轮补录 / Filled this pass | 仍缺 / NULL | 总行数 / Total |
|---|---|---:|---:|---:|
| `matches.scheduled_at` | 开赛时间 / Published start time | 19 | 0 | 621 |
| `matches.round_no` | 阶段内数字轮次 / Round number | 82 | 352 | 621 |
| `matches.bracket_label` | 签表标签 / Bracket label | 146 | 30 | 621 |
| `player_map_stats.grenades_thrown` | 投掷次数 / Grenade throws | 330 | 4,970 | 14,370 |
| `player_map_stats.grenades_source_url` | 投掷来源 / Grenade source | 330 | 4,970 | 14,370 |
| `player_map_stats.total_damage` | 精确总伤害 / Exact damage | 0 | 14,370 | 14,370 |
| `match_maps.replay_filename` | 录像文件名 / Replay filename | 0 | 462 | 1,437 |
| `players.current_team_id` | 当前战队 / Current team | 0 | 242 | 343 |
| `teams.country_or_region` | 战队国家或地区 / Team country or region | 0 | 23 | 65 |

开赛时间是 HLTV 比赛页显示的分钟，`scheduled_at` 采用带中欧冬夏令时偏移的 ISO 8601。下表列出本轮补录的 19 场。对照来源能确认对阵或阶段日期，ESL 公开档案只列瑞士轮阶段日期，逐场分钟仍取自 HLTV。

Published match times use the minute shown by HLTV and are stored as ISO 8601 with the Central European UTC offset. The table lists the 19 matches filled in this pass. Cross-check sources confirm the fixture or stage dates. ESL’s public archive gives the Swiss-stage window, while the individual minutes come from HLTV.

此前补录的时间也使用过 HLTV 逐图页，入库前抽样对照了比赛页。 / Earlier backfills also used the HLTV map-stats clock after sampling it against the match page. [HLTV Beijing final](https://www.hltv.org/matches/2400011/the-mongolz-vs-mouz-iem-beijing-2026) · [ESL Beijing schedule](https://pro.eslgaming.com/tour/zh/cs/beijing/eventguide/)

<details>
<summary>本轮补齐的 19 场开赛时间 / 19 start times filled in this pass</summary>

| 赛事 / Event | HLTV 对阵 / Match | 时间 / Time (CEST) | 赛程对照 / Schedule cross-check |
|---|---|---|---|
| BLAST Bounty 2026 Season 2 | [FaZe Clan vs The MongolZ](https://www.hltv.org/matches/2396016/faze-vs-the-mongolz-blast-bounty-2026-season-2-finals) | 2026-07-31 14:30 | [BLAST Bounty 官方档案 / Archive](https://blast.tv/cs/tournaments/bounty-2026-season-2/match?view=results) |
| Esports World Cup 2026 | [G2 Esports vs M80](https://www.hltv.org/matches/2396561/g2-vs-m80-esports-world-cup-2026) | 2026-08-12 14:10 | [EWC BLAST 对阵页 / Match](https://blast.tv/cs/tournaments/Esports%20World%20Cup%202026%20CS2/match/9567101d/g2-m80/matchups) |
| BLAST Open Porto 2026 | [Aurora vs DENDELE](https://www.hltv.org/matches/2396931/aurora-vs-dendele-blast-open-porto-2026) | 2026-08-28 11:00 | [BLAST Porto 官方档案 / Archive](https://blast.tv/cs/tournaments/open-2026-season-2/match) |
| BLAST Open Porto 2026 | [Vitality vs 9z](https://www.hltv.org/matches/2396935/vitality-vs-9z-blast-open-porto-2026) | 2026-08-29 11:00 | [BLAST Porto 官方档案 / Archive](https://blast.tv/cs/tournaments/open-2026-season-2/match) |
| BLAST Open Porto 2026 | [Team Spirit vs FURIA](https://www.hltv.org/matches/2396943/spirit-vs-furia-blast-open-porto-2026) | 2026-08-31 11:00 | [BLAST Porto 官方档案 / Archive](https://blast.tv/cs/tournaments/open-2026-season-2/match) |
| BLAST Open Porto 2026 | [Falcons vs G2 Esports](https://www.hltv.org/matches/2396947/falcons-vs-g2-blast-open-porto-2026) | 2026-09-04 16:00 | [BLAST Porto 官方档案 / Archive](https://blast.tv/cs/tournaments/open-2026-season-2/match) |
| ESL Pro League Season 24 | [Falcons vs TYLOO](https://www.hltv.org/matches/2398717/falcons-vs-tyloo-esl-pro-league-season-24) | 2026-10-03 11:00 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [MOUZ vs M80](https://www.hltv.org/matches/2398722/mouz-vs-m80-esl-pro-league-season-24) | 2026-10-03 17:25 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [G2 Esports vs Natus Vincere](https://www.hltv.org/matches/2398723/g2-vs-natus-vincere-esl-pro-league-season-24) | 2026-10-03 18:30 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [SHINDEN vs Legacy](https://www.hltv.org/matches/2398726/shinden-vs-legacy-esl-pro-league-season-24) | 2026-10-04 11:00 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [9z vs TYLOO](https://www.hltv.org/matches/2398727/9z-vs-tyloo-esl-pro-league-season-24) | 2026-10-04 13:30 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [Falcons vs Aurora](https://www.hltv.org/matches/2398728/falcons-vs-aurora-esl-pro-league-season-24) | 2026-10-04 14:20 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [FURIA vs MOUZ](https://www.hltv.org/matches/2398729/furia-vs-mouz-esl-pro-league-season-24) | 2026-10-04 16:25 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [BetBoom Team vs M80](https://www.hltv.org/matches/2398732/betboom-vs-m80-esl-pro-league-season-24) | 2026-10-04 19:10 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [Legacy vs 1win](https://www.hltv.org/matches/2398736/legacy-vs-1win-esl-pro-league-season-24) | 2026-10-05 13:30 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [9z vs Natus Vincere](https://www.hltv.org/matches/2398735/9z-vs-natus-vincere-esl-pro-league-season-24) | 2026-10-05 14:20 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [Team Spirit vs MOUZ](https://www.hltv.org/matches/2398737/spirit-vs-mouz-esl-pro-league-season-24) | 2026-10-05 16:25 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| ESL Pro League Season 24 | [9z vs BetBoom Team](https://www.hltv.org/matches/2398744/9z-vs-betboom-esl-pro-league-season-24) | 2026-10-06 16:30 | [ESL 官方阶段日程 / Stage schedule](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) |
| Thunderpick World Championship 2026 | [Legacy vs PARIVISION](https://www.hltv.org/matches/2399386/legacy-vs-parivision-thunderpick-world-championship-2026) | 2026-10-14 17:40 | [BLAST 播出档案 / Broadcast archive](https://blast.tv/cs/tournaments/thunderpick-world-championship-2026/match?view=results) |

</details>

阶段内数字轮次优先采用 HLTV 明示的编号。瑞士轮中可唯一确定的轮次按双方赛前胜负记录复核，要求两队同战绩、整阶段 33 场对阵齐全，并与已有编号一致。签表标签按发布的文字或通过上述校验的瑞士轮补录。 [ESL S24](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) · [PGL Astana](https://www.pglesports.com/cs2/pgl-astana-2026/) · [PGL Cluj-Napoca](https://www.pglesports.com/cs2/pgl-cluj-napoca-2026/) · [ESL Cologne Stage 3](https://pro.eslgaming.com/tour/2026/02/iem-cologne-2026-stage-3-update/)

Round numbers come from explicit HLTV labels where available. Unambiguous Swiss rounds are also checked using equal pre-match records, all 33 stage fixtures and agreement with published round numbers. Bracket labels use published text or the verified Swiss round. [ESL S24](https://pro.eslgaming.com/tour/2025/11/esl-pro-league-season-24-additional-information/) · [PGL Astana](https://www.pglesports.com/cs2/pgl-astana-2026/) · [PGL Cluj-Napoca](https://www.pglesports.com/cs2/pgl-cluj-napoca-2026/) · [ESL Cologne Stage 3](https://pro.eslgaming.com/tour/2026/02/iem-cologne-2026-stage-3-update/)

投掷次数覆盖 940 / 1,437 张地图。本轮复查了 68 张有文件名的缺图，补齐 33 张，其中 22 张核对后拼合分段录像。仍有 462 张缺录像文件名，35 张的录像比分、回合数据或选手身份尚不能完整核对。精确总伤害仍为空，当前解析 JSON 缺少逐次受伤事件，未取得可核验的原始录像。 [CS2dave](https://cs2dave.com/)

Grenade throws cover 940 of 1,437 maps. This pass rechecked 68 missing maps with replay filenames and added 33, including 22 with verified replay fragments. Another 462 lack verified filenames, and 35 still have unresolved replay or player checks. The parsed JSON lacks per-hit damage events and no verifiable raw demo was obtained, so exact damage remains NULL. [CS2dave](https://cs2dave.com/)

未通过的 35 张中，15 张未核对到完整回合，10 张的击杀、死亡无法与 HLTV 对账，10 张无法唯一确认录像中的选手身份。 / Of the 35 still unverified, 15 lacked a verifiable full set of rounds, 10 had kills and deaths that did not reconcile with HLTV, and 10 had unresolved player identities.

分段地图的 `grenades_source_url` 记录第一段。以下列出两段来源。 / For combined maps, `grenades_source_url` points to the first part. Both sources are listed below.

<details>
<summary>分段录像来源 / Replay fragments</summary>

| 比赛 ID / Match ID | 地图 / Map | 来源 / Sources |
|---:|---|---|
| 2393083 | `de_ancient` | [Part 1](https://cs2dave.com/api/demos/2393083_spirit-vs-liquid-m1-ancient-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2393083_spirit-vs-liquid-m1-ancient-p2.dem) |
| 2393086 | `de_dust2` | [Part 1](https://cs2dave.com/api/demos/2393086_b8-vs-natus-vincere-m3-dust2-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2393086_b8-vs-natus-vincere-m3-dust2-p2.dem) |
| 2393224 | `de_dust2` | [Part 1](https://cs2dave.com/api/demos/2393224_vitality-vs-g2-m3-dust2-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2393224_vitality-vs-g2-m3-dust2-p2.dem) |
| 2393224 | `de_mirage` | [Part 1](https://cs2dave.com/api/demos/2393224_vitality-vs-g2-m1-mirage-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2393224_vitality-vs-g2-m1-mirage-p2.dem) |
| 2393227 | `de_nuke` | [Part 1](https://cs2dave.com/api/demos/2393227_liquid-vs-3dmax-m1-nuke-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2393227_liquid-vs-3dmax-m1-nuke-p2.dem) |
| 2393231 | `de_ancient` | [Part 1](https://cs2dave.com/api/demos/2393231_legacy-vs-hotu-m2-ancient-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2393231_legacy-vs-hotu-m2-ancient-p2.dem) |
| 2393243 | `de_overpass` | [Part 1](https://cs2dave.com/api/demos/2393243_furia-vs-vitality-m1-overpass-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2393243_furia-vs-vitality-m1-overpass-p2.dem) |
| 2394161 | `de_ancient` | [Part 1](https://cs2dave.com/api/demos/2394161_natus-vincere-vs-gamerlegion-m2-ancient-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394161_natus-vincere-vs-gamerlegion-m2-ancient-p2.dem) |
| 2394166 | `de_nuke` | [Part 1](https://cs2dave.com/api/demos/2394166_faze-vs-vitality-m1-nuke-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394166_faze-vs-vitality-m1-nuke-p2.dem) |
| 2394168 | `de_mirage` | [Part 1](https://cs2dave.com/api/demos/2394168_gamerlegion-vs-liquid-m1-mirage-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394168_gamerlegion-vs-liquid-m1-mirage-p2.dem) |
| 2394169 | `de_dust2` | [Part 1](https://cs2dave.com/api/demos/2394169_betboom-vs-pain-m1-dust2-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394169_betboom-vs-pain-m1-dust2-p2.dem) |
| 2394864 | `de_dust2` | [Part 1](https://cs2dave.com/api/demos/2394864_nrg-vs-big-m1-dust2-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394864_nrg-vs-big-m1-dust2-p2.dem) |
| 2394869 | `de_nuke` | [Part 1](https://cs2dave.com/api/demos/2394869_legacy-vs-mibr-nuke-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394869_legacy-vs-mibr-nuke-p2.dem) |
| 2394893 | `de_mirage` | [Part 1](https://cs2dave.com/api/demos/2394893_g2-vs-big-m2-mirage-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394893_g2-vs-big-m2-mirage-p2.dem) |
| 2394905 | `de_nuke` | [Part 1](https://cs2dave.com/api/demos/2394905_mouz-vs-legacy-m2-nuke-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394905_mouz-vs-legacy-m2-nuke-p2.dem) |
| 2394973 | `de_ancient` | [Part 1](https://cs2dave.com/api/demos/2394973_fut-vs-g2-m2-ancient-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394973_fut-vs-g2-m2-ancient-p2.dem) |
| 2394984 | `de_inferno` | [Part 1](https://cs2dave.com/api/demos/2394984_parivision-vs-legacy-m1-inferno-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394984_parivision-vs-legacy-m1-inferno-p2.dem) |
| 2394991 | `de_anubis` | [Part 1](https://cs2dave.com/api/demos/2394991_natus-vincere-vs-falcons-m3-anubis-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394991_natus-vincere-vs-falcons-m3-anubis-p2.dem) |
| 2394999 | `de_anubis` | [Part 1](https://cs2dave.com/api/demos/2394999_falcons-vs-vitality-m1-anubis-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2394999_falcons-vs-vitality-m1-anubis-p2.dem) |
| 2396001 | `de_anubis` | [Part 1](https://cs2dave.com/api/demos/2396001_dendele-vs-furia-m1-anubis-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2396001_dendele-vs-furia-m1-anubis-p2.dem) |
| 2396578 | `de_inferno` | [Part 1](https://cs2dave.com/api/demos/2396578_aurora-vs-m80-m2-inferno-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2396578_aurora-vs-m80-m2-inferno-p2.dem) |
| 2399744 | `de_nuke` | [Part 1](https://cs2dave.com/api/demos/2399744_nemiga-vs-dendele-m1-nuke-p1.dem) · [Part 2](https://cs2dave.com/api/demos/2399744_nemiga-vs-dendele-m1-nuke-p2.dem) |

</details>

战队地区和当前战队使用已核实的 HLTV 旗标与 `Current lineup`。 / Team regions and current teams use verified HLTV flags and current lineups. [HLTV G2 roster](https://www.hltv.org/stats/teams/5995/g2)

## 5. 九个离线查询与详情页 / Nine offline queries and detail pages

在 `group_project` 下运行 `python app/server.py` 即可打开本地查询网页，启动步骤见 [README](README.md)。网页从 [app/queries.sql](app/queries.sql) 读取下方九条功能 SQL，并通过 Python `sqlite3` 绑定命名参数。例如 `event_id=8245` 对应北京，`match_id=2400011` 对应北京决赛。

Run `python app/server.py` from `group_project` to start the local app. See the [README](README.md) for launch steps. The app reads the nine feature queries below from [app/queries.sql](app/queries.sql) and binds named parameters through Python `sqlite3`. For example, `event_id=8245` is Beijing and `match_id=2400011` is its grand final.

在 Q1 点击赛事名称，进入该届赛事的对局（Q3）和选手榜（Q7）。点击 **View match** 进入比赛详情，再点任意已打地图，查看逐图比分（Q4）和该图双方计分板（Q9）。首次进入比赛详情默认显示第 1 图。也可从导航的 Q9 直接选比赛。

Click an event name in Q1 to see its matches (Q3) and player leaderboard (Q7). Click **View match**, then choose any played map to see the map results (Q4) and both teams' player scoreboard (Q9). Match details initially show the first map. You can also choose a series from Q9 in the navigation.

```sql
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
```

Q3 显示带中欧时区偏移的开赛时间 `scheduled_at`。赛程按公布的开赛时间排序，日期筛选使用 `match_date`。`stage` 列优先显示「阶段 · Round 数字」，其次是「阶段 · 签表标签」，两者都缺时只显示阶段。

Q3 shows `scheduled_at` with the Central European UTC offset. It sorts by start time and filters by `match_date`. The `stage` column shows the stage and numbered round when available, otherwise the stage and bracket label, or just the stage when both are missing.

Q7 的 `estimated_total_damage` 在页面标为「估算总伤害 / Estimated Total Damage」。先将有 ADR 的地图逐图计算 `ADR × 参赛回合数`，求和后取整。加权 ADR 使用取整前的伤害估计和对应的总回合数，`maps_with_reported_adr` 显示样本地图数。

Label Q7's `estimated_total_damage` as “Estimated Total Damage.” Sum `ADR × rounds played` over maps with published ADR, then round the sum to a whole number. Weighted ADR uses the unrounded sum and the corresponding total rounds. `maps_with_reported_adr` shows the number of maps used.

Q5 保留有效但无交手记录的队伍组合。Q6 的分母为有结果的地图。Q8 返回本快照无该地图记录的战队，包括期间没有比赛的战队。

Q5 preserves valid pairs without a recorded meeting. Q6 counts recorded maps. Q8 includes teams with no matches in the selected period.

Q9 用 `match_id` 和 `map_id` 查一张已打地图，显示历史代表队、选手昵称、击杀、死亡、助攻、爆头击杀、首杀、ADR、KAST 和 Rating 3.0。选手按当场代表队分组，组内按击杀数排序。以北京决赛为例，可从 IEM Beijing 2026 点进 The MongolZ 对 MOUZ，再从 Mirage 切换到 Dust2 或 Inferno。

Q9 uses `match_id` and `map_id` to fetch one played map. It shows the team represented in that match, nickname, kills, deaths, assists, headshot kills, opening kills, ADR, KAST, and Rating 3.0. The page groups players by team and sorts by kills within each team. For example, open IEM Beijing 2026, select The MongolZ vs MOUZ, and switch from Mirage to Dust2 or Inferno.

## 6. 三人分工 / Three-person split

| 成员 / Member | 负责 / Responsibility |
|---|---|
| A | ER 图、数据库约束、数据与来源验收、Q1–Q2 / ER diagram, constraints, data validation, Q1–Q2 |
| B | Q3–Q5、starter kit 接入、赛果与逐图演示 / Q3–Q5, starter-kit integration, results and map demo |
| C | Q6–Q8、统计口径、报告功能表与统计演示 / Q6–Q8, statistical definitions, feature table and stats demo |

三人共同核对报告、录制与打包。功能验收可以用 `2400011` 的地图结果和计分板，或 `2398757` 的 3:0 决赛与 Inferno 计分板。现有数据和 SQL 可以离线使用。

All three members review the report, record the video and test the submission package. Use `2400011` for a map and scoreboard demo, or `2398757` for the 3–0 series and its Inferno scoreboard. The supplied data and SQL work offline. Full player-map coverage still requires an authorized export or additional verifiable replays.
