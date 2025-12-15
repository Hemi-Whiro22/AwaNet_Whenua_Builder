#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [options] RealmName

Options:
  --hostname VALUE        Cloudflare hostname (default kitenga-<realm>.example.com)
  --tunnel-id VALUE       Cloudflare Tunnel ID
  --tunnel-name VALUE     Cloudflare Tunnel name (default kitenga-<realm>)
  --pages-project VALUE   Cloudflare Pages project (default te-ao-<realm>)
  --backend-url VALUE     Public backend URL (default https://<realm>.example.com)
EOF
}

CF_HOST=""
CF_TUNNEL_ID=""
CF_TUNNEL_NAME=""
CF_PAGES_PROJECT=""
PUBLIC_BACKEND_URL=""

CF_HOST_SET=0
CF_TUNNEL_ID_SET=0
CF_TUNNEL_NAME_SET=0
CF_PAGES_PROJECT_SET=0
PUBLIC_BACKEND_URL_SET=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hostname)
      CF_HOST="$2"
      CF_HOST_SET=1
      shift 2
      ;;
    --tunnel-id)
      CF_TUNNEL_ID="$2"
      CF_TUNNEL_ID_SET=1
      shift 2
      ;;
    --tunnel-name)
      CF_TUNNEL_NAME="$2"
      CF_TUNNEL_NAME_SET=1
      shift 2
      ;;
    --pages-project)
      CF_PAGES_PROJECT="$2"
      CF_PAGES_PROJECT_SET=1
      shift 2
      ;;
    --backend-url)
      PUBLIC_BACKEND_URL="$2"
      PUBLIC_BACKEND_URL_SET=1
      shift 2
      ;;
    --help)
      usage
      exit 0
      ;;
    --*)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

REALM="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${ROOT_DIR}/.env.template" "${ENV_FILE}"
fi

slug=$(echo "${REALM}" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

CF_HOST=${CF_HOST:-"kitenga-${slug}.example.com"}
CF_TUNNEL_NAME=${CF_TUNNEL_NAME:-"kitenga-${slug}"}
CF_PAGES_PROJECT=${CF_PAGES_PROJECT:-"te-ao-${slug}"}
PUBLIC_BACKEND_URL=${PUBLIC_BACKEND_URL:-"https://${slug}.example.com"}

if [[ -z "${CF_TUNNEL_ID}" ]]; then
  read -rp "Cloudflare Tunnel ID: " CF_TUNNEL_ID
else
  echo "Using Cloudflare Tunnel ID: ${CF_TUNNEL_ID}"
fi

if [[ ${CF_HOST_SET} -eq 0 ]]; then
  read -rp "Cloudflare hostname [${CF_HOST}]: " input
  CF_HOST=${input:-$CF_HOST}
else
  echo "Using Cloudflare hostname: ${CF_HOST}"
fi

if [[ ${CF_TUNNEL_NAME_SET} -eq 0 ]]; then
  read -rp "Cloudflare Tunnel name [${CF_TUNNEL_NAME}]: " input
  CF_TUNNEL_NAME=${input:-$CF_TUNNEL_NAME}
else
  echo "Using Cloudflare Tunnel name: ${CF_TUNNEL_NAME}"
fi

if [[ ${CF_PAGES_PROJECT_SET} -eq 0 ]]; then
  read -rp "Cloudflare Pages project [${CF_PAGES_PROJECT}]: " input
  CF_PAGES_PROJECT=${input:-$CF_PAGES_PROJECT}
else
  echo "Using Cloudflare Pages project: ${CF_PAGES_PROJECT}"
fi

if [[ ${PUBLIC_BACKEND_URL_SET} -eq 0 ]]; then
  read -rp "Public backend URL [${PUBLIC_BACKEND_URL}]: " input
  PUBLIC_BACKEND_URL=${input:-$PUBLIC_BACKEND_URL}
else
  echo "Using backend URL: ${PUBLIC_BACKEND_URL}"
fi

BEARER=$(openssl rand -hex 32)

if command -v perl >/dev/null 2>&1; then
  perl -0pi -e "s/TemplateRealm/${REALM}/g" $(grep -rl "TemplateRealm" "${ROOT_DIR}")
else
  find "${ROOT_DIR}" -type f -not -path ".git/*" -print0 | xargs -0 sed -i "s/TemplateRealm/${REALM}/g"
fi

sed -i "s|^HUMAN_BEARER_KEY=.*|HUMAN_BEARER_KEY=${BEARER}|" "${ENV_FILE}"
sed -i "s|^CF_TUNNEL_ID=.*|CF_TUNNEL_ID=${CF_TUNNEL_ID}|" "${ENV_FILE}"
sed -i "s|^CF_TUNNEL_NAME=.*|CF_TUNNEL_NAME=${CF_TUNNEL_NAME}|" "${ENV_FILE}"
sed -i "s|^CF_TUNNEL_HOSTNAME=.*|CF_TUNNEL_HOSTNAME=${CF_HOST}|" "${ENV_FILE}"
sed -i "s|^PROJECT_NAME=.*|PROJECT_NAME=${REALM}|" "${ENV_FILE}"
sed -i "s|^REALM_NAME=.*|REALM_NAME=${REALM}|" "${ENV_FILE}"

perl -0pi -e "s|kitenga-template\\.example\\.com|${CF_HOST}|g" "${ROOT_DIR}/config/proxy.toml"
perl -0pi -e "s|te-ao-template|${CF_PAGES_PROJECT}|g" "${ROOT_DIR}/config/proxy.toml"
perl -0pi -e "s|https://te-po-template\\.example\\.com|${PUBLIC_BACKEND_URL}|g" "${ROOT_DIR}/config/realm.json"
perl -0pi -e "s|projectName: .*|projectName: ${CF_PAGES_PROJECT}|g" "${ROOT_DIR}/.github/workflows/cloudflare-pages.yml"

echo "Generated bearer token for ${REALM}: ${BEARER}"
echo "Register this token and Cloudflare secrets in the primary Te Pō backend before deploying."
