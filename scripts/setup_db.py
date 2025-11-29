import sys
from pathlib import Path
from importlib import import_module
import time

# --- Ensure consistent project root ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "src" / "epoch_explorer" / "database"

sys.path.append(str(DATABASE_DIR))
sys.path.append(str(BASE_DIR / "src"))

from epoch_explorer.database.db.connection import get_connection

def validate_directory(dir_path, dir_name):
	"""Check if directory exists and return it if valid."""
	if not dir_path.exists():
		print(f"Error: {dir_name} directory not found at {dir_path}")
		return None
	if not dir_path.is_dir():
		print(f"Error: {dir_path} is not a directory")
		return None
	return dir_path

def run_migrations(conn):
	migrations_dir = DATABASE_DIR / "migrations"

	if not validate_directory(migrations_dir, "Migrations"):
		print("Skipping migrations.\n")
		return

	for file in sorted(migrations_dir.glob("*.py")):
		with open(file, 'r') as f:
			code = f.read()

		namespace = {'conn': conn}
		exec(code, namespace)

		if 'run' in namespace:
			namespace['run'](conn)

	print("Migration completed.\n")

def run_seeders(conn):
	seeders_dir = DATABASE_DIR / "seeders"

	if not validate_directory(seeders_dir, "Seeders"):
		print("Skipping seeders.\n")
		return

	for file in sorted(seeders_dir.glob("*.py")):

		with open(file, 'r') as f:
			code = f.read()

		namespace = {'conn': conn}
		exec(code, namespace)

		if 'table_name' in namespace:
			table_name = namespace['table_name']
			cursor = conn.cursor()
			try:
				cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
				count = cursor.fetchone()[0]

				if count > 0:
					continue
			except Exception as e:
				print(f"Skipping seeder {file.name}: table '{table_name}' does not exist or error occurred: {e}")
				continue

		if 'run' in namespace:
			namespace['run'](conn)

	print("Seeders complete.\n")

def run():
	conn = get_connection()

	run_migrations(conn)
	run_seeders(conn)

if __name__ == "__main__":
    run()
