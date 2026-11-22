# Table de 3 — Vidéo animée style jeu vidéo vintage (football)

Animation 1080x1920 (vertical, 30 fps, ~49 s) : vu du dessus, un joueur de foot
tire des ballons vers un but ou s'affichent les opérations de la table de 3
(3*1 a 3*10). Un gardien patrouille et plonge. Quand le ballon touche
l'operation hors de portée du gardien : explosion, texte GOAL! et le bon
resultat s'affiche. Sur le deuxieme essai (3*2), le gardien arrete le ballon :
son d'erreur (NON !), puis tir reussi. Finale : CHAMPION, coupe doree,
feux d'artifice et confettis. Le bandeau **MATHS MONDE** est affiche en
permanence. Couleurs : #F72585, #7209B7, #3A0CA3, #4361EE, #4CC9F0.

Musique 8-bit a 136 BPM : melodie carree sur partition 8 mesures (Mib6-Si5-Sol#5 ; mib6/si6...
accordee en Sol# mineur - basse rebond G#2/C#3/D#3, grosse caisse sur tous les temps,
caisse claire sur les temps 2 et 4)
+ effets : sifflet, frappe, buzz d'erreur, jingle GOAL + foule, fanfare.

## Contenu du depot

- `table_de_3_1080x1920.mp4` — la video generee (re-generee par le workflow CI)
- `font5x7.py` — police pixel 5x7
- `timeline3.py` — chronologie et logique des tirs (trajectoires, plongeons)
- `audio3.py` — musique 8-bit + effets sons (numpy -> WAV)
- `render3.py` — rendu des frames + encodage ffmpeg (1080x1920)
- `.github/workflows/generate.yml` — workflow qui regenere la video et la commite

## Regeneration

`pip install pillow numpy imageio-ffmpeg` puis `python3 audio3.py && python3 render3.py`
ou lancer le workflow **Generate video** (onglet Actions).
