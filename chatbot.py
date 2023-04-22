import time, os, sys
import openai

# Rich library
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.syntax import Syntax
console = Console()

color = "#26A269"
color2 = "#FFB700" # "#F6E61F"
color3 = "#1DC4FF"

path = "/home/plsek/GitHub/ChadGPT"

OPENAI_API_KEY = open("/home/plsek/Documents/Keys/openai.txt").read().strip("\n")
openai.api_key = OPENAI_API_KEY

# Exit phrases
exits = ["exit", "Exit", "Exit.", "EXIT", "q", "That's enough.", "That's enough", "Konec", "konec", "Konec.", "konec."]

# System prompt
history = [{"role":"system","content":"You are a helpful assistant"}]

write = True if "write" in sys.argv[1:] else False
speak = True if "speak" in sys.argv[1:] else False

if not write:
    import speech_recognition as sr
    r = sr.Recognizer()

    # # Whisper locally
    # from whisper_jax import FlaxWhisperPipline
    # pipeline = FlaxWhisperPipline("openai/whisper-small")

if speak:
    from gtts import gTTS

# # Clear the logs
# with open("logs.txt", "w") as logs: logs.write("")

# Remove leading and trailing newlines
def remove_newlines(string):
    if "\n" == string[0]: string = string[1:]
    if "\n" == string[-1]: string = string[:-1]
    return remove_newlines(string) if "\n" in [string[0], string[-1]] else string

# Strip code from answer
def get_code(string):
    s_new = ""
    lines = string.split("\n")
    add = False
    for line in lines:
        if line.startswith("```"): 
            add = not add
        if add and not line.startswith("```"): 
            if "pip install" in line: continue
            s_new += line + "\n"
    return s_new

# Split answer into lines of 120 characters
def split_input(user_string, chunk_size=120):
    output = ""
    lines = user_string.split("\n")
    for line in lines:
        words = line.split(" ")
        total_length = 0

        while (total_length < len(user_string) and len(words) > 0):
            line = []
            next_word = words[0]
            line_len = len(next_word) + 1

            while  (line_len < chunk_size) and len(words) > 0:
                words.pop(0)
                line.append(next_word)

                if (len(words) > 0):
                    next_word = words[0]
                    line_len += len(next_word) + 1

            line = " ".join(line)
            output += line + "\n"
            total_length += len(line) 

    return output


print(f"[#FFFFFF]\n\t Chatbot powered by Whisper and GPT-3.5-turbo[/]\n")

while True:
    if write:
        question = Prompt.ask(f"[{color}]User[/]")

    else:
        question = Prompt.ask(f"[{color}][Press Enter to record][/]")
        if question in exits: break

        # obtain audio from the microphone
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print(f"\n[{color}]Recording![/]\n")
            audio = r.listen(source) #, timeout=5)
            # audio = r.record(source, duration=3)

        with open(f"{path}/question.wav", "wb") as f:
            f.write(audio.get_wav_data())

        question = r.recognize_whisper_api(audio, api_key=OPENAI_API_KEY) #, language="english")
        # question = r.recognize_whisper(audio, model="small") #, language="english")
        # question = pipeline(f"{path}/question.wav")["text"]
        print(f"[{color}]User[/]:", question)

    # If question is smth like "exit", break the loop
    if question in exits: break

    # Add the question to the history
    history.append({"role":"user","content":question})

    # Ask GPT-3.5 for an answer
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )
    reply_content = completion.choices[0].message.content.strip("\n")

    # Add the answer to the history
    history.append({"role":"assistant","content":reply_content})

    # Print the answer
    print(f"[{color2}]\nGPT3[/]:", "[#FFFFFF]" + split_input(remove_newlines(reply_content)) + "[/]")

    # Execute the code
    if "```" in reply_content:
        s_pref, s_code, s_suf = get_code(reply_content)
        print(f"[{color3}]Code overview[/]:\n")
        console.print(Syntax(s_code, "python", background_color="#181818"))

        run = Prompt.ask(f"[{color3}]\nRun the code?[/]")
        if run not in ["n", "no", "N", "No", "NO"]:
            print(f"\n[{color3}]Running the code![/]\n")
            # print("\33[93m" + "Code output:" + "\33[0m")
            print(f"[{color3}]Code output:[/]\n")
            try:
                exec(get_code(reply_content)[1])
            except Exception as e: 
                print(e)
            print()

            # with open(f"{path}/logs.txt", "a") as logs:
            #     logs.write(get_code(reply_content)[1] + "\n\n")

    # Say the answer with machine voice
    if speak and ("```" not in reply_content):
        audio = gTTS(text=reply_content, lang="en", slow=False)
        audio.save(f"{path}/reply.mp3")
        _ = os.system(f"cvlc --rate 1.3 --play-and-exit {path}/reply.mp3")
        # os.system("rm reply.mp3")
