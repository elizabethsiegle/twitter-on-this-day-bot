import datetime
from dotenv import load_dotenv
import tweepy
from random import randint
import requests
import os

# Retrieve API keys, tokens from env vars
load_dotenv()
twitter_api_key = os.environ.get("TWITTER_API_KEY")
twitter_api_secret = os.environ.get("TWITTER_API_SECRET") 
twitter_access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
twitter_access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
AUTH_TOKEN = os.environ.get("CLOUDFLARE_AUTH_TOKEN")

# Initialize Tweepy client
twitter_client = tweepy.Client(
    consumer_key=twitter_api_key,
    consumer_secret=twitter_api_secret,
    access_token=twitter_access_token,
    access_token_secret=twitter_access_token_secret
)


def get_on_this_day_events():
    today = datetime.datetime.now()
    date = today.strftime('%m/%d')
    print(f"date: {date}")

    url = 'https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/selected/' + date

    headers = {
    'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI3MmZlOGFmOTAwNjUxOGNmZDQwMmQxODlhNDYxYmQzYyIsImp0aSI6IjUyN2YzZjQxZTM2OGY3M2I4NzRlZWQ3NmU0YzE4YWExN2ZlZGI3M2IxYWJjNTFlZWI4MjkwMGE5NDI3MDRkODc1NTkyYTVkMzkyMDU5OTU5IiwiaWF0IjoxNjY2NDI0NzQ2LjIxMDE3OCwibmJmIjoxNjY2NDI0NzQ2LjIxMDE4MywiZXhwIjozMzIyMzMzMzU0Ni4yMDg0NTgsInN1YiI6IjcwOTgxMzA0IiwiaXNzIjoiaHR0cHM6Ly9tZXRhLndpa2ltZWRpYS5vcmciLCJyYXRlbGltaXQiOnsicmVxdWVzdHNfcGVyX3VuaXQiOjUwMDAsInVuaXQiOiJIT1VSIn0sInNjb3BlcyI6WyJiYXNpYyJdfQ.egiyPFxIge7FJ6gMsmCzHs3asIGjPrs3KkwOUNb7Vyjub3dzCB1CJBj7piNMplSr9CLAeVsWam9EXzK48UkynOuIGwcSVm8MprDWhK94pLowTwvmt1U9JNGbesAj59QTh-QIl4YTLl7_p0K25lhlEQWdC_o_soe5B7DfA5x4vBDbhCP4rnn4bmanxX5QgH31p6NaqKYmSQGe7CbUY8kJCzPXf3jflbvzNnzS0HEh-MnGkPNDMviVWQcRwqs0W5yrLibKc97hROVzEl5gfVnk_Fc5MeV-uXmrTaO1EMdJ_biCov46CLEOU5gcwr_z_uNKV-oYVZlJE9Ztm_OAjISYmXGjw37xh0q49j63sz7zsYiRWtXCKZZY1JIeuEbTHv0TXwZEQ6ImjkK6Mg7A2WErjUYMpNgnQy-eGt9IX2KTaK-IXjdSjPiwfmPixsb5YwlDvQeDOc0xBb_tGgiqbLrG_I36_oqyge-myGbnIvDsx2cqWltpPPMHG-kKvvE_YCYS0oCz-QZB7dapdHwR69sguePhZFdS4oXgN9VM4FIRW_U2kqGLy2AFj0NuHWEDGtVQXLDgDKXsZA8ZE9pxG6FthnQm7J7n2cvoPnyh7Hwa_5pjOOJqWWQW4ls7RkC3wfhObCCROEbYWKKSQS89YXUQm2piSrGzJB7NUrWnel3Yrw8',
    'User-Agent': 'YOUR_APP_NAME (YOUR_EMAIL_OR_CONTACT_PAGE)'
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    rn = randint(0, len(data["selected"]))
    print(data["selected"][rn]["text"]) # , data["selected"][rn]["year"])
    return data["selected"][rn]["text"], data["selected"][rn]["year"]
    

def generate_tweet():
    onthisday = get_on_this_day_events()
    response = requests.post(
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct",
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
        json={
            "messages": [
                {"role": "system", "content": "My Twitter account tweets about history and what happened in history on this day."},
                {"role": "user", "content": f"Parse the information about what happened on this day throughout history from the following JSON and include the year: {onthisday}. Use it to craft an engaging, educational, and informational tweet."}
            ]
        }
    )
    print(f"response {response.json()}") # ['result']['response']}")
    result = response.json() # ['result']['response']
    return result
  
def new_tweet():
  while True:
    try:
        new_tweet = generate_tweet()
        response = twitter_client.create_tweet(text =str(new_tweet))
        print(f"success {response.data["text"]}")
        break # exit loop if successful
    except tweepy.errors.Forbidden as e:
        print("403 Forbidden Err")
        pass
    except Exception as e:
        if "Your Tweet text is too long" in str(e):
            print("Tweet too long")
            pass
        else:
            raise e 

# Streamlit app
def main():
    new_tweet()

if __name__ == "__main__":
    main()