import sqlite3
import os

def verify_database():
    db_path = "database/movies.db"
    
    if not os.path.exists(db_path):
        print("DB doesnt exist.")
        print(f"run python src/database.py")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Verifying")
    print("=" * 60)
    
    # Sprawdź tabele
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    
    expected_tables = ['movies', 'links', 'ratings', 'tags']
    existing_tables = [t[0] for t in tables if t[0] != 'sqlite_sequence']
    
    print("\n1. Check tables:")
    for table in expected_tables:
        if table in existing_tables:
            print(f"Table '{table}' exists")
        else:
            print(f"Table '{table}' missing!")

    print("\n2. Records count:")
    counts = {}
    for table in expected_tables:
        try:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            counts[table] = count
            status = "✓" if count > 0 else "⚠"
            print(f"   {status} {table.capitalize()}: {count:,} records")
        except sqlite3.Error as e:
            print(f"{table}: Error - {e}")

    print("\n3. Checking indices:")
    indexes = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
    ).fetchall()
    
    expected_indexes = ['idx_ratings_movie', 'idx_ratings_user', 'idx_tags_movie', 'idx_tags_user']
    for idx in expected_indexes:
        if any(idx in i[0] for i in indexes):
            print(f"Index '{idx}' exists")
        else:
            print(f"Index '{idx}' missing")

    print("\n4. Data head:")
    print("\nMovies (top 5):")
    for row in cursor.execute("SELECT movieId, title FROM movies LIMIT 5"):
        print(f"     • [{row[0]}] {row[1]}")
    
    print("\nRatings (top 5):")
    for row in cursor.execute("SELECT r.userId, m.title, r.rating FROM ratings r join movies m on r.movieID = m.movieID  LIMIT 5"):
        print(f"     • User {row[0]} rated {row[1]} with {row[2]}")
    
    print("\nTags (top 5):")
    for row in cursor.execute("SELECT t.userId, m.title, t.tag FROM tags t join movies m on t.movieID = m.movieID LIMIT 5"):
        print(f"     • User {row[0]}: '{row[2]}' for {row[1]}")
    
    conn.close()

    print("\n" + "=" * 60)
    total_records = sum(counts.values())
    print(f"Sum up: {total_records:,} records in {len(existing_tables)} tables")
    print("=" * 60)
    
    if len(existing_tables) == len(expected_tables) and all(counts.values()):
        print("\nDatabase is OK. ✅")
        return True
    else:
        print("\nDatabase verification failed.")
        return False


if __name__ == "__main__":
    verify_database()

