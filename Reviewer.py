from save import save_chapter_auto_version, get_latest_version, fetch_chapter_by_version

# Get the latest version number for rewritten chapters
latest_version = get_latest_version("chapter1", "rewritten")

# Construct the full versioned ID
versioned_id = f"chapter1_ver{latest_version}"

# Fetch the chapter data
data = fetch_chapter_by_version(versioned_id, "rewritten")
print(data)