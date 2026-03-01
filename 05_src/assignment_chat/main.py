from openai import OpenAI
from dotenv import load_dotenv
from assignment_chat.prompts import return_instructions_root
import json
import requests
from utils.logger import get_logger
import os


_logs = get_logger(__name__)

load_dotenv(".env")
load_dotenv('/Users/grahamflick/Desktop/DSI/deploying-ai/05_src/.secrets')

if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

open_ai_model = os.getenv("OPENAI_MODEL", "gpt-4")

tools = [
    {
        "type": "function",
        "name": "get_synonyms",
        "description": "This tool retrieves synonyms for a given word.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "A word in the English language.",
                },
            },
            "required": ["word"],
            "additionalProperties": False
        },
        
    },
]

def get_synonym_from_service(word:str):
    '''
    API call to get synonyms for the word.
    '''
    url = "https://api.datamuse.com/words"
    params = {
        "rel_syn":word.lower(),
    }
    response = requests.get(url, params=params)
    return response

def get_synonym_from_response(word: str, response: requests.Response) -> str:
    '''
    Returns the top 3 synonyms for a word.
    '''
    data = response.json()
    synonyms = [item['word'] for item in data][:3]
    format_string = f"Synonyms for {word}: " + ", ".join(["{}"]*len(synonyms))
    synonym_result = format_string.format(*synonyms)
    return synonym_result

def get_synonyms(word:str) -> str:
    """
    An API call to a synonym service is made.
    The API call is to https://api.datamuse.com/words
    and takes one argument: the word that you want synonyms for.
    """
    
    response = get_synonym_from_service(word)
    horoscope = get_synonym_from_response(word, response)
    return horoscope

def get_lyrics_from_service(song: str, artist: str) -> str:
    '''
    API call to get lyrics for a song, given the song name and artist
    '''
    url = "https://lrclib.net/api/get"
    params = {'track_name': song, 'artist_name': artist}
    response = requests.get(url, params=params)
    return response

def get_lyrics_from_response(song: str, artist: str, response: requests.Response) -> str:
    '''
    Returns the lyrics for the song and artist of choice.
    '''
    data = response.json()
    lyrics = data['plainLyrics']
    lyrics_clean = lyrics.replace("\n", " ") # remove line rbeak characters
    response_clean = f"The lyrics for {song} by {artist} are:\n\n {lyrics_clean}"
    return response_clean

def get_lyrics(song: str, artist: str) -> str:
    '''
    An API call to a lyrics service is made.
    The API call is to https://lrclib.net/api/get.
    This takes as arguments the names of the song and the artist.
    '''
    response = get_lyrics_from_service(song, artist)
    lyrics_answer = get_lyrics_from_response(song, artist, response)
    return lyrics_answer

def sanitize_history(history: list[dict]) -> list[dict]:
    clean_history = []
    for msg in history:
        clean_history.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })
    return clean_history


def assignment_chat(message: str, history: list[dict] = []) -> str:
    _logs.info(f'User message: {message}')
    
    instructions = return_instructions_root()
    
    user_msg = {
        "role": "user",
        "content": message
    }
    
    conversation_input = sanitize_history(history) + [user_msg]
    
    response = client.responses.create(
        model="gpt-4o-mini",  
        instructions=instructions,
        input=conversation_input,
        tools=tools,
        
    )
    
    conversation_input += response.output

    # Handle function calls if any
    for item in response.output:
        if item.type == "function_call":
            if item.name == "get_synonyms":
                args = json.loads(item.arguments)
                _logs.info(f'Function call args: {args}')
                
                # Call the horoscope function
                synonym_result = get_synonyms(**args)
                
                # Add function call result to conversation
                
                func_call_output = {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "synonyms": synonym_result
                    })
                }
                
                _logs.debug(f"Function call output: {func_call_output}")

                conversation_input = conversation_input + [func_call_output]
                
                # Make second API call with function result
                response = client.responses.create(
                    model=open_ai_model,
                    instructions=instructions,
                    tools=tools,
                    input=conversation_input
                )
                break
    return response.output_text
