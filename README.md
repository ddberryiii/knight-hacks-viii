## Inspiration

Our webapp uses its very own Machine Learning model to quickly and accurately recommend up to 20 different animes that it believes you would enjoy. When viewing the app, you are prompted to enter in an anime that you enjoyed, so that our model can recommend you similar animes that you will enjoy. After inputting your favorite anime, our model will handpick 8 different animes, with their ratings based of off 'myanimelist.com' and then allows for quick access to their website to more information. (Synopsis, Genres, Reviews)

## What it does

Our app turns the data about the anime into embeddings, then it finds similar vectors which are similar shows. So an user can query a show, and it will find similar anime based on the features such as synopsis, genre, and themes.

## How we built it
We used Flask as the framework for defining our API endpoint calls and serving them to our html file. 
Our backend consisted of a style sheet file for our website's aesthetic design and JavaScript for mapping our endpoints to their corresponding backend functions. Our backend consists of the embedding model and our knn searchr along with the implementation of the google Gemini 2.5 flash api as a personal chat assistant in the web application. 

## Challenges we ran into

Some challenges we ran into initially was how do we process the data and clean it so the model has good embeddings. We played around and ended up with removing certain features such as ranking, and the number of favorites. The major problem we encountered was when we did the knn, it would just return the same series, so we had to work to filter out entries of the same franchise.
 
## Accomplishments that we're proud of
Some accomplishments that we're proud of is just going to this hackathon and finishing our project all the way to the end. For all of us, this is the first hackathon we've done and we're proud to have finished a project all the way from end to end.

## What we learned
Along the course of this project, we learned how api calls for llm chatbots work like the google gemini. Additionally, we figured out how to set up a website with google colab. The most important thing we learned is how an embedding model actually works and how a knn search is used in recommendation systems.

## What's next for senpAI
We plan to get more data either from web scraping or an api call from a database website as this will make the embedding models much more accurate. Then we can add a database so we can actually store the embeddings instead of just storing it in our backend. Additionally, we can do more than just anime such are tv shows, games, etc.. We can make it a media recommender.
