import time, os, sys
import openai
import speech_recognition as sr

OPENAI_API_KEY = open("/home/plsek/Documents/Keys/openai.txt").read().strip("\n")
openai.api_key = OPENAI_API_KEY

history = [{"role":"system","content":"You are a helpful assistant"}]

print("Chatbot based on Whisper and GPT-3.5-turbo")

write = True if "write" in sys.argv[1:] else False
speak = True if "speak" in sys.argv[1:] else False

if speak:
    from gtts import gTTS

with open("logs.txt", "w") as logs:
    logs.write("")

def get_code(string):
    new = ""
    lines = string.split("\n")
    add = False
    for line in lines:
        if line.startswith("```"): add = not add
        
        if add and not line.startswith("```"): new += line + "\n"

    return new

while True:
    if write:
        question = input("\nChatGPT> ")

    else:
        _ = input("\nPress Enter to start recording>")

        # obtain audio from the microphone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("\nSay something!\n")
            audio = r.listen(source) #, timeout=5)
            # audio = r.record(source, duration=3)

        question = r.recognize_whisper_api(audio, api_key=OPENAI_API_KEY) #, language="english")
        print(question)

    if question in ["exit", "Exit", "Exit.", "EXIT", "q", "That's enough.", "That's enough", "Konec", "konec", "Konec.", "konec."]: break

    history.append({"role":"user","content":question})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )

    reply_content = completion.choices[0].message.content.strip("\n")

    history.append({"role":"assistant","content":reply_content})

    print()
    print(reply_content)

    if speak:
        audio = gTTS(text=reply_content, lang="en", slow=False)
        audio.save("reply.mp3")
        _ = os.system("cvlc --rate 1.3 --play-and-exit reply.mp3")
        os.system("rm reply.mp3")

    # time.sleep(1)

    if "```" in reply_content:
        print(get_code(reply_content))
        exec(get_code(reply_content))
        # exec(reply_content.replace("*```python", "").replace("```*", ""))

        with open("logs.txt", "a") as logs:
            logs.write(get_code(reply_content) + "\n\n")
