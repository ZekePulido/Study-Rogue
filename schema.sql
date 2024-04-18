CREATE TABLE IF NOT EXISTS Terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    question TEXT,
    answer TEXT,
    term TEXT,
    definition TEXT,
    tag TEXT NOT NULL
);