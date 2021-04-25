"""
    PROJET LANCELOT - Niv 4
    =======================
    Author : Matthieu PELINGRE
    Date : April 04, 2021

    Niv 1 : Affichage du plan du chateau dans Turtle.
    Niv 2 : Déplacement du personnage sur le plan.
    Niv 3 : Collecte des objets dans le chateau.
    Niv 4 : Gestion des portes et des enigmes.
"""

# modules
import turtle
from CONFIGS import *

# constantes globales
COULOIR = 0
MUR = 1
SORTIE = 2
PORTE = 3
OBJET = 4
VUE = 5

# variables globales
liste_inventaire = []
position_perso = POSITION_DEPART


"""Niveau 1 : lecture du plan et affichage avec turtle"""


# fonction de lecture du plan : lire_matrice()
def lire_matrice(fichier):
    """
    Permet de transposer le fichier en matrice python.

    :param fichier: chemin du fichier texte (encodé en UTF-8) du plan du chateau
    :type fichier: str
    :return: liste de liste d'entiers représentant le plan du chateau
    :rtype: list[list[int]]
    """
    with open(fichier, encoding='UTF-8') as fichier_in:
        return [[int(colonne) for colonne in ligne.split()] for ligne in fichier_in]  # crée et renvoie la matrice


# dépendances de afficher_plan()
def calculer_pas(matrice):
    """
    Calcule la dimension à donner aux cases pour l'affichage du plan.

    :param matrice: liste de liste d'entiers représentant le plan du chateau
    :type matrice: list[list[int]]
    :return: la longueur des côté des cases qui composent le plan
    :rtype: int

    .. warning:: utilise CONFIGS.py (ZONE_PLAN_MINI, ZONE_PLAN_MAXI)
    """
    nb_lignes = len(matrice)
    nb_colonnes = len(matrice[0])
    lx_affichage = abs(ZONE_PLAN_MAXI[0]) + abs(ZONE_PLAN_MINI[0])  # longueur sur l'axe des x de la zone d'affichage
    ly_affichage = abs(ZONE_PLAN_MAXI[1]) + abs(ZONE_PLAN_MINI[1])  # longueur sur l'axe des y de la zone d'affichage
    return min(lx_affichage//nb_colonnes, ly_affichage//nb_lignes)  # calcul le pas selon x et y, renvoie le plus petit


def coordonnees(case, pas):
    """
    Calcule les coordonnées en pixels turtle du coin inférieur gauche d'une case définie
    par ses coordonnées.

    :param case: coordonnées matricielles de la case sur le plan
    :param pas: longueur des côtés de la case
    :type case: tuple[int, int]
    :type pas : int
    :return: coordonnées (turtle) du coin inférieur gauche de la case
    :rtype: tuple[int, int]

    .. warning:: utilise CONFIGS.py (ZONE_PLAN_MINI, ZONE_PLAN_MAXI)
    """
    x_case = ZONE_PLAN_MINI[0] + case[1] * pas
    y_case = ZONE_PLAN_MAXI[1] - (1 + case[0]) * pas
    return x_case, y_case


def tracer_carre(dimension):
    """
    Trace un carré dans turtle de dimension donnée en argument.

    :param dimension: dimension du carré
    :type dimension: int
    :return: trace un carré
    :rtype: turtle

    .. warning:: utilise turtle
    .. note:: on assume turtle dans le sens initial et up() (en cas de translation)
    """
    turtle.down()
    turtle.begin_fill()
    for cote in range(4):  # pour chaque côté du carré
        turtle.forward(dimension)  # trace le côté
        turtle.left(90)  # tourne de 90° vers la gauche
    turtle.end_fill()
    turtle.up()


def tracer_case(case, couleur, pas):
    """
    Reçoit les coordonnées de la case, sa couleur et le pas.
    Appelle la fonction tracer_carre pour tracer le carre correspondant.

    :param case: coordonnées de la case en pixel turtle
    :param couleur: couleur à appliquer à la case
    :param pas: longueur des côtés de la case
    :type case: tuple[int, int]
    :type couleur: str
    :type pas: int
    :return: trace une case de coordonnée, de pas et de couleur indiquée
    :rtype: turtle

    .. warning:: utilise turtle, CONFIGS.py (COULEUR_EXTERIEUR) et tracer_carre(dimension)
    .. note:: on assume turtle dans le sens initial et down()
    .. seealso:: tracer_carre()
    """
    turtle.color(COULEUR_EXTERIEUR, couleur)
    turtle.up()
    turtle.goto(case)  # se déplace vers les coordonnées de la case
    tracer_carre(pas)   # trace le carré


# fonction principale d'affichage : afficher_plan()
def afficher_plan(matrice):
    """
    Dessine le plan dans turtle à partir de la matrice.

    :param matrice: liste de liste d'entiers représentant le plan du chateau
    :type matrice: list[list[int]]
    :return: trace le plan du chateau selon la matrice en paramètres
    :rtype: turtle

    .. warning:: utilise turtle, CONFIGS.py (COULEURS), calculer_pas(matrice), coordonnees(case, pas),
                 tracer_case(case, couleur, pas), tracer_annonce(texte), tracer_inventaire(inventaire),
                 tracer_perso(matrice, position)
    .. note:: on assume turtle dans le sens initial et down()
    .. seealso:: calculer_pas(), coordonnees(), tracer_carre(), tracer_annonce(), tracer_inventaire(),
                 tracer_perso()
    """
    nb_lignes = len(matrice)
    nb_colonnes = len(matrice[0])
    pas_mat = calculer_pas(matrice)
    for line in range(nb_lignes):  # pour chaque ligne
        for column in range(nb_colonnes):  # pour chaque colonne
            color = COULEURS[matrice[line][column]]  # on récupère la couleur de la case dans la liste
            coord_turtle = coordonnees((line, column), pas_mat)
            tracer_case(coord_turtle, color, pas_mat)  # on trace le carré
    tracer_annonce('Vous devez mener le point rouge jusqu\'à la sortie jaune.')  # initialisation des annonces
    tracer_inventaire([])  # initialisation de la zone de l'inventaire
    tracer_perso(matrice, POSITION_DEPART)  # trace la position initiale du personnage


"""Niveau 2 : gestion des déplacements"""


# fonctions de tracé, dépendances de deplacer()
def tracer_perso(matrice, position):
    """
    Trace le personnage à une position donnée.

    :param matrice: matrice du plan
    :param position: position en coordonnées matricielles
    :type matrice: list[list[int]]
    :type position: tuple[int, int]
    :return: trace le personnage à la position donnée
    :rtype: turtle

    .. warning:: utilise turtle, CONFIGS.py (COULEUR_PERSONNAGE) et la fonction coordonnées(case, pas)
    .. note:: on assume turtle dans le sens initial et up()
    .. seealso:: coordonnées()
    """
    pas_mat = calculer_pas(matrice)
    taille_perso = RATIO_PERSONNAGE * pas_mat  # calcul de la taille du perso
    x_perso, y_perso = coordonnees(position, pas_mat)  # calcul des coordonnées de la case du perso en pixel turtle
    turtle.goto(x_perso + pas_mat/2, y_perso + pas_mat/2)  # va au centre de la case
    turtle.down()
    turtle.dot(taille_perso, COULEUR_PERSONNAGE)  # trace le personnage
    turtle.up()


def case_def(matrice, position, type_case):
    """
    Change le type de case à la position donnée dans la matrice du plan et sur turtle.
    type_case :
    0 = couloir ;
    1 = mur ;
    2 = sortie ;
    3 = porte ;
    4 = objet ;
    5 = vue.

    :param matrice: matrice du plan
    :param position: position en coordonnées matricielles
    :param type_case: type voulu de la nouvelle case [0, 5]
    :type matrice: list[list(int)]
    :type position: tuple[int, int]
    :type type_case: int
    :return: trace la case et remplace sa valeur dans la matrice
    :rtype: turtle

    .. warning:: utilise CONFIGS.py (COULEURS) et la fonction tracer_case(case, couleur, pas)
    .. note:: modifie la matrice
    .. seealso:: tracer_case()
    """
    pas_mat = calculer_pas(matrice)
    ligne_pos, colonne_pos = position
    matrice[ligne_pos][colonne_pos] = type_case  # changement de la définition de la case dans la matrice du plan
    tracer_case(coordonnees(position, pas_mat), COULEURS[matrice[ligne_pos][colonne_pos]], pas_mat)
    # on trace la case de la bonne couleur sur turtle


# fonction de gestion des déplacements : deplacer()
def deplacer(matrice, position, mouvement, inventaire):
    """
    Déplace le personnage si le déplacement est possible.
    Possible si :
        - ne sort pas du plan
        - ne rentre pas dans un mur
        - n'est pas sur la case sortie

    :param matrice: matrice du plan
    :param position: position initiale
    :param mouvement: mouvement demandé
    :param inventaire: inventaire du personnage
    :type matrice: list[list(int)]
    :type position: tuple[int, int]
    :type mouvement: tuple[int, int]
    :type inventaire: list[str]
    :return: modifie la position du personnage si possible, trace le perso et retourne sa position
    :rtype: turtle or tuple[int, int]]

    .. warning:: utilise case_def(position, type_case), ramasser_objet(matrice, position, inventaire),
                 tracer_perso(position) et poser_question(matrice, case, mouvement)
    .. note:: - une porte (3) comme un mur (1)
              - modifie la matrice et l'inventaire
    .. seealso::  case_def(), tracer_perso(), ramasser_objet(), poser_question()
    """
    ligne_fin, colonne_fin = position[0] + mouvement[0], position[1] + mouvement[1]
    # coordonnées matricielles de la position finale
    if 0 <= ligne_fin < len(matrice) and 0 <= colonne_fin < len(matrice[0]) and matrice[position[0]][position[1]] != 2:
        # si la position finale est dans le plan (et que l'on est pas sur la sortie)
        if matrice[ligne_fin][colonne_fin] != MUR and matrice[ligne_fin][colonne_fin] != PORTE:
            # si la position finale n'est ni un mur, ni une porte
            case_def(matrice, position, VUE)  # la position précédente devient "vue"
            position = ligne_fin, colonne_fin  # change de position
            if matrice[ligne_fin][colonne_fin] == OBJET:  # si la case contient un objet
                ramasser_objet(matrice, position, inventaire)  # il est ramassé
            elif matrice[ligne_fin][colonne_fin] == SORTIE:  # si c'est la sortie
                tracer_annonce('Bravo ! Vous avez gagné !')
            tracer_perso(matrice, position)  # trace la nouvelle position du perso
        elif matrice[ligne_fin][colonne_fin] == PORTE:  # si on arrive sur une porte
            position = poser_question(matrice, position, mouvement)  # on pose la question correspondante
    return position


# fonctions évènements clavier
def deplacer_gauche():
    """
    Fonction événementielle d'appui sur la flèche gauche du clavier.
    Déplace le personnage si possible

    :return: modifie la position du personnage si possible
    :rtype: turtle

    .. warning:: utilise turtle, la fonction deplacer(matrice, position, mouvement, inventaire), ainsi que
                 les variables globales mat_plan, position_perso et liste_inventaire
    .. note:: - désactive la touche le temps du traitement
              - modifie mat_plan, position_perso et liste_inventaire
    .. seealso::  deplacer()
    """
    global mat_plan, position_perso, liste_inventaire
    turtle.onkeypress(None, "Left")   # Désactive la touche Left
    position_perso = deplacer(mat_plan, position_perso, (0, -1), liste_inventaire)
    # applique la fonction deplacer() pour modifier la position du perso
    turtle.onkeypress(deplacer_gauche, "Left")   # Réassocie la touche Left à la fonction deplacer_gauche


def deplacer_droite():
    """
    Fonction événementielle d'appui sur la flèche droite du clavier.
    Déplace le personnage si possible

    :return: modifie la position du personnage si possible
    :rtype: turtle

    .. warning:: utilise turtle, la fonction deplacer(matrice, position, mouvement, inventaire), ainsi que
                 les variables globales mat_plan, position_perso et liste_inventaire
    .. note:: - désactive la touche le temps du traitement
              - modifie mat_plan, position_perso et liste_inventaire
    .. seealso::  deplacer()
    """
    global mat_plan, position_perso, liste_inventaire
    turtle.onkeypress(None, "Right")
    position_perso = deplacer(mat_plan, position_perso, (0, 1), liste_inventaire)
    turtle.onkeypress(deplacer_droite, "Right")


def deplacer_haut():
    """
    Fonction événementielle d'appui sur la flèche haut du clavier.
    Déplace le personnage si possible

    :return: modifie la position du personnage si possible
    :rtype: turtle

    .. warning:: utilise turtle, la fonction deplacer(matrice, position, mouvement, inventaire), ainsi que
                 les variables globales mat_plan, position_perso et liste_inventaire
    .. note:: - désactive la touche le temps du traitement
              - modifie mat_plan, position_perso et liste_inventaire
    .. seealso::  deplacer()
    """
    global mat_plan, position_perso, liste_inventaire
    turtle.onkeypress(None, "Up")
    position_perso = deplacer(mat_plan, position_perso, (-1, 0), liste_inventaire)
    turtle.onkeypress(deplacer_haut, "Up")


def deplacer_bas():
    """
    Fonction événementielle d'appui sur la flèche bas du clavier.
    Déplace le personnage si possible

    :return: modifie la position du personnage si possible
    :rtype: turtle

    .. warning:: utilise turtle, la fonction deplacer(matrice, position, mouvement, inventaire), ainsi que
                 les variables globales mat_plan, position_perso et liste_inventaire
    .. note:: - désactive la touche le temps du traitement
              - modifie mat_plan, position_perso et liste_inventaire
    .. seealso::  deplacer()
    """
    global mat_plan, position_perso, liste_inventaire
    turtle.onkeypress(None, "Down")
    position_perso = deplacer(mat_plan, position_perso, (1, 0), liste_inventaire)
    turtle.onkeypress(deplacer_bas, "Down")


"""Niveau 3 : gestion des objets"""


# fonction de lecture des dictionnaires
def creer_dictionnaire(fichier_texte):
    """
    Permet de transposer le fichier en dictionnaire.

    :param fichier_texte: chemin du fichier texte (encodé en UTF-8) du dictionnaire
    :type fichier_texte: str
    :return: dictionnaire
    :rtype: dict
    """
    with open(fichier_texte, encoding='UTF-8') as fichier_in:
        return dict([eval(ligne) for ligne in fichier_in])  # crée et renvoie le dictionnaire


# dépendances de ramasser_objet()
def tracer_rectangle(dim_x, dim_y):
    """
    Trace un rectangle dans turtle de dimensions données en argument.

    :param dim_x: liste de liste d'entiers représentant le plan du chateau
    :param dim_y: liste de liste d'entiers représentant le plan du chateau
    :type dim_x: int
    :type dim_y: int
    :return: trace un rectangle
    :rtype: turtle

    .. warning:: utilise turtle
    .. note:: on assume turtle dans le sens initial et up() (en cas de translation)
    """
    turtle.down()
    turtle.begin_fill()
    for i in range(2):
        turtle.forward(dim_x)  # trace un côté dans l'axe des x
        turtle.right(90)
        turtle.forward(dim_y)  # trace un côté dans l'axe des y
        turtle.right(90)
    turtle.end_fill()
    turtle.up()


def tracer_annonce(texte):
    """
    Trace le texte dans la zone d'affichage des annonces (efface la précédente)

    :param texte: texte à écrire dans la zone d'affichage des annonces
    :type texte: str
    :return: affiche le texte dans la zone d'affichage des annonces
    :rtype: turtle

    .. warning:: utilise turtle
    .. note:: on assume turtle dans le sens initial et up() (en cas de translation)
    """
    turtle.goto(POINT_AFFICHAGE_ANNONCES)  # translation au point initial de la zone des annonces
    turtle.color(COULEUR_EXTERIEUR, COULEUR_CASES)  # applique la couleur de la zone
    long_annonce = abs(POINT_AFFICHAGE_ANNONCES[0]) * 2
    largeur_annonce = POINT_AFFICHAGE_ANNONCES[1] - POINT_AFFICHAGE_INVENTAIRE[1]
    tracer_rectangle(long_annonce, largeur_annonce)  # trace la zone d'affichage
    turtle.goto(0, POINT_AFFICHAGE_ANNONCES[1] - 4*largeur_annonce/5)  # déplace à l'emplacement du texte
    turtle.down()
    turtle.color('black')  # couleur du texte
    turtle.write(texte, align="center", font=('Arial', 10, 'bold'))  # affiche le texte
    turtle.up()


def tracer_inventaire(inventaire):
    """
    Trace l'inventaire dans la zone d'affichage de l'inventaire (n'efface pas la précédente)

    :param inventaire: texte à écrire dans la zone d'affichage des annonces
    :type inventaire: list[str]
    :return: affiche l'inventaire dans la zone d'affichage de l'inventaire
    :rtype: turtle

    .. warning:: utilise turtle
    .. note:: - on assume turtle dans le sens initial et up() (en cas de translation)
              - ne peut pas être utilisée si des objets doivent être enlevés de l'inventaire
    """
    if len(inventaire) == 0:  # initialisation de l'inventaire
        turtle.goto(POINT_AFFICHAGE_INVENTAIRE[0], POINT_AFFICHAGE_INVENTAIRE[1] - 40)
        # déplace à l'emplacement du texte
        turtle.down()
        turtle.color('black')  # couleur du texte
        turtle.write('        Inventaire :', font=('Arial', 8, 'bold'))  # affiche le titre de la zone d'inventaire
        turtle.up()
    else:  # pour tracer la dernière entrée de l'inventaire
        n_dernier = len(inventaire)
        turtle.goto(POINT_AFFICHAGE_INVENTAIRE[0], POINT_AFFICHAGE_INVENTAIRE[1] - 50 - 20 * n_dernier)
        turtle.write(f' N°{n_dernier} : {inventaire[n_dernier - 1]}')  # inscrit l'entrée
        turtle.up()


# fonction principale de gestion des objets : ramasser_objet()
def ramasser_objet(matrice, position, inventaire):
    """
    Ramasse l'objet à la position donnée et l'ajoute à l'inventaire.
    La case devient vide.

    :param matrice: matrice du plan
    :param position: position en coordonnées matricielles
    :param inventaire: inventaire du personnage
    :type matrice: list[list(int)]
    :type position: tuple[int, int]
    :type inventaire: list[str]
    :return: ajoute l'objet à l'inventaire et remplace la case par une case vide
    :rtype: turtle

    .. warning:: dict_objet et les fonction tracer_annonce(texte), tracer-inventaire(inventaire)
                 et case_def(matrice, position, type_case)
    .. note:: modifie la matrice et l'inventaire
    .. seealso:: tracer_annonce(), tracer-inventaire() et case_def()
    """
    new_object = dict_objet[position]
    tracer_annonce(f'Vous avez trouvé : {new_object}')  # trace l'annonce de la découverte de l'objet
    inventaire.append(new_object)  # ajoute l'objet à l'inventaire
    tracer_inventaire(inventaire)  # trace l'inventaire dans turtle
    case_def(matrice, position, COULOIR)  # change en couloir la case où se trouvait l'objet


"""Niveau 4 : Gestion des portes"""


def poser_question(matrice, case, mouvement):
    """
    Pose la question de la porte rencontrée après mouvement de la case.

    :param matrice: plan du château
    :param case: position initiale du perso
    :param mouvement: mouvement à effectuer pour arriver sur la porte
    :type matrice: list[list[int]]
    :type case: tuple[int, int]
    :type mouvement: tuple[int, int]
    :return: deplace ou non le personnage en fonction de la réponse
    :rtype: turtle or tuple[int, int]
    """
    new_case = (case[0] + mouvement[0], case[1] + mouvement[1])
    tracer_annonce('Cette porte est fermée.')
    if turtle.textinput('Question', dict_porte[new_case][0]) == dict_porte[new_case][1]:
        tracer_annonce('La porte s\'ouvre.')
        case_def(matrice, case, VUE)  # la position précédente devient "vue"
        case = new_case
        case_def(matrice, case, COULOIR)  # la porte devient un couloir
        tracer_perso(matrice, case)  # le personnage se déplace
    else:
        tracer_annonce('Mauvaise réponse.')
    turtle.listen()
    return case  # on renvoie la position du personnage


"""End : Core"""


# core - turtle : paramètres d'affichage
turtle.title('Escape Game - Lancelot au château du Python des Neiges')  # change le titre de la fenêtre
turtle.tracer(0, 0)  # désactive le rafraichissement d'écran de turtle (tracé instantané)
turtle.hideturtle()  # cache le pointeur turtle
turtle.setup(480, 480)  # affiche une fenêtre aux bonnes dimensions (optionnel)

# core - Niv 1 : initialisation du plan
mat_plan = lire_matrice(fichier_plan)  # convertit le plan.txt en matrice
afficher_plan(mat_plan)  # affiche le plan

# core - Niv 3 : initialisation des objets
dict_objet = creer_dictionnaire(fichier_objets)

# core - Niv 4 : initialisation des portes
dict_porte = creer_dictionnaire(fichier_questions)

# core - Niv 2 : déplacements
turtle.listen()    # Déclenche l’écoute du clavier
turtle.onkeypress(deplacer_gauche, "Left")   # Associe à la touche Left la fonction deplacer_gauche
turtle.onkeypress(deplacer_droite, "Right")
turtle.onkeypress(deplacer_haut, "Up")
turtle.onkeypress(deplacer_bas, "Down")
turtle.mainloop()    # Place le programme en position d’attente d’une action du joueur
