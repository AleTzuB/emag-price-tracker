create table if not exists products (
  id serial primary key,
  url text unique not null,
  name text,
  currency text default 'RON',
  created_at timestamptz default now()
);

create table if not exists prices (
  id serial primary key,
  product_id int not null references products(id),
  price_cents int not null,
  currency text default 'RON',
  created_at timestamptz default now()
);
