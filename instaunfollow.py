from config import L, user_profiles


def dont_followers(chat_id):
    profile_list_dont_followers = []
    followers = []
    following = []

    for follower in user_profiles[chat_id].get('profile_data').get_followers():
        followers.append(follower.username)

    for followees in user_profiles[chat_id].get('profile_data').get_followees():
        following.append(followees.username)

    for profile in following:
        if profile not in followers:
            profile_list_dont_followers.append(profile)

    return profile_list_dont_followers


def update_followers(chat_id):
    updated_dont_followers_base = []
    new_nonfollowers_base = []

    if user_profiles[chat_id].get('base') != None:
        updated_dont_followers_base = dont_followers(chat_id)

        for profile in updated_dont_followers_base:
            if profile not in user_profiles[chat_id].get('base'):
                new_nonfollowers_base.append(profile)

        user_profiles[chat_id].update({'base' : updated_dont_followers_base})
    else:
        user_profiles[chat_id].update({'base' : dont_followers(chat_id)})

    return new_nonfollowers_base