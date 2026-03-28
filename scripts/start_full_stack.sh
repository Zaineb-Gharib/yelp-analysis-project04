#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$ROOT_DIR/.runtime"
mkdir -p "$RUNTIME_DIR"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
HIVE_HOST="${HIVE_HOST:-127.0.0.1}"
HIVE_PORT="${HIVE_PORT:-10000}"
HMS_HOST="${HMS_HOST:-127.0.0.1}"
HMS_PORT="${HMS_PORT:-9083}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"
STREAMLIT_BACKEND_URL="http://${BACKEND_HOST}:${BACKEND_PORT}"
HADOOP_HOME="${HADOOP_HOME:-/home/zineb/hadoop-3.3.6}"
HIVE_HOME="${HIVE_HOME:-/opt/hive}"

DFS_NAMENODE_PORT="${DFS_NAMENODE_PORT:-9000}"
DFS_WEB_PORT="${DFS_WEB_PORT:-9870}"
DATANODE_WEB_PORT="${DATANODE_WEB_PORT:-9864}"
YARN_RM_PORT="${YARN_RM_PORT:-8032}"
YARN_WEB_PORT="${YARN_WEB_PORT:-8088}"
YARN_NM_WEB_PORT="${YARN_NM_WEB_PORT:-8042}"

log() {
  printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"
}

port_is_listening() {
  local port="$1"
  ss -ltn "( sport = :$port )" 2>/dev/null | tail -n +2 | grep -q .
}

wait_for_port() {
  local port="$1"
  local label="$2"
  local attempts="${3:-60}"
  local sleep_sec="${4:-2}"

  for ((i = 1; i <= attempts; i++)); do
    if port_is_listening "$port"; then
      log "$label is listening on port $port"
      return 0
    fi
    sleep "$sleep_sec"
  done

  log "Timed out waiting for $label on port $port"
  return 1
}

wait_for_http() {
  local url="$1"
  local label="$2"
  local attempts="${3:-30}"
  local sleep_sec="${4:-2}"

  for ((i = 1; i <= attempts; i++)); do
    if curl --max-time 5 -fsS "$url" >/dev/null 2>&1; then
      log "$label is responding at $url"
      return 0
    fi
    sleep "$sleep_sec"
  done

  log "Timed out waiting for $label at $url"
  return 1
}

start_background() {
  local name="$1"
  local command="$2"
  local log_file="$RUNTIME_DIR/${name}.log"
  local pid_file="$RUNTIME_DIR/${name}.pid"

  log "Starting $name"
  nohup bash -lc "$command" >"$log_file" 2>&1 &
  local pid=$!
  echo "$pid" >"$pid_file"
  log "$name started with pid $pid, log: $log_file"
}

ensure_hdfs() {
  if port_is_listening "$DFS_NAMENODE_PORT"; then
    log "HDFS already appears to be running"
  else
    log "Starting HDFS via $HADOOP_HOME/sbin/start-dfs.sh"
    bash "$HADOOP_HOME/sbin/start-dfs.sh"
  fi

  wait_for_port "$DFS_NAMENODE_PORT" "NameNode"
  wait_for_port "$DFS_WEB_PORT" "NameNode web UI"
  wait_for_port "$DATANODE_WEB_PORT" "DataNode web UI"
}

ensure_yarn() {
  if port_is_listening "$YARN_RM_PORT"; then
    log "YARN already appears to be running"
  else
    log "Starting YARN via $HADOOP_HOME/sbin/start-yarn.sh"
    bash "$HADOOP_HOME/sbin/start-yarn.sh"
  fi

  wait_for_port "$YARN_RM_PORT" "ResourceManager"
  wait_for_port "$YARN_WEB_PORT" "ResourceManager web UI"
  wait_for_port "$YARN_NM_WEB_PORT" "NodeManager web UI"
}

ensure_metastore() {
  if port_is_listening "$HMS_PORT"; then
    log "Hive Metastore already appears to be running"
    return
  fi

  start_background "metastore" "unset DEBUG; exec \"$HIVE_HOME/bin/hive\" --service metastore"
  wait_for_port "$HMS_PORT" "Hive Metastore"
}

ensure_hiveserver2() {
  if port_is_listening "$HIVE_PORT"; then
    log "HiveServer2 already appears to be running"
    return
  fi

  start_background "hiveserver2" "unset DEBUG; exec \"$HIVE_HOME/bin/hiveserver2\""
  wait_for_port "$HIVE_PORT" "HiveServer2"
}

ensure_backend() {
  if port_is_listening "$BACKEND_PORT"; then
    log "Backend already appears to be running"
  else
    start_background "backend" "cd \"$ROOT_DIR\" && export PYTHONPATH=. && exec python3 hive_copilot/backend/run_backend.py"
    wait_for_port "$BACKEND_PORT" "Backend"
  fi

  wait_for_http "http://${BACKEND_HOST}:${BACKEND_PORT}/api/schema" "Backend API"
}

ensure_frontend() {
  if port_is_listening "$STREAMLIT_PORT"; then
    log "Streamlit frontend already appears to be running"
  else
    start_background "frontend" "cd \"$ROOT_DIR\" && export PYTHONPATH=. && export STREAMLIT_BACKEND_URL=\"$STREAMLIT_BACKEND_URL\" && exec streamlit run hive_copilot/frontend/app.py --server.port \"$STREAMLIT_PORT\" --server.headless true"
    wait_for_port "$STREAMLIT_PORT" "Streamlit frontend"
  fi

  wait_for_http "http://127.0.0.1:${STREAMLIT_PORT}" "Streamlit frontend"
}

verify_hive_defaults() {
  local output
  output="$(unset DEBUG; beeline -u "jdbc:hive2://${HIVE_HOST}:${HIVE_PORT}/${HIVE_DATABASE:-default}" --silent=true --showHeader=true --outputformat=csv2 -e 'set hive.execution.engine;' 2>/dev/null || true)"
  if grep -q 'hive.execution.engine=tez' <<<"$output"; then
    log "Verified Hive default execution engine is tez"
  else
    log "Warning: could not verify Hive default execution engine as tez"
  fi
}

main() {
  log "Runtime logs will be written under $RUNTIME_DIR"
  ensure_hdfs
  ensure_yarn
  ensure_metastore
  ensure_hiveserver2
  verify_hive_defaults
  ensure_backend
  ensure_frontend

  cat <<EOF

Stack is ready.

Frontend: http://127.0.0.1:${STREAMLIT_PORT}
Backend:  http://${BACKEND_HOST}:${BACKEND_PORT}
Hive:     jdbc:hive2://${HIVE_HOST}:${HIVE_PORT}/${HIVE_DATABASE:-default}
Metastore thrift: thrift://${HMS_HOST}:${HMS_PORT}

Logs:
  $RUNTIME_DIR/metastore.log
  $RUNTIME_DIR/hiveserver2.log
  $RUNTIME_DIR/backend.log
  $RUNTIME_DIR/frontend.log
EOF
}

main "$@"
