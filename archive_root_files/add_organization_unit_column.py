import sqlite3

# Connect to the database
conn = sqlite3.connect('c:\\Users\\ramon\\OneDrive\\Documentos\\windsurf\\gestionVehiculos\\gestion_vehiculos.db')
cursor = conn.cursor()

try:
    # Check if organization_unit_id column exists
    cursor.execute("PRAGMA table_info(reservations)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'organization_unit_id' not in columns:
        print("Adding organization_unit_id column to reservations table...")
        cursor.execute("ALTER TABLE reservations ADD COLUMN organization_unit_id INTEGER")

        # Set a default value for existing records (assuming organization_units table has at least one record)
        cursor.execute("SELECT id FROM organization_units LIMIT 1")
        default_org_id = cursor.fetchone()

        if default_org_id:
            cursor.execute("UPDATE reservations SET organization_unit_id = ? WHERE organization_unit_id IS NULL", (default_org_id[0],))
            print(f"Updated existing reservations with default organization_unit_id: {default_org_id[0]}")
        else:
            print("Warning: No organization_units found. Please create at least one organization unit first.")

        conn.commit()
        print("Successfully added organization_unit_id column to reservations table")
    else:
        print("organization_unit_id column already exists in reservations table")

except sqlite3.Error as e:
    print(f"Database error: {e}")
    conn.rollback()
finally:
    conn.close()
