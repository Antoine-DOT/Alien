import time
import pyautogui

# Délai avant de commencer l'automatisation
time.sleep(5)

# Positionnez le curseur de la souris sur la fenêtre où vous souhaitez taper les commandes
# Assurez-vous que la fenêtre est active et visible avant de lancer le script

# Délai pour vous permettre de positionner le curseur de la souris sur la fenêtre
time.sleep(2)

# Fonction pour exécuter la macro 1
def executer_macro_1():
    for _ in range(35):
        # Saisie de la commande "zone"
        pyautogui.typewrite("zone")
        pyautogui.press("enter")

        # Délai entre les commandes
        time.sleep(0.1)

        # Saisie de la commande "meteor"
        pyautogui.typewrite("meteor")
        pyautogui.press("enter")

        # Délai entre les commandes
        time.sleep(0.8)

    # Saisie de la commande "monster" après les 30 itérations
    pyautogui.typewrite("monster")
    pyautogui.press("enter")

# Fonction pour exécuter la macro 2
def executer_macro_2():
    for _ in range(35):
        # Saisie de la commande "zone"
        pyautogui.typewrite("zone")
        pyautogui.press("enter")

        # Délai entre les commandes
        time.sleep(0.1)

        # Saisie de la commande "spatiofarm"
        pyautogui.typewrite("spatiofarm")
        pyautogui.press("enter")

        # Délai entre les commandes
        time.sleep(0.8)

    # Saisie de la commande "monster" après les 30 itérations
    pyautogui.typewrite("monster")
    pyautogui.press("enter")


def executer_macro_3():
    for _ in range(35):
        # Saisie de la commande "zone"
        pyautogui.typewrite("zone")
        pyautogui.press("enter")

        # Délai entre les commandes
        time.sleep(0.1)

        # Saisie de la commande "astropolis"
        pyautogui.typewrite("astropolis")
        pyautogui.press("enter")

        # Délai entre les commandes
        time.sleep(0.8)

    # Saisie de la commande "monster" après les 30 itérations
    pyautogui.typewrite("monster")
    pyautogui.press("enter")

# Demande à l'utilisateur de choisir une macro
print("Choisissez une macro à exécuter :")
print("1. Macro 1 (zone + meteor)")
print("2. Macro 2 (zone + spatiofarm)")
print("3. Macro 3 (zone + astropolis)")

choix = input("Votre choix : ")

# Exécute la macro en fonction du choix de l'utilisateur
if choix == "1":
    executer_macro_1()
elif choix == "2":
    executer_macro_2()
elif choix == "3":
    executer_macro_3()
else:
    print("Choix invalide. Le script se termine.")
