#!/usr/bin/env python
# coding: utf-8

# # Gathering Data:

# In[1681]:


#importing needed modules
import pandas as pd
import numpy as np
import requests
import os
import json
import datetime
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns
sns.set_style('darkgrid')


# In[1682]:


#reading twitter-archive-enhanced.csv as a df
twitter_archive=pd.read_csv('twitter-archive-enhanced.csv')


# In[1683]:


#downloading the image_predictions.tsv to the current working directory
url=' https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv'
response=requests.get(url)
filename=url.split('/')[-1]
if not os.path.isfile(filename):
    with open(filename,'wb') as file:
        file.write(response.content)


# In[1684]:


#reading the tsv file downloaded above in a df
image_predictions=pd.read_csv(filename,sep='\t')


# In[1685]:


#getting additional data from twitter API and saving them to a file named tweet_json.txt
#I tried getting access to twitter API but I faced a verification issue so I used the provided file in the resources
#this cell code is copied from the udacity resources and is slightly modified to only work if the file isn't already created
if not os.path.isfile('tweet_json.txt'):
    from timeit import default_timer as timer
    import tweepy
    from tweepy import OAuthHandler
    

# Query Twitter API for each tweet in the Twitter archive and save JSON in a text file
# These are hidden to comply with Twitter's API terms and conditions
    consumer_key = 'HIDDEN'
    consumer_secret = 'HIDDEN'
    access_token = 'HIDDEN'
    access_secret = 'HIDDEN'

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

# NOTE TO REVIEWER: this student had mobile verification issues so the following
# Twitter API code was sent to this student from a Udacity instructor
# Tweet IDs for which to gather additional data via Twitter's API
    tweet_ids = twitter_archive.tweet_id.values
    len(tweet_ids)
# Query Twitter's API for JSON data for each tweet ID in the Twitter archive
    count = 0
    fails_dict = {}
    start = timer()
# Save each tweet's returned JSON as a new line in a .txt file
    with open('tweet_json.txt', 'wb') as outfile:
    # This loop will likely take 20-30 minutes to run because of Twitter's rate limit
        for tweet_id in tweet_ids:
            count += 1
            print(str(count) + ": " + str(tweet_id))
            try:
                tweet = api.get_status(tweet_id, tweet_mode='extended')
                print("Success")
                json.dump(tweet._json, outfile)
                outfile.write('\n')
            except tweepy.TweepError as e:
                print("Fail")
                fails_dict[tweet_id] = e
                pass
    end = timer()
    print(end - start)
    print(fails_dict)


# In[1686]:


#reading from the json file
#making a temporary list of dictionaries that will have the three keys we want id, retweet_count and favourite_count
temp_list=[]
with open('tweet_json.txt','r') as f:
    for l in f:
        tweet=json.loads(l)
        retweet_count=tweet['retweet_count']
        tweet_id=tweet['id']
        fav_count=tweet['favorite_count']
        temp_list.append({'retweet_count':retweet_count,'tweet_id':tweet_id,'favorite_count':fav_count})
        #named "id" as "tweet_id" to be consistent with the twitter_archive df
        
#creating a df from temp_list
api_df=pd.DataFrame(temp_list)


# # Assessing Data

# In[1687]:


twitter_archive


# In[1688]:


twitter_archive.info()


# In[1689]:


twitter_archive.describe()


# In[1690]:


twitter_archive.rating_denominator.value_counts()


# In[1691]:


twitter_archive.query('name=="a"').shape


# In[1692]:


twitter_archive.query('rating_numerator<10')


# In[1693]:


twitter_archive.rating_numerator.sort_values()


# In[1694]:


twitter_archive.rating_denominator.sort_values()


# In[1695]:


twitter_archive.query('rating_denominator>10')


# In[1696]:


twitter_archive.duplicated().sum()


# In[1697]:


twitter_archive.expanded_urls.isnull().sum()


# In[1698]:


image_predictions


# In[1699]:


image_predictions.info()


# In[1700]:


image_predictions.p1_dog.value_counts()


# In[1701]:


image_predictions.describe()


# In[1702]:


image_predictions.duplicated().sum()


# In[1703]:


api_df


# In[1704]:


api_df.info()


# In[1705]:


api_df.describe()


# ### Quality issues:
# 
# 1-so many missing values in these 5 columns: in_reply_to_status_id, in_reply_to_user_id, retweeted_status_id, retweeted_status_user_id,retweeted_status_timestamp.
# 
# 2-timestamp is string not datetime object.
# 
# 3-"None" instead of Nan in dog breeds columns and name column.
# 
# 4-rating numerator values aren't correctly extracted as they're integers in the rating_numerator column.
# 
# 5-"rating_numerator" has a minimum value of 0.
# 
# 6-"rating_numerator" has a maximum value of 1776 and 'ratings_denominator" has a maximum value of 170.
# 
# 7-"+0000" in timestamp column.
# 
# 8-the denomenator is inconsistent (isn't always 10).
# 
# 9- 55 dogs names as "a".
# 
# 10-the source column mostly has the same value for all entries.
# 
# 11-project requirement: some tweets don't have images in the image_predictions dataframe.
# 
# 
# ### Tidiness issues:
# 
# 1-"doggo", "floffer", "puppo" "pupper" are in 4 columns instead of 1 (values are column names).
# 
# 3-the image_predictions dataframe should be reshaped because values are column names.
# 
# 2-twitter_api dataframes should be merged to the twitter_archive df as it's not an observational unit.

# # Cleaning Data:

# In[1706]:


#making copies of all three dataframes before cleaning
clean_tw_arch=twitter_archive.copy()
clean_img_pred=image_predictions.copy()


# ### quality:

# ##### define: 
# *many missing values in in_reply_to_status_id, in_reply_to_user_id, retweeted_status_id, retweeted_status_user_id and retweeted_status_timestamp columns.
# the solution is to drop these columns since they are irrelevant.

# ##### code:

# In[1707]:


clean_tw_arch.drop(columns=['in_reply_to_status_id', 'in_reply_to_user_id', 'retweeted_status_id', 'retweeted_status_user_id','retweeted_status_timestamp'],inplace=True)


# ##### test:

# In[1708]:


clean_tw_arch.columns


# ##### define:
# the "+0000" in the timestamp column can be removed using replace method

# ##### code:

# In[1709]:


clean_tw_arch.timestamp=clean_tw_arch.timestamp.str.replace('\+0000','')


# ##### test:

# In[1710]:


clean_tw_arch.head()


# ##### define:
# timestamp is string instead of datetime object.
# I will convert it using pandas to_datetime 

# ##### code:

# In[1711]:


clean_tw_arch.timestamp=pd.to_datetime(clean_tw_arch.timestamp)


# ##### test:

# In[1712]:


clean_tw_arch.timestamp.dtype
# https://stackoverflow.com/questions/29206612/difference-between-data-type-datetime64ns-and-m8ns


# ##### define:
# "None" instead of Nan in dog breeds columns and name column can be replaced using method "replace"

# In[1713]:


dog_none=clean_tw_arch.loc[:-1,'name':]
for col in dog_none.columns:
    clean_tw_arch[col].replace('None',np.nan,inplace=True)


# ##### test:

# In[1714]:


clean_tw_arch.sample(10)


# ##### define:
# the source column has almost the same value for all entries and since we already know the source, the sensible solution is to drop this column.

# ##### code:

# In[1715]:


clean_tw_arch.drop(columns='source',inplace=True)


# ##### test:

# In[1716]:


clean_tw_arch.columns


# ##### define:
# in the poject requiremnets it's stated that we want only tweets with images, so I will drop any tweet without an image using query.
# then I will merge the jpg_url from the clean_img_pred df to clean_tw_arch df,then will drop any tweet that has no image.

# ##### code:

# In[1717]:


clean_tw_arch=pd.merge(clean_tw_arch,clean_img_pred[['tweet_id','jpg_url']],on='tweet_id',how='left')
clean_tw_arch= clean_tw_arch.query('jpg_url == jpg_url')
# source: https://stackoverflow.com/questions/32207264/pandas-query-none-values


# ##### test:

# In[1718]:


clean_tw_arch.jpg_url.isnull().sum()


# ##### define:
# 55 dogs names are "a", since these data is unimportant and can't be retrieved from text without errors, I choosed to replace all these dog names with NaN.

# ##### code:

# In[1719]:


clean_tw_arch.name.replace('a',np.nan,inplace=True)


# ##### test

# In[1720]:


clean_tw_arch.query('name=="a"')


# ##### define:
# some rating_numerator values are less than 10, this means these people didn't use the weratedogs default rating system so the apropriate solution is to add 10 to all of these values.
# this will make all ratings less than 10 consistent with the rest of the ratings.
# the issues with these inconsistent ratings numerators and denomenators gives me no other choice but to extract it again from text using regex. 

# ##### code:

# In[1721]:


clean_tw_arch.rating_numerator=clean_tw_arch.text.str.extract('(\d+\.?\d?\d?)\/\d{1,3}',expand=False).astype(float)


# ##### test:

# In[1722]:


clean_tw_arch.rating_numerator.sort_values()


# ### This obviously didn't solve the problem, so I have to investigate more..

# In[1723]:


clean_tw_arch.query('rating_numerator>20').shape


# So, 20 values need cleaning to make data consistent, let's have a closer look at these ratings.

# In[1724]:


clean_tw_arch.query('rating_numerator>20')


# the dog Sam rating isn't correctly extracted so I have to change it, yet after looking closer, the dog sam doesn't have a rating so I choose to drop its row from the dataframe.
# also I noticed that entry which has a rating of 420/10 isn't a dog, so I choose to drop this row aswell.
# additionally the rating for atticus might be problematic as an outlier.

# In[1725]:


clean_tw_arch.drop([516,2074,979],inplace=True)


# I noticed that when the denominator is greater than 10, this means this rating is for a group of dogs, so I choosed to subtract the denominator from the numerator, then divide by the denominator divided by 10, and then add 10, this will give us the mean rating for every dog in the group.

# In[1726]:


incon_ratings=clean_tw_arch.query('rating_numerator>20').copy()


# In[1727]:


incon_ratings.rating_numerator=(incon_ratings.rating_numerator-incon_ratings.rating_denominator)/(incon_ratings.rating_denominator/10)+10


# In[1728]:


incon_ratings


# now I will drop these rows from the clean_tw_arch df and then add the corrected df (incon_ratings)

# In[1729]:


clean_tw_arch=clean_tw_arch.query('rating_numerator<=20')


# In[1730]:


clean_tw_arch=clean_tw_arch.append(incon_ratings,sort=False)


# now there's no need for the denominator column as all of its values are supposed to be 10. so I will drop it.

# In[1731]:


clean_tw_arch.drop(columns='rating_denominator',inplace=True)


# In[1732]:


clean_tw_arch.query('rating_numerator<5')


# Wow, some people actually don't like their dogs, this is strange.

# ##### test:

# In[1733]:


clean_tw_arch.query("rating_numerator>20")


# ### tidiness:

# ##### define:
# "doggo", "floffer", "puppo" "pupper" are in 4 columns instead of 1. this can be solved using the melt function.

# ##### code:

# In[1734]:


clean_tw_arch=pd.melt(clean_tw_arch,id_vars=['tweet_id', 'timestamp','text', 'expanded_urls',
       'rating_numerator','name','jpg_url'],value_name='breed').drop(columns='variable',axis=1)


# ##### test:

# In[1735]:


clean_tw_arch.breed.value_counts()


# ##### define:
# in image_predictions df (p1,p2,p3) , (p1_conf,p2_conf_p3_conf) and (p1_dog,p2_dog,p3_dog) should be reshaped using wide_to_long function.
# 
# source: https://nfpdiscussions.udacity.com/t/weratedogs-project-wide-to-long-reshaping/33037/4

# ##### code:

# In[1736]:


# Renaming the dataset columns
clean_img_pred.columns = ['tweet_id', 'jpg_url', 'img_num', 
       'prediction_1', 'confidence_1', 'breed_1',
       'prediction_2', 'confidence_2', 'breed_2',
       'prediction_3', 'confidence_3', 'breed_3']
# Reshaping the dataframe
clean_img_pred = pd.wide_to_long(clean_img_pred, stubnames=['prediction', 'confidence', 'breed'], 
    i=['tweet_id', 'jpg_url', 'img_num'], j='prediction_level', sep="_").reset_index()


# ##### test:

# In[1737]:


clean_img_pred.head()


# ##### define:
# the twitter_archive and twitter_api dataframes should be merged using merge function.

# ##### code:

# In[1738]:


master_df=pd.merge(clean_tw_arch,api_df,on=['tweet_id'],how='left')


# ##### test:

# In[1739]:


master_df.head()


# # Storing Data:

# In[1740]:


master_df.to_csv("twitter_archive_master.csv",index=False)
clean_img_pred.to_csv('clean_image_pred.csv',index=False)


# # Visualizing & Analyzing Data:

# In[1741]:


master_df.groupby('breed').retweet_count.mean().sort_values().plot(kind='bar',title='Average retweet count per breed',figsize=(8,8));


# This bar plot shows us that doggo breed has the most retweet count per average.

# In[1742]:


master_df.groupby('breed').favorite_count.mean().sort_values().plot(kind='bar',title='Average favorite count per breed',figsize=(8,8));


# This bar plot shows that "puppo" breed has the most favorite count per average which can indicate that twitter users prefer this breed more than other breeds.
# we can also observe that average retweet count is far lower than the average favorite count which indicates that most people choose to favorite a tweet rather than retweet it.

# In[1743]:


plt.figure(figsize=(8,8))
plt.scatter(master_df['retweet_count'],master_df['favorite_count'])
plt.xlabel('retweet count')
plt.ylabel('favorite count')
plt.title('relation between retweet count and favorite count');


# This plot shows a very strong relationship between retweet count and favourite count.

# In[1744]:


master_df.describe()


# In[1745]:


master_df.rating_numerator.describe()


# This shows interestingly that most rating numerators are close to 10.
# surprisingly, no numerators exceeded 15.
# additionally it shows that sometime people don't like their dogs because the minimum numerator is 0.

# In[1748]:


master_df.groupby('breed').rating_numerator.mean().sort_values().plot(kind='bar',title="Rating numerator per do breed",figsize=(8,8))


# This bar plot shows that puppo foofer, doggo have very similar rating numerator per average.
