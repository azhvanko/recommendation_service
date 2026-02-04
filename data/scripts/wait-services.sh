#!/usr/bin/env bash

set -euo pipefail

CHECK_CLICKHOUSE=false

: "${WAIT_FOR_COMMAND_SCRIPT:=/app/data/scripts/wait-for-command.sh}"
: "${CLICKHOUSE_HOST:=clickhouse}"
: "${CLICKHOUSE_PORT:=8123}"

set +e
options=$(
  getopt -o '' \
    --l clickhouse \
    -- "$@"
)
# shellcheck disable=SC2181
[[ $? -eq 0 ]] || {
  echo "Incorrect options provided"
  exit 1
}
set -e

eval set -- "${options}"

while true; do
  case "$1" in
  --clickhouse)
    CHECK_CLICKHOUSE=true;
    shift
    ;;
  --)
    shift
    break
    ;;
  *)
    break
    ;;
  esac
done

function clickhouse_ready() {
  sh "${WAIT_FOR_COMMAND_SCRIPT}" -t 5 -c "nc -z $CLICKHOUSE_HOST $CLICKHOUSE_PORT"
}

function main() {
  if [ "${CHECK_CLICKHOUSE}" == "true" ]; then
    until clickhouse_ready; do
      echo >&2 "ClickHouse is unavailable - sleeping"
    done
    echo >&2 "ClickHouse is up - continuing..."
  fi
}

main
