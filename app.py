import streamlit as st
import pandas as pd
import pickle
import requests
import random
import re


st.set_page_config(page_title="Movie Factory" , page_icon=':clapper:',layout='wide')
st.title('Movie Factory')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

movie_list = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl','rb'))
model = pickle.load(open('model.pkl','rb'))


your_movie = st.selectbox(
    'Select your Movie',
    (movies['title']))


def movie_info(id):
    api_link = f'https://api.themoviedb.org/3/movie/{id}?api_key=a2beae1401c2d48af273258951fe0f1c'
    data = requests.get(api_link).json()
    release_date = data['release_date']
    runtime = data['runtime']
    vote_average = data['vote_average']
    runtime = f'{int(runtime/60)}hr {runtime%60}min'
    vote_average = round(vote_average,1)

    return release_date, runtime, vote_average

def storyline(imdbid):
    try:
        import imdb
        ia = imdb.IMDb()
        movie_access = ia.get_movie(imdbid)
        movie_data = movie_access.data
        story = movie_data['plot']
    except:
        story = 'No Story availabe at this time'
    f_story = []
    for line in story:
        if "—" in line:
            f_story.append(line.split("—")[0])
            
    return '\n\n'.join(f_story)


def director(imdbid):
    try:
        import imdb
        ia = imdb.IMDb()
        movie_access = ia.get_movie(imdbid)
        movie_data = movie_access.data
        director = movie_data['director']
        for i in director:
            crew = i['name']
    except:
        crew = 'Unknown Director'
    return crew


def movie_poster(id):
    api_link = f'https://api.themoviedb.org/3/movie/{id}?api_key=a2beae1401c2d48af273258951fe0f1c'
    data = requests.get(api_link).json()

    if 'poster_path' in data and data['poster_path'] is not None :
        poster = 'https://image.tmdb.org/t/p/original' + data['poster_path']
    else:
        poster = 'https://www.prokerala.com/movies/assets/img/no-poster-available.jpg'

    return poster

def movie_backdrop(id):
    api_link = f'https://api.themoviedb.org/3/movie/{id}?api_key=a2beae1401c2d48af273258951fe0f1c'
    data = requests.get(api_link).json()

    if 'backdrop_path' in data and data['backdrop_path'] is not None :
        backdrop = 'https://image.tmdb.org/t/p/original' + data['backdrop_path']
    else:
        backdrop = 'https://kannauj.nic.in/wp-content/themes/district-theme/images/blank.jpg'
    
    return backdrop

def movie_trailer(id):
    api_link = f'https://api.themoviedb.org/3/movie/{id}/videos?api_key=a2beae1401c2d48af273258951fe0f1c'
    data = requests.get(api_link).json()
    trailers = [video for video in data['results'] if video['type'] == 'Trailer']

    if trailers:
        first_trailer_key = trailers[0]['key']
        trailer_url = f'https://www.youtube.com/watch?v={first_trailer_key}'
    else:
        trailer_url = f'https://www.youtube.com/watch?v=8E31ZkAYsSw'
    return trailer_url


def prediction(rev):
    rev_vec = vectorizer.transform([rev]).toarray()
    predictions = model.predict(rev_vec)

    sentiment = "Positive" if predictions > 0.5 else "Negative"
    
    return sentiment


def movie_reviews(id):
    api_link = f'https://api.themoviedb.org/3/movie/{id}/reviews?api_key=a2beae1401c2d48af273258951fe0f1c'
    data = requests.get(api_link).json()
    reviews = [rev for rev in data['results']]

    all_author = []
    all_reviews = []

    for i in reviews:
        all_author.append(i['author'])
        each_rev = i['content']
        clean = re.compile('<.*?>')
        clean_rev = re.sub(clean, '', each_rev)
        all_reviews.append(clean_rev)
    return all_author , all_reviews


def recommender(your_movie):
    index = movies[movies['title'] == your_movie].index[0]
    id = movies.iloc[index].id
    name = movies.iloc[index].title
    imdb_id = movies.iloc[index].imdbid
    poster = movie_poster(id)
    backdrop = movie_backdrop(id)
    release_date, runtime, vote_average = movie_info(id)
    story = storyline(imdb_id)
    trailer = movie_trailer(id)
    all_author , all_reviews = movie_reviews(id)
    genres = movies.iloc[index].genres
    cast = movies.iloc[index].cast
    crew = director(imdb_id)
    overview = movies.iloc[index].overview
    overview = ' '.join(overview)

    top10 = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])[1:11]
    recommended_name = []
    recommended_posters = []

    for i in top10:
        m = movies.iloc[i[0]].title
        p = movie_poster(movies.iloc[i[0]].id)

        recommended_name.append(m)
        recommended_posters.append(p)

    return name, poster, backdrop, release_date, runtime, vote_average, genres, cast, crew, overview, story, trailer, all_author, all_reviews, recommended_name, recommended_posters

def filter_movie(genre):
    filtered_mov = []
    for i in range(len(movies)):
        if genre in movies['genres'][i]:
            if movies['vote_average'][i] >= 6 :
                movie_id = movies['id'][i]
                filtered_mov.append(movie_id)

    random_10 = random.sample(filtered_mov, min(10, len(filtered_mov)))

    return random_10


def filter_movie_2(genre,rating):
    filtered_mov = []
    for i in range(len(movies)):
        if genre in movies['genres'][i]:
            if movies['vote_average'][i] >= rating :
                movie_id = movies['id'][i]
                filtered_mov.append(movie_id)

    random_20 = random.sample(filtered_mov, min(20, len(filtered_mov)))

    return random_20
#############################################################################
genres = ['Action', 'Romance', 'Adventure', 'Horror','Drama']

all_filtred = []

for x in genres :
    each_filtred = filter_movie(x)
    all_filtred.append(each_filtred)
#############################################################################

def detailed_genre_wise(id):
    f_index = movies[movies['id'] == id].index[0]
    f_name = movies.iloc[f_index].title
    f_poster = movie_poster(id)

    return f_name , f_poster

######################################################################################################
all_genres = ['Drama','Thriller','TV Movie','Romance','Horror','Western','Mystery',
              'Documentary','Foreign','Music','Science Fiction','Comedy','War','Animation','Family',
              'Fantasy','History','Adventure','Crime','Action']


######################################################################################################


if st.button('Search'):
    name, poster, backdrop, release, runtime, ratings, genres, cast, crew, overview, story ,trailer, all_authors, all_reviews, r_name , r_poster = recommender(your_movie)


    col1, col, col2 = st.columns((5, .60, 3))


    with col1:
        st.subheader(name)
        st.markdown(
        f"""
        <div style="position: relative; padding-bottom: 30px;">
            <img src="{backdrop}" alt="Backdrop Image" style="width: 100%; height: 100%; object-fit: cover;">
        </div>
        """,
        unsafe_allow_html=True)


        c1, c2, c3 = st.columns(3)

        c1.write(f'<div style="background-color: #FFCCCC; text-align: center;"><b style="color: black;">Release Date : <em style="color: blue;">{release}</em></b></div>', unsafe_allow_html=True)
        c2.write(f'<div style="background-color: #FFCCCC; text-align: center;"><b style="color: black;">Movie Runtime : <em style="color: blue;">{runtime}</em></b></div>', unsafe_allow_html=True)
        if ratings < 5 :
            c3.write(f'<div style="background-color: #FFCCCC; text-align: center;"><b style="color: black;">Rating : <em style="color: red;" >{ratings}</em></b></div>', unsafe_allow_html=True)
        else:
            c3.write(f'<div style="background-color: #FFCCCC;      text-align: center;"><b style="color: black;">Rating : <em style="color: green;">{ratings}</em></b></div>', unsafe_allow_html=True)
    


        st.write(f'<div style ="padding-top: 40px;"><b>Genres   : </b><em style="color: #5c677d;">{" | ".join([i for i in genres])}</em></div>', unsafe_allow_html=True)
        st.write(f'<div><b>Cast   : </b><em style="color: #5c677d;">{" | ".join([i for i in cast])}</em></div>', unsafe_allow_html=True)
        st.write(f'<div style ="padding-bottom: 50px;"><b>Director   : </b><em style="color: #5c677d;">{crew}</em></div>', unsafe_allow_html=True)


        st.markdown('##### Overview')
        st.write(f'<em style="color: #5c677d;">{overview}</em>', unsafe_allow_html=True)

        st.markdown('##### Trailer')
        st.video(trailer)

        st.markdown('##### StoryLine')
        st.write(f'<em style="color: #5c677d;">{story}</em>', unsafe_allow_html=True)

        st.markdown('##### Reviews')
        for i in range(len(all_authors)):
            if i !=8:
                st.markdown(f'<div style="font-size: 15px; color: #5e5f66;"><b>{all_authors[i]}</b></div>',unsafe_allow_html=True)
                senti = prediction(all_reviews[i])
                if senti == 'Positive':
                    st.markdown(f'<div style="color: green;">{all_reviews[i]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="color: red;">{all_reviews[i]}</div>', unsafe_allow_html=True)
                st.markdown('<div style="font-size:30px; padding-bottom: 30px;"></div>', unsafe_allow_html=True)
            else:
                break

    
    with col2:
        num_rows = 5
        num_columns = 2

        st.markdown('#### Recommended Movies')

        for row in range(num_rows):
            col1, col2 = st.columns(num_columns)

            with col1:
                idx = row * num_columns
                if idx < len(r_poster):
                    st.markdown(
                    f"""
                    <div style="position: relative; padding-bottom: 5px;">
                        <img src="{r_poster[idx]}" alt="Poster" style="width: 100%; height: 300px; object-fit: cover;">
                    </div>
                    """,unsafe_allow_html=True)
                    st.write(r_name[idx])

            with col2:
                idx = row * num_columns + 1
                if idx < len(r_poster):
                    st.markdown(
                    f"""
                    <div style="position: relative; padding-bottom: 5px;">
                        <img src="{r_poster[idx]}" alt="Poster" style="width: 100%; height: 300px; object-fit: cover;">
                    </div>
                    """,unsafe_allow_html=True)
                    st.write(r_name[idx])

else:
    st.write('')
    st.write('')
    st.markdown('##### Get upto 20 Movies Name according to your Genre and Rating...')

    co1,co2,co3 = st.columns(3)

    your_genre = co1.selectbox('Genre',all_genres)
    your_rating = co2.slider('Rating',0.0,10.0,0.1) 
    button_s = co3.button('Find your Movies according to your Genre and Rating')

    if button_s:
        filtred_20 = filter_movie_2(your_genre,your_rating)
        for i in range(4):
            fs = st.columns(5)
            for j in range(5):

                fst = fs[j]
                # fst.write(5*i+j)
                try:
                    id = filtred_20[5*i+j]
                    f_name , f_poster = detailed_genre_wise(id)
                    
                    fst.markdown(
                                f"""
                                <div style="position: relative; padding-bottom: 5px;">
                                    <img src="{f_poster}" alt="Poster" style="width: 100%; height: 300px; object-fit: cover;">
                                </div>
                                """,unsafe_allow_html=True)
                    fst.write(f'<span style="font-size: 12px;">{f_name}</span>', unsafe_allow_html=True)
                except:
                    pass


for x in range(len(genres)):

    st.markdown(f'<section style="padding-top: 30px; padding-bottom: 10px;"><div style=" font-size: 30px; background-color: #31343F;"><b style="padding-left: 10px;">{genres[x]}</b></div></section>', unsafe_allow_html=True)
    cols = st.columns(10)
    for i in range(10):
        col = cols[i]
        id = all_filtred[x][i]
        f_name , f_poster = detailed_genre_wise(id)
        
        col.markdown(
                    f"""
                    <div style="position: relative; padding-bottom: 5px;">
                        <img src="{f_poster}" alt="Poster" style="width: 100%; height: 132px; object-fit: cover;">
                    </div>
                    """,unsafe_allow_html=True)
        col.write(f'<span style="font-size: 12px;">{f_name}</span>', unsafe_allow_html=True)



st.markdown('#### Sentimental Analysis Of Movie Reviews...')

left , right = st.columns((6.5,3.5))
with left:
    txt = st.text_area('Write a Review to analyze')
with right:
    st.markdown('<p style="text-align: center;">&#x1F604; <b>:Sentiment:</b> &#x1F61E;</p>',unsafe_allow_html=True)

    result = prediction(txt)
    if txt =='':
        pass
    else:
        sl1 , sl2 = st.columns(2)

        if result == 'Positive':
            with sl1:
                st.markdown(f'<div style="padding-left: 90px;"><img src="https://i.gifer.com/YARz.gif" alt="Poster" style="width: 80px; height: 80px; object-fit: cover;"></div>',unsafe_allow_html=True)
            with sl2:
                st.markdown(f'<p style="padding-top: 25px;">{result}</p>',unsafe_allow_html=True)
        else:
            with sl1:
                st.markdown(f'<div style="padding-left: 90px;"><img src="https://media.giphy.com/media/h4OGa0npayrJX2NRPT/giphy.gif" alt="Poster" style="width: 80px; height: 80px; object-fit: cover;"></div>',unsafe_allow_html=True)
            with sl2:
                st.markdown(f'<p style="padding-top: 25px;">{result}</p>',unsafe_allow_html=True)



st.write('')
st.write('')
st.write('')
st.write('')
st.markdown('<span>Created By <a href="https://www.asbpintu.com">asbpintu</a></span>',unsafe_allow_html=True)