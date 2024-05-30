import os
import time
import json
import torch
import curses
import asyncio
import keyboard
import pyfiglet
import sounddevice as sd
from colorama import Fore, Style
from characterai import aiocai, sendCode, authUser
from whisper_mic import WhisperMic
from elevenlabs import play
from elevenlabs.client import ElevenLabs

char_list = []
char_name = {}
character_id = {}
config = {}

class MainMenu:
    def __init__(self):
        self.stdscr = curses.initscr()

    def create_menu(self):
        # turn off cursor blinking
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.refresh()
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()
        
        options = ['Start a dialog', 'Character Editor', 'Edit configuration file', 'Exit']

        current_option = 0

        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "Welcome to Soul of Waifu, a place where characters come to life!", curses.A_BOLD)

            for i, option in enumerate(options):
                if i == current_option:
                    self.stdscr.addstr(i+2, 0, f"> {option}", curses.A_REVERSE)
                else:
                    self.stdscr.addstr(i+2, 0, f"  {option}")

            key = self.stdscr.getch()
            if key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == curses.KEY_DOWN and current_option < len(options)-1:
                current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == 3:
                    if self.confirm("Are you sure you want to quit?"):
                        exit()
                elif current_option == 0:
                    asyncio.run(self.create_menu_mode())
                elif current_option == 1:
                    curses.endwin()
                    configuration = Configuration()
                    configuration.editor_char() 
                elif current_option == 2:
                    curses.endwin()
                    configuration = Configuration()
                    configuration.update_config()
    
    async def create_menu_mode(self):
        #Turn off cursor blinking
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.refresh()
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()
        
        if tts_service == "SileroTTS":
            options = ['Text mode', 'Conversational mode with Silero TTS voicing', 'Conversational mode with ElevenLabs voicing (Unavailable)', 'Exit to main menu']
        elif tts_service == "ElevenLabs":
            options = ['Text mode', 'Conversational mode with Silero TTS voicing (Unavailable)', 'Conversational mode with ElevenLabs voicing', 'Exit to main menu']

        current_option = 0

        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "Select the dialog mode", curses.A_BOLD)

            for i, option in enumerate(options):
                if i == current_option:
                    self.stdscr.addstr(i+2, 0, f"> {option}", curses.A_REVERSE)
                else:
                    self.stdscr.addstr(i+2, 0, f"  {option}")

            key = self.stdscr.getch()
            if key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == curses.KEY_DOWN and current_option < len(options)-1:
                current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == 3:
                    print("Going to the main menu...")
                    time.sleep(1)
                    menu = MainMenu()
                    menu.create_menu()
                elif current_option == 0:
                    if tts_service == "SileroTTS":
                        curses.endwin()
                        await mode1()
                elif current_option == 1:
                    if tts_service == "SileroTTS":
                        curses.endwin()
                        await mode3()
                elif current_option == 2:
                    if tts_service == "ElevenLabs":
                        curses.endwin()
                        await mode4()
    
    def confirm(self, confirmation_text):
        self.print_center(confirmation_text)

        current_option = "Yes"
        self.print_confirm(current_option)

        while 1:
            key = self.stdscr.getch()

            if key == curses.KEY_RIGHT and current_option == "Yes":
                current_option = "No"
            elif key == curses.KEY_LEFT and current_option == "No":
                current_option = "Yes"
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return True if current_option == "Yes" else False

            self.print_confirm(current_option)
    
    def print_confirm(self, selected="Yes"):
        curses.setsyx(self.screen_height // 2 + 1, 0)
        self.stdscr.clrtoeol()

        y = self.screen_height // 2 + 1
        options_width = 10

        #Show "Yes"
        option = "Yes"
        x = self.screen_width // 2 - options_width // 2 + len(option)
        if selected == option:
            self.color_print(y, x, option, 1)
        else:
            self.stdscr.addstr(y, x, option)

        #Show "No"
        option = "No"
        x = self.screen_width // 2 + options_width // 2 - len(option)
        if selected == option:
            self.color_print(y, x, option, 1)
        else:
            self.stdscr.addstr(y, x, option)

        self.stdscr.refresh()
    
    def print_center(self, text):
        self.stdscr.clear()
        x = self.screen_width // 2 - len(text) // 2
        y = self.screen_height // 2
        self.stdscr.addstr(y, x, text)
        self.stdscr.refresh()
    
    def color_print(self, y, x, text, pair_num):
        stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(pair_num, curses.COLOR_BLACK, curses.COLOR_WHITE)
        stdscr.attron(curses.color_pair(pair_num))
        stdscr.addstr(y, x, text)
        stdscr.attroff(curses.color_pair(pair_num))
        stdscr.refresh()
        curses.endwin()

class Configuration:
    def load_config(self):
        config_path = os.path.join(current_dir, 'config.json')
        if not os.path.exists(config_path):
            print("Creating a configuration file...")
            time.sleep(1)
            data_config = {
                "config": {}
            }
            with open('config.json', 'w') as config_file:
                json.dump(data_config, config_file)
        else:
            with open('config.json', 'r') as config_file:
                main_config = json.load(config_file)
            return main_config
        
        if 'characterai_api' not in config:
            email = input("Enter email (if you already have an API key, enter " + Fore.CYAN + "Key" + Style.RESET_ALL +"): ")
            if email == "Key" or email == "key":
                config['characterai_api'] = input("Enter your API key: ")
            else:
                self.getlink(email)
                link = input("Paste the link from the email: ")
                config['characterai_api'] = self.gettoken(email, link)
            self.save_configuration()
            print("API key from Character AI has been successfully added")
            
        while True:
            chosen_variable = input(f"What do you want to use for voice generation({Fore.CYAN}SileroTTS{Style.RESET_ALL} or {Fore.CYAN}ElevenLabs{Style.RESET_ALL}): ")
            if chosen_variable == "ElevenLabs" or chosen_variable == "elevenlabs" or chosen_variable == "Elevenlabs" or chosen_variable == "elevenLabs":
                config['tts_service'] = "ElevenLabs"
                if 'elevenlabs_api' not in config:
                    config['elevenlabs_api'] = input("Enter your ElevenLabs API key: ")
                    self.save_configuration()
                    print("ElevenLabs API key successfully added")

                if 'speaker_elevenlabs' not in config:
                    config['speaker_elevenlabs'] = input("Enter the voice name for ElevenLabs: ")
                    self.save_configuration()
                    print("Voice successfully selected")
                break
            elif chosen_variable == "SileroTTS" or chosen_variable == "sileroTTS" or chosen_variable == "silerotts":
                config['tts_service'] = "SileroTTS"
                if 'device_torch' not in config:
                    while True:
                        config['device_torch'] = input("Choose the device for SileroTTS voice generation (cuda (GPU) or cpu (CPU)): ")
                        if config["device_torch"].lower() == "cuda" or config["device_torch"].lower() == "cpu":
                            self.save_configuration()
                            print("Device successfully selected")
                            break
                        else:
                            print("Error: enter the device name correctly")

                if 'speaker_silero' not in config:            
                    while True:
                        config['speaker_silero'] = input("Enter the voice name for Silero (aidar, baya, kseniya, xenia, random): ")
                        if config['speaker_silero'].lower() == "aidar" or config['speaker_silero'].lower() == "baya" or config['speaker_silero'].lower() == "kseniya" or config['speaker_silero'].lower() == "xenia" or config['speaker_silero'].lower() == "random":
                            self.save_configuration()
                            print("Voice successfully selected")
                            break
                        else:
                            print("Error: enter the speaker name correctly")
                break
            else:
                print("Error: enter the service name correctly")     
            
        print("The configuration file was successfully created!")

    def getlink(self, email):
        sendCode(email)
    
    def gettoken(self, email, link):
        authUser(link, email)
    
    def load_char_config(self):
        current_dir = os.getcwd()
        config_path = os.path.join(current_dir, 'char_config.json')
        if not os.path.exists(config_path):
            print("Creating a configuration file for storing characters...")
            time.sleep(1)
            data_char = {
                "char_list": [],
                "char_name": {},
                "character_id": {}
            }
            with open('char_config.json', 'w') as config_file:
                json.dump(data_char, config_file)
        else:
            with open('char_config.json', 'r') as config_file:
                data = json.load(config_file)
                char_list.extend(data["char_list"])
                char_name.update(data["char_name"])
                character_id.update(data["character_id"])
            
        if 'persona' not in character_id:
            character_id['persona'] = config['characterai_api']
            self.save_char_data()
            print("The configuration file was successfully created!")
        
        time.sleep(1)
    
    def update_config(self):
        clear_console()
        configuration = Configuration()
        config = configuration.load_config()
        print("Available variables to change: ")
        print("")
        for key in config['config']:
            print(key)
        
        print('--------------------')
        chosen_variable = input("Enter " + Fore.CYAN + "name" + Style.RESET_ALL + " of the variable you want to change or type " + Fore.CYAN + "Exit" + Style.RESET_ALL +", to go to the main menu: ")
        print("")
        
        if chosen_variable == "Exit" or chosen_variable == "exit":
            print("")
            print("Going to the main menu...")
            time.sleep(1)
            menu = MainMenu()
            menu.create_menu()

        if chosen_variable == "characterai_api":
            email = input("Enter email (if you already have an API key, enter " + Fore.CYAN + "Key" + Style.RESET_ALL +"): ")
            if email == "Key" or email == "key":
                token = input("Enter your API key: ")
            else:
                self.getlink(email)
                link = input("Paste the link from the email: ")
                token = self.gettoken(email, link)
            config['config'][chosen_variable] = token
        
        if chosen_variable not in config['config']:
            print('Error: the selected variable is not present in the config...')
            return

        if chosen_variable != "characterai_api":
            new_value = input(f"Value of variable {chosen_variable}:  " + Fore.CYAN + f"{config['config'][chosen_variable]}." + Style.RESET_ALL + " Enter a new value for the variable: ")
            config['config'][chosen_variable] = new_value
    
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        
        print("")
        print("Config variable successfully updated!")
        print("")
        time.sleep(1)
        print("Going to the main menu...")
        time.sleep(1)
        print("-------------------------------------")   
        menu = MainMenu()
        menu.create_menu()
    
    def print_char(self):
        if len(char_list) > 0:
            print("Available characters:")
            for i, char in enumerate(char_list):
                name = char_name.get(char, f"Character{i+1}")
                print(Fore.CYAN + f"{i+1}. {name} " + Style.RESET_ALL + f"ID: ({char})")
        else:
            print("You haven't added any characters")
            print("")
    
    def editor_char(self):
        clear_console()
        configuration = Configuration()
        print("Welcome to character editor!")
        print("")  
        while True:
            configuration.print_char()
            selection = input("Enter the word " + Fore.CYAN + 'Add' + Style.RESET_ALL + " to add a new character or the word " + Fore.CYAN + 'Delete' + Style.RESET_ALL + " to delete a character or the word " + Fore.CYAN + 'Exit' + Style.RESET_ALL + ", to exit to the main menu: ")
            print("")
            if selection.lower() == 'Add' or selection.lower() == 'add':
                name = input("Enter the new character's name: ")
                char_id = input("Enter the new character's ID: ")
                configuration.add_char(name, char_id)
            elif selection.lower() == 'Delete' or selection.lower() == 'delete':
                configuration.del_char()
            elif selection.lower() == 'Exit' or selection.lower() == 'exit':
                print("Going to the main menu...")
                time.sleep(1)
                menu = MainMenu()
                menu.create_menu()
            else:
                print(Fore.RED + "Error: enter the command correctly" + Style.RESET_ALL)
        
    def selector_char(self):
        clear_console()
        print("Welcome to the character selector!")
        print("")  
        time.sleep(1)
        while True:
            self.print_char()
            print("-------------------------------------")   
            selection = input("Enter " + Fore.CYAN + "number" + Style.RESET_ALL + " of the character you want to start communicating with: ")
            if selection.isdigit() and 1 <= int(selection) <= len(char_list):
                return char_list[int(selection)-1]
            else:
                print(Fore.RED + "Error: enter the character's number" + Style.RESET_ALL)
        
    def add_char(self, name, char_id):
        configuration = Configuration()
        if char_id in char_list:
            print("This character is already in the config")
            return
        c_api = character_id.get('persona', '')
        char_list.append(char_id)
        char_name[char_id] = name
        character_id[char_id] = c_api
        
        configuration.save_char_data()
        
        print("Character has been successfully added!")
    
    def del_char(self):
        configuration = Configuration()
        if len(char_list) > 0:
            configuration.print_char()
            while True:
                selection = input("Enter the number of the character you want to delete: ")
                if selection.isdigit() and 1 <= int(selection) <= len(char_list):
                    remove_char = char_list.pop(int(selection)-1)
                    name = char_name.pop(remove_char)
                    character_id.pop(remove_char)
                    configuration.save_char_data()
                    print(f"Character '{name}' has been deleted")
                    break
                else:
                    print(Fore.RED + "Error: enter the character's number" + Style.RESET_ALL)
        else:
            print("The list of available characters is empty. Switching to the editor...")
            time.sleep(1)
            self.editor_char()
                   
    def save_char_data(self):
        data_char = {
            "char_list": char_list,
            "char_name": char_name,
            "character_id": character_id  
        }
        with open('char_config.json', 'w') as config_file:
            json.dump(data_char, config_file)
    
    def save_configuration(self):
        data_config = {
            "config": config
        }
        with open('config.json', 'w') as config_file:
            json.dump(data_config, config_file)

def logoPRINT():
    naming = "Soul of Waifu"
    signature = "                                                         [by jofi]"
    ascii_text = pyfiglet.figlet_format(naming, font="slant")
    space = ""
    result = ascii_text + space + signature 
    print(result)
    print(space)

def logoPRINT_time():
    logoPRINT()
    time.sleep(2)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    logoPRINT()

def check_silero_models():
    if not os.path.isfile(local_file_eng):
        print("SileroTTS model download in progress")
        print("")
        torch.hub.download_url_to_file('https://models.silero.ai/models/tts/en/v3_en.pt',
                                    local_file_eng)

def whisper_mic(): #Microphone recording
    mic = WhisperMic(model='base', english=False, energy=300, pause=1)
    print(Fore.CYAN + "The record went, " + Fore.RED + "say something..." + Style.RESET_ALL)
    mic_message = mic.listen()
    return mic_message

def silero_dub_en(model, text_cai, sample_rate):
    audio = model.apply_tts(text = text_cai, speaker = speaker_en, sample_rate = sample_rate)
    sd.play(audio, sample_rate)
    time.sleep(len(audio) / sample_rate)
    sd.stop

def eleven_dub(message_char):
    audio = ELClient.generate(
        text=message_char,
        voice=voice,
        model="eleven_multilingual_v2"
    )
    play(audio, use_ffmpeg=False)

def get_char():
    configuration = Configuration()
    print("-------------------------------------")
    char = configuration.selector_char()
    return char

async def get_message(text, char):
    chatid = await client.get_chat(char)
    async with await client.connect() as chat:
        message = await chat.send_message(char, chatid.chat_id, text)
    return message

def main():
    #Logo display
    logoPRINT_time()
    
    #Create main menu
    menu = MainMenu()
    menu.create_menu()

async def mode1(): #SileroTTS voicing mode, but in text version
    print("-------------------------------------")
    print("Mode with " + Fore.CYAN + "text communication and SileroTTS voiceover is selected" + Style.RESET_ALL)
    time.sleep(1)
    char = get_char()
    clear_console()
    print("Character " + Fore.RED + f"{char_name.get(char)}" + Style.RESET_ALL + " was chosen")
    print("To exit to the main menu, write" + Fore.CYAN + " Exit" + Style.RESET_ALL)
    print("")
    while True:
        time.sleep(1)
        message_user = input(Fore.CYAN + "You: " + Style.RESET_ALL)
        if message_user.lower() == 'Exit' or message_user.lower() == 'exit':
            break
        ai_message = await get_message(message_user, char)
        model = torch.package.PackageImporter(local_file_eng).load_pickle("tts_models", "model")
        model.to(device)
        print(Fore.BLUE + "Character: " + Style.RESET_ALL + f"{ai_message}")
        print("-------------------------------------")
        if tts_service == "SileroTTS":
            silero_dub_en(model, ai_message, sample_rate)
        elif tts_service == "ElevenLabs":
            eleven_dub(ai_message)

async def mode3(): #SileroTTS EN voicing mode
    print("-------------------------------------")
    print("Mode with " + Fore.CYAN + "SileroTTS voicing was chosen" + Style.RESET_ALL)
    time.sleep(1)
    char = get_char()
    clear_console()
    print("Character " + Fore.RED + f"{char_name.get(char)}" + Style.RESET_ALL + " was chosen")
    print("")
    print("Click on " + Fore.CYAN +"RIGHT SHIFT" + Style.RESET_ALL + ", to run the program...")
    while True:
        if keyboard.is_pressed('RIGHT_SHIFT'):
            while True:
                message_user = whisper_mic()
                print(Fore.CYAN + "You: " + Style.RESET_ALL, message_user)
                ai_message = await get_message(message_user, char)
                model = torch.package.PackageImporter(local_file_eng).load_pickle("tts_models", "model")
                model.to(device)
                print(Fore.BLUE + "Character: " + Style.RESET_ALL + f"{ai_message}")
                print("-------------------------------------") 
                silero_dub_en(model, ai_message, sample_rate)

async def mode4(): #ElevenLabs voicing mode
    print("-------------------------------------")
    print("Mode with " + Fore.CYAN + "ElevenLabs voicing was chosen" + Style.RESET_ALL)
    time.sleep(1)
    char = get_char()
    clear_console()
    print("Character " + Fore.RED + f"{char_name.get(char)}" + Style.RESET_ALL + " was chosen")
    print("")
    print("Click on " + Fore.CYAN +"RIGHT SHIFT" + Style.RESET_ALL + ", to run the program...")
    while True:
        if keyboard.is_pressed('RIGHT_SHIFT'):
            while True:
                message_user = whisper_mic()
                print(Fore.CYAN + "You: " + Style.RESET_ALL, message_user)
                message_char = await get_message(message_user, char)
                print(Fore.BLUE + "Character: " + Style.RESET_ALL + f"{message_char}")
                print("-------------------------------------") 
                eleven_dub(message_char)  

#Creating and loading a config file
current_dir = os.getcwd()
conf = Configuration()
conf.load_config()
conf.load_char_config()
main_config = conf.load_config()
    
#Variables from config file
characterai_api = main_config['config']['characterai_api']
tts_service = main_config['config']['tts_service']
if tts_service == "ElevenLabs":
    elevenlabs_api = main_config['config']['elevenlabs_api']
    speaker_elevenlabs = main_config['config']['speaker_elevenlabs']
    ELClient = ElevenLabs(api_key=elevenlabs_api)
elif tts_service == "SileroTTS":
    device_torch = main_config['config']['device_torch']
    speaker_silero = main_config['config']['speaker_silero']

#Main variables
client = aiocai.Client(characterai_api)

#Variables for dub
if tts_service == "ElevenLabs":
    voice = speaker_elevenlabs
elif tts_service == "SileroTTS":
    local_file_ru = 'model_silero_ru.pt'
    local_file_eng = 'model_silero_eng.pt'
    device = torch.device(device_torch)
    torch.set_num_threads(12)
    speaker = speaker_silero
    speaker_en = 'en_0'
    sample_rate = 48000
    put_accent = True
    put_yo = True
    check_silero_models()

current_dir = os.getcwd()
config_path = os.path.join(current_dir, 'config.json')

#Launch a program
main()