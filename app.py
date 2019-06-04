from flask import Flask,render_template,request
import tweepy                 #library for fetching tweets from twitter API
from textblob import TextBlob # library for processing textual data
import dataset                #library for working with database
import matplotlib.pyplot as plt
app=Flask(__name__,template_folder='template', static_folder = 'static')

@app.route('/')
def home():
	return render_template('index.html')
@app.route('/get_data',methods=['POST','GET'])
def get_topic():
    
    if request.method=='POST':
        topic=request.form['topic']
        #credentials that let us authenticate with the Twitter Streaming API.
        consumer_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        consumer_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        access_token='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        access_token_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        
        #authenticating with twitter that is logging in with code
        
        auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token,access_token_secret)
        
        #we create an API object to pull data from Twitter — we'll pass in the authentication:
        api=tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        
        #this api variable will be used perform different oprations of twitter and to search for tweets
        #connecting to the database
        db=dataset.connect("sqlite:///tweets.db")
        # opening a Twitter stream using tweepy requires a user-defined listener class to  implement some custom logic.
        class MyStreamListener(tweepy.StreamListener):
            
            pos_score=0
            neg_score=0
            nuet_score=0
            def __init__(self):
                super().__init__()
                self.counter = 0
                self.limit = 100 #time limit for streaming tweets from API 
          
            def on_status(self,status):
                if status.retweeted:
                    return
                print(status.text)
                loc = status.user.location
                text=status.text
                blob = TextBlob(text)
                sent = blob.sentiment        #analysing the tweet's sentiment and collecting scores
                if sent.polarity<0:
                    label='negative'
                    self.neg_score+=1
                if sent.polarity==0:
                    label='nuetral'
                    self.nuet_score+=1
                else:
                    label='positive'
                    self.pos_score+=1
               
                table=db['tweets1']
                table.insert(dict(             #saving the streamed tweets in a database
                        user_location=loc,
                        tweet_text=text,
                        sentiment=label))
                self.counter += 1
                if self.counter < self.limit: #checking that the time limit does not exceed
                    return True
                else:
                    stream.disconnect()
        #The above code will create a listener that analyses and stores the text of any tweet that comes from the Twitter API in a database            
            def on_error(self,status_code):#Handling errors that may occur while streaming
                if status_code==420:
                    return False
        
        #creating a object for listening the tweets that will come from twiter API
        stream_listener=MyStreamListener()
        #creating a stream for extracting tweets
        stream=tweepy.Stream(auth=api.auth,listener=stream_listener)
        #we want to collect tweets that contain a certain keyword filter is method of tweepy.Stream that allows us to do this
        keyword=topic
        stream.filter(track=[keyword])
        #visualizing the collected data after analysis using a pie chart 
        val=[stream_listener.pos_score,stream_listener.neg_score,stream_listener.nuet_score]
        label=['positive','negative','nuetral']
        plt.axis("equal")
        plt.pie(val,labels=label,radius=1.0,autopct='%0.2f%%',explode=[0.1,0.1,0.1])
        plt.title("Sentiments on twitter for "+topic)
        #plt.show(block=False)
       
        plt.savefig('static/images/'+topic+'.png',block=False)
        plt.clf()
        return render_template('result.html', url ='/static/images/'+topic+'.png')


if __name__ == '__main__':
	app.run(debug=True)
