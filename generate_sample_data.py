#!/usr/bin/env python3
"""
Sample Data Generator for Filtered Scenes Feature Testing
Creates realistic test data to demonstrate the filtered scenes functionality
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Sample data
SAMPLE_PERFORMERS = [
    "Riley Reid", "Mia Malkova", "Lana Rhoades", "Adriana Chechik", "Abella Danger",
    "Kendra Lust", "Lisa Ann", "Phoenix Marie", "Asa Akira", "Tori Black",
    "Angela White", "Alexis Texas", "Rachel Starr", "Brandi Love", "Nicole Aniston"
]

SAMPLE_STUDIOS = [
    "Brazzers", "Reality Kings", "Digital Playground", "Wicked Pictures", "Evil Angel",
    "Naughty America", "Bang Bros", "TeamSkeet", "Mofos", "Pure Taboo",
    "Adult Time", "Girlsway", "Bellesa Films", "SexArt", "Vixen"
]

SAMPLE_TAGS = [
    "blonde", "brunette", "big tits", "small tits", "anal", "oral", "hardcore",
    "lesbian", "threesome", "POV", "creampie", "facial", "rough", "romantic",
    "outdoor", "lingerie", "stockings", "uniform", "massage", "shower"
]

FILTER_REASONS = [
    ("already_downloaded", "content"),
    ("unwanted_tags", "content"),
    ("studio_filter", "preference"),
    ("date_range", "temporal"),
    ("duration_filter", "technical"),
    ("rating_filter", "quality"),
    ("custom_rules", "preference")
]

SCENE_TITLES = [
    "Afternoon Delight with {performer}",
    "{performer}'s Wild Weekend",
    "Passionate Moments: {performer}",
    "{performer} Takes Control",
    "Sensual Sunday with {performer}",
    "{performer}'s Secret Fantasy",
    "Late Night Sessions: {performer}",
    "{performer} Gets What She Wants",
    "Private Time with {performer}",
    "{performer}'s Perfect Day"
]

def generate_scene_title(performer):
    """Generate a realistic scene title."""
    template = random.choice(SCENE_TITLES)
    return template.format(performer=performer)

def generate_filtered_scenes(db_path, count=100):
    """Generate sample filtered scenes."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='filtered_scenes'")
    if not cursor.fetchone():
        print("Error: filtered_scenes table not found. Run migration first.")
        return False
    
    print(f"Generating {count} sample filtered scenes...")
    
    for i in range(count):
        # Generate scene data
        performer = random.choice(SAMPLE_PERFORMERS)
        studio = random.choice(SAMPLE_STUDIOS)
        title = generate_scene_title(performer)
        
        # Random performers list (1-3 performers)
        performers_list = [performer]
        if random.random() < 0.3:  # 30% chance of additional performers
            additional = random.sample([p for p in SAMPLE_PERFORMERS if p != performer], 
                                     random.randint(1, 2))
            performers_list.extend(additional)
        
        # Random tags (3-8 tags)
        scene_tags = random.sample(SAMPLE_TAGS, random.randint(3, 8))
        
        # Random filter reason
        filter_reason, filter_category = random.choice(FILTER_REASONS)
        
        # Generate filter details based on reason
        filter_details = {}
        if filter_reason == "already_downloaded":
            filter_details = {"matched_title": title, "similarity": random.uniform(0.8, 1.0)}
        elif filter_reason == "unwanted_tags":
            filter_details = {"unwanted_tags": random.sample(scene_tags, random.randint(1, 2))}
        elif filter_reason == "studio_filter":
            filter_details = {"studio": studio, "rule": "blocked_studio"}
        elif filter_reason == "date_range":
            filter_details = {"release_date": "2020-01-15", "min_date": "2021-01-01"}
        elif filter_reason == "duration_filter":
            duration = random.randint(300, 7200)  # 5 minutes to 2 hours
            filter_details = {"duration": duration, "min_duration": 900}
        elif filter_reason == "rating_filter":
            filter_details = {"rating": random.uniform(1.0, 4.5), "min_rating": 5.0}
        
        # Random filtered date (last 90 days)
        filtered_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        # Some scenes have exceptions (20% chance)
        is_exception = random.random() < 0.2
        exception_date = None
        exception_reason = None
        
        if is_exception:
            exception_date = filtered_date + timedelta(days=random.randint(1, 30))
            exception_reasons = [
                "Manual review - scene is actually good quality",
                "Requested by user",
                "False positive from filter",
                "Special collection addition",
                "Performer spotlight week"
            ]
            exception_reason = random.choice(exception_reasons)
        
        # Generate thumbnail URL (placeholder)
        thumbnail_url = f"https://via.placeholder.com/320x180/007bff/ffffff?text={performer.replace(' ', '+')}"
        
        # Insert filtered scene
        cursor.execute("""
            INSERT INTO filtered_scenes (
                stash_id, stashdb_id, title, performers, studio, tags, duration,
                release_date, filter_reason, filter_category, filter_details,
                scene_url, thumbnail_url, is_exception, exception_date, 
                exception_reason, filtered_date, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"stash_{i+1000}",  # Mock Stash ID
            f"stashdb_{i+2000}",  # Mock StashDB ID
            title,
            json.dumps(performers_list),
            studio,
            json.dumps(scene_tags),
            random.randint(600, 7200) if random.random() < 0.8 else None,  # Duration in seconds
            f"202{random.randint(0, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            filter_reason,
            filter_category,
            json.dumps(filter_details),
            f"https://example.com/scene/{i+1000}",  # Mock scene URL
            thumbnail_url,
            is_exception,
            exception_date.isoformat() if exception_date else None,
            exception_reason,
            filtered_date.isoformat(),
            datetime.now().isoformat()
        ))
        
        # If scene has exception, create exception record
        if is_exception:
            scene_id = cursor.lastrowid
            exception_types = ["permanent", "temporary", "one-time"]
            exception_type = random.choice(exception_types)
            
            expires_at = None
            if exception_type == "temporary":
                expires_at = (exception_date + timedelta(days=random.randint(30, 365))).isoformat()
            
            cursor.execute("""
                INSERT INTO filter_exceptions (
                    filtered_scene_id, exception_type, reason, created_by,
                    expires_at, is_active, times_used, last_used_date,
                    auto_add_to_whisparr, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scene_id,
                exception_type,
                exception_reason,
                "admin",
                expires_at,
                True,
                random.randint(0, 5) if exception_type != "one-time" else 1,
                (exception_date + timedelta(days=random.randint(1, 10))).isoformat() if random.random() < 0.7 else None,
                random.random() < 0.3,  # 30% chance of auto-add to Whisparr
                exception_date.isoformat(),
                exception_date.isoformat()
            ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Generated {count} sample filtered scenes with exceptions")
    return True

def generate_sample_config(db_path):
    """Generate sample configuration data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if config table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
    if not cursor.fetchone():
        print("Warning: config table not found, skipping config generation")
        conn.close()
        return
    
    # Insert sample config if none exists
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO config (
                unwanted_categories, required_categories, min_duration_minutes,
                max_duration_minutes, min_rating, discovery_enabled,
                discovery_frequency_hours, max_scenes_per_check, auto_add_to_whisparr,
                whisparr_quality_profile, concurrent_requests, request_timeout,
                rate_limit_delay, created_date, updated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(["scat", "vomit", "extreme"]),  # Unwanted categories
            json.dumps(["hardcore", "oral"]),  # Required categories
            15,  # Min duration
            180,  # Max duration
            6.0,  # Min rating
            True,  # Discovery enabled
            24,  # Discovery frequency
            50,  # Max scenes per check
            False,  # Auto add to Whisparr
            "HD-1080p",  # Quality profile
            3,  # Concurrent requests
            30,  # Request timeout
            1,  # Rate limit delay
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        print("✅ Generated sample configuration")
    
    conn.close()

def cleanup_sample_data(db_path):
    """Remove all sample data from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete sample data
    cursor.execute("DELETE FROM filter_exceptions")
    cursor.execute("DELETE FROM filtered_scenes")
    
    conn.commit()
    conn.close()
    
    print("✅ Removed all sample data")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sample data for Stash-Filter testing")
    parser.add_argument("--db-path", default="/app/data/stash_filter.db", 
                       help="Path to SQLite database")
    parser.add_argument("--count", type=int, default=100, 
                       help="Number of filtered scenes to generate")
    parser.add_argument("--cleanup", action="store_true", 
                       help="Remove all sample data instead of generating")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_sample_data(args.db_path)
    else:
        print(f"Generating sample data for database: {args.db_path}")
        success = generate_filtered_scenes(args.db_path, args.count)
        if success:
            generate_sample_config(args.db_path)
        print("✅ Sample data generation complete!")

if __name__ == "__main__":
    main()
