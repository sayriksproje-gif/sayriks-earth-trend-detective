-- NASA Earth Trend Detective - SQLite schema (açık kaynak/ücretsiz, yerel)

PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  country TEXT,
  location_type TEXT,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(name, lat, lon)
);

CREATE TABLE IF NOT EXISTS nasa_power_raw (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  location_id INTEGER,
  source TEXT NOT NULL DEFAULT 'NASA_POWER',
  parameter TEXT NOT NULL,
  community TEXT NOT NULL DEFAULT 'RE',
  temporal TEXT NOT NULL DEFAULT 'daily',
  date TEXT NOT NULL,
  value REAL,
  unit TEXT,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  start_date TEXT,
  end_date TEXT,
  fetched_at TEXT DEFAULT (datetime('now')),
  quality_flag TEXT,
  FOREIGN KEY(location_id) REFERENCES locations(id)
);
CREATE INDEX IF NOT EXISTS idx_nasa_param_date ON nasa_power_raw(parameter, date);
CREATE INDEX IF NOT EXISTS idx_nasa_loc_param_date ON nasa_power_raw(lat, lon, parameter, date);

CREATE TABLE IF NOT EXISTS worldbank_indicator_raw (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  country_code TEXT NOT NULL,
  country_name TEXT,
  indicator_code TEXT NOT NULL,
  indicator_name TEXT,
  year INTEGER NOT NULL,
  value REAL,
  source TEXT NOT NULL DEFAULT 'WorldBank',
  fetched_at TEXT DEFAULT (datetime('now')),
  UNIQUE(country_code, indicator_code, year)
);
