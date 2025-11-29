def run(conn):
    assignments = [
        # email,        role,       company_id
        ('root@example.com', 'admin',     1),
        ('souvik@example.com',  'manager',   2),
        ('sourav@example.com',  'developer',  2),
        ('prasun@example.com',  'employee',  2),
        ('rupankar@example.com',  'developer',  2),
        ('samya@example.com',  'employee',  2),
    ]

    for email, role_name, company_id in assignments:
        user = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        role = conn.execute(
            "SELECT id FROM roles WHERE name = ?",
            (role_name,)
        ).fetchone()

        if user and role:
            conn.execute(
                "INSERT OR IGNORE INTO user_roles (user_id, role_id, company_id) VALUES (?, ?, ?)",
                (user['id'], role['id'], company_id)
            )

    conn.commit()
