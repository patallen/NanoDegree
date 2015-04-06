import media

toy_story = media.Movie(
        "Toy Story",
        "Story of a boy and his toys that come to life.",
        "http://upload.wikimedia.org/wikipedia/en/1/13/Toy_Story.jpg",
        "https://youtu.be/KYz2wyBy3kc"
    )
avatar = media.Movie(
        "Avatar",
        "Blue people jump around wildly.",
        "http://upload.wikimedia.org/wikipedia/en/b/b0/Avatar-Teaser-Poster.jpg",
        "https://youtu.be/cRdxXPV9GNQ"
    )
school_of_rock = media.Movie(
        "School of Rock",
        "Some goofy dude teaches kids how to live the rock life.",
        "http://upload.wikimedia.org/wikipedia/en/1/11/School_of_Rock_Poster.jpg",
        "https://youtu.be/3PsUJFEBC74"
    )
midnight_in_paris = media.Movie(
        "Midnight in Paris",
        "Going back in time to meet authors.",
        "http://upload.wikimedia.org/wikipedia/en/9/9f/Midnight_in_Paris_Poster.jpg",
        "https://youtu.be/BYRWfS2s2v4"
    )




print(toy_story.storyline)
print(avatar.storyline)
avatar.show_trailer()
