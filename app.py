import pprint
from urllib.parse import urlparse, parse_qs
from flask import Flask, render_template, url_for, request
import swapi
app = Flask(__name__)

api = swapi.Swapi()


@app.route("/")
def root():
    return render_template("root.html")

@app.route("/people_list")
def people_list():
    req_qs = parse_qs(request.query_string.decode("utf-8"))
    page = int(req_qs['page'][0]) if 'page' in req_qs else None
    resp = api.get(swapi.People, page=page)
    pprint.pprint(resp)
    page_next = [None, None]
    pprint.pprint(resp.next)
    if resp.next is not None:
        urlp = urlparse(resp.next)
        qs = parse_qs(urlp.query)
        pprint.pprint(qs)
        if 'page' in qs:
            page_next[0] = url_for('root', page=qs['page'][0])
            page_next[1] = f"Page: {qs['page'][0]}"
    page_previous = [None, None]
    if resp.previous is not None:
        urlp = urlparse(resp.previous)
        qs = parse_qs(urlp.query)
        if 'page' in qs:
            page_previous[0] = url_for('root', page=qs['page'][0])
            page_previous[1] = f"Page: {qs['page'][0]}"
    return render_template(
        'people_list.html',
        peoples=resp,
        next=page_next,
        previous=page_previous,
    )

@app.route("/people/<int:people_id>")
def people(people_id):
    # Fetch data for a specific person using their ID from the SWAPI
    people_data = api.get(swapi.People, obj_id=people_id)
    # Extract movie IDs from the person's film URLs using the id_from_url method
    movie_ids = [swapi.Films(url=film_url).id_from_url() for film_url in people_data.films]
    # Fetch data for each movie using the extracted movie IDs
    movie_data = [api.get(swapi.Films, obj_id=movie_id) for movie_id in movie_ids]
    # Render the 'people.html' template, passing the person's data and their film data
    return render_template("people.html", people=people_data, movies=movie_data)

@app.route("/movies")
def movies():
    # Parse the query string to get the page number if provided
    req_qs = parse_qs(request.query_string.decode("utf-8"))
    page = int(req_qs['page'][0]) if 'page' in req_qs else None
    # Fetch a page of movie data from SWAPI
    resp = api.get(swapi.Films, page=page)
    # Pretty print the response for debugging purposes
    pprint.pprint(resp)
    # Initialize the next page link and label
    page_next = [None, None]
    if resp.next is not None:
        # Parse the next page URL to get the page number
        urlp = urlparse(resp.next)
        qs = parse_qs(urlp.query)
        if 'page' in qs:
            # Create a URL for the next page and a label for it
            page_next[0] = url_for('movies', page=qs['page'][0])
            page_next[1] = f"Page: {qs['page'][0]}"
    # Initialize the previous page link and label
    page_previous = [None, None]
    if resp.previous is not None:
        # Parse the previous page URL to get the page number
        urlp = urlparse(resp.previous)
        qs = parse_qs(urlp.query)
        if 'page' in qs:
            # Create a URL for the previous page and a label for it
            page_previous[0] = url_for('movies', page=qs['page'][0])
            page_previous[1] = f"Page: {qs['page'][0]}"
    # Render the 'movies.html' template, passing the movie data and pagination links
    return render_template(
        'movies.html',
        movies=resp,
        next=page_next,
        previous=page_previous,
    )

@app.route("/movie/<int:movie_id>")
def movie(movie_id):
    # Fetch data for a specific movie using its ID from the SWAPI
    movie_data = api.get(swapi.Films, obj_id=movie_id)
    # Extract people IDs from the movie's character URLs using the id_from_url method
    people_ids = [swapi.People(url=person_url).id_from_url() for person_url in movie_data.characters]
    # Fetch data for each person using the extracted people IDs
    people_data = [api.get(swapi.People, obj_id=person_id) for person_id in people_ids]
    # Render the 'movie.html' template, passing the movie's data and its character data
    return render_template("movie.html", movie=movie_data, people=people_data)