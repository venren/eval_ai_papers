import urllib.request
import os


def get_verdict_story(output_path: str = "the_verdict.txt", force_download: bool = False) -> str:
    url = "https://raw.githubusercontent.com/rasbt/LLMs-from-scratch/main/ch02/01_main-chapter-code/the-verdict.txt"
    
    # Load from file if exists and not forcing download
    if os.path.exists(output_path) and not force_download:
        with open(output_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Download the story
    print("Downloading 'The Verdict' short story...")
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Saved to {output_path} ({len(content)} characters)")
    return content
