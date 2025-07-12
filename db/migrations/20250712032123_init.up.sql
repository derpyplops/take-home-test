CREATE TABLE campaign_threads (
  id VARCHAR(255) NOT NULL PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status VARCHAR(255) NOT NULL DEFAULT 'not_started'
);

CREATE TABLE classifications (
  id VARCHAR(255) NOT NULL PRIMARY KEY,
  campaign_thread_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  interested_time TIMESTAMPTZ,
  call_back_time TIMESTAMPTZ,
  intent VARCHAR(255) NOT NULL DEFAULT 'voice_unknown'
);

CREATE TABLE voice_calls (
  id VARCHAR(255) NOT NULL PRIMARY KEY,
  campaign_thread_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  called_at TIMESTAMPTZ,
  status VARCHAR(255) NOT NULL DEFAULT 'queued',
  transcript TEXT NOT NULL DEFAULT '',
  time_zone TEXT NOT NULL DEFAULT 'UTC'
);
