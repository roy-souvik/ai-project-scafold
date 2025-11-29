from .base_model import BaseModel


class CompanyDepartmentRole(BaseModel):
    __tablename__ = 'company_department_role'
    
    def __init__(self, company_id, department_id, role_id, company_name=None, department_name=None, role_name=None):
        self.company_id = company_id
        self.department_id = department_id
        self.role_id = role_id
        self.company_name = company_name
        self.department_name = department_name
        self.role_name = role_name
        self.cdr_code = f"{company_id}||{department_id}||{role_id}"
    
    @staticmethod
    def generate_cdr_code(company_id, department_id, role_id):
        """Generate CDR code from IDs"""
        return f"{company_id}||{department_id}||{role_id}"
    
    @staticmethod
    def create(conn, company_id, department_id, role_id, company_name=None, department_name=None, role_name=None):
        """Create a new CDR mapping"""
        cursor = conn.cursor()
        
        # If names not provided, fetch from database
        if not company_name:
            cursor.execute('SELECT name FROM companies WHERE id = ?', (company_id,))
            result = cursor.fetchone()
            company_name = result[0] if result else f"Company_{company_id}"
        
        if not department_name:
            cursor.execute('SELECT name FROM departments WHERE id = ?', (department_id,))
            result = cursor.fetchone()
            department_name = result[0] if result else f"Department_{department_id}"
        
        if not role_name:
            cursor.execute('SELECT name FROM roles WHERE id = ?', (role_id,))
            result = cursor.fetchone()
            role_name = result[0] if result else f"Role_{role_id}"
        
        cdr_code = CompanyDepartmentRole.generate_cdr_code(company_id, department_id, role_id)
        
        cursor.execute('''
            INSERT INTO company_department_role 
            (company_id, department_id, role_id, company_name, department_name, role_name, cdr_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (company_id, department_id, role_id, company_name, department_name, role_name, cdr_code))
        conn.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_id(conn, cdr_id):
        """Get a CDR mapping by ID"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_id, department_id, role_id, company_name, department_name, role_name, cdr_code, created_at, updated_at
            FROM company_department_role
            WHERE id = ?
        ''', (cdr_id,))
        return cursor.fetchone()
    
    @staticmethod
    def get_by_cdr_code(conn, cdr_code):
        """Get a CDR mapping by CDR code"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_id, department_id, role_id, company_name, department_name, role_name, cdr_code, created_at, updated_at
            FROM company_department_role
            WHERE cdr_code = ?
        ''', (cdr_code,))
        return cursor.fetchone()
    
    @staticmethod
    def get_by_company_department_role(conn, company_id, department_id, role_id):
        """Get a CDR mapping by company, department, and role"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_id, department_id, role_id, company_name, department_name, role_name, cdr_code, created_at, updated_at
            FROM company_department_role
            WHERE company_id = ? AND department_id = ? AND role_id = ?
        ''', (company_id, department_id, role_id))
        return cursor.fetchone()
    
    @staticmethod
    def get_all_for_company(conn, company_id):
        """Get all CDR mappings for a company"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_id, department_id, role_id, company_name, department_name, role_name, cdr_code, created_at, updated_at
            FROM company_department_role
            WHERE company_id = ?
        ''', (company_id,))
        return cursor.fetchall()
    
    @staticmethod
    def get_all_for_department(conn, department_id):
        """Get all CDR mappings for a department"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_id, department_id, role_id, company_name, department_name, role_name, cdr_code, created_at, updated_at
            FROM company_department_role
            WHERE department_id = ?
        ''', (department_id,))
        return cursor.fetchall()
    
    @staticmethod
    def get_all_for_role(conn, role_id):
        """Get all CDR mappings for a role"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_id, department_id, role_id, company_name, department_name, role_name, cdr_code, created_at, updated_at
            FROM company_department_role
            WHERE role_id = ?
        ''', (role_id,))
        return cursor.fetchall()
    
    @staticmethod
    def get_all(conn):
        """Get all CDR mappings"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_id, department_id, role_id, company_name, department_name, role_name, cdr_code, created_at, updated_at
            FROM company_department_role
        ''')
        return cursor.fetchall()
    
    @staticmethod
    def delete(conn, cdr_id):
        """Delete a CDR mapping"""
        cursor = conn.cursor()
        cursor.execute('DELETE FROM company_department_role WHERE id = ?', (cdr_id,))
        conn.commit()
