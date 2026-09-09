# Cantine Radis la Toque - custom integration Home Assistant

Cette intégration reprend le scraping du site https://www.radislatoque.fr et l'intègre directement dans Home Assistant.

## Fonctionnement

- configuration par l'interface Home Assistant avec l'id du restaurant (ville) + nom du sensor désiré ;
- récupération du planning de la semaine courante ;
- actualisation automatique tous les jours à 06:10 (heure locale de Home Assistant) ;
- après un redémarrage postérieur à 06:00, une actualisation est faite si celle du jour manque ;
- actualisation manuelle par un bouton ;
- conservation en stockage interne Home Assistant de la dernière récupération réussie ;
- si une actualisation réseau échoue, le planning précédent n'est pas écrasé ;

## Installation

Copier le dossier :

    custom_components/cantine_radislatoque

dans le dossier `/config/custom_components/` de Home Assistant.

La structure doit donc être :

    /config/custom_components/cantine_radislatoque/manifest.json
    /config/custom_components/cantine_radislatoque/__init__.py
    ...

Redémarrer Home Assistant, puis aller dans :

    Paramètres > Appareils et services > Ajouter une intégration

et rechercher :

    Cantine Radis la Toque

## Entités

L'intégration crée notamment :

    sensor.menu_cantine_radis_la_toque
    button.cantine_radis_la_toque_actualiser_le_menu
    select.jour_du_menu

Les entity_id exacts peuvent varier si des entités portant ces noms existent déjà.
Utiliser les noms affichés dans Home Assistant pour confirmer.

L'état du sensor est la date/heure de la dernière récupération réussie.

Attributs principaux :

    planning
    last_update
    last_error

`planning` contient uniquement la semaine courante (pour le moment).

## Exemple Markdown Lovelace
La partie pour sélectionné le jour à afficher (se met à jour au moment de l'actualisation automatique) :
```
type: tile
entity: select.jour_du_menu
show_entity_picture: false
hide_state: true
vertical: false
features:
  - type: select-options
features_position: inline
```
La partie qui affiche le menu du jour sélectionné : 
```
type: markdown
content: >
  {% set planning = state_attr('sensor.menu_cantine_radis_la_toque', 'planning')
  | default({}, true) %}

  {% set selection = states('select.jour_du_menu') %}

  {# Recherche du menu correspondant au jour sélectionné #}

  {% set menu = namespace(data=none) %}

  {% for cle, repas in planning.items() %}
    {% if repas.jour | lower == selection | lower %}
      {% set menu.data = repas %}
    {% endif %}
  {% endfor %}

  {% if menu.data %}

  # <center>📅 {{ menu.data.jour | capitalize }}</center>

  {% if menu.data.repas_vegetarien %} 
    --- 
    🌱 **Option végétarienne disponible**
  {% endif %}

  ---

  🥗 **ENTRÉE**   {{ menu.data.entree }}


  🍽️ **PLAT**   {{ menu.data.plat }}

    
  {% if menu.data.plat_vegetarien %} 🌱 **VÉGÉTARIEN** {{
  menu.data.plat_vegetarien }}

  {% endif %}

  🥕 **ACCOMPAGNEMENT**   {{ menu.data.legumes }}


  🧀 **FROMAGE**   {{ menu.data.fromage }}

    
  🍎 **DESSERT**   {{ menu.data.dessert }}

    
  {% else %} ## 😕 Pas de menu Aucun menu disponible pour **{{ selection }}**.
  {% endif %}

```

## Débogage

Pour activer les logs détaillés :

    logger:
      default: info
      logs:
        custom_components.espace_citoyen: debug
