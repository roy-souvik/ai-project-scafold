import hashlib

table_name = "users"
def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def run(conn):
    conn.execute(
        "INSERT OR IGNORE INTO users (id, name, email, password) VALUES (1, ?, ?, ?)",
        ('Root User', 'root@example.com', _hash('rootpass'))
    )
    conn.execute("INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", ('Souvik', 'souvik@example.com', _hash('Password@123')))
    conn.execute("INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", ('Sourav', 'sourav@example.com', _hash('Password@123')))
    conn.execute("INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", ('Prasun', 'prasun@example.com', _hash('Password@123')))
    conn.execute("INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", ('Rupankar', 'rupankar@example.com', _hash('Password@123')))
    conn.execute("INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", ('Samya', 'samya@example.com', _hash('Password@123')))
    conn.commit()
