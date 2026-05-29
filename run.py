import requests
import json
from google import genai
from google.genai import types


url1=f"https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
url2=f"https://trends.google.com/trending?geo=IN&hours=48&category=6&&status=active"
url3=f"https://trends.google.com/trending?geo=IN&hours=48&category=18&&status=active"

client=genai.Client(api_key="AIzaSyBhp-HCYhH8eY9C53kVtfAuhMNodXE5fPY")


def fetchingTrends():

    trends=[]

    result1=requests.get(url1)
    
    for i in range(10):
        storyId=result1.json()[i]
        storyUrl=f"https://hacker-news.firebaseio.com/v0/item/{storyId}.json"
        request=requests.get(storyUrl).json()
        trends.append(request.get("title"))
    print("Trending topics in tech and ai:", trends)
    print("\n")
    return trends



def get_reddit_gaming_trends():
    subreddits = ["pcgaming", "Valorant", "Minecraft", "IndianGaming"]
    
    # Reddit REQUIRES a custom User-Agent, otherwise they block the request with a 429 Too Many Requests error
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
     
    trendingGamingTopics=[]
    for sub in subreddits:

        url=f"https://www.reddit.com/r/{sub}/hot.json?limit=100"
        response=requests.get(url, headers=headers)



        if response.status_code == 200:
            data=response.json()


            posts=data.get("data",{}).get("children",[])
            
            for post in posts:

                post_data=post["data"]            
                title=post_data.get("title")
                title = post_data.get('title')
                upvotes = post_data.get('ups')
                is_stickied = post_data.get('stickied')
                comments=post_data.get('num_comments')
                
                
                # We skip stickied posts (usually just weekly server rules or mega-threads)
                if upvotes >0 and comments>0:
                    if not is_stickied and comments/upvotes > 0.1 and upvotes > 50 and comments > 20 and check_seo_intent(title):
                        trendingGamingTopics.append(title)
    print(f"Trending topics in r/{sub}:", trendingGamingTopics)
    print("\n")
    return trendingGamingTopics
                    



def check_seo_intent(title):
    title_lower = title.lower()
    
    # 1. The Blacklist (Instantly reject nostalgia, opinions, and vague titles)
    bad_words = ['remember', 'wish', 'unpopular opinion', 'am i the only one', 'anyone else', 'thoughts on', 'megathread', 'just bought']
    if any(word in title_lower for word in bad_words):
        return False
        
    # 2. The Whitelist (Require at least one "high-intent" SEO trigger)
    # These are words people actually type into Google when looking for tech/gaming solutions
    good_words = ['how to', 'fix', 'error', 'guide', 'vs', 'build', 'review', 'best settings', 'optimize', 'tutorial', 'setup']
    if not any(word in title_lower for word in good_words):
        return False
        
    return True



def askingWithGeming():
    gamingList=get_reddit_gaming_trends()
    aiTechlist=fetchingTrends()
    
    prompt=f"""
    You are an expert SEO researcher. I will give you a list of raw trending topics.
    Your ONLY job is to convert these broad topics into EXACT, highly searched user QUESTIONS. 
    
    CRITICAL RULES:
    1. Do NOT return broad topics or keywords. 
    2. EVERY single item MUST be a question format (starting with "How to", "Why", "What is", "Fix for", etc.).
    3. The questions must be targeted towards troubleshooting, tutorials, or guides that can be easily answered by summarizing a YouTube video.
    4. Focus on long-term sustainability (evergreen queries), high search intent, and low competition.
    
    EXAMPLES OF WHAT I WANT:
    - Bad Output: "Minecraft Geyser Plugin"
    - Good Output: "How to setup GeyserMC and Floodgate to allow Bedrock players on Java servers?"
    
    - Bad Output: "Next.js App Router"
    - Good Output: "How to handle dynamic routing in Next.js 14 App Router?"
    
    - Bad Output: "GTA V ASI Mods"
    - Good Output: "Why is my GTA V .asi mod not loading in the main directory?"

    Raw Gaming Topics: {gamingList}
    Raw Tech Topics: {aiTechlist}
    
    Return a JSON array of objects. Each object must have these exact keys:
    - "blog_question": The exact long-tail question to use as the blog title.
    - "youtube_search_query": The exact phrase to search on YouTube to find a tutorial answering this question.
    - "success_rate": A number from 1 to 100 indicating the SEO viability.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1, # Low temperature makes the AI highly deterministic and focused
            ))
        text= response.text
        print(text)
        extracted_keywordList=json.loads(text)
        print("Extracted SEO topics with success rates:", extracted_keywordList)
        print("\n")
        
        return extracted_keywordList
    except Exception as e:
        print("Error generating content:", e)
        return None


askingWithGeming()