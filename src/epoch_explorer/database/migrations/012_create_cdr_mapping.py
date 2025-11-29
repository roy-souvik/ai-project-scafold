"""Create company department role mapping table"""

def run(conn):
    conn.execute('''
    CREATE TABLE IF NOT EXISTS company_department_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    company_name TEXT NOT NULL,
    department_name TEXT NOT NULL,
    role_name TEXT NOT NULL,
    cdr_code TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(company_id, department_id, role_id),
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE CASCADE,
    FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE
    );
    ''')
    conn.commit()
