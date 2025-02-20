from fonction import *

class Utilisateur:
    def __init__(self, login, prenom, nom, mdp, type_utilisateur, ville):
        """
        Initialise un nouvel utilisateur.
        
        :param login: Le login de l'utilisateur.
        :param prenom: Le prénom de l'utilisateur.
        :param nom: Le nom de l'utilisateur.
        :param mdp: Le mot de passe de l'utilisateur.
        :param type_utilisateur: Le type de l'utilisateur (par exemple, admin, client, etc.).
        :param ville: La ville de l'utilisateur.
        """
        self.login = login
        self.prenom = prenom
        self.nom = nom
        self.mdp = mdp
        self.type_utilisateur = type_utilisateur
        self.ville = ville

    def set_type(self, type_utilisateur):
        self.type_utilisateur = type_utilisateur
        zdfpih

    def get_type(self):
        return self.type_utilisateur

    def set_ville(self, ville):
        self.ville = ville

    def get_ville(self):
        return self.ville
    def set_login(self, login):
        self.login = login

    def get_login(self):
        return self.login

    def set_mdp(self, mdp):
        self.mdp = mdp

    def get_mdp(self):
        return self.mdp
    
    def set_prenom(self, prenom):
        self.prenom = prenom

    def get_prenom(self):
        return self.prenom
    
    def set_nom(self, nom):
        self.nom = nom

    def get_nom(self):
        return self.nom
    
    def get_utilisateur(self):
        return self
