from django.shortcuts import render
import requests
import datetime
from collections import Counter

def get_github_user_details(username):
    # ... existing code from main.py ...
    base_url = f"https://api.github.com/users/{username}"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    try:
        user_response = requests.get(base_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        repos_response = requests.get(f"{base_url}/repos", headers=headers)
        repos_response.raise_for_status()
        repos_data = repos_response.json()
        
        return analyze_user_data(user_data, repos_data)
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}"

def analyze_user_data(user_data, repos_data):
    # Basic user information
    analysis = {
        "Basic_Information": {
            "Name": user_data.get("name", "Not available"),
            "Location": user_data.get("location", "Not available"),
            "Public Repositories": user_data.get("public_repos", 0),
            "Followers": user_data.get("followers", 0),
            "Following": user_data.get("following", 0),
            "Account Created": datetime.datetime.strptime(
                user_data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%Y-%m-%d") if user_data.get("created_at") else "Not available"
        }
    }
    
    if repos_data:
        # Repository analysis
        languages = []
        stars = 0
        forks = 0
        largest_repo = {"name": "", "size": 0}
        
        for repo in repos_data:
            # Count languages
            if repo.get("language"):
                languages.append(repo["language"])
            
            # Count stars and forks
            stars += repo.get("stargazers_count", 0)
            forks += repo.get("forks_count", 0)
            
            # Track largest repository
            if repo.get("size", 0) > largest_repo["size"]:
                largest_repo = {
                    "name": repo["name"],
                    "size": repo.get("size", 0)
                }
        
        # Calculate language statistics
        language_stats = Counter(languages)
        most_used_languages = dict(language_stats.most_common(5))
        
        analysis["Repository_Analysis"] = {
            "Total Stars": stars,
            "Total Forks": forks,
            "Most Used Languages": most_used_languages,
            "Largest Repository": largest_repo["name"],
            "Average Repository Size": sum(repo.get("size", 0) for repo in repos_data) / len(repos_data) if repos_data else 0
        }
    
    return analysis


def home(request):
    return render(request, 'home.html')

def user_detail(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            analysis = get_github_user_details(username)
            if isinstance(analysis, str):
                # Handle error
                return render(request, 'user_detail.html', {'error': analysis})
            return render(request, 'user_detail.html', {'analysis': analysis, 'username': username})
    return render(request, 'home.html')
