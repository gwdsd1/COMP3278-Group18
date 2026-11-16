# CS2 Match Explorer

HKU COMP3278 · Group 18 Course Project

离线查询平台使用现有 SQLite 数据，包含 Q1–Q9。需要 **Python 3.10+** 和浏览器。安装好 Python 后即可断网运行，无需安装 Python 包。

在 `group_project` 目录打开终端运行：

```powershell
python app/server.py
```

如果系统的 Python 命令是 `python3`，用 `python3 app/server.py`。启动后在浏览器打开 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)。如果端口被占用，可以运行 `python app/server.py --port 8001` 并打开终端显示的地址。按 Ctrl+C 停止。

从导航选择任意查询，调整预填条件后点 **Run query**。Q3 显示开赛时间、阶段和可用的轮次或签表标签。Q7 的 **Estimated total damage** 按逐图 ADR 和回合数在查询时计算。

在 Q1 结果中点击赛事名称，可查看该届赛事的对局和选手榜。点击 **View match** 进入比赛详情，再点击任意已打地图可查看 Q9 双方计分板。也可以从导航的 **Q9 Map scoreboard** 直接选比赛并点击 **Open series**。

网页读取 `database/app.db`，九条功能 SQL 在 [app/queries.sql](app/queries.sql)。查询定义、统计口径和数据覆盖见[中英数据手册](CS2_Data_Guide_ZH_EN.md)。
