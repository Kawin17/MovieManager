import sqlite3
from imdb import IMDb

# Initialize IMDb instance
ia = IMDb()

# Connect to SQLite database
conn = sqlite3.connect('movies.db')
cursor = conn.cursor()

# Create tables for movies, watchlist, and watched movies
cursor.execute('''
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    year INTEGER,
    genres TEXT,
    director TEXT,
    rating REAL,
    plot TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS watchlist (
    movie_id INTEGER,
    FOREIGN KEY(movie_id) REFERENCES movies(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS watched (
    movie_id INTEGER,
    FOREIGN KEY(movie_id) REFERENCES movies(id)
)
''')

conn.commit()

def search_movie(movie_title):
    """Searches for a movie in the database, or fetches it from IMDb if not found."""
    cursor.execute('SELECT * FROM movies WHERE title = ?', (movie_title,))
    movie = cursor.fetchone()
    
    if movie:
        print(f"Movie found in database: {movie[1]}")
        display_movie_info(movie)
    else:
        print("Movie not found in database. Fetching from IMDb...")
        movies = ia.search_movie(movie_title)
        movie_id = movies[0].movieID
        movie_data = ia.get_movie(movie_id)
        
        title = movie_data.get('title')
        year = movie_data.get('year')
        genres = ', '.join(movie_data.get('genres', []))
        director = ', '.join([director['name'] for director in movie_data.get('directors', [])])
        rating = movie_data.get('rating')
        plot = movie_data.get('plot outline')
        
        store_movie(title, year, genres, director, rating, plot)
        
        # Fetch the movie info again after storing
        cursor.execute('SELECT * FROM movies WHERE title = ?', (title,))
        movie = cursor.fetchone()
        display_movie_info(movie)

    user_choice(movie[0])

def store_movie(title, year, genres, director, rating, plot):
    """Stores the movie information in the database."""
    cursor.execute('''
    INSERT INTO movies (title, year, genres, director, rating, plot)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, year, genres, director, rating, plot))
    conn.commit()
    print(f"Movie '{title}' added to the database.")

def display_movie_info(movie):
    """Displays the movie's information."""
    print(f"\nTitle: {movie[1]}")
    print(f"Year: {movie[2]}")
    print(f"Genres: {movie[3]}")
    print(f"Director: {movie[4]}")
    print(f"Rating: {movie[5]}")
    print(f"Plot: {movie[6]}")

def user_choice(movie_id):
    """Gives the user options to add to watchlist or mark as watched."""
    while True:
        print("\nOptions:")
        print("1. Add to Watchlist")
        print("2. Mark as Watched")
        print("3. Go back")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            add_to_watchlist(movie_id)
            break
        elif choice == '2':
            mark_as_watched(movie_id)
            break
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def add_to_watchlist(movie_id):
    """Adds the movie to the user's watchlist."""
    cursor.execute('INSERT INTO watchlist (movie_id) VALUES (?)', (movie_id,))
    conn.commit()
    print("Movie added to watchlist.")

def mark_as_watched(movie_id):
    """Marks the movie as watched."""
    cursor.execute('INSERT INTO watched (movie_id) VALUES (?)', (movie_id,))
    conn.commit()
    print("Movie marked as watched.")

def view_watchlist():
    """Displays the user's watchlist."""
    cursor.execute('''
    SELECT movies.title, movies.year FROM movies
    JOIN watchlist ON movies.id = watchlist.movie_id
    ''')
    watchlist = cursor.fetchall()
    
    if not watchlist:
        print("Your watchlist is empty.")
    else:
        print("\nYour Watchlist:")
        for movie in watchlist:
            print(f"Title: {movie[0]}, Year: {movie[1]}")

def view_watched():
    """Displays the user's watched movies."""
    cursor.execute('''
    SELECT movies.title, movies.year FROM movies
    JOIN watched ON movies.id = watched.movie_id
    ''')
    watched = cursor.fetchall()
    
    if not watched:
        print("You haven't watched any movies yet.")
    else:
        print("\nYour Watched Movies:")
        for movie in watched:
            print(f"Title: {movie[0]}, Year: {movie[1]}")

def movie_management_system():
    """Main function to run the Movie Management System."""
    while True:
        print("\nMovie Management System")
        print("1. Search for a Movie")
        print("2. View Watchlist")
        print("3. View Watched Movies")
        print("4. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            movie_title = input("Enter the movie title: ")
            search_movie(movie_title)
        elif choice == '2':
            view_watchlist()
        elif choice == '3':
            view_watched()
        elif choice == '4':
            print("Exiting the Movie Management System.")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the Movie Management System
movie_management_system()

# Close the connection when done
conn.close()
