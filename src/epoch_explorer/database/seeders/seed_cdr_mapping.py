import uuid
from datetime import datetime

table_name = "company_department_role"

def run(conn):
    """Seed company_department_role table with sample data"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM company_department_role")
    
    # First, get all companies, departments, and roles
    cursor.execute("SELECT id, name FROM companies")
    companies = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM roles")
    roles = cursor.fetchall()
    
    if not companies or not roles:
        print("Warning: No companies or roles found. Skipping CDR seeding.")
        return
    
    # Create mappings for all combinations
    cdr_mappings = []
    
    for company_id, company_name in companies:
        # Get departments for this company
        cursor.execute("SELECT id, name FROM departments WHERE company_id = ?", (company_id,))
        company_departments = cursor.fetchall()
        
        for dept_id, dept_name in company_departments:
            # Assign roles to department (let's assign first 2-3 roles)
            for i, (role_id, role_name) in enumerate(roles[:3]):
                cdr_code = f"{company_id}||{dept_id}||{role_id}"
                cdr_mappings.append((company_id, dept_id, role_id, company_name, dept_name, role_name, cdr_code))
    
    # Insert CDR mappings
    for company_id, dept_id, role_id, company_name, dept_name, role_name, cdr_code in cdr_mappings:
        try:
            cursor.execute('''
                INSERT INTO company_department_role 
                (company_id, department_id, role_id, company_name, department_name, role_name, cdr_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, dept_id, role_id, company_name, dept_name, role_name, cdr_code))
        except Exception as e:
            # Skip duplicates
            pass
    
    conn.commit()
    
    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM company_department_role")
    count = cursor.fetchone()[0]
    print(f"Seeded {count} company-department-role mappings")
