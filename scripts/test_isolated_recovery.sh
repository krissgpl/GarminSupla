#!/usr/bin/env bash
# Synthetic, isolated GarminSupla file + Caddy volume recovery test.
# Never uses production archives or production Docker volumes.

set -euo pipefail
umask 077

if [ "$#" -ne 1 ] || [ "$1" != "--confirm-synthetic" ]; then
  echo "ERROR: --confirm-synthetic is required" >&2
  exit 2
fi

cd /opt/garminsupla

test -f scripts/create_backup.py
test -f scripts/restore_file_backup.py
test -f scripts/create_caddy_volume_backup.py
test -f scripts/restore_caddy_volumes.py

scratch="$(mktemp -d /tmp/gsrecovery06b1.XXXXXXXX)"
nonce="$(python3 -c 'import secrets; print(secrets.token_hex(8))')"

source_project="gsfixture${nonce}"
target_project="gsrestore${nonce}"

shorts=(
  garminsupla_caddy_data
  garminsupla_caddy_config
)

preflight_passed=0

owned() {
  local volume="$1"
  local project="$2"
  local kind="$3"
  local short="$4"

  docker volume inspect "$volume" |
    python3 -c '
import json
import re
import sys

name, project, kind, short, nonce = sys.argv[1:]

try:
    entries = json.load(sys.stdin)
    info = entries[0]
    labels = info.get("Labels") or {}

    valid = (
        len(entries) == 1
        and info.get("Name") == name
        and info.get("Driver") == "local"
        and info.get("Scope") == "local"
        and info.get("Options") in (None, {})
        and labels.get("com.docker.compose.project") == project
        and labels.get("com.docker.compose.volume") == short
    )

    if kind == "source":
        valid = valid and (
            labels.get("org.garminsupla.recovery-fixture")
            == nonce
        )
    else:
        valid = valid and bool(
            re.fullmatch(
                r"[0-9a-f]{32}",
                labels.get("org.garminsupla.restore-token", ""),
            )
        )

except (ValueError, IndexError, TypeError, AttributeError):
    valid = False

sys.exit(0 if valid else 1)
' "$volume" "$project" "$kind" "$short" "$nonce"
}

cleanup() {
  local rc=$?
  local cleanup_failed=0
  trap - EXIT
  set +e

  echo "=== Sprzątanie izolowanych zasobów ==="

  if [ "$preflight_passed" -eq 1 ]; then
    for project in "$target_project" "$source_project"; do
      for short in "${shorts[@]}"; do
        volume="${project}_${short}"

        if ! docker volume inspect "$volume" >/dev/null 2>&1; then
          continue
        fi

        kind="source"
        if [ "$project" = "$target_project" ]; then
          kind="target"
        fi

        if ! owned "$volume" "$project" "$kind" "$short"; then
          echo "ERROR: unverified volume ownership: $volume"
          cleanup_failed=1
          continue
        fi

        if ! docker volume rm "$volume" >/dev/null; then
          echo "ERROR: failed to remove volume: $volume"
          cleanup_failed=1
        fi
      done
    done
  fi

  case "$scratch" in
    /tmp/gsrecovery06b1.*)
      if [ -d "$scratch" ] && [ ! -L "$scratch" ]; then
        rm -rf -- "$scratch" || cleanup_failed=1
      fi
      ;;
    *)
      echo "ERROR: unsafe temporary directory"
      cleanup_failed=1
      ;;
  esac

  if [ "$cleanup_failed" -eq 0 ]; then
    echo "OK: synthetic resources cleaned"
  else
    echo "ERROR: incomplete cleanup"
    echo "Projects: $source_project / $target_project"
    rc=1
  fi

  if [ "$rc" -ne 0 ]; then
    echo "ERROR: isolated recovery test failed"
  fi

  exit "$rc"
}

trap cleanup EXIT

echo "=== 1. Kontrola izolacji ==="

image_ref="$(
  docker compose images -q garminsupla-api |
    head -n 1
)"

test -n "$image_ref"

image="$(
  docker image inspect --format '{{.Id}}' "$image_ref"
)"

[[ "$image" =~ ^sha256:[0-9a-f]{64}$ ]]

for project in "$source_project" "$target_project"; do
  for short in "${shorts[@]}"; do
    if docker volume inspect "${project}_${short}" \
      >/dev/null 2>&1; then
      echo "ERROR: fixture volume already exists"
      exit 1
    fi
  done

  test -z "$(
    docker ps -a -q \
      --filter "label=com.docker.compose.project=$project"
  )"

  test -z "$(
    docker network ls --format '{{.Name}}' \
      --filter "label=com.docker.compose.project=$project"
  )"
done

preflight_passed=1
echo "OK: isolated project names available"

echo "=== 2. Syntetyczny backup plików ==="

mkdir -m 700 "$scratch/archives"
mkdir -m 700 "$scratch/restores"

PYTHONDONTWRITEBYTECODE=1 python3 -B - "$scratch" <<'PY'
import sys
from pathlib import Path

from scripts.create_backup import FILES, create_backup

base = Path(sys.argv[1])
root = base / "installation"
certs = base / "certificates"

names = list(FILES) + [
    "certs/fullchain.pem",
    "certs/private.key",
    "data/pairing.json",
    "deploy/caddy/secrets/nested/token",
]

for name in names:
    path = (
        certs / name.removeprefix("certs/")
        if name.startswith("certs/")
        else root / name
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"synthetic:" + name.encode())
    path.chmod(0o600)

for name in (
    "deploy/caddy/secrets",
    "deploy/caddy/secrets/nested",
):
    (root / name).chmod(0o700)

create_backup(
    root,
    certs,
    base / "archives/files.tar.gz",
    check_offline=False,
)

print("OK: synthetic file archive created")
PY

echo "=== 3. Syntetyczne wolumeny ==="

for short in "${shorts[@]}"; do
  volume="${source_project}_${short}"

  docker volume create \
    --driver local \
    --label "com.docker.compose.project=$source_project" \
    --label "com.docker.compose.volume=$short" \
    --label "org.garminsupla.recovery-fixture=$nonce" \
    "$volume" >/dev/null

  owned "$volume" "$source_project" source "$short"

  docker run --rm \
    --pull never \
    --network none \
    --read-only \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --user 0:0 \
    --mount "type=volume,source=$volume,target=/fixture,volume-nocopy" \
    --entrypoint python \
    "$image" -B -S -c '
from pathlib import Path
import sys

root = Path("/fixture")
short = sys.argv[1]
nested = root / "nested"

nested.mkdir(mode=0o700)
(nested / "empty").mkdir(mode=0o700)

file = nested / "state.txt"
file.write_bytes(b"synthetic:" + short.encode())
file.chmod(0o600)
' "$short"

  echo "OK: synthetic volume $short"
done

PYTHONDONTWRITEBYTECODE=1 \
python3 -B -m scripts.create_caddy_volume_backup \
  --project "$source_project" \
  --image "$image" \
  --root "$scratch/installation" \
  --cert-dir "$scratch/certificates" \
  --output "$scratch/archives/volumes.tar.gz" \
  --confirm-stopped

echo "=== 4. Weryfikacja archiwów ==="

files_archive="$scratch/archives/files.tar.gz"
volumes_archive="$scratch/archives/volumes.tar.gz"

PYTHONDONTWRITEBYTECODE=1 \
python3 -B -m scripts.verify_file_backup \
  --archive "$files_archive"

PYTHONDONTWRITEBYTECODE=1 \
python3 -B -m scripts.verify_caddy_volume_backup \
  --archive "$volumes_archive" \
  --project "$source_project"

files_sha="$(sha256sum "$files_archive" | awk '{print $1}')"
volumes_sha="$(sha256sum "$volumes_archive" | awk '{print $1}')"

echo "OK: both archives verified"

echo "=== 5. Odtwarzanie ==="

target="$scratch/restores/$target_project"

PYTHONDONTWRITEBYTECODE=1 \
python3 -B -m scripts.restore_file_backup \
  --archive "$files_archive" \
  --target "$target" \
  --confirm-isolated

PYTHONDONTWRITEBYTECODE=1 \
python3 -B -m scripts.restore_caddy_volumes \
  --archive "$volumes_archive" \
  --source-project "$source_project" \
  --target-project "$target_project" \
  --image "$image" \
  --confirm-isolated

echo "=== 6. Niezależna kontrola plików ==="

PYTHONDONTWRITEBYTECODE=1 python3 -B - "$scratch" "$target_project" <<'PY'
import stat
import sys
from pathlib import Path

from scripts.create_backup import FILES

base = Path(sys.argv[1])
target = base / "restores" / sys.argv[2]
root = base / "installation"
certs = base / "certificates"

names = list(FILES) + [
    "certs/fullchain.pem",
    "certs/private.key",
    "data/pairing.json",
    "deploy/caddy/secrets/nested/token",
]

for name in names:
    original = (
        certs / name.removeprefix("certs/")
        if name.startswith("certs/")
        else root / name
    )

    restored = target / name

    assert restored.read_bytes() == original.read_bytes()
    assert not restored.is_symlink()
    assert stat.S_IMODE(restored.stat().st_mode) == 0o600

for directory in (
    target,
    target / "data",
    target / "certs",
    target / "deploy",
    target / "deploy/caddy",
    target / "deploy/caddy/secrets",
    target / "deploy/caddy/secrets/nested",
):
    assert stat.S_IMODE(directory.stat().st_mode) == 0o700

assert len(names) == 9
assert not (target / "manifest.json").exists()

print("OK: all 9 restored files match")
PY

echo "=== 7. Niezależna kontrola wolumenów ==="

for short in "${shorts[@]}"; do
  volume="${target_project}_${short}"

  owned "$volume" "$target_project" target "$short"

  docker run --rm \
    --pull never \
    --network none \
    --read-only \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --user 0:0 \
    --mount "type=volume,source=$volume,target=/check,readonly,volume-nocopy" \
    --entrypoint python \
    "$image" -B -S -c '
import stat
import sys
from pathlib import Path

root = Path("/check")
short = sys.argv[1]
nested = root / "nested"
file = nested / "state.txt"
empty = nested / "empty"

assert file.read_bytes() == b"synthetic:" + short.encode()
assert stat.S_IMODE(file.stat().st_mode) == 0o600
assert stat.S_IMODE(nested.stat().st_mode) == 0o700
assert empty.is_dir()
assert stat.S_IMODE(empty.stat().st_mode) == 0o700
assert sorted(p.name for p in root.iterdir()) == ["nested"]
' "$short"

  echo "OK: restored volume $short"
done

echo "=== 8. Ochrona przed nadpisywaniem ==="

if PYTHONDONTWRITEBYTECODE=1 \
python3 -B -m scripts.restore_file_backup \
  --archive "$files_archive" \
  --target "$target" \
  --confirm-isolated \
  >"$scratch/file-duplicate.log" 2>&1; then
  echo "ERROR: file restore accepted existing target"
  exit 1
fi

grep -Fq \
  "Restore target already exists" \
  "$scratch/file-duplicate.log"

if PYTHONDONTWRITEBYTECODE=1 \
python3 -B -m scripts.restore_caddy_volumes \
  --archive "$volumes_archive" \
  --source-project "$source_project" \
  --target-project "$target_project" \
  --image "$image" \
  --confirm-isolated \
  >"$scratch/volume-duplicate.log" 2>&1; then
  echo "ERROR: volume restore accepted existing target"
  exit 1
fi

grep -Fq \
  "Restore target volume already exists" \
  "$scratch/volume-duplicate.log"

echo "OK: both restore mechanisms reject existing targets"

echo "=== 9. Kontrola końcowa ==="

test "$files_sha" = "$(
  sha256sum "$files_archive" | awk '{print $1}'
)"

test "$volumes_sha" = "$(
  sha256sum "$volumes_archive" | awk '{print $1}'
)"

echo "OK: original archives unchanged"
echo "OK: synthetic isolated recovery PASS"
