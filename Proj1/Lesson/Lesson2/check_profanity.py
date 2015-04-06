import urllib

def read_text():
    quotes = open("/home/patrick/Code/Udacity/Proj1/Lesson/Lesson2/movie_quotes.txt")
    contents_of_file = quotes.read()

    quotes.close()

    check_profanity(contents_of_file)

def check_profanity(text_to_check):
    connection = urllib.urlopen("http://www.wdyl.com/profanity?q="+text_to_check)
    output = connection.read()
    
    if "true" in output:
        print("Profanity Alert!")
    elif "false" in output:
        print("No profanity here.")
    else:
        print("Could not scan document properly.")

    connection.close()

read_text()
