import csv
import random
import re

def load_nouns(filename="nouns.csv"):
    """Loads nouns and their genders, removing non-breaking spaces."""
    nouns = []
    try:
        with open(filename, 'r', encoding='windows-1252') as csvfile:  # Use the correct encoding
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row

            for row in reader:
                if len(row) >= 2:
                    german_noun = row[0].strip()
                    article_gender_str = row[1].strip().lower()

                    # Replace non-breaking space with a regular space
                    article_gender_str = article_gender_str.replace('\xa0', ' ')

                    match = re.match(r'^(der|die|das)\b', article_gender_str)
                    if match:
                        gender = match.group(1)
                        nouns.append({'noun': german_noun, 'gender': gender})
                    else:
                        print(f"Warning: Could not extract valid gender from '{article_gender_str}' in row: {row}")
                else:
                    print(f"Warning: Skipping row with insufficient data: {row}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    return nouns

def play_game(nouns):
    """Runs the German noun gender guessing game with y/n and detailed feedback."""
    if not nouns:
        print("No nouns loaded. Please check the CSV file.")
        return

    score = 0
    total_attempts = 0

    while True:
        current_noun_data = random.choice(nouns)
        current_noun = current_noun_data['noun']
        correct_gender = current_noun_data['gender']

        user_guess = input(f"What is the gender of '{current_noun}' (der/die/das)? ").lower()

        total_attempts += 1

        if user_guess == correct_gender:
            print(f"Correct! {correct_gender} {current_noun} {current_noun_data.get('english', '')}\n")
            score += 1
        else:
            print(f"Incorrect. The correct gender is '{correct_gender}'. {correct_gender} {current_noun} {current_noun_data.get('english', '')}\n")

        play_again = input("Play again? (y/n): ").lower()
        if play_again != 'y':
            break

    if total_attempts > 0:
        print(f"\nGame Over! Your final score: {score}/{total_attempts} ({(score / total_attempts) * 100:.2f}%)")

if __name__ == "__main__":
    noun_list = load_nouns()
    if noun_list:
        play_game(noun_list)