import json
from langchain_community.tools import DuckDuckGoSearchResults
import ast

# Load existing scenarios
with open('data/news_scenarios.json', 'r') as f:
    data = json.load(f)

search = DuckDuckGoSearchResults(backend="auto", num_results=5)

for scenario in data['scenarios']:
    event = scenario['name']
    date = scenario['date']
    
    # Search for real news related to the event
    query = f"{event} news headlines {date[:4]}"  # Use year for historical search
    
    try:
        raw_results = search.invoke(query)
        print(f"Raw results type: {type(raw_results)}, content: {repr(raw_results[:500])}")
        # Try to parse
        if isinstance(raw_results, str):
            try:
                results = ast.literal_eval(raw_results)
            except:
                # If it's not parseable, split by some delimiter
                results = raw_results.split('\n')
        else:
            results = raw_results
        
        print(f"Parsed results: {results[:2]}")
        
        headlines = []
        for i, result in enumerate(results[:5]):
            if isinstance(result, dict):
                title = result.get('title', result.get('snippet', f'Headline {i+1}'))
            else:
                title = str(result)[:100]  # If string, take first 100 chars
            timestamp = date  # Use scenario date
            headlines.append(f"[{timestamp}] {title}")
        
        scenario['news'] = headlines
        print(f"Updated {event} with {len(headlines)} headlines")
        
    except Exception as e:
        print(f"Error fetching for {event}: {e}")
        import traceback
        traceback.print_exc()

# Save updated scenarios
with open('data/news_scenarios.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Real news headlines downloaded and saved.")