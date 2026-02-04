#!/usr/bin/env bash

set -eo pipefail

echo -e "
CREATE TABLE IF NOT EXISTS user_events
(
  \`uid\` UInt64 CODEC(Delta, LZ4),
  \`pid\` UInt64 CODEC(Delta, LZ4),
  \`brand\` LowCardinality(String),
  \`date\` Date CODEC(Delta, ZSTD(1)),
  \`click\` UInt8 CODEC(ZSTD(1)),
  \`add_to_cart\` UInt8 CODEC(ZSTD(1)),
  \`purchase\` UInt8 CODEC(ZSTD(1))
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (uid, pid, date)
SETTINGS
  index_granularity = 8192;

ALTER TABLE user_events ADD PROJECTION user_events_global_top_projection
(
  SELECT pid, brand, sum(click), sum(add_to_cart), sum(purchase)
  GROUP BY pid, brand
);
" >>/tmp/init.sql

clickhouse-client --multiquery --host "127.0.0.1" -u "$CLICKHOUSE_USER" --password "$CLICKHOUSE_PASSWORD" \
  -d "$CLICKHOUSE_DB" </tmp/init.sql
rm -f /tmp/init.sql
