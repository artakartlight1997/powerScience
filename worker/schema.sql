-- ============================================================
-- Power BI Mastery — アクセス/学習ログ用スキーマ (Cloudflare D1 / SQLite)
-- IPアドレスは保存しません。国・地域は Cloudflare がリクエストに付与する
-- 位置情報メタデータ(request.cf)から取得します。
-- ============================================================

CREATE TABLE IF NOT EXISTS events (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  ts         INTEGER NOT NULL,          -- epoch ms (サーバ受信時刻)
  day        TEXT    NOT NULL,          -- YYYY-MM-DD (UTC)
  hour       INTEGER NOT NULL,          -- 0-23 (UTC)
  event      TEXT    NOT NULL,          -- pageview / heartbeat / leave / lesson_complete / quiz_result ...
  vid        TEXT,                      -- 端末ごとの匿名ID
  sid        TEXT,                      -- セッションID
  page       TEXT,                      -- index.html など
  path       TEXT,
  title      TEXT,
  ref        TEXT,                      -- リファラ(オリジンのみ)
  country    TEXT,                      -- JP, US ...
  region     TEXT,                      -- 都道府県/州
  city       TEXT,
  continent  TEXT,
  colo       TEXT,                      -- 最寄りのCloudflareデータセンター
  tz         TEXT,                      -- ブラウザのタイムゾーン
  lang       TEXT,
  mobile     INTEGER,                   -- 1 = スマホ幅
  screen     TEXT,
  browser    TEXT,
  os         TEXT,
  lesson     TEXT,
  quiz       TEXT,
  score      INTEGER,
  seconds    INTEGER,
  meta       TEXT                       -- 追加情報(JSON)
);

CREATE INDEX IF NOT EXISTS idx_events_day     ON events(day);
CREATE INDEX IF NOT EXISTS idx_events_ts      ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_event   ON events(event);
CREATE INDEX IF NOT EXISTS idx_events_country ON events(country);
CREATE INDEX IF NOT EXISTS idx_events_page    ON events(page);
CREATE INDEX IF NOT EXISTS idx_events_vid     ON events(vid);
