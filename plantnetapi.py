import requests
import os
import json
import urllib.parse

def enregistrer_image(url, chemin_local):
    try:
        # Télécharger l'image depuis l'URL
        reponse = requests.get(url)
        reponse.raise_for_status()
        
        # Ouvrir un fichier en mode binaire et écrire le contenu de l'image téléchargée
        with open(chemin_local, 'wb') as fichier:
            fichier.write(reponse.content)
            
        print("The image was successfully saved as", chemin_local)
    except Exception as e:
        print("Une erreur est survenue lors de l'enregistrement de l'image :", str(e))

def render_json_as_text(json_data):
    rendered_text = ""
    data = json_data

    rendered_text += f"language: {data.get('language')}\n"
    rendered_text += f"preferedReferential: {data.get('preferedReferential')}\n"
    rendered_text += f"bestMatch: {data.get('bestMatch')}\n"
    
    rendered_text += "resultat:\n"
    results = data.get("results", [])
    for result in results:
        rendered_text += "  -\n"
        rendered_text += f"    score: {result['score']}\n"
        species = result.get("species", {})
        rendered_text += f"    scientific name: {species.get('scientificNameWithoutAuthor')}\n"
        rendered_text += f"    autor: {species.get('scientificNameAuthorship')}\n"
        genus = species.get("genus", {})
        rendered_text += f"    gender: {genus.get('scientificNameWithoutAuthor')}\n"
        family = species.get("family", {})
        rendered_text += f"    family: {family.get('scientificNameWithoutAuthor')}\n"
        common_names = species.get("commonNames", [])
        rendered_text += "    commons names:\n"
        for name in common_names:
            rendered_text += f"      - {name}\n"
        rendered_text += f"    ^full scientific name: {species.get('scientificName')}\n"
        gbif = result.get("gbif", {})
        rendered_text += f"    ID GBIF: {gbif.get('id')}\n"
        powo = result.get("powo", {})
        rendered_text += f"    ID POWO: {powo.get('id')}\n"

    rendered_text += f"version: {data.get('version')}\n"
    rendered_text += f"he's staying: {data.get('remainingIdentificationRequests')} requestes\n"

    return rendered_text


def encode_url(url):
    # Vérifier si l'URL commence par "http://" ou "https://"
    if url.startswith("http://") or url.startswith("https://"):
        # Encoder seulement la partie après "http://" ou "https://"
        encoded_url = url[:url.find("://") + 3] + urllib.parse.quote(url[url.find("://") + 3:], safe='')
    else:
        # Encoder l'URL complète si elle ne commence pas par "http://" ou "https://"
        encoded_url = urllib.parse.quote(url, safe='')
    return encoded_url


try:
    with open("compteur.txt", "r") as f:
        compteur = int(f.read())
except FileNotFoundError:
    compteur = 1



while True:
    api_key = input("Enter your API key:")
    url_image = input("Enter the image URL (or 'exit' to leave):")
    if url_image.lower() == 'exit':
        break
    encoded_url = encode_url(url_image)
    
    typedeplante = input("Enter flower, leaf, fruit, bark ou auto : ")

    url = f'https://my-api.plantnet.org/v2/identify/all?images={encoded_url}&organs={typedeplante}&include-related-images=false&no-reject=false&lang=fr&type=kt&api-key={api_key}'
    print(encoded_url)
    print(url)

    # Effectuer la requête HTTP et vérifier le code d'état
    response = requests.get(url)

    if response.status_code == 200:
        # Charger le JSON depuis la réponse
        json_data = response.json()
        text_output = render_json_as_text(json_data)

        print(text_output)
        enregistrer = input("Do you want to save the query results + Image? (Yes No) :")
        if enregistrer.lower() == 'yes':
            nom_fichier = f"recherche{compteur}.txt"
            with open(nom_fichier, "w") as fichier:
                fichier.write(text_output)

            print(f"Result saved in'{nom_fichier}'")
        
            # Enregistrer l'image à partir de l'URL saisie
            chemin_image = f'image{compteur}.jpg'
            enregistrer_image(url_image, chemin_image)
            # Incrémenter le compteur et le sauvegarder dans le fichier
            compteur += 1
            with open("compteur.txt", "w") as f:
                f.write(str(compteur))

        # Afficher le nombre de requêtes restantes
        print(f"He's staying{json_data.get('remainingIdentificationRequests')} requests.")
    else:
        print("The request failed with status code:", response.status_code)
