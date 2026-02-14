from models.intent import PlayIntent


def build_platform_url(intent: PlayIntent) -> str | None:
    if intent.platform == "youtube":
        return "https://www.youtube.com/results?search_query=" + intent.query.replace(
            " ", "+"
        )

    if intent.platform == "spotify":
        return "https://open.spotify.com/search/" + intent.query.replace(" ", "%20")

    return None
