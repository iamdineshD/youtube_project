import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import time
from isodate import parse_duration
from dateutil import parser
import pymongo as py
import mysql.connector
from streamlit_option_menu import option_menu

api_key = 'AIzaSyDOo6bnJ2XEHI8-VDouVMg_tmYQ_9PPKI4'
# channel_id = 'UCnVpEcfut-Bu1IFmQr7vRuw'  # deep Matrix
youtube = build('youtube', 'v3', developerKey=api_key)

# channel details
def get_channel_stats(channel_id):
    channel_name = []
    request = youtube.channels().list(
        id=channel_id, part='snippet,statistics,contentDetails')
    data = request.execute()
    for i in range(len(data['items'])):
        particular_data = dict(channel_name=data['items'][i]['snippet']['title']
                               , channel_id=data['items'][i]['id']
                               , channel_description=data['items'][i]['snippet']['description']
                               , channel_view=int(data['items'][i]['statistics']['viewCount'])
                               , vedio_count=int(data['items'][i]['statistics']['videoCount'])
                               , playlist_id=data['items'][i]['contentDetails']['relatedPlaylists']['uploads']
                               , subscriberCount=int(data['items'][i]['statistics']['subscriberCount']),)

        channel_name.append(particular_data)
    return channel_name
# channel_info = get_channel_stats(channel_id)

# to get Playlist details
def get_playlist_details(channel_id,playlist_id):
  
  playlist_details=[]
  request = youtube.playlists().list(
      part="snippet,contentDetails",
      channelId=channel_id,
      maxResults=25
  )
  response = request.execute()
  for item in response['items']:
     playlist_info=dict(playlist_id=playlist_id,
                        channel_id=item['snippet']['channelId'],
                        playlist_title=item['snippet']['title'],
                        item_count=int(item['contentDetails']['itemCount']),)
     playlist_details.append(playlist_info)
  return playlist_details

# playlist_info=get_playlist_details(channel_info[0]['channel_id'],channel_info[0]['playlist_id'])

# to get video_id function
def get_video_ids_details(playlist_info):
    video_ids = []
    request = youtube.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=playlist_info,
        maxResults=50)
    response_playlist = request.execute()

    for i in range(len(response_playlist['items'])):
        video_ids.append(response_playlist['items'][i]['contentDetails']['videoId'])

    next_page_token = response_playlist.get('nextPageToken')
    more_page = True

    while more_page:
        if next_page_token is None:
            more_page = False
        else:
            request = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_info,
                maxResults=50, pageToken=next_page_token
            )
            response_playlist = request.execute()

            for i in range(len(response_playlist['items'])):
                video_ids.append(response_playlist['items'][i]['contentDetails']['videoId'])

            next_page_token = response_playlist.get('nextPageToken')

    return video_ids
# video_ids = get_video_ids_details(playlist_info[0]['playlist_id'])

#to convert durtion str to seconds
def duration_str(duration):
  duration_str = duration
  duration_td = parse_duration(duration_str)
  duration_sec = duration_td.total_seconds()
  return duration_sec

#to change publishedAt to dateformat

def change_publishedAt(publishedAt):
  formatted_date=parser.parse(publishedAt)
  return formatted_date.strftime('%Y-%m-%d %H:%M:%S')

# to get vedio details
def get_video_details(video_ids):
    video_details = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i + 50]))
        get_videos = request.execute()
        for i in range(len(get_videos['items'])):
            videoo_id = {'video_id': get_videos['items'][i]['id'],
                         'video_name': get_videos['items'][i]['snippet']['title'],
                         'video_description': get_videos['items'][i]['snippet']['description'],
                         'PublishedAt': change_publishedAt(get_videos['items'][i]['snippet']['publishedAt']),
                         'view_count': int(get_videos['items'][i]['statistics']['viewCount']),
                         'like_count': int(get_videos['items'][i]['statistics']['likeCount']),
                         'Dislike_count': int(get_videos['items'][i]['statistics']['dislikeCount'] if 'dislikeCount' in get_videos['items'][i]['statistics'] else '0'),
                         'Favorite_count': int(get_videos['items'][i]['statistics']['favoriteCount']),
                         'Comment_count':int( get_videos['items'][i]['statistics']['commentCount'] if 'commentCount' in get_videos['items'][i]['statistics'] else '0'),
                         'Duration':duration_str( get_videos['items'][i]['contentDetails']['duration']),
                        #  'Thumbnails': get_videos['items'][i]['snippet']['thumbnails'],
                         'Caption_status': get_videos['items'][i]['contentDetails']['duration'],}
                        #  'Tags': [get_videos['items'][i]['snippet']['tags'] if 'tags' in get_videos['items'][i][
                            #  'snippet'] else 'no tags'] ,}
            video_details.append(videoo_id)
    return video_details
# video_info = get_video_details(video_ids)

# comment details
def get_comment_details(video_ids):
    all_comments = []
    for video_id in video_ids:
        try:
            request = youtube.commentThreads().list(part="snippet,replies", 
                                                    videoId=video_id, 
                                                    maxResults=50)
            response = request.execute()
            for i in range(len(response['items'])):
                comment_details = {'video_id': video_id,
                                   'comment_id': response['items'][i]['snippet']['topLevelComment']['id'],
                                   'comment_text': response['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'],
                                   'comment_author': response['items'][i]['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                   'comment_publishedAct':change_publishedAt(response['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt']),}
                all_comments.append(comment_details)
        except:
            pass
    return all_comments
# comment_info = get_comment_details(video_ids)

#main function
def get_main(channel_id):

    channel_info = get_channel_stats(channel_id)
    playlist_info = get_playlist_details(channel_info[0]['channel_id'],channel_info[0]['playlist_id'])
    video_ids = get_video_ids_details(playlist_info[0]['playlist_id'])
    video_info = get_video_details(video_ids)
    comment_info = get_comment_details(video_ids)

    data = {'channel_name': channel_info,
            'playlist_id': playlist_info,
            'video_id': video_info,
            'comments': comment_info}

    return data
# channel_id = 'UC38PDlv1vGvi8djaFf4fdKA'    
# channel_in=get_main(channel_id)

# print(channel_in)

#store to mongodb

uri='mongodb+srv://dinesh:PassKing01@cluster0.kxn1kk9.mongodb.net/?retryWrites=true&w=majority'
# uri='mongodb://localhost:27017'
connection=py.MongoClient(uri)
list_of_db=connection.list_database_names()
print(list_of_db)
#to create db
youtube_db=connection.youtube_channel_datas
# to create collection
try:
   collection=youtube_db.create_collection('information')
except:
    pass
collection=youtube_db.get_collection('information')
# # to insert value
# try:
#    data_insert=collection.insert_one(channel_in)
# except:
#     pass

# to get data
# mongo_data=collection.find_one({'channel_name.channel_id':channel_id},{'_id':0})
# print(mongo_data)

# to connect sql
conn=mysql.connector.connect(host='localhost',
                             user='root',
                             passwd='PassKing01')
mycursor=conn.cursor()
print(conn)
# create database
mycursor.execute('create database if not exists youtube_harvesting')
mycursor.execute('use youtube_harvesting')

# channel_table
create_channel_table='create table if not exists channel(channel_id varchar(50),channel_name varchar(50),channel_description text,channel_view bigint,video_count int,playlist_id varchar(50),subscriberCount int);'
mycursor.execute(create_channel_table)

# playlist_table
create_playlist_table='create table if not exists playlist(playlist_id varchar(100),channel_id varchar(50),playlist_title varchar(255),item_count int);'
mycursor.execute(create_playlist_table)

# create videos table
create_videos_table='create table if not exists videos(video_id varchar(255),video_name varchar(255),video_description text,publishedAt DateTime,view_count int,like_count int,Dislike_count int,Favorite_count int,Comment_count int,Duration int,Caption_status varchar(255),playlist_id varchar(50),unique (video_id));'
mycursor.execute(create_videos_table)

# create comment table
create_comment_table='create table if not exists comment(video_id varchar(255),comment_id varchar(50),comment_text text,comment_author varchar(255),comment_publishedAct DateTime,unique(comment_id));'
mycursor.execute(create_comment_table)

# insert data into respected table
def commit_sql(mongo_data):
    channel_data_query='insert into channel(channel_name, channel_id, channel_description, channel_view, video_count, playlist_id, subscriberCount) values (%s,%s,%s,%s,%s,%s,%s);'
    c_data=tuple(mongo_data['channel_name'][0].values())
    mycursor.execute(channel_data_query,c_data)
    conn.commit()  
    
    time.sleep(3)

    playlist_data_query='insert into playlist(playlist_id,channel_id,playlist_title,item_count) values(%s,%s,%s,%s);'
    playlist_data=mongo_data['playlist_id']

    for i in playlist_data:
        p_data=tuple(i.values())
        mycursor.execute(playlist_data_query,p_data)
    conn.commit()  
    
    time.sleep(3)

    
    video_detail_query='insert into videos(video_id,video_name,video_description,publishedAt,view_count,like_count,Dislike_count,Favorite_count,Comment_count,Duration,Caption_status,playlist_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
    video_details=mongo_data['video_id']
    d=mongo_data['playlist_id'][0]['playlist_id']
    for i in video_details:
        v_data=tuple(i.values())
        l=list(v_data)
        l.append(d)
        v=tuple(l)

        mycursor.execute(video_detail_query,v)
    conn.commit()      
    
    time.sleep(3)

    comment_insert_query='insert into comment(video_id,comment_id,comment_text,comment_author,comment_publishedAct)values(%s,%s,%s,%s,%s);'
    comment_data=mongo_data['comments']
    for i in comment_data:
        c_data=tuple(i.values())
        mycursor.execute(comment_insert_query,c_data)
    conn.commit()      
    
# commit_sql(mongo_data)
# streamlit connect
with st.sidebar:
    selected=option_menu('YOUTUBE HARVESTING AND WAREHOUSING',['DATA COLLECTION','SELECT AND STORE','MIGRATION OF DATA','DATA ANALYSIS'],default_index=0)

if selected=='DATA COLLECTION':
    df=st.table({'channel_name':["Error Makes Clever Academy",'Eruma Saani','Finally','Finally Raj','G M Dance Centre','Mic Set','Nakkalites FZone','STRIKER','Village Cooking Channel','Deep Matrix','Narikootam'],
                     'channel_id':['UCwr-evhuzGZgDFrq_1pLt_A','UCPyFYlqbkxkWX_dWCg0eekA','UCi3o8sgPl4-Yt501ShuiEgA','UCCbeAlV68kirK2LFLMAimOg','UCPbUTEjdU04ChIZfi53jczw','UC5EQWvy59VeHPJz8mDALPxg','UCpnJuQkNm9j9R7LCqWtf56g','UC0B7Snfw0Yg3OwpDuyW7PGQ','UCk3JZr7eS3pg5AGEvBdEvFg','UCnVpEcfut-Bu1IFmQr7vRuw','UC38PDlv1vGvi8djaFf4fdKA']})
    

if selected=='SELECT AND STORE':
     channel_id=st.text_input('enter the channel_id')
     if st.button('STORE DATA IN MONGODB'):
         if channel_id:
            channel_in=get_main(channel_id)
            insert_data=collection.insert_one(channel_in)
            get_data=collection.find_one({'channel_name.channel_id':channel_id},{'_id':0})
            st.write('Data stored in MonogDB')
            st.json(get_data)
         else:
            st.error('Enter the valid_channel_id')

if selected=='MIGRATION OF DATA':
    st.title('DATA MIGRATION ZONE')
    get_channel_name=collection.find({},{'channel_name.channel_name':1,'_id':0})
    x=list(get_channel_name)
    list_of_channel_name=[]
    for i in range(0,len(x)):
        list_of_channel_name.append(x[i]['channel_name'][0]['channel_name'])
    select_channel_name=st.selectbox('select channel_name',list_of_channel_name)
    st.write('Click below to migrate data to MySQL from mongoDB')
    if st.button('migrate to sql'):
       mongo_data=collection.find_one({'channel_name.channel_name':select_channel_name},{'_id':0})
       migrate=commit_sql(mongo_data)
       st.success('migrate completed successfull')

if selected=='DATA ANALYSIS':
    st.title('Data Analysis')
    data=st.selectbox('Select a question:',['1.What are the names of all the videos and their corresponding channels?',
                                      '2.Which channels have the most number of videos, and how many videos do they have?',
                                      '3.What are the top 10 most viewed videos and their respective channels?',
                                      '4.How many comments were made on each video, and what are their corresponding video names?',
                                      '5.Which videos have the highest number of likes, and what are their corresponding channel names?',
                                      '6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                                      '7.What is the total number of views for each channel, and what are their corresponding channel names?',
                                      '8.What are the names of all the channels that have published videos in the year 2022?',
                                      '9.What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                                      '10.Which videos have the highest number of comments and what are their corresponding channel names?'])
    
    
    if data=='1.What are the names of all the videos and their corresponding channels?':
        q1='select v.video_name,c.channel_name from videos as v inner join channel as c on v.playlist_id=c.playlist_id order by channel_name asc;'
        mycursor.execute(q1)
        result1=mycursor.fetchall()
        columns=['video_name','channel_name']
        df=pd.DataFrame(result1,columns=columns)
        st.table(df)

    if data=='2.Which channels have the most number of videos, and how many videos do they have?':
        q2=""" select channel_name,video_count from channel order by video_count desc; """
        mycursor.execute(q2)
        result2=mycursor.fetchall()
        columns=['channel_name','video_count']
        df=pd.DataFrame(result2,columns=columns)
        st.table(df)

    if data=='3.What are the top 10 most viewed videos and their respective channels?':
        q3='select c.channel_name,v.video_name,v.view_count from videos as v inner join channel as c on v.playlist_id=c.playlist_id order by v.view_count desc limit 10;'
        mycursor.execute(q3)
        result3=mycursor.fetchall()
        columns=['channel_name','video_name','view_count']
        df=pd.DataFrame(result3,columns=columns)
        st.table(df)

    if data=='4.How many comments were made on each video, and what are their corresponding video names?':
        q4='select video_name,Comment_count from videos order by video_name asc;'
        mycursor.execute(q4)
        result4=mycursor.fetchall()
        columns=['video_name','Comment_count']
        df=pd.DataFrame(result4,columns=columns)
        st.table(df)

    if data=='5.Which videos have the highest number of likes, and what are their corresponding channel names?':
        q5='select channel.channel_name,videos.video_name,videos.like_count from videos inner join channel on videos.playlist_id=channel.playlist_id order by videos.like_count desc;'
        mycursor.execute(q5)
        result5=mycursor.fetchall()
        columns=['channel_name','video_name','like_count']
        df=pd.DataFrame(result5,columns=columns)
        st.table(df)

    if data=='6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        q6='select video_name,like_count,Dislike_count from videos order by like_count desc;'
        mycursor.execute(q6)
        result6=mycursor.fetchall()
        columns=['video_name','like_count','Dislike_count']
        df=pd.DataFrame(result6,columns=columns)
        st.table(df)

    if data=='7.What is the total number of views for each channel, and what are their corresponding channel names?':
        q7='select channel_name,channel_view from channel order by channel_name asc;'
        mycursor.execute(q7)
        result7=mycursor.fetchall()
        columns=['channel_name','channel_viewsS']
        df=pd.DataFrame(result7,columns=columns)
        st.table(df)

    if data=='8.What are the names of all the channels that have published videos in the year 2022?':
        q8='select channel.channel_name,videos.video_name, videos.publishedAt from videos inner join channel on videos.playlist_id=channel.playlist_id where extract(year from publishedAt) between "2022-01-01" and "2022-12-31" order by publishedAt asc;'
        mycursor.execute(q8)
        result8=mycursor.fetchall()
        columns=['channel_name','videos_name','publishedAt']
        df=pd.DataFrame(result8,columns=columns)
        st.table(df)

    if data=='9.What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        q9='select channel.channel_name,videos.video_name,avg(videos.Duration) from videos inner join channel on videos.playlist_id=channel.playlist_id group by channel_name order by channel_name asc;'
        mycursor.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
        mycursor.execute(q9)
        result9=mycursor.fetchall()
        columns=['channel_name','videos_name','AVG_Duration']
        df=pd.DataFrame(result9,columns=columns)
        st.table(df)

    if data=='10.Which videos have the highest number of comments and what are their corresponding channel names?':
        q10='select channel.channel_name,videos.video_name,videos.Comment_count from videos inner join channel on videos.playlist_id=channel.playlist_id order by Comment_count desc;'
        mycursor.execute(q10)
        result10=mycursor.fetchall()
        columns=['channel_name','videos_name','comment_count']
        df=pd.DataFrame(result10,columns=columns)
        st.table(df)
        

