-- NASA Earth Trend Detective - MySQL schema (ham veri depolama)
-- Veritabanı adı kullanıcı tarafından belirlenebilir; örnek: sayriks_earth_trend_detective

CREATE DATABASE IF NOT EXISTS sayriks_earth_trend_detective
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sayriks_earth_trend_detective;

CREATE TABLE IF NOT EXISTS locations (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(191) NOT NULL,
  country VARCHAR(128) NULL,
  location_type VARCHAR(32) NULL, -- capital/city/custom/grid
  lat DECIMAL(10,6) NOT NULL,
  lon DECIMAL(10,6) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_location (name, lat, lon)
);

CREATE TABLE IF NOT EXISTS nasa_power_raw (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  location_id BIGINT UNSIGNED NULL,
  source VARCHAR(64) NOT NULL DEFAULT 'NASA_POWER',
  parameter VARCHAR(64) NOT NULL,
  community VARCHAR(16) NOT NULL DEFAULT 'RE',
  temporal VARCHAR(16) NOT NULL DEFAULT 'daily',
  date DATE NOT NULL,
  value DOUBLE NULL,
  unit VARCHAR(64) NULL,
  lat DECIMAL(10,6) NOT NULL,
  lon DECIMAL(10,6) NOT NULL,
  start_date DATE NULL,
  end_date DATE NULL,
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  quality_flag VARCHAR(32) NULL,
  KEY idx_param_date (parameter, date),
  KEY idx_loc_param_date (lat, lon, parameter, date),
  KEY idx_location_id (location_id),
  CONSTRAINT fk_nasa_location FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS worldbank_indicator_raw (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  country_code VARCHAR(8) NOT NULL,
  country_name VARCHAR(128) NULL,
  indicator_code VARCHAR(64) NOT NULL,
  indicator_name VARCHAR(255) NULL,
  year INT NOT NULL,
  value DOUBLE NULL,
  source VARCHAR(64) NOT NULL DEFAULT 'WorldBank',
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_wb (country_code, indicator_code, year)
);

CREATE TABLE IF NOT EXISTS analysis_results (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  location_id BIGINT UNSIGNED NULL,
  parameter VARCHAR(64) NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  resolution VARCHAR(16) NOT NULL, -- daily/monthly
  n_obs INT NULL,
  mean_val DOUBLE NULL,
  min_val DOUBLE NULL,
  max_val DOUBLE NULL,
  std_val DOUBLE NULL,
  slope_per_year DOUBLE NULL,
  slope_per_decade DOUBLE NULL,
  slope_ci95_decade DOUBLE NULL,
  r_squared DOUBLE NULL,
  p_value DOUBLE NULL,
  mk_p_value DOUBLE NULL,
  mk_trend VARCHAR(64) NULL,
  significance VARCHAR(255) NULL,
  source VARCHAR(64) NULL,
  computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  KEY idx_analysis_loc_param (location_id, parameter, period_start, period_end)
);
