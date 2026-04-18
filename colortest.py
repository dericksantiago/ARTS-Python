from colorama import init, Fore, Back, Style
init()
print(Fore.GREEN + "Hello ARTS! - GREEN" + Style.RESET_ALL)
print(Fore.CYAN + "Hello ARTS! - CYAN" + Style.RESET_ALL)
print(Fore.YELLOW + "Hello ARTS! - YELLOW" + Style.RESET_ALL)
print(Fore.WHITE + "Hello ARTS! - WHITE" + Style.RESET_ALL)
print(Fore.LIGHTGREEN_EX + "Hello ARTS! - LIGHT GREEN" + Style.RESET_ALL)
print("Normal text - no color")

print(Fore.GREEN + "Hello ARTS!" + Style.RESET_ALL)
print("Normal text after")