import time
from fonction import *
from utilisateur import *

# Chemin vers la base de données
db_path = "bdd.db"
fermer_prog = False
utilisateur_connecte = False

# Dictionnaire pour suivre les tentatives de connexion et appliquer un verrouillage si nécessaire
tentatives_utilisateurs = {}  # Format : {login: (nombre_de_tentatives, timestamp_du_premier_echec)}



# Boucle principale du programme
while not fermer_prog:
    afficher_menu_generale()  # Affiche le menu principal
    choix_connexion = input("Saisir une action : ")

    if choix_connexion == "1":
        # Bloc de connexion de l'utilisateur
        connexion_terminee = False

        while not connexion_terminee:
            login_util = input("Saisir le login : ")

            # Vérification si l'utilisateur est actuellement verrouillé après plusieurs tentatives
            if login_util in tentatives_utilisateurs:
                tentatives, debut_verrouillage = tentatives_utilisateurs[login_util]
                if tentatives >= 3:
                    temps_restant = 30 - (time.time() - debut_verrouillage)
                    if temps_restant > 0:
                        print(f"Trop de tentatives. Réessayez dans {int(temps_restant)} secondes.")
                        continue  # Empêche la saisie du mot de passe tant que le délai n'est pas écoulé
                    else:
                        # Le délai de verrouillage est passé, on réinitialise le compteur
                        del tentatives_utilisateurs[login_util]

            # Saisie et hachage du mot de passe
            mdp_util = input("Saisir le mot de passe : ")
            mdp_util = hacher_mot_de_passe(mdp_util)

            # Tentative de connexion via la base de données
            result_connexion = connexion_utilisateur(db_path, login_util, mdp_util)

            if result_connexion:
                # Connexion réussie : création de l'objet utilisateur connecté
                utilisateur_connecte = creation_utilisateur_connexion(db_path, login_util)
                print(f"Connecté en tant que : {utilisateur_connecte.get_type()}")

                # Réinitialise les tentatives pour ce login après un succès
                tentatives_utilisateurs.pop(login_util, None)
                connexion_terminee = True  # Sortie de la boucle de connexion

                # Boucle pour gérer les actions de l'utilisateur connecté
                action_terminee = False
                while not action_terminee:
                    afficher_menu_connecter(utilisateur_connecte.get_type())
                    choix_action = input("Saisir une action : ")

                    # Gestion pour Super Administrateur (type "sa")
                    if utilisateur_connecte.get_type() == "sa":
                        # 1 - Ajout d'un utilisateur ou d'un administrateur
                        if choix_action == "1":
                            prenom = input("Saisir le prenom du nouvel utilisateur/admin : ")
                            nom = input("Saisir le nom du nouvel utilisateur/admin : ")
                            # Saisie du choix de génération de mot de passe
                            # Saisie du choix de génération de mot de passe
                            choix_mdp = input("Voulez-vous générer un mot de passe aléatoire (o/n) ? ")
                            if choix_mdp != "o" and choix_mdp != "n":
                                while choix_mdp =="o" and choix_mdp == "n":
                                    print("Erreur saisi")
                                    choix_mdp = input("Voulez-vous générer un mot de passe aléatoire (o/n) ? ")

                            # Vérification des saisies
                            if choix_mdp == "o":
                                choix_generation_mdp = "o"
                                while choix_generation_mdp == "o":
                                    try:
                                        # Demande de la longueur souhaitée pour le mot de passe
                                        longueur_mdp = int(input("Combien de caractères voulez-vous ? "))
                                    except ValueError:
                                        print("Entrée invalide. Veuillez saisir un nombre.")
                                        continue  # Redemande la longueur si la conversion échoue
                                    mdp = generer_mdp(longueur_mdp)
                                    print(mdp)
                                    afficher_menu_mdp()
                                    mdp_ok = input("Saisir une action : ")
                                    if mdp_ok == "1":
                                        # Mot de passe validé
                                        choix_generation_mdp = "n"
                                    elif mdp_ok == "3":
                                        # Annulation de la génération automatique
                                        choix_mdp = "n"
                                        choix_generation_mdp = "n"

                            elif choix_mdp == "n":
                                # Saisie manuelle du mot de passe
                                mdp = input("Saisir le mot de passe : ")

                                # Hachage du mot de passe et saisie des autres informations
                                mdp = hacher_mot_de_passe(mdp)
                            login = generer_login(db_path, prenom, nom)
                            recuperer_villes(db_path)
                            ville_nom = input("Saisir la ville de l'utilisateur : ")
                            if verifier_ville_existe(db_path, ville_nom):
                                type_utilisateur_ajout = input("Saisir le type de l'utilisateur/admin (u/a): ")
                                creation_utilisateur = Utilisateur(login, prenom, nom, mdp, type_utilisateur_ajout, ville_nom)
                                ajouter_utilisateur(db_path, creation_utilisateur)
                            else:
                                print("La ville n'existe pas")



                           

                        # 2 - Modification d'un utilisateur ou d'un administrateur
                        elif choix_action == "2":
                            list_u = recuperer_utilisateurs(db_path, utilisateur_connecte.get_login())
                            afficher_liste_utilisateurs(list_u)
                            afficher_menu_modification()
                            choix_modif = input("Saisir une action : ")
                            if choix_modif in ["1", "2", "3", "4", "5"]:
                                if choix_modif == "5":
                                    recuperer_villes(db_path)
                                login_modif = input("Saisir le login de l'utilisateur : ")
                                nouvelle_valeur = input("Saisir la nouvelle valeur : ")
                                utilisateur_modif = creation_utilisateur_connexion(db_path, login_modif)
                                if recherche_utilisateur(db_path, login_modif):
                                    modifier_utilisateur(db_path, utilisateur_modif, nouvelle_valeur, choix_modif, utilisateur_connecte)
                                else:
                                    print("utiisateur inexistant")
                            print("Retour au menu d'administration.")

                        # 3 - Suppression d'un utilisateur ou d'un administrateur
                        elif choix_action == "3":
                            login_supp = input("Saisir le login de l'utilisateur à supprimer : ")
                            utilisateur_a_supprimer = recherche_utilisateur(db_path, login_supp)

                            if utilisateur_a_supprimer:  # Vérifie si l'utilisateur existe
                                if utilisateur_a_supprimer.get_type() == "u" or utilisateur_a_supprimer.get_type() == "a":  # Vérifie si c'est un utilisateur standard
                                    suppression_reussie = supprimer_utilisateur(db_path, login_supp)
                                    if suppression_reussie:
                                        print(f"L'utilisateur '{login_supp}' a été supprimé avec succès.")
                                    else:
                                        print(f"Erreur lors de la suppression de '{login_supp}'.")
                                else:
                                    print("Vous ne pouvez supprimer qu'un utilisateur ou un administrateur.")
                            else:
                                print(f"Aucun utilisateur trouvé avec le login '{login_supp}'.")


                        elif choix_action == "4":
                            list_u = recuperer_utilisateurs(db_path, utilisateur_connecte.get_login())
                            afficher_liste_utilisateurs(list_u)


                        # Toute autre saisie retourne au menu principal
                        else:
                            print("Retour au menu principal.")
                            action_terminee = True

                    # Gestion pour Administrateur (type "a")
                    elif utilisateur_connecte.get_type() == "a":
                        # 1 - Ajout d'un utilisateur
                        if choix_action == "1":
                            prenom = input("Saisir le prenom du nouvel utilisateur/admin : ")
                            nom = input("Saisir le nom du nouvel utilisateur/admin : ")
                            # Saisie du choix de génération de mot de passe
                            # Saisie du choix de génération de mot de passe
                            choix_mdp = input("Voulez-vous générer un mot de passe aléatoire (o/n) ? ")
                            if choix_mdp != "o" and choix_mdp != "n":
                                while choix_mdp =="o" and choix_mdp == "n":
                                    print("Erreur saisi")
                                    choix_mdp = input("Voulez-vous générer un mot de passe aléatoire (o/n) ? ")

                            # Vérification des saisies
                            if choix_mdp == "o":
                                choix_generation_mdp = "o"
                                while choix_generation_mdp == "o":
                                    try:
                                        # Demande de la longueur souhaitée pour le mot de passe
                                        longueur_mdp = int(input("Combien de caractères voulez-vous ? "))
                                    except ValueError:
                                        print("Entrée invalide. Veuillez saisir un nombre.")
                                        continue  # Redemande la longueur si la conversion échoue
                                    mdp = generer_mdp(longueur_mdp)
                                    print(mdp)
                                    afficher_menu_mdp()
                                    mdp_ok = input("Saisir une action : ")
                                    if mdp_ok == "1":
                                        # Mot de passe validé
                                        choix_generation_mdp = "n"
                                    elif mdp_ok == "3":
                                        # Annulation de la génération automatique
                                        choix_mdp = "n"
                                        choix_generation_mdp = "n"

                            elif choix_mdp == "n":
                                # Saisie manuelle du mot de passe
                                mdp = input("Saisir le mot de passe : ")

                                # Hachage du mot de passe et saisie des autres informations
                                mdp = hacher_mot_de_passe(mdp)
                            login = generer_login(db_path, prenom, nom)
                            recuperer_villes(db_path)
                            ville_nom = input("Saisir la ville de l'utilisateur : ")
                            if verifier_ville_existe(db_path, ville_nom):
                                creation_utilisateur = Utilisateur(login, prenom, nom, mdp, "u", ville_nom)
                                ajouter_utilisateur(db_path, creation_utilisateur)
                            else:
                                print("La ville n'existe pas")

                        # 3 - Suppression d'un utilisateur
                        elif choix_action == "3":
                            login_supp = input("Saisir le login de l'utilisateur à supprimer : ")
                            utilisateur_a_supprimer = recherche_utilisateur(db_path, login_supp)

                            if utilisateur_a_supprimer:  # Vérifie si l'utilisateur existe
                                if utilisateur_a_supprimer.get_type() == "u":  # Vérifie si c'est un utilisateur standard
                                    if utilisateur_a_supprimer.get_ville() == utilisateur_connecte.get_ville(): #Vérifie que l'utilisateur à supprimier et dans la même ville que l'administrateur.
                                        suppression_reussie = supprimer_utilisateur(db_path, login_supp)
                                        if suppression_reussie:
                                            print(f"L'utilisateur '{login_supp}' a été supprimé avec succès.")
                                        else:
                                            print(f"Erreur lors de la suppression de '{login_supp}'.")
                                    else:
                                        print("L'utilisateur à supprimé doit être dans la même ville que vous.")
                                else:
                                    print("Vous ne pouvez supprimer qu'un utilisateur standard.")
                            else:
                                print(f"Aucun utilisateur trouvé avec le login '{login_supp}'.")

                        elif choix_action == "4":
                            list_u = recuperer_utilisateurs(db_path, utilisateur_connecte.get_login())
                            afficher_liste_utilisateurs(list_u)

                        else:
                            print("Retour au menu principal.")
                            action_terminee = True

                    # Gestion pour les utilisateurs standards (type "u")
                    elif utilisateur_connecte.get_type() == "u":
                        print("Aucune action disponible pour les utilisateurs standard.")
                        action_terminee = True

            else:
                # Connexion échouée : mise à jour du compteur de tentatives
                tentatives_utilisateurs[login_util] = tentatives_utilisateurs.get(login_util, (0, time.time()))
                tentatives, _ = tentatives_utilisateurs[login_util]
                tentatives_utilisateurs[login_util] = (tentatives + 1, time.time())

                print("Erreur de connexion. Veuillez réessayer.")

                if tentatives_utilisateurs[login_util][0] >= 3:
                    print("Trop d'échecs. Vous devez attendre 30 secondes avant de réessayer.")

    elif choix_connexion == "2":
        # Fin du programme
        print("Fin du programme.")
        fermer_prog = True

    else:
        # Saisie invalide dans le menu principal
        print("Erreur de saisie.")
