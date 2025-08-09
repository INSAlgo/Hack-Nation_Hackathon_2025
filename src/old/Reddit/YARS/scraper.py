import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)
project_root = current_dir
src_path = os.path.join(project_root, "src")
sys.path.append(src_path)

from yars.yars import YARS

# Initialize the YARS Reddit miner
miner = YARS()
filename = "data.json"

# Function to scrape subreddit post details and comments and save to JSON
def scrape_subreddit_data(subreddit_name, limit=10, filename=filename):
    try:
        subreddit_posts = miner.fetch_subreddit_posts(
            subreddit_name, limit=limit, category="hot", time_filter="week"
        )

        return subreddit_posts

    except Exception as e:
        print(f"Error occurred while scraping subreddit: {e}")


# Function to save post data to a JSON file
def save_to_json(data, filename=filename):
    try:
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to JSON file: {e}")

# Main execution
if __name__ == "__main__":
    subreddit_name = "AITAH"

    # Scrape and save subreddit post data to JSON
    subreddit_posts = scrape_subreddit_data(subreddit_name, limit=3)

    # Load existing data from the JSON file, if available
    try:
        with open(filename, "r") as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.extend(subreddit_posts)

    # Save the data incrementally to the JSON file
    save_to_json(existing_data, filename)