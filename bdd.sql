-- Suppression des tables si elles existent déjà
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS type_utilisateur;
DROP TABLE IF EXISTS ville;

-- Création de la table "ville"
CREATE TABLE ville (
    id_ville INTEGER PRIMARY KEY AUTOINCREMENT, -- ID unique auto-incrémenté
    nom_ville TEXT NOT NULL                     -- Nom de la ville
);

-- Création de la table "type_utilisateur"
CREATE TABLE type_utilisateur (
    id_type INTEGER PRIMARY KEY AUTOINCREMENT, -- ID unique auto-incrémenté
    type_u TEXT NOT NULL                       -- Type d'utilisateur
);

-- Création de la table "utilisateur"
CREATE TABLE utilisateur (
    id_u INTEGER PRIMARY KEY AUTOINCREMENT,-- ID unique auto-incrémenté
    login_u TEXT NOT NULL,     
    prenom_u TEXT NOT NULL,                -- Login utilisateur
    nom_u TEXT NOT NULL, 
    mdp_u TEXT NOT NULL,                   -- Mot de passe utilisateur
    id_type INTEGER NOT NULL DEFAULT 3,    -- Référence vers le type d'utilisateur, par défaut 3
    id_ville INTEGER NOT NULL,             -- Référence vers la ville
    FOREIGN KEY (id_type) REFERENCES type_utilisateur(id_type), -- Clé étrangère vers type_utilisateur
    FOREIGN KEY (id_ville) REFERENCES ville(id_ville)           -- Clé étrangère vers ville
);

-- Insertion des villes
INSERT INTO ville (nom_ville) VALUES
('Paris'),
('Rennes'),
('Strasbourg'),
('Grenoble'),
('Nantes');

-- Insertion des types d'utilisateur
INSERT INTO type_utilisateur (type_u) VALUES
('sa'),
('a'),
('u');

-- Insertion d'un utilisateur
INSERT INTO utilisateur (login_u, prenom_u, nom_u, mdp_u, id_type, id_ville)
VALUES ('sadmin', 'super', 'admin', '86f83ca82104570c257479d73978418422d78569ce7eae3c77c4c1b2093d1d5b', 1, 1);

