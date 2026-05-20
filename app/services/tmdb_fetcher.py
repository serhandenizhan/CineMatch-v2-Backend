import httpx
import os
import random
import asyncio

TMDB_API_KEY = "296a050c356699a086aedbbd54308c2f" # KODUN İÇİNE DOĞRUDAN YAZALIM ŞİMDİLİK
BASE_URL = "https://api.themoviedb.org/3" # Changed to themoviedb.org to prevent 410 Gone error

async def fetch_movie_details(client, movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
    resp = await client.get(url)
    if resp.status_code == 200:
        return resp.json()
    return None

async def fetch_popular_movies(filter_type: str = "popular"):
    page = random.randint(1, 5) # Mix it up!
    url = f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
    
    if filter_type == "toprated":
        url = f"{BASE_URL}/movie/top_rated?api_key={TMDB_API_KEY}&language=en-US&page={page}"
    elif filter_type == "latest":
        url = f"{BASE_URL}/movie/now_playing?api_key={TMDB_API_KEY}&language=en-US&page={page}"
    elif filter_type.startswith("genre_"):
        genre_mapping = {
            "genre_action": "28",
            "genre_comedy": "35",
            "genre_drama": "18",
            "genre_horror": "27",
            "genre_scifi": "878",
            "genre_romance": "10749"
        }
        genre_id = genre_mapping.get(filter_type, "28")
        url = f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc&page={page}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            movies = []
            results = data.get('results', [])
            random.shuffle(results) # Shuffle them for extra randomness
            selected = results[:10]
            
            tasks = [fetch_movie_details(client, m['id']) for m in selected]
            details_results = await asyncio.gather(*tasks)

            for m, details in zip(selected, details_results):
                director = "Unknown"
                actors = []
                if details and 'credits' in details:
                    crew = details['credits'].get('crew', [])
                    director_obj = next((c for c in crew if c['job'] == 'Director'), None)
                    if director_obj:
                        director = director_obj['name']
                    cast = details['credits'].get('cast', [])
                    actors = [c['name'] for c in cast[:3]]

                movies.append({
                    "movie_id": str(m['id']), # mapped to movie_id for frontend
                    "title": m['title'],
                    "overview": m['overview'],
                    "genre": filter_type, # mapped for frontend
                    "poster_url": f"https://image.tmdb.org/t/p/w500{m.get('poster_path')}" if m.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster",
                    "release_date": m.get('release_date', 'Unknown'),
                    "director": director,
                    "actors": ", ".join(actors) if actors else "Unknown"
                })
            return movies
        else:
            print(f"TMDB API ERROR: {response.status_code}")
            return [] # Boş dönüyorsa terminalde bu hatayı göreceğiz
