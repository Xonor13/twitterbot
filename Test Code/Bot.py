import tweepy, time, sys, datetime, random

class Bot:
    def RunMainBot(self, botInfo):
        print("\nRUNNING MAIN BOT-----------------", datetime.datetime.now().strftime("%H:%M:%S"))
        while True:
            display_counter = 1
            new_tweet_counter = 0

            for current_search in botInfo.search_words:
                filtered_search = current_search + " -filter:retweets -filter:replies"
                overflow_count = 0
                current_search_counter = 0
                already_retweeted_counter = 0

                #Checks the amount of followers and decides whether or not to purge some
                self.CheckFollowerCount(botInfo)
                self.DeleteTweets(botInfo)
                self.RemoveLikes(botInfo)

                print("\n--Search #", display_counter,"--", datetime.datetime.now().strftime("%H:%M:%S"))

                while current_search_counter < botInfo.TWEET_LIMIT_PER_SEARCH and overflow_count <= botInfo.OVERFLOW_SEARCH_REPEAT:
                    if overflow_count != 0:
                        print("Overflow Mode----")
                        time.sleep(5)

                    #grabs all the tweets and decides whether or not to like, retweet, or follow them
                    for tweet in tweepy.Cursor(botInfo.api.search, q=filtered_search, lang="en", since=botInfo.date_since, tweet_mode = "extended").items(botInfo.TWEET_SEARCH_LIMIT + (overflow_count * botInfo.OVERFLOW_EXTRA_SEARCHES)):
                        if current_search_counter > botInfo.TWEET_LIMIT_PER_SEARCH:
                            print("Tweet limit reached for search")
                            break

                        user = tweet.user
                        id = tweet.id
                        url = 'https://twitter.com/' + user.screen_name +  '/status/' + str(id)

                        try:
                            text = tweet.retweeted_status.full_text.lower()
                        except:
                            text = tweet.full_text.lower()

                        #checks the tweet for any competition rules that can't work with this bot
                        tweet_passes_filter = True
                        for word_filter in botInfo.filtered_words:
                            if word_filter in text:
                                tweet_passes_filter = False

                        #check for bot spotters or other annoying users
                        for user_filter in botInfo.filtered_users:
                            if user_filter in user.screen_name.lower() or user_filter in user.name.lower():
                                tweet_passes_filter = False
                                print("\tBot Spotter avoided: " + user.screen_name)

                        #only likes, retweets, or follows if the tweet passes all the filters
                        if tweet_passes_filter == True:
                            retweet_status = self.Retweet(botInfo, tweet, text)

                            if retweet_status != 0:
                                self.Follow(botInfo, tweet, text, user)
                                self.Tag(botInfo, text, user, id)
                                self.CashApp(botInfo, text, user, id)
                                self.Like(tweet, text)
                                current_search_counter += 1
                                new_tweet_counter += 1
                            else:
                                already_retweeted_counter += 1

                    overflow_count += 1

                    if current_search_counter == 0:
                        print("\tAll tweets failed filter!")
                    else:
                        print("\tAlready Retweeted: ", already_retweeted_counter)
                        print("\tCurrent Search - New Tweets: ", current_search_counter)
                    if current_search_counter == None:
                        print("ERROR: TWEET COUNTER = NONE")

                display_counter += 1

            print("\nCurrent Run Finished----")
            print ("Time: ", datetime.datetime.now().strftime("%H:%M:%S"))
            print ("New Tweets: ", new_tweet_counter)
            print ("Total Tweets: ", botInfo.total_tweets_since_start)
            time.sleep(botInfo.SEARCH_TIMER)

    #This is a backup version of the bot that does not follow users when the follow limit is reached
    def BackupBot(self, botInfo):
        print("\nRUNNING IN LIKE AND RETWEET ONLY MODE--------------", datetime.datetime.now().strftime("%H:%M:%S"))
        custom_filtered_words = botInfo.filtered_words + ["follow"]
        switch_counter = 0

        self.DeleteTweets(botInfo)
        self.RemoveLikes(botInfo)

        time.sleep(10)
        while True:
            display_counter = 1
            new_tweet_counter = 0

            if switch_counter >= botInfo.RUNS_BEFORE_SWITCH:
                self.RunMainBot(botInfo)

            #runs through all custom searches and finds tweets within this search
            for current_search in botInfo.search_words:
                filtered_search = current_search + " -filter:retweets -filter:replies"
                overflow_count = 0
                current_search_counter = 0
                already_retweeted_counter = 0

                print("\n--Search #", display_counter,"--", datetime.datetime.now().strftime("%H:%M:%S"))

                while current_search_counter < botInfo.TWEET_LIMIT_PER_SEARCH and overflow_count <= botInfo.OVERFLOW_SEARCH_REPEAT:
                    if overflow_count != 0:
                        print("Overflow Mode----")
                        time.sleep(5)

                    #grabs all the tweets and decides whether or not to like or retweet (following has been removed)
                    for tweet in tweepy.Cursor(botInfo.api.search, q=filtered_search, lang="en", since=botInfo.date_since, tweet_mode = "extended").items(botInfo.TWEET_SEARCH_LIMIT + (overflow_count * botInfo.OVERFLOW_EXTRA_SEARCHES)):
                        if current_search_counter > botInfo.TWEET_LIMIT_PER_SEARCH:
                            print("Tweet limit reached for search")
                            break

                        user = tweet.user
                        id = tweet.id
                        url = 'https://twitter.com/' + user.screen_name +  '/status/' + str(id)

                        try:
                            text = tweet.retweeted_status.full_text.lower()
                        except:
                            text = tweet.full_text.lower()

                        #checks the tweet for any competition rules that can't work with this bot
                        tweet_passes_filter = True
                        for word_filter in botInfo.filtered_words:
                            if word_filter in text:
                                tweet_passes_filter = False

                        #check for bot spotters or other annoying users
                        for user_filter in botInfo.filtered_users:
                            if user_filter in user.screen_name.lower() or user_filter in user.name.lower():
                                tweet_passes_filter = False
                                print("\tBot Spotter avoided: " + user.screen_name)

                        #only likes or retweets if the tweet passes all the filters
                        if tweet_passes_filter == True:
                            retweet_status = self.Retweet(botInfo, tweet, text)

                            if retweet_status != 0:
                                self.Tag(botInfo, text, user, id)
                                self.CashApp(botInfo, text, user, id)
                                self.Like(tweet, text)
                                current_search_counter += 1
                                new_tweet_counter += 1
                            else:
                                already_retweeted_counter += 1

                    overflow_count += 1

                    if current_search_counter == 0:
                        print("\tAll tweets failed filter!")
                    else:
                        print("\tAlready Retweeted: ", already_retweeted_counter)
                        print("\tCurrent Search - New Tweets: ", current_search_counter)
                    if current_search_counter == None:
                        print("ERROR: TWEET COUNTER = NONE")

                display_counter += 1

            switch_counter += 1
            print("\nCurrent Run Finished----")
            print ("Time: ", datetime.datetime.now().strftime("%H:%M:%S"))
            print ("New Tweets: ", new_tweet_counter)
            print ("Total Tweets: ", botInfo.total_tweets_since_start)
            time.sleep(botInfo.LIKE_RETWEET_ONLY_TIMER)

    def TestCodeOne(self, botInfo):
        test_search = "retweet" + " -filter:retweets -filter:replies"

        for tweet in tweepy.Cursor(botInfo.api.search, q=test_search, lang="en", since=botInfo.date_since, tweet_mode = "extended").items(1):
            user = tweet.user
            id = tweet.id
            url = 'https://twitter.com/' + user.screen_name +  '/status/' + str(id)

            try:
                text = tweet.retweeted_status.full_text.lower()
            except:
                text = tweet.full_text.lower()

            self.CheckLimits(botInfo)
            #print("User - screen_name: " + user.screen_name)
            #print("URL: " + url)

    def CheckLimits(self, botInfo):
        current_user = botInfo.api.get_user(botInfo.USERNAME)
        friend_count = current_user.friends_count
        tweet_count = current_user.statuses_count

        self.CheckFriendCount(botInfo, friend_count)
        self.DeleteTweets(botInfo, tweet_count)
        self.RemoveLikes(botInfo, tweet_count)

    def CheckFriendCount(self, botInfo, friend_count):

        #checks follower count to remove followers if over limit
        if(friend_count >= botInfo.FRIEND_LIMIT):
            #will remove followers until it reaches a lower limit threshold
            while(friend_count >= botInfo.FRIEND_RESET_LIMIT):
                friend_count = botInfo.api.get_user(botInfo.USERNAME).friends_count
                friend_list = botInfo.api.friends_ids()

                print("REMOVING FOLLOWERS: ", friend_count)

                for friend in friend_list[len(friend_list)-101:]:
                    try:
                        botInfo.api.destroy_friendship(friend)
                    except tweepy.TweepError as e:
                        print("ERROR unfollowing")
                        print(e)

    def Like(self, tweet, text):
        if "like" in text or "fav" in text:
            try:
                tweet.favorite()
                print('\tLiked')
            except tweepy.TweepError as e:
                DoNothing = None

    def Retweet(self, botInfo, tweet, text):
        if "retweet" in text or "rt" in text:
            if not tweet.retweeted:
                try:
                    tweet.retweet()
                    print("\tRetweeted")
                    botInfo.total_tweets_since_start += 1
                    return 1
                except tweepy.TweepError as e:
                    return 0
        return 0

    def Follow(self, botInfo, tweet, text, user):
        if "follow" in text:
            try:
                to_follow = [user.screen_name] + [i['screen_name'] for i in tweet.entities['user_mentions']]

                for screen_name in list(set(to_follow)):
                    botInfo.api.create_friendship(screen_name)
                    print('\t' + "Followed: " + screen_name)

            except tweepy.TweepError as e:
               if("161" in e.response.text):
                   print("Follow limit reached!")
                   self.BackupBot(botInfo)
               else:
                   print(e)
                   print("ERROR Following")
        blah = 0

    def Tag(self, botInfo, text, user, id):
        if "tag" in text:
            people_to_tag = []
            tag_index = text.index("tag")

            if text.find("1", tag_index) or text.find("one", tag_index):
                people_to_tag += [followers_list[0]]
                self.TagPeople(botInfo, user, people_to_tag, id)
            elif text.find("2", tag_index) or text.find("two", tag_index):
                people_to_tag += [followers_list[0]] + [followers_list[1]]
                self.TagPeople(botInfo, user, people_to_tag, id)
            elif text.find("3", tag_index) or text.find("three", tag_index):
                people_to_tag += [followers_list[0]] + [followers_list[1]] + [followers_list[2]]
                self.TagPeople(botInfo, user, people_to_tag, id)
            else:
                people_to_tag += [followers_list[0]]
                self.TagPeople(botInfo, user, people_to_tag, id)

    def TagPeople(self, botInfo, user, id):
        reply = "@" + user.screen_name + "\n"
        for people in botInfo.tag_list:
            reply += "@" + people.screen_name + " "

        random_reply = random.randint(0,2)
        if random_reply == 0:
            reply += "\nDone!"
        elif random_reply == 1:
            reply += "\nGL!"

        reply = self.CashAppTag(botInfo, text, reply)

        botInfo.api.update_status(reply, in_reply_to_status_id=id)
        print(reply)

    def CashApp(self, botInfo, text, user, id):
        if "tag" not in text:
            if "cashapp" in text or "cash app" in text or "cashtag" in text:
                reply = "@" + user.screen_name + "\n$" + botInfo.CASHAPP
                botInfo.api.update_status(reply, in_reply_to_status_id=id)

    def CashAppTag(self, botInfo, text, reply):
        if "cashapp" in text or "cash app" in text or "cashtag" in text:
            reply += " $" + botInfo.CASHAPP

        return reply

    # delete old tweets
    def DeleteTweets(self, botInfo, tweet_count):
        if tweet_count >= botInfo.TWEET_LIMIT:
            try:
                # get all timeline tweets
                print("Deleting Tweets!")
                timeline = tweepy.Cursor(botInfo.api.user_timeline).items()
                deletion_count = 0

                for tweet in timeline:
                    tweet_count = botInfo.api.get_user(botInfo.USERNAME).statuses_count

                    if tweet_count > botInfo.TWEET_RESET_LIMIT:
                        if tweet.created_at < botInfo.DELETE_DATE:
                            print("Deleting %d: [%s] %s" % (tweet.id, tweet.created_at))
                            #api.destroy_status(tweet.id)

                            deletion_count += 1
                    else:
                        print("Tweet deletions finished")
                        break

                print("Deleted %d tweets" % (deletion_count))
            except tweepy.TweepError as e:
                print("Error deleting tweets")

    # unfavor old favorites
    def RemoveLikes(self, botInfo, tweet_count):
        if tweet_count >= botInfo.TWEET_LIMIT:
            try:
                # get all favorites
                print("Removing Likes!")
                favorites = tweepy.Cursor(botInfo.api.favorites).items()
                unfav_count = 0

                for tweet in favorites:
                    tweet_count = botInfo.api.get_user(botInfo.USERNAME).statuses_count

                    if tweet_count > botInfo.TWEET_RESET_LIMIT:
                        if tweet.created_at < botInfo.DELETE_DATE:
                            print("Unfavoring %d: [%s] %s" % (tweet.id, tweet.created_at, tweet.text))
                            #api.destroy_favorite(tweet.id)

                            unfav_count += 1
                    else:
                        print("Like removals finished!")
                        break

                print("Unfavored %d tweets" % (unfav_count))
            except tweepy.TweepError as e:
                print("Error deleting tweets")