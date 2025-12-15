# how to run cloudflare with The Awa Network

# how to start
from the terminal in root start the servers can be added to an sh script later.

# Private Den tunnel
cloudflared tunnel --config .cloudflared/kitenga_whiro_den.yml run kitenga_whiro_den

This connection has metrics for private sub processing.

# Public Awanet tunnel
cloudflared tunnel --config .cloudflared/kitenga_whiro_public.yml run kitenga_whiro_public

This connection is for future publica facing projects.

# metrics

Adding metrics to run on a seperate




