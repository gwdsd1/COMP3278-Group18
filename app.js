"use strict";

const main = document.querySelector("main");
const navigation = document.querySelector("nav");
const escapeHtml = (value) => String(value ?? "—").replace(/[&<>"']/g, (char) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);

function urlFor(params, anchor = "") {
    return `?${new URLSearchParams(params)}${anchor ? "#" + anchor : ""}`;
}

function link(title, params, { anchor, className, label, current } = {}) {
    return `<a data-route href="${escapeHtml(urlFor(params, anchor))}"${className ? ` class="${className}"` : ""}
        ${label ? ` aria-label="${escapeHtml(label)}"` : ""}${current ? ' aria-current="true"' : ""}>${escapeHtml(title)}</a>`;
}

const eventLink = (row) => link(row.name, { event: row.event_id });
const matchLink = (row) => link("View match", { match: row.match_id }, {
    className: "match-action", label: `View match: ${row.team1} vs ${row.team2}, ${row.match_date}`,
});
const mapLink = (row, match, selected) => link(row.map, { match, map: row.map_id }, {
    anchor: "scoreboard", current: row.map_id === selected,
});

async function loadAsset(name, type) {
    const response = await fetch(new URL(name, document.baseURI));
    if (!response.ok) throw new Error(`Couldn't load ${name} (${response.status}).`);
    return response[type]();
}

async function start() {
    const [SQL, snapshot, sqlText, config] = await Promise.all([
        initSqlJs({ locateFile: (file) => new URL(file, document.baseURI).href }),
        loadAsset("app.db", "arrayBuffer"),
        loadAsset("queries.sql", "text"),
        loadAsset("config.json", "json"),
    ]);
    const db = new SQL.Database(new Uint8Array(snapshot));
    db.run("PRAGMA query_only = ON");
    const blocks = sqlText.split(/^-- (Q[1-9]|event_detail|match_detail):[^\n]*\n/gm);
    const queries = {};
    for (let i = 1; i < blocks.length; i += 2) queries[blocks[i]] = blocks[i + 1];
    const { FEATURES, FIELDS, OPTIONS, COLUMN_NAMES, NOTES } = config;

    function select(sql, params = {}) {
        const bound = Object.fromEntries(Object.entries(params).map(([name, value]) => [`:${name}`, value]));
        const [result] = db.exec(sql, bound);
        if (!result) return { columns: [], rows: [] };
        const { columns, values } = result;
        const rows = values.map((row) => Object.fromEntries(columns.map((column, i) => [column, row[i]])));
        return { columns, rows };
    }

    const run = (name, params) => select(queries[name], params);
    const options = Object.fromEntries(Object.entries(OPTIONS).map(([kind, sql]) =>
        [kind, select(sql).rows.map((row) => Object.values(row))]));
    const [dates] = select("SELECT MIN(start_date) AS first, MAX(end_date) AS last FROM events").rows;
    const [recent] = select(`SELECT team1_id, team2_id FROM matches
        ORDER BY COALESCE(datetime(scheduled_at), datetime(match_date)) DESC, match_id DESC LIMIT 1`).rows;
    const defaults = {
        from_date: dates.first, to_date: dates.last, min_prize: 0, min_maps: 1,
        team_id: recent.team1_id, team_a: recent.team1_id, team_b: recent.team2_id,
        event_id: options.event[0][0], map_id: options.map[0][0], match_id: options.match[0][0],
    };

    function table(result, { links = {}, hidden = [], label = "Query results" } = {}) {
        if (!result.rows.length) return '<p class="feedback" role="status">No results for these filters.</p>';
        let columns = result.columns.filter((name) => !hidden.includes(name));
        const matchList = Boolean(links.match_id);
        if (matchList) {
            const leading = ["match_id", "team1", "team2"];
            columns = [...leading, ...columns.filter((name) => !leading.includes(name))];
        }
        const heads = columns.map((name) => {
            const text = COLUMN_NAMES[name] ?? name[0].toUpperCase() + name.slice(1).replaceAll("_", " ");
            return `<th scope="col">${escapeHtml(text)}</th>`;
        }).join("");
        const body = result.rows.map((row) => `<tr>${columns.map((name) =>
            `<td>${links[name] ? links[name](row) : escapeHtml(row[name])}</td>`).join("")}</tr>`).join("");
        const count = result.rows.length;
        return `<p class="row-count" role="status">${count.toLocaleString("en-US")} ${count === 1 ? "result" : "results"}</p>
            <div class="results" role="region" aria-label="${escapeHtml(label)}" tabindex="0">
            <table${matchList ? ' class="match-list"' : ""}><thead><tr>${heads}</tr></thead><tbody>${body}</tbody></table></div>`;
    }

    function show(title, content, active) {
        document.title = `${title} | CS2 Match Explorer`;
        navigation.innerHTML = FEATURES.map(([name], i) => `<a data-route href="${urlFor({ q: i + 1 })}"
            ${i + 1 === active ? 'aria-current="page"' : ""}><span>Q${i + 1}</span> ${escapeHtml(name)}</a>`).join("");
        main.innerHTML = content;
    }

    function home() {
        const [counts] = select(`SELECT (SELECT COUNT(*) FROM events) AS Events,
            (SELECT COUNT(*) FROM matches) AS Series, (SELECT COUNT(*) FROM match_maps) AS Maps,
            (SELECT COUNT(*) FROM player_map_stats) AS "Player-map records"`).rows;
        const stats = Object.entries(counts).map(([name, count]) =>
            `<div><dt>${name}</dt><dd>${count.toLocaleString("en-US")}</dd></div>`).join("");
        const cards = FEATURES.map(([name, description], i) => `<a data-route class="card" href="${urlFor({ q: i + 1 })}">
            <span class="query-id">Q${i + 1}</span><h2>${escapeHtml(name)}</h2><p>${escapeHtml(description)}</p></a>`).join("");
        show("Queries", `<h1>CS2 Match Explorer</h1><dl class="stats">${stats}</dl><div class="cards">${cards}</div>`);
    }

    function eventPage(id) {
        const [event] = run("event_detail", { event_id: id }).rows;
        if (!event) return show("Event not found", "<h1>Event not found</h1>");
        const games = run("Q3", { event_id: id, from_date: event.start_date, to_date: event.end_date });
        const leaderboard = run("Q7", { event_id: id, min_maps: 1 });
        const prize = event.prize_pool == null ? "" : ` · $${event.prize_pool.toLocaleString("en-US")} prize pool`;
        show(event.name, `
            <p class="breadcrumb">${link("Find events", { q: 1, run: 1 })}</p><h1>${escapeHtml(event.name)}</h1>
            <p class="intro">${escapeHtml(`${event.start_date} to ${event.end_date} · ${event.location}${prize}`)}</p>
            <div class="section-links"><a href="#matches">Matches</a><a href="#players">Player leaderboard</a></div>
            <section id="matches"><h2>Matches</h2>${table(games, { links: { match_id: matchLink }, label: "Event matches" })}</section>
            <section id="players"><h2>Player leaderboard</h2><p class="note">${escapeHtml(NOTES[7])}</p>
            ${table(leaderboard, { label: "Event player leaderboard" })}</section>`, 1);
    }

    function matchPage(id, mapId) {
        const [match] = run("match_detail", { match_id: id }).rows;
        if (!match) return show("Match not found", "<h1>Match not found</h1>", 9);
        const maps = run("Q4", { match_id: id });
        const selected = mapId == null ? maps.rows[0] : maps.rows.find((row) => row.map_id === mapId);
        if (mapId != null && !selected) return show("Map not found", "<h1>Map not found in this match</h1>", 9);
        const title = `${match.team1} vs ${match.team2}`;
        const details = [match.scheduled_at, match.stage, match.best_of ? `BO${match.best_of}` : null,
            match.status[0].toUpperCase() + match.status.slice(1)].filter(Boolean).join(" · ");
        const score = match.team1_map_wins == null || match.team2_map_wins == null ? "" :
            `<p class="series-score">${match.team1_map_wins}–${match.team2_map_wins} <span>Series score</span></p>`;
        const header = `<p class="breadcrumb">${link(match.event_name, { event: match.event_id }, { anchor: "matches" })}</p>
            <h1>${escapeHtml(title)}</h1><p class="intro">${escapeHtml(details)}</p>${score}`;
        if (!selected) return show(title, header + '<p class="feedback">No map results recorded for this series.</p>', 9);
        const board = run("Q9", { match_id: id, map_id: selected.map_id });
        const teams = [match.team1, match.team2].map((team) => `<h3>${escapeHtml(team)}</h3>${table(
            { columns: board.columns, rows: board.rows.filter((row) => row.team === team) },
            { hidden: ["team"], label: `${team} player stats` }
        )}`).join("");
        show(title, `${header}<section><h2>Played maps</h2>${table(maps, {
            links: { map: (row) => mapLink(row, id, selected.map_id) }, hidden: ["map_id"], label: "Played maps",
        })}</section><section id="scoreboard"><h2>${escapeHtml(selected.map)} player scoreboard</h2>${teams}</section>`, 9);
    }

    function readFilters(keys, filters) {
        const params = {};
        for (const key of keys) {
            const [label, kind] = FIELDS[key];
            const value = filters[key];
            if (kind === "date") {
                const checked = new Date(`${value}T00:00:00Z`);
                if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || Number.isNaN(checked.getTime()) || checked.toISOString().slice(0, 10) !== value) {
                    throw new Error(`${label} must be a valid date.`);
                }
                params[key] = value;
            } else if (kind === "number") {
                const min = key === "min_maps" ? 1 : 0;
                const number = Number(value);
                if (!/^\d+$/.test(value) || !Number.isSafeInteger(number) || number < min) {
                    throw new Error(`${label} must be a whole number of at least ${min}.`);
                }
                params[key] = number;
            } else {
                const choice = options[kind].find(([id]) => String(id) === value);
                if (!choice) throw new Error(`Choose a valid value for ${label}.`);
                params[key] = choice[0];
            }
        }
        if (params.from_date > params.to_date) throw new Error("From date must be on or before To date.");
        if ("team_a" in params && params.team_a === params.team_b) throw new Error("Choose two different teams.");
        return params;
    }

    function feature(number, route) {
        const [title, description, fields] = FEATURES[number - 1];
        const submitted = route.get("run") === "1";
        const filters = Object.fromEntries(fields.map((key) => [
            key, submitted ? (route.get(key) ?? String(defaults[key])) : String(defaults[key]),
        ]));
        const controls = fields.map((key) => {
            const [label, kind] = FIELDS[key];
            const value = filters[key];
            const choices = options[kind];
            const input = choices ? `<select id="${key}" name="${key}" required>${choices.map(([id, name]) =>
                `<option value="${id}"${String(id) === value ? " selected" : ""}>${escapeHtml(name)}</option>`).join("")}</select>` :
                `<input id="${key}" name="${key}" type="${kind}" value="${escapeHtml(value)}"
                  ${kind === "number" ? `min="${key === "min_maps" ? 1 : 0}" step="1"` : ""} required>`;
            return `<div class="field"><label for="${key}">${escapeHtml(label)}</label>${input}</div>`;
        }).join("");
        let results = "";
        if (submitted) {
            let params;
            try {
                params = readFilters(fields, filters);
            } catch (error) {
                results = `<p class="feedback error" role="alert">${escapeHtml(error.message)}</p>`;
            }
            if (params) {
                if (number === 9) return matchPage(params.match_id);
                const links = { 1: { name: eventLink }, 3: { match_id: matchLink },
                    4: { map: (row) => mapLink(row, params.match_id) } };
                results = table(run(`Q${number}`, params), { links: links[number], hidden: number === 4 ? ["map_id"] : [] });
            }
        }
        show(title, `<span class="query-id">Q${number}</span><h1>${escapeHtml(title)}</h1>
            <p class="intro">${escapeHtml(description)}</p><form class="filters" method="get">
            <input type="hidden" name="q" value="${number}"><input type="hidden" name="run" value="1">${controls}
            <button type="submit">${number === 9 ? "Open series" : "Run query"}</button></form>
            ${NOTES[number] ? `<p class="note">${escapeHtml(NOTES[number])}</p>` : ""}${results}`, number);
    }

    function render() {
        const route = new URLSearchParams(location.search);
        const id = (key) => {
            const value = route.get(key);
            return value != null && /^\d{1,15}$/.test(value) ? Number(value) : -1;
        };
        if (route.has("event")) eventPage(id("event"));
        else if (route.has("match")) matchPage(id("match"), route.has("map") ? id("map") : null);
        else if (!route.has("q")) home();
        else if (id("q") >= 1 && id("q") <= FEATURES.length) feature(id("q"), route);
        else show("Query not found", "<h1>Query not found</h1>");

        const anchor = document.getElementById(location.hash.slice(1));
        if (anchor) anchor.scrollIntoView();
        else window.scrollTo(0, 0);
    }

    function navigate(href) {
        history.pushState(null, "", href);
        render();
    }

    document.addEventListener("click", (event) => {
        const target = event.target.closest("a[data-route]");
        if (!target || event.button !== 0 || event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
        event.preventDefault();
        navigate(target.href);
    });
    main.addEventListener("submit", (event) => {
        event.preventDefault();
        navigate(urlFor(new FormData(event.target)));
    });
    window.addEventListener("popstate", render);
    render();
}

start().catch((error) => {
    main.innerHTML = `<h1>CS2 Match Explorer</h1><p class="feedback error" role="alert">${escapeHtml(error.message)}</p>`;
});
