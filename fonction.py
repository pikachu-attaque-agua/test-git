import random
import string
import sqlite3
import hashlib
import os

# Importation des classes pour les objects
from utilisateur import *

######################################################      Ouverture et fermeture à la bdd
def connexion_BDD(db_path):
    """
    Ouvre une connexion à la base de données.

    :param db_path: Chemin vers le fichier de la base de données SQLite.
    :return: L'objet connexion SQLite.
    """
    try:
        connexion = sqlite3.connect(db_path)
        return connexion
    except sqlite3.Error as e:
        print("Connexion BDD KO")
        print(f"Erreur lors de l'ouverture de la connexion : {e}")
        return None

def deconnexion_BDD(connexion):
    """
    Ferme une connexion à la base de données.

    :param connexion: L'objet connexion SQLite à fermer.
    """
    if connexion:
        try:
            connexion.close()
        except sqlite3.Error as e:
            print(f"Erreur lors de la fermeture de la connexion : {e}")



######################################################      Gestions des mots de passes et login




def hacher_mot_de_passe(mot_de_passe):
    """
    Hache un mot de passe en utilisant SHA-256 avec un sel fixe.

    :param mot_de_passe: Mot de passe en clair.
    :return: Chaîne hachée du mot de passe.
    """
    sel = "sel"  # Salage fixe
    mot_de_passe_salade = mot_de_passe + sel  # Ajout du sel au mot de passe
    hash_mdp = hashlib.sha256(mot_de_passe_salade.encode()).hexdigest()
    return hash_mdp





def generer_mdp(longueur):
    """
    Génère un mot de passe aléatoire.

    :param longueur: La longueur du mot de passe à générer.
    :return: Un mot de passe aléatoire composé de lettres, chiffres et caractères spéciaux.
    """
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(longueur))



def generer_login(db_path, prenom, nom):
    """
    Génère un login basé sur la première lettre du prénom et le nom entier.
    Si ce login existe déjà dans la base de données, ajoute un numéro auto-incrémenté à la fin.

    :param db_path: Chemin vers la base de données SQLite.
    :param prenom: Prénom de l'utilisateur.
    :param nom: Nom de l'utilisateur.
    :return: Un login unique.
    """
    # Construire le login de base
    login_base = prenom[0].lower() + nom.lower()

    # Connexion à la base de données
    try:
        connexion = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

    try:
        curseur = connexion.cursor()

        # Vérifier si le login existe déjà
        login_unique = login_base
        compteur = 1
        while True:
            curseur.execute("SELECT COUNT(*) FROM utilisateur WHERE login_u = ?", (login_unique,))
            if curseur.fetchone()[0] == 0:
                # Si le login n'existe pas, on l'utilise
                break
            # Si le login existe déjà, on ajoute un numéro à la fin
            login_unique = f"{login_base}{compteur}"
            compteur += 1

        return login_unique

    except sqlite3.Error as e:
        print(f"Erreur lors de la génération du login : {e}")
        return None

    finally:
        # Fermer la connexion à la base de données
        connexion.close()



def recherche_utilisateur(db_path, login_utilisateur):
    """
    Recherche un utilisateur par son login et retourne un objet Utilisateur.
    """
    connexion = sqlite3.connect(db_path)
    curseur = connexion.cursor()

    # Requête pour récupérer les informations de l'utilisateur par login
    query = """
    SELECT u.login_u, u.prenom_u, u.nom_u, u.mdp_u, t.type_u, v.nom_ville
    FROM utilisateur u
    JOIN type_utilisateur t ON u.id_type = t.id_type
    JOIN ville v ON u.id_ville = v.id_ville
    WHERE u.login_u = ?;
    """
    curseur.execute(query, (login_utilisateur,))

    # Récupérer un seul résultat
    result = curseur.fetchone()

    if result:
        login, prenom, nom, mdp, type_utilisateur, ville = result
        # Vérification des valeurs
        # print(f"Récupéré: login={login}, prenom={prenom}, nom={nom}, mdp={mdp}, type_utilisateur={type_utilisateur}, ville={ville}")
        
        # Retourner l'objet Utilisateur
        return Utilisateur(login, prenom, nom, mdp, type_utilisateur, ville)
    else:
        print(f"Aucun utilisateur trouvé avec le login '{login_utilisateur}'.")
        return None




def connexion_utilisateur(db_path, login, mdp):
    """
    Vérifie si un utilisateur avec le login et le mot de passe spécifiés existe dans la base de données.

    :param db_path: Chemin vers le fichier de la base de données SQLite.
    :param login: Login de l'utilisateur à vérifier.
    :param mdp: Mot de passe de l'utilisateur à vérifier.
    :return: True si l'utilisateur existe, sinon False.
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        return False

    try:
        curseur = connexion.cursor()

        # Requête pour vérifier si un utilisateur avec le login et le mot de passe existe
        query = """
        SELECT COUNT(*)
        FROM utilisateur
        WHERE login_u = ? AND mdp_u = ?;
        """
        curseur.execute(query, (login, mdp))
        result = curseur.fetchone()

        # Vérifier si un utilisateur correspondant est trouvé
        if result and result[0] > 0:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"Erreur lors de la vérification de l'utilisateur : {e}")
        return False
    finally:
        deconnexion_BDD(connexion)


def recuperer_utilisateurs(db_path, login_utilisateur):
    """
    Récupère les utilisateurs de la base de données selon le type de l'utilisateur connecté.

    :param db_path: Chemin vers la base de données SQLite.
    :param login_utilisateur: Login de l'utilisateur connecté.
    :return: Liste des utilisateurs correspondants.
    """
    # On commence par récupérer l'utilisateur connecté et son type
    utilisateur_connecte = recherche_utilisateur(db_path, login_utilisateur)
    if not utilisateur_connecte:
        return None  # Si l'utilisateur n'est pas trouvé, on retourne None

    # Si l'utilisateur est de type "sa", on récupère tous les utilisateurs
    if utilisateur_connecte.get_type() == "sa":
        return recuperer_tous_les_utilisateurs(db_path)
    
    # Si l'utilisateur est de type "a", on récupère tous les utilisateurs de la même ville
    if utilisateur_connecte.get_type() == "a":
        return recuperer_utilisateurs_par_ville(db_path, utilisateur_connecte.get_ville())
    
    return []  # Aucun utilisateur ne correspond si ce n'est pas de type "sa" ou "a"

def recuperer_tous_les_utilisateurs(db_path):
    """
    Récupère tous les utilisateurs de la base de données.

    :param db_path: Chemin vers la base de données SQLite.
    :return: Liste des utilisateurs
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        return None

    try:
        curseur = connexion.cursor()
        query = """
        SELECT u.login_u, u.prenom_u, u.nom_u, t.type_u, v.nom_ville
        FROM utilisateur u
        JOIN type_utilisateur t ON u.id_type = t.id_type
        JOIN ville v ON u.id_ville = v.id_ville;
        """
        curseur.execute(query)
        result = curseur.fetchall()

        utilisateurs = []
        for row in result:
            login, prenom, nom, type_u, ville = row
            utilisateurs.append({
                'login': login,
                'prenom': prenom,
                'nom': nom,
                'type': type_u,
                'ville': ville
            })

        # Afficher chaque utilisateur avec un retour à la ligne
        # for utilisateur in utilisateurs:
        #     print()
        #     print(f"Login: {utilisateur['login']}, Prénom: {utilisateur['prenom']}, Nom: {utilisateur['nom']}, Type: {utilisateur['type']}, Ville: {utilisateur['ville']}")
        # print()
        return utilisateurs

    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des utilisateurs : {e}")
        return None
    finally:
        deconnexion_BDD(connexion)


def recuperer_utilisateurs_par_ville(db_path, ville_nom):
    """
    Récupère les utilisateurs classiques d'une ville spécifique.

    :param db_path: Chemin vers la base de données SQLite.
    :param ville_nom: Nom de la ville.
    :return: Liste des utilisateurs classiques de la ville
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        return None

    try:
        curseur = connexion.cursor()
        query = """
        SELECT u.login_u, u.prenom_u, u.nom_u, t.type_u, v.nom_ville
        FROM utilisateur u
        JOIN type_utilisateur t ON u.id_type = t.id_type
        JOIN ville v ON u.id_ville = v.id_ville
        WHERE v.nom_ville = ? AND t.type_u = 'u';  -- Filtrage par type "u"
        """
        curseur.execute(query, (ville_nom,))
        result = curseur.fetchall()

        utilisateurs = []
        for row in result:
            login, prenom, nom, type_u, ville = row
            utilisateurs.append({
                'login': login,
                'prenom': prenom,
                'nom': nom,
                'type': type_u,
                'ville': ville
            })

        # Afficher chaque utilisateur avec un retour à la ligne
        # for utilisateur in utilisateurs:
        #     print(f"Login: {utilisateur['login']}, Prénom: {utilisateur['prenom']}, Nom: {utilisateur['nom']}, Type: {utilisateur['type']}, Ville: {utilisateur['ville']}")
        #     print()  # Retour à la ligne

        return utilisateurs

    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des utilisateurs : {e}")
        return None
    finally:
        deconnexion_BDD(connexion)


def afficher_liste_utilisateurs(utilisateurs):
    """
    Affiche proprement la liste des utilisateurs.
    
    :param utilisateurs: Liste de dictionnaires contenant les informations des utilisateurs.
    """
    if not utilisateurs:
        print("Aucun utilisateur trouvé.")
        return

    # Affichage de l'en-tête du tableau
    print(f"{'Login':<20}{'Prénom':<20}{'Nom':<20}{'Type':<15}{'Ville'}")
    print("=" * 80)  # Séparateur

    # Affichage des informations pour chaque utilisateur
    for utilisateur in utilisateurs:
        print(f"{utilisateur['login']:<20}{utilisateur['prenom']:<20}{utilisateur['nom']:<20}{utilisateur['type']:<15}{utilisateur['ville']}")
    
    print("=" * 80)  # Séparateur de fin


def creation_utilisateur_connexion(db_path, login):
    """
    Recherche un utilisateur par son login et retourne un objet Utilisateur.

    :param db_path: Chemin vers le fichier de la base de données SQLite.
    :param login: Login de l'utilisateur à rechercher.
    :return: Une instance de Utilisateur ou None si l'utilisateur n'existe pas.
    """
    # Connexion à la base de données
    try:
        connexion = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

    try:
        curseur = connexion.cursor()

        # Requête pour récupérer les informations de l'utilisateur par login
        query = """
        SELECT u.login_u, u.prenom_u, u.nom_u, u.mdp_u, t.type_u, v.nom_ville
        FROM utilisateur u
        JOIN type_utilisateur t ON u.id_type = t.id_type
        JOIN ville v ON u.id_ville = v.id_ville
        WHERE u.login_u = ?;
        """
        curseur.execute(query, (login,))

        # Récupérer un seul résultat
        result = curseur.fetchone()

        # Si un résultat est trouvé, créer et retourner l'objet Utilisateur
        if result:
            login, prenom, nom, mdp, type_utilisateur, ville = result
            return Utilisateur(login, prenom, nom, mdp, type_utilisateur, ville)
        else:
            print(f"Aucun utilisateur trouvé avec le login '{login}'.")
            return None

    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération de l'utilisateur : {e}")
        return None

    finally:
        # Fermer la connexion à la base de données
        connexion.close()


def verifier_ville_existe(db_path, ville_nom):
    """
    Vérifie si une ville existe dans la base de données.

    :param db_path: Chemin vers la base de données SQLite.
    :param ville_nom: Nom de la ville à vérifier.
    :return: True si la ville existe, False sinon.
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        print("Échec de la connexion à la base de données.")
        return False

    try:
        curseur = connexion.cursor()
        query = "SELECT 1 FROM ville WHERE nom_ville = ? LIMIT 1;"
        curseur.execute(query, (ville_nom,))
        result = curseur.fetchone()

        if result:
            return True  # La ville existe
        else:
            return False  # La ville n'existe pas

    except sqlite3.Error as e:
        print(f"Erreur lors de la vérification de la ville : {e}")
        return False
    finally:
        deconnexion_BDD(connexion)


def recuperer_id_ville(db_path, ville_nom):
    """
    Récupère l'ID de la ville à partir de son nom.

    :param db_path: Chemin vers le fichier de la base de données SQLite.
    :param ville_nom: Nom de la ville.
    :return: ID de la ville ou None si la ville n'existe pas.
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        return None

    try:
        curseur = connexion.cursor()
        query = "SELECT id_ville FROM ville WHERE nom_ville = ?;"
        curseur.execute(query, (ville_nom,))
        result = curseur.fetchone()

        if result:
            return result[0]  # Retourne l'ID de la ville
        else:
            print(f"Ville '{ville_nom}' introuvable.")
            return None
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération de l'ID de la ville : {e}")
        return None
    finally:
        deconnexion_BDD(connexion)

def recuperer_id_type(db_path, type_nom):
    """
    Récupère l'ID du type d'utilisateur à partir de son nom.

    :param db_path: Chemin vers le fichier de la base de données SQLite.
    :param type_nom: Nom du type d'utilisateur.
    :return: ID du type d'utilisateur ou None si le type n'existe pas.
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        return None

    try:
        curseur = connexion.cursor()
        query = "SELECT id_type FROM type_utilisateur WHERE type_u = ?;"
        curseur.execute(query, (type_nom,))
        result = curseur.fetchone()

        if result:
            return result[0]  # Retourne l'ID du type utilisateur
        else:
            print(f"Type utilisateur '{type_nom}' introuvable.")
            return None
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération de l'ID du type utilisateur : {e}")
        return None
    finally:
        deconnexion_BDD(connexion)


##################################################          Gestion utilisateur
def recuperer_id_utilisateur(db_path, login):
    """
    Recherche un utilisateur par son login et retourne son ID.

    :param db_path: Chemin vers le fichier de la base de données SQLite.
    :param login: Login de l'utilisateur à rechercher.
    :return: ID de l'utilisateur ou None si l'utilisateur n'existe pas.
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        return None

    try:
        curseur = connexion.cursor()
        query = """
        SELECT id_u
        FROM utilisateur
        WHERE login_u = ?;
        """
        curseur.execute(query, (login,))
        result = curseur.fetchone()

        if result:
            id_utilisateur = result[0]
            print(f"ID trouvé pour l'utilisateur '{login}' : {id_utilisateur}")
            return id_utilisateur
        else:
            print(f"Aucun utilisateur trouvé avec le login '{login}'.")
            return None
    except sqlite3.Error as e:
        print(f"Erreur lors de la recherche de l'utilisateur : {e}")
        return None
    finally:
        deconnexion_BDD(connexion)




def ajouter_utilisateur(db_path, utilisateur):
    """
    Ajoute un nouvel utilisateur Admin dans la base de données en utilisant un objet Utilisateur
    avec des noms (texte) pour le type et la ville.

    :param db_path: Chemin vers le fichier de la base de données SQLite.
    :param utilisateur: Objet Utilisateur contenant les informations (login, mdp, type, ville).
    :return: True si l'utilisateur est ajouté avec succès, False sinon.
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        print("Échec de la connexion à la base de données.")
        return False

    try:
        # Récupérer l'ID du type d'utilisateur depuis son nom
        curseur = connexion.cursor()
        query_type = "SELECT id_type FROM type_utilisateur WHERE type_u = ?;"
        curseur.execute(query_type, (utilisateur.get_type(),))
        type_result = curseur.fetchone()

        if not type_result:
            print(f"Type '{utilisateur.get_type()}' introuvable.")
            return False
        id_type = type_result[0]

        # Récupérer l'ID de la ville depuis son nom
        query_ville = "SELECT id_ville FROM ville WHERE nom_ville = ?;"
        curseur.execute(query_ville, (utilisateur.get_ville(),))
        ville_result = curseur.fetchone()

        if not ville_result:
            print(f"Ville '{utilisateur.get_ville()}' introuvable.")
            return False
        id_ville = ville_result[0]

        # Insérer le nouvel utilisateur dans la table en ajoutant le prénom et le nom
        query_insert = """
        INSERT INTO utilisateur (login_u, prenom_u, nom_u, mdp_u, id_type, id_ville)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        curseur.execute(query_insert, (
            utilisateur.get_login(), 
            utilisateur.get_prenom(), 
            utilisateur.get_nom(),     
            utilisateur.get_mdp(), 
            id_type, 
            id_ville
        ))

        connexion.commit()
        print(f"Utilisateur '{utilisateur.get_login()}' ajouté avec succès dans la base de données.")
        return True
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de l'utilisateur : {e}")
        return False
    finally:
        deconnexion_BDD(connexion)


def afficher_liste_villes(villes):
    """
    Affiche proprement la liste des villes.

    :param villes: Liste des villes à afficher.
    """
    if not villes:
        print("Aucune ville trouvée.")
        return

    # Affichage de l'en-tête du tableau
    print(f"{'Ville':<30}")
    print("=" * 30)  # Séparateur

    # Affichage des villes
    for ville in villes:
        print(f"{ville:<30}")
    
    print("=" * 30)  # Séparateur de fin

def recuperer_villes(db_path):
    """
    Récupère toutes les villes présentes dans la base de données et les affiche.

    :param db_path: Chemin vers le fichier de la base de données SQLite.
    :return: Une liste de noms de villes ou une liste vide si aucune ville n'est trouvée.
    """
    # Connexion à la base de données
    connexion = connexion_BDD(db_path)
    if not connexion:
        print("Échec de la connexion à la base de données.")
        return []

    try:
        curseur = connexion.cursor()

        # Requête pour récupérer tous les noms de villes
        query = "SELECT nom_ville FROM ville;"
        curseur.execute(query)

        # Récupérer tous les résultats
        result = curseur.fetchall()

        # Extraire seulement les noms des villes
        villes = [row[0] for row in result]

        # Afficher les villes
        afficher_liste_villes(villes)
        return villes

    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des villes : {e}")
        return []

    finally:
        # Fermer la connexion à la base de données
        deconnexion_BDD(connexion)


def modifier_utilisateur(db_path, utilisateur, modification, type_modification, utilisateur_connecte):
    """
    Modifie une information spécifique d'un utilisateur dans la base de données avec des restrictions selon le rôle.

    :param db_path: Chemin vers la base de données SQLite.
    :param utilisateur: Objet Utilisateur contenant les informations actuelles.
    :param modification: Nouvelle valeur à appliquer.
    :param type_modification: Champ à modifier ('1' pour login, '2' pour prenom, '3' pour nom, '4' pour mdp, '5' pour ville).
    :param utilisateur_connecte: Utilisateur qui effectue la modification.
    :return: True si la modification a réussi, False sinon.
    """
    connexion = connexion_BDD(db_path)
    if not connexion:
        print("Échec de la connexion à la base de données.")
        return False

    # Vérification des droits de modification
    if utilisateur_connecte.get_type() == "a":
        if utilisateur.get_type() != "u":
            print("Échec : Un administrateur ne peut modifier que des utilisateurs.")
            return False
        if utilisateur_connecte.get_ville() != utilisateur.get_ville():
            print("Échec : L'utilisateur n'est pas dans la même ville que l'administrateur.")
            return False
    elif utilisateur_connecte.get_type() == "sa":
        if utilisateur.get_type() == "sa":
            print("Échec : Un super administrateur ne peut pas modifier un autre super administrateur.")
            return False
    else:
        print("Échec : Seuls les administrateurs et super administrateurs peuvent modifier des utilisateurs.")
        return False

    try:
        curseur = connexion.cursor()
        # Vérification de l'existence de l'utilisateur dans la base de données
        id_utilisateur = recuperer_id_utilisateur(db_path, utilisateur.get_login())

        if id_utilisateur is None:
            print(f"Erreur : L'utilisateur '{utilisateur.get_login()}' n'existe pas.")
            return False

        update_query = ""
        params = []

        # Modification du login
        if type_modification == "1":
            update_query = "UPDATE utilisateur SET login_u = ? WHERE id_u = ?;"
            params = [modification, id_utilisateur]
        
        # Modification du prénom
        elif type_modification == "2":
            update_query = "UPDATE utilisateur SET prenom_u = ? WHERE id_u = ?;"
            params = [modification, id_utilisateur]
        
        # Modification du nom
        elif type_modification == "3":
            update_query = "UPDATE utilisateur SET nom_u = ? WHERE id_u = ?;"
            params = [modification, id_utilisateur]
        
        # Modification du mot de passe
        elif type_modification == "4":
            modification = hacher_mot_de_passe(modification)
            update_query = "UPDATE utilisateur SET mdp_u = ? WHERE id_u = ?;"
            params = [modification, id_utilisateur]
        
        # Modification de la ville
        elif type_modification == "5":
            query_ville = "SELECT id_ville FROM ville WHERE nom_ville = ?;"
            curseur.execute(query_ville, (modification,))
            ville_result = curseur.fetchone()

            if not ville_result:
                print(f"Échec : Ville '{modification}' introuvable.")
                return False

            id_ville = ville_result[0]
            update_query = "UPDATE utilisateur SET id_ville = ? WHERE id_u = ?;"
            params = [id_ville, id_utilisateur]
        
        else:
            print(f"Échec : Type de modification '{type_modification}' non valide.")
            return False

        # Exécution de la requête si elle a été construite
        if update_query:
            curseur.execute(update_query, params)
            connexion.commit()
            print(f"Modification de '{type_modification}' effectuée avec succès pour '{utilisateur.get_login()}'.")
            return True
        else:
            print("Aucune mise à jour effectuée.")
            return False

    except sqlite3.Error as e:
        print(f"Erreur lors de la modification : {e}")
        return False
    finally:
        deconnexion_BDD(connexion)





def supprimer_utilisateur(db_path, login):
    """
    Supprime un utilisateur de la base de données en utilisant son login.

    :param db_path: Chemin vers la base de données SQLite.
    :param login: Login de l'utilisateur à supprimer.
    :return: True si la suppression a réussi, False sinon.
    """
    # print(f"[DEBUG] Début de la suppression de l'utilisateur '{login}'")

    connexion = connexion_BDD(db_path)
    if not connexion:
        print("Échec de la connexion à la base de données.")
        return False

    try:
        curseur = connexion.cursor()

        # Récupérer l'ID de l'utilisateur via son login
        id_utilisateur = recuperer_id_utilisateur(db_path, login)
        
        if id_utilisateur is None:
            # print(f"[DEBUG] Utilisateur '{login}' introuvable.")
            return False

        # print(f"[DEBUG] ID de l'utilisateur trouvé : {id_utilisateur}")

        # Supprimer l'utilisateur
        delete_query = "DELETE FROM utilisateur WHERE id_u = ?;"
        params = (id_utilisateur,)

        # print(f"[DEBUG] Exécution de la requête : {delete_query} avec paramètres {params}")
        curseur.execute(delete_query, params)
        connexion.commit()

        print(f"Utilisateur '{login}' supprimé avec succès.")
        return True

    except sqlite3.Error as e:
        print(f" Erreur lors de la suppression : {e}")
        return False

    finally:
        print("suppression terminé")
        deconnexion_BDD(connexion)




##################################################          Affichage menu
def afficher_menu_generale():
    menu_ascii = """
    ===========================================
    |                                           |
    |   1. Se connecter                         |
    |   2. Quitter                              |
    |                                           |
    ===========================================
    Entrez votre choix (1-2) : 
    """
    print(menu_ascii)


def afficher_menu_connecter(type_u):
    if(type_u == "sa"):
        menu_ascii = """
        ===========================================
        |                                           |
        |   1. Ajouter un Utilisateur/Admin         |
        |   2. Modifier un Utilisateur/Admin        |
        |   3. Supprimer un Utilisateur/Admin       |
        |   4. Afficher les tous les utilisateurs   |
        |   5. Quitter                              |
        |                                           |
        ===========================================
        Entrez votre choix (1-5) : 
        """
    elif(type_u == "a"):
        menu_ascii = """
        ===========================================
        |                                           |
        |   1. Ajouter un Utilisateur               |
        |   2. Modifier un Utilisateur              |
        |   3. Supprimer un Utilisateur             |
        |   4. Afficher les utilisateurs            |
        |   5. Quitter                              |
        |                                           |
        ===========================================
        Entrez votre choix (1-4) : 
        """
    elif(type_u == "u"):
        menu_ascii = """
        ===========================================
        |                                           |
        |   Utilisateur standard connecté           |
        |                                           |
        ===========================================
        Entrez appuyer pour quitter 
        """
    else:
        menu_ascii = "Erreur"

    print(menu_ascii)


def afficher_menu_modification():
    menu_ascii = """
    ==============================================
    |                                             |
    |   1. Modifier le login                      |
    |   2. Modifier le prénom                     |
    |   3. Modifier le nom                        |
    |   4. Modifier le mot de passe               |
    |   5. Modifier la ville                      |
    |   Appuyez sur une autre touche pour quitter |
    |                                             |
    ==============================================
    Entrez votre choix (1-5) : 
    """
    print(menu_ascii)



def afficher_menu_mdp():
    menu_ascii = """
    ===========================================
    |                                           |
    |   1. Continuer avec ce mot de passe       |
    |   2. Générer un nouveau mot de passe      |
    |   3. Choisir mon mot de passer            |
    |                                           |
    ===========================================
    Entrez votre choix (1-3) : 
    """


    print(menu_ascii)

