-- Stores image + metadata for cards listed/saved
create table cards_for_sale (
  id uuid primary key default gen_random_uuid(),
  image_url text,
  card_name text,
  card_number text,
  series text,
  value_estimate numeric,
  ebay_link text,
  brave_snippet text,
  listed_at timestamp default now()
);

-- Stores raw value fetches for graphing
create table dbs_card_prices (
  id uuid primary key default gen_random_uuid(),
  card_name text,
  card_number text,
  source text, -- 'ebay' or 'brave'
  price numeric,
  fetched_at timestamp default now()
);
create index idx_dbs_card_prices_card_name on dbs_card_prices(card_name);