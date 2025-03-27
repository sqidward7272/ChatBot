CREATE TABLE plagiarism_checks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    plagiarism_score FLOAT NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
