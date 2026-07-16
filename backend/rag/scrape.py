import os
import json
import re
import wikipediaapi
from places import PLACES

def clean_era_name(era):
    # e.g., "Mughal Empire (c. 1650 CE)" -> "Mughal Empire"
    return re.sub(r'\s*\(.*?\)\s*', '', era).strip()

def get_short_era(cleaned_era):
    # e.g., "Mughal Empire" -> "Mughal"
    return re.sub(r'\s+(Empire|Dynasty|Kingdom|Sultanate|Period|East India Company|Raj)\b', '', cleaned_era, flags=re.IGNORECASE).strip()

def recursive_extract_sections(sections, list_to_append, page_title):
    for s in sections:
        if s.text.strip():
            list_to_append.append({
                "title": f"{page_title} - {s.title}",
                "text": s.text.strip()
            })
        recursive_extract_sections(s.sections, list_to_append, page_title)

def scrape():
    # Setup wikipedia client
    wiki = wikipediaapi.Wikipedia(
        user_agent="YatraHistoricalWalkthrough/1.0 (contact@yatra.org)",
        language="en"
    )
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(current_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    print(f"Starting scraping for {len(PLACES)} places...")
    
    for entry in PLACES:
        place = entry["place"]
        era = entry["era"]
        
        cleaned_era = clean_era_name(era)
        short_era = get_short_era(cleaned_era)
        era_first_word = era.split()[0]
        
        # Generate candidate page titles to attempt
        candidates = []
        
        # 1. Place name
        candidates.append(place)
        
        # 2. Economy
        candidates.append(f"{era} economy")
        candidates.append(f"{cleaned_era} economy")
        candidates.append(f"{short_era} economy")
        candidates.append(f"Economy of the {cleaned_era}")
        candidates.append(f"Economy of {cleaned_era}")
        candidates.append(f"Economy of the {short_era}")
        candidates.append(f"Economy of {short_era}")
        
        # 3. Architecture
        candidates.append(f"{era} architecture")
        candidates.append(f"{cleaned_era} architecture")
        candidates.append(f"{short_era} architecture")
        candidates.append(f"Architecture of the {cleaned_era}")
        candidates.append(f"Architecture of {cleaned_era}")
        candidates.append(f"Architecture of the {short_era}")
        candidates.append(f"Architecture of {short_era}")
        
        # 4. Culture
        candidates.append(f"{era} culture")
        candidates.append(f"{cleaned_era} culture")
        candidates.append(f"{short_era} culture")
        candidates.append(f"Culture of the {cleaned_era}")
        candidates.append(f"Culture of {cleaned_era}")
        candidates.append(f"Culture of the {short_era}")
        candidates.append(f"Culture of {short_era}")
        
        # Deduplicate candidates while preserving order
        seen_candidates = set()
        unique_candidates = []
        for c in candidates:
            if c not in seen_candidates:
                seen_candidates.add(c)
                unique_candidates.append(c)
        
        sections_data = []
        seen_page_ids = set()
        pages_scraped = []
        
        for title in unique_candidates:
            try:
                page = wiki.page(title)
                if page.exists():
                    if page.pageid in seen_page_ids:
                        continue
                    seen_page_ids.add(page.pageid)
                    pages_scraped.append(page.title)
                    
                    # 1. Add summary
                    if page.summary.strip():
                        sections_data.append({
                            "title": f"{page.title} - Introduction",
                            "text": page.summary.strip()
                        })
                    
                    # 2. Recursively add sections
                    recursive_extract_sections(page.sections, sections_data, page.title)
            except Exception as e:
                # Skip gracefully if network error or page doesn't exist
                print(f"  Error fetching page '{title}': {e}")
                continue
                
        # Write to JSON file in raw/ directory
        filename = f"{place}_{era_first_word}.txt"
        filepath = os.path.join(raw_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(sections_data, f, ensure_ascii=False, indent=2)
            
            print(f"Place: {place} | Era: {era} | First Word: {era_first_word}")
            print(f"  Pages scraped: {', '.join(pages_scraped)}")
            print(f"  Sections found: {len(sections_data)}")
            print(f"  Saved to {filename}\n")
        except Exception as e:
            print(f"  Error writing to file {filename}: {e}\n")

if __name__ == "__main__":
    scrape()
