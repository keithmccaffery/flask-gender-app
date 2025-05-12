import csv
import re
import sqlite3

def clean_noun_data(filename="nouns.csv"):
    """Reads and cleans noun data from a CSV file."""
    print("Starting clean_noun_data()")  # Debug print
    cleaned_nouns = []
    try:
        with open(filename, 'r', encoding='windows-1252') as csvfile:
            reader = csv.DictReader(csvfile)
            print(f"CSV file opened successfully: {filename}")  # Debug print
            for row in reader:
                print(f"Processing row: {row}")  # Debug print
                german_noun = row.get('German', '').strip()  # Correct key
                article_gender_str = row.get('Article and Gender', '').strip().lower()  # Correct key
                english_translation = row.get('English', '').strip()  # Correct key

                article_gender_str = article_gender_str.replace('\xa0', ' ')
                match = re.match(r'^(der|die|das)\b', article_gender_str)
                if match:
                    gender = match.group(1)
                    cleaned_nouns.append({'noun': german_noun, 'gender': gender, 'english': english_translation})
                    print(f"Cleaned noun: {german_noun}, gender: {gender}, english: {english_translation}") # Debug
                else:
                    print(f"Warning: Could not extract valid gender from '{article_gender_str}' in row: {row}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    print(f"Finished clean_noun_data(). Found {len(cleaned_nouns)} cleaned nouns.") # Debug
    return cleaned_nouns

def create_sqlite_table(db_name="nouns.db"):
    """Creates a SQLite3 table named 'nouns'."""
    print("Starting create_sqlite_table()")  # Debug print
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nouns (
            noun TEXT UNIQUE,
            gender TEXT,
            english TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"SQLite table 'nouns' created in '{db_name}'")  # Debug print

def insert_nouns_into_sqlite(nouns_data, db_name="nouns.db"):
    """Inserts cleaned noun data into the SQLite 'nouns' table."""
    print("Starting insert_nouns_into_sqlite()")  # Debug print
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    inserted_count = 0
    for noun_data in nouns_data:
        try:
            cursor.execute("INSERT OR IGNORE INTO nouns (noun, gender, english) VALUES (?, ?, ?)",
                           (noun_data['noun'], noun_data['gender'], noun_data['english']))
            inserted_count += 1
        except sqlite3.IntegrityError:
            print(f"Warning: Skipping duplicate noun '{noun_data['noun']}'")
    conn.commit()
    conn.close()
    print(f"{inserted_count} nouns inserted into '{db_name}'")  # Debug print

if __name__ == "__main__":
    print("Starting main execution.")  # Debug print
    cleaned_data = clean_noun_data()
    if cleaned_data:
        print("Cleaned data is not empty. Proceeding to create table and insert.") # Debug
        create_sqlite_table()
        insert_nouns_into_sqlite(cleaned_data)
    else:
        print("Cleaned data is empty. Aborting database creation.") # Debug
    print("Finished main execution.") # Debug