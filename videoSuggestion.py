def assess_relevance(user_query, video_summary):
    if user_query.lower() in video_summary.lower():
        return True
    return False


def suggest_best_video(videos, user_query):
    if user_query.strip() == "":
        best_video = None
        best_score = 0
        for video in videos:
            score = len(video['summary'])
            if "tutorial" in video['summary'].lower():
                score += 20
            elif "review" in video['summary'].lower():
                score += 15
            elif "how-to" in video['summary'].lower():
                score += 10

            if score > best_score:
                best_score = score
                best_video = video

        return best_video

    else:
        relevant_videos = []
        
        for video in videos:
            if assess_relevance(user_query, video['summary']):
                relevant_videos.append(video)

        if not relevant_videos:
            return None
        
        best_video = None
        best_score = 0
        for video in relevant_videos:
            score = len(video['summary'])
            if "tutorial" in video['summary'].lower():
                score += 20
            elif "review" in video['summary'].lower():
                score += 15
            elif "how-to" in video['summary'].lower():
                score += 10

            if score > best_score:
                best_score = score
                best_video = video

        return best_video
