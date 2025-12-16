# CHANGELOG

## 未发布

### Added

-   新增 `/api/railways`，提供按服务器划分的铁路网系统数据。
-   统一 `server` 查询参数（兼容旧 `source`），支持 `zth`、`naraku`、`houtu` 三个服务器。
-   前端首页升级为“莉亚统一数据开放共享平台”，新增铁路网展示模块。

### Changed

-   `data/landmark/` 与新建的 `data/railway/` 目录根据服务器读取数据，地标 ID 支持字符串。

## 0.3.0 - 2025-07-08

### Added

-   New API endpoint `/api/wiki_search` for searching RIA Wiki content.
-   `wiki/wiki_search_parser.py` for parsing RIA Wiki search results.

### Changed

-   Renamed project to `RIA_Data`.
-   Updated `static/index.html` title to "莉亚格式化数据服务".
-   Modified `main.py` to support both ZTH and Houtu landmark data via `source` query parameter.
-   Moved `zth.json` generation and reading to `data/landmark/zth.json`.
-   Updated GitHub Action (`.github/workflows/deploy.yml`) to fetch both ZTH and Houtu data and commit changes to `data/landmark/`.
-   Refactored `main.py` to load landmark data directly from JSON files instead of importing variables from `landmark/zth.py` and `landmark/houtu.py`.

### Fixed

-   Corrected `ImportError` in `main.py` by changing data loading mechanism.
