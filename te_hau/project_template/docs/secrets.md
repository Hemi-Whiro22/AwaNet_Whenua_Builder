| Secret             | Local `.env` | Cloudflare Pages | Render | Source of Truth                          |
|--------------------|--------------|------------------|--------|------------------------------------------|
| HUMAN_BEARER_KEY   | ✅            | ✅ (if frontend makes API calls) | ✅ | Generated via `project_template/scripts/new_realm.sh` and registered in primary Te Pō backend |
| PIPELINE_TOKEN     | ✅            | ✅                | ✅      | Primary Te Pō `.env`                     |
| SUPABASE_URL       | ✅            | ✅                | ✅      | Supabase dashboard / secrets manager     |
| SUPABASE_ANON_KEY  | ✅            | ✅                | ✅      | Supabase dashboard                       |
| SUPABASE_SERVICE_ROLE_KEY | ✅      | ❌                | ✅      | Supabase dashboard                       |
| OPENAI_API_KEY     | ✅            | ❌                | ✅      | Secrets manager                          |
| OPENAI_ADMIN_KEY   | ✅            | ❌                | ✅      | Secrets manager                          |
| OPENAI_ORG_ID      | ✅            | ❌                | ✅      | Secrets manager                          |
| CLOUDFLARE_API_TOKEN | ❌           | ✅                | ❌      | Cloudflare dashboard (store as GitHub secret) |
| CLOUDFLARE_ACCOUNT_ID | ❌          | ✅                | ❌      | Cloudflare dashboard                     |
| CF_TUNNEL_ID       | ✅            | ✅ (if needed)    | ✅      | Cloudflare dashboard                     |
| CF_TUNNEL_NAME     | ✅            | ✅                | ✅      | Cloudflare dashboard                     |
| CF_TUNNEL_HOSTNAME | ✅            | ✅                | ✅      | Cloudflare dashboard                     |
| VITE_API_URL       | ✅            | ✅                | ✅      | Deployment configuration                 |
