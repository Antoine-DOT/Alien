import time
import pyautogui
import keyboard

# Délai avant de commencer l'automatisation
time.sleep(5)

# Positionnez le curseur de la souris sur la fenêtre où vous souhaitez taper les commandes
# Assurez-vous que la fenêtre est active et visible avant de lancer le script

# Délai pour vous permettre de positionner le curseur de la souris sur la fenêtre
time.sleep(2)

while True:
    # Saisie de la commande "zone"
    pyautogui.typewrite("zone")
    pyautogui.press("enter")

    # Délai entre les commandes
    time.sleep(1)

    # Saisie de la commande "meteor"
    pyautogui.typewrite("meteor")
    pyautogui.press("enter")

    # Délai entre les commandes
    time.sleep(1)

    # Vérification de l'appui sur la touche "Échap" pour arrêter le script
    if keyboard.is_pressed("esc"):
        print("Erreur : Le script a été interrompu par l'utilisateur.")
        break
