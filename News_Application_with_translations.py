import io
import webbrowser
import requests
from tkinter import *
from urllib.request import urlopen
from PIL import ImageTk, Image
from gtts import gTTS
import os
from playsound import playsound
from deep_translator import GoogleTranslator

Country_code = None


class NewsApp:

    def __init__(self):
        # Initialize the GUI
        self.load_gui()
        self.root.mainloop()

    def load_gui(self):
        self.root = Tk()
        self.root.geometry('350x750')
        # self.root.resizable(0, 0)
        self.root.iconbitmap('icon.ico')
        self.root.title('News App')
        self.root.configure(background='black')

        # Adding the buttons for different countries
        countries = {
            "India": 'in', "USA": 'us', "Canada": 'ca', "China": 'cn', "Ukraine": 'ua',
            "Australia": 'au', "Argentina": 'ar', "Poland": 'pl', "Romania": 'ro', "Russia": 'ru'
        }

        for country, code in countries.items():
            button = Button(self.root, text=f'Press to load news article of {country}', fg='#FFFFFF', bg='#4CAF50',
                            width=35, height=2, command=lambda c=code: self.handle_country_name(c))
            button.pack(pady=(5, 10))
            button.config(font=('verdana', 12))

    def handle_country_name(self, code):
        global Country_code
        Country_code = code
        self.fetch_news_data()  # Fetch new data based on selected country

    def fetch_news_data(self):
        # Fetch the news articles for the given country code
        try:
            response = requests.get(
                f'https://api.mediastack.com/v1/news?access_key=9fdb3249de0c6d7cc3ce3991a6821556&countries={Country_code}'
            )
            response.raise_for_status()
            self.data = response.json()
            self.load_news_item(0)  # Load the first news item

        except requests.RequestException as e:
            print(f"Error fetching news: {e}")

    def clear(self):
        for i in self.root.pack_slaves():
            i.destroy()

    def load_news_item(self, index):
        # Clear the screen for the new news item
        self.clear()

        # Author details and source
        author_text = self.data['data'][index]['source']
        label_text = f"Source: {author_text}"
        Author = Label(self.root, text=label_text, fg='orange', bg='black', wraplength=350, justify='center')
        Author.pack(pady=(10, 10))
        Author.config(font=('verdana', 15))

        # Time and date of the published news article
        Time_Date = Label(self.root, text=self.data['data'][index]['published_at'], bg='black', fg='blue',
                          wraplength=350, justify='center')
        Time_Date.pack(pady=(5, 10))
        Time_Date.config(font=('verdana', 15))

        # Image handling
        try:
            img_url = self.data['data'][index]['image']
            raw_data = urlopen(img_url).read()
            im = Image.open(io.BytesIO(raw_data)).resize((350, 250))
            photo = ImageTk.PhotoImage(im)
        except:
            img_url = 'https://media.gettyimages.com/id/1318698827/vector/breaking-news.jpg?s=2048x2048&w=gi&k=20&c=uaLCWps3hPTgEyca016pP505tOda7QxwkI04XWgzIL4='
            raw_data = urlopen(img_url).read()
            im = Image.open(io.BytesIO(raw_data)).resize((350, 250))
            photo = ImageTk.PhotoImage(im)

        # Creating a label for the image
        label = Label(self.root, image=photo)
        label.image = photo  # keep a reference to avoid garbage collection
        label.pack()

        # Creating a label for the heading of the news article
        heading = Label(self.root, text=self.data['data'][index]['title'], bg='black', fg='white',
                        wraplength=350, justify='center')
        heading.pack(pady=(10, 20))
        heading.config(font=('verdana', 15))




        # Adding buttons to read out the headline in both original and translated English
        button_frame = Frame(self.root, bg='black')
        button_frame.pack(pady=(5, 5))

        speak_button = Button(button_frame, text='🔊 Listen Original', fg='yellow', bg='black', width=18, height=1,
                              command=lambda: self.speak_headline(self.data['data'][index]['title'], Country_code))
        speak_button.pack(side=LEFT, padx=(5, 5))

        translate_button = Button(button_frame, text='🔊 Listen in English', fg='yellow', bg='black', width=18, height=1,
                                  command=lambda: self.translate_and_speak(self.data['data'][index]['title'],
                                                                           Country_code))
        translate_button.pack(side=LEFT, padx=(5, 5))




        # Creating a label for the description of the news article
        details = Label(self.root, text=self.data['data'][index]['description'], bg='black', fg='white',
                        wraplength=350, justify='center')
        details.pack(pady=(2, 20))
        details.config(font=('verdana', 12))

        # Creating a frame for functionality buttons
        frame = Frame(self.root, bg='black')
        frame.pack(expand=True, fill=BOTH)

        # Adding a prev button to navigate to the previous news article if present
        if index != 0:
            prev = Button(frame, text='Prev', fg='#FFFFFF', bg='#4CAF50', width=16, height=3,
                          command=lambda: self.load_news_item(index - 1))
            prev.pack(side=LEFT)

        # Adding a read button to open the news article in a web browser
        read = Button(frame, text='Read More', fg='#FFFFFF', bg='#4CAF50', width=16, height=3,
                      command=lambda: self.open_link(self.data['data'][index]['url']))
        read.pack(side=LEFT)

        # Adding a next button to navigate to the next news article if available
        if index != len(self.data['data']) - 1:
            next = Button(frame, text='Next', fg='#FFFFFF', bg='#4CAF50', width=16, height=3,
                          command=lambda: self.load_news_item(index + 1))
            next.pack(side=LEFT)

    def speak_headline(self, text, country_code):
        # Determine the language to use based on the country code
        language_map = {
            'in': 'hi',  # Hindi for India
            'us': 'en',  # English for USA
            'ca': 'en',  # English for Canada
            'cn': 'zh-cn',  # Chinese for China
            'ua': 'uk',  # Ukrainian for Ukraine
            'au': 'en',  # English for Australia
            'ar': 'es',  # Spanish for Argentina
            'pl': 'pl',  # Polish for Poland
            'ro': 'ro',  # Romanian for Romania
            'ru': 'ru'  # Russian for Russia
        }

        language = language_map.get(country_code, 'en')  # Default to English if country code is not mapped

        # Use gTTS to convert text to speech in the appropriate language
        tts = gTTS(text=text, lang=language)
        tts.save("headline.mp3")
        playsound("headline.mp3")
        os.remove("headline.mp3")  # Remove the file after playing

    def translate_and_speak(self, text, country_code):
        # Translate the text to English using Google Translate
        translated_text = GoogleTranslator(source='auto', target='en').translate(text)

        # Use gTTS to convert the translated text to speech in English
        tts = gTTS(text=translated_text, lang='en')
        tts.save("translated_headline.mp3")
        playsound("translated_headline.mp3")
        os.remove("translated_headline.mp3")  # Remove the file after playing

    # Function to open the full news article
    def open_link(self, url):
        webbrowser.open(url)


if __name__ == '__main__':
    NewsApp()
