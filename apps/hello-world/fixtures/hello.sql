-- In-memory exercise only. No database is deployed.
CREATE TABLE episodes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL
);
INSERT INTO episodes (id, title, status)
VALUES ('001', 'Hello, Ops World!', 'ready');
