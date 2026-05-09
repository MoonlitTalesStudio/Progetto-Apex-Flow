CREATE SCHEMA IF NOT EXISTS b2b;

-- 1. Tabella Prodotti
CREATE TABLE b2b.products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) DEFAULT 0.00 NOT NULL, -- Usiamo i decimali qui
    stock_quantity INTEGER DEFAULT 0 NOT NULL,
    category VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabella Ordini
CREATE TABLE b2b.orders (
    id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL,
    status SMALLINT DEFAULT 0 NOT NULL, -- 0: Cart, 1: Placed, 2: Completed
    total_amount NUMERIC(10, 2) DEFAULT 0.00 NOT NULL, -- Totale ordine decimale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP NULL
);

-- 3. Tabella Dettaglio (Snapshot)
CREATE TABLE b2b.order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES b2b.orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES b2b.products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_purchase NUMERIC(10, 2) NOT NULL -- Prezzo bloccato al momento dell'ordine
);