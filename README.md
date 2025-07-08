# RIA_Data

一个 FastAPI 应用程序，旨在提供来自 RIA Wiki 的格式化数据，包括地标信息和搜索结果。

## 功能

- **地标数据 API**: 提供对零洲和后土地标数据的访问。
- **RIA Wiki 搜索 API**: 允许搜索 RIA Wiki 并检索结构化结果。

## 版本

0.3.0

## 设置

要在本地设置和运行项目，请按照以下步骤操作：

1.  **克隆仓库**：

    ```bash
    git clone https://github.com/RainC7/RIA_Data.git
    cd RIA_Data
    ```

2.  **安装依赖**：

    建议使用虚拟环境。

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # 在 Windows 上，使用 `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **获取初始数据**：

    运行数据获取脚本以填充 `data/landmark` 目录。

    ```bash
    python landmark/zth.py
    python landmark/houtu.py
    ```

## 运行应用程序

启动 FastAPI 服务器：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

应用程序将可通过 `http://localhost:8000` 访问。

## API 端点

### 地标数据

-   **获取所有地标（可选过滤）**：
    `GET /api/landmarks?source={zth|houtu}&name={可选名称}`
    -   `source`: 指定 `zth` 或 `houtu` 以从相应来源获取数据。
    -   `name`: （可选）按名称过滤地标（不区分大小写）。

-   **按 ID 获取地标**：
    `GET /api/landmarks/{landmark_id}?source={zth|houtu}`
    -   `landmark_id`: 地标的 ID。
    -   `source`: 指定 `zth` 或 `houtu`。

### RIA Wiki 搜索

-   **搜索 RIA Wiki**：
    `GET /api/wiki_search?query={搜索词}`
    -   `query`: Wiki 的搜索词。