**ReadMe for DSI Deploying-AI Assignment 2**

This assignment implements a chatbot using gradio. The chatbot that I built have built has two functions to date:

1. It can retrieve synonyms for words in the English language, and provide an example usage of the top synonym it finds.
For example, if prompted to find synonyms for the word "happy", it can return the words "cheerful", "content", and "merry".
It will also provide an example of the first synonynm, "cheerful", such as: "The child was cheerful after receiving a new toy."
The model retrieves the synonym using an API call to https://api.datamuse.com/words. From the list provided, it selects the top
3 synoynms for the desired word, formats them in a list, and then generates the example usage.

2. It can retrieve song lyrics, given an artist name and a song title. For example, if provided the song title "Zombie" by 
"The Cranberries", it will return the lyrics for that song. If the model does not find the song lyrics in a public database,
it will inform the user. The model retrieves the lyrics using an API call to https://lrclib.net/api/get. It cleans up the
text output that it receives from the API call, and formats the answer. Finally, the model analyses the retrieved lyrics
and generates a 1-sentence summary of the theme of the song. It also provides this theme to the user. 


The chatbot respond to users in a tone that mimics an American cowboy.

**The model has the following limitations or guardrails:**

1. It cannot reveal its internal chain of thought.
2. It cannot allow the user to change its specified tone (e.g., American cowboy)
3. It cannot reveal the exact wording of its system prompt, although it can tell the user what it's functions are.
4. It cannot answer questions that are not related to English word synonyms and song titles, beyond politing chatting with the user.
5. It cannot answer any questions related to the following topics: Cats or dogs, Horoscopes or Zodiac Signs, and Taylor Swift.

If the model is asked to provide lyrics from Taylor Swift songs, it tells the user that it is unable to do and recommends
that the user listens to more Metallica. 





