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
            
        print("L'image a été enregistrée avec succès sous", chemin_local)
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
        rendered_text += f"    nom scientifique: {species.get('scientificNameWithoutAuthor')}\n"
        rendered_text += f"    auteur: {species.get('scientificNameAuthorship')}\n"
        genus = species.get("genus", {})
        rendered_text += f"    genre: {genus.get('scientificNameWithoutAuthor')}\n"
        family = species.get("family", {})
        rendered_text += f"    famille: {family.get('scientificNameWithoutAuthor')}\n"
        common_names = species.get("commonNames", [])
        rendered_text += "    noms communs:\n"
        for name in common_names:
            rendered_text += f"      - {name}\n"
        rendered_text += f"    nom scientifique complet: {species.get('scientificName')}\n"
        gbif = result.get("gbif", {})
        rendered_text += f"    ID GBIF: {gbif.get('id')}\n"
        powo = result.get("powo", {})
        rendered_text += f"    ID POWO: {powo.get('id')}\n"

    rendered_text += f"version: {data.get('version')}\n"
    rendered_text += f"il reste: {data.get('remainingIdentificationRequests')} requetes\n"

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
    api_key = input("Entrez votre clé d'API :")
    url_image = input("Entrez l'URL de l'image (ou 'exit' pour quitter) : ")
    if url_image.lower() == 'exit':
        break
    encoded_url = encode_url(url_image)
    
    typedeplante = input("Entrez flower, leaf, fruit, bark ou auto : ")

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
        enregistrer = input("Voulez-vous enregistrer les résultats de la requête + L'image? (oui/non) : ")
        if enregistrer.lower() == 'oui':
            nom_fichier = f"recherche{compteur}.txt"
            with open(nom_fichier, "w") as fichier:
                fichier.write(text_output)

            print(f"Résultat enregistré dans '{nom_fichier}'")
        
            # Enregistrer l'image à partir de l'URL saisie
            chemin_image = f'image{compteur}.jpg'
            enregistrer_image(url_image, chemin_image)
            # Incrémenter le compteur et le sauvegarder dans le fichier
            compteur += 1
            with open("compteur.txt", "w") as f:
                f.write(str(compteur))

        # Afficher le nombre de requêtes restantes
        print(f"Il reste {json_data.get('remainingIdentificationRequests')} requêtes.")
    else:
        print("La requête a échoué avec le code d'état :", response.status_code)