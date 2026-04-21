### III. 4. Interface utilisateur

Afin d'apporter un outil interactif et un démonstrateur concret aux opérateurs de centrales hydroélectriques, une interface utilisateur (IHM) a été modélisée et implémentée. Il est primordial de souligner que seule l'approche par Programmation Dynamique (DP) a été formellement intégrée au sein de cette plateforme web. Ce choix méthodologique se justifie par la rapidité d'exécution largement supérieure de la DP comparativement à l'algorithme d'optimisation par boîte noire (NOMAD), garantissant ainsi un temps de réponse instantané pour l'utilisateur. En conséquence, l'interaction avec le site est proposée à titre d'exemple applicatif (*Proof of Concept*). Les résultats détaillés de l'algorithme NOMAD — dont l'évaluation itérative s'avère plus couteuse en temps — demeurent quant à eux rigoureusement documentés dans la suite de l'article, en dehors de l'interface utilisateur.

La méthodologie de conception de l'IHM s'est concentrée sur la séparation des préoccupations par l'entremise d'une architecture client-serveur (Frontend/Backend).

Côté serveur, l'interface s'appuie sur le *framework* Python asynchrone **FastAPI**, sélectionné pour ses hautes performances et sa fluidité de parsing JSON via **Pydantic**. L'algorithme d'optimisation (préalablement encapsulé dans les classes `HydroPlantModel` et `DPHydroOptimizer`) a été instancié globalement dans l'application pour répondre aux requêtes REST. Le backend expose ainsi deux interfaces de programmation (API) distinctes :
1.  **`/api/optimize`** : Conçue pour traiter des calculs ponctuels d'optimisation basés sur les saisies asynchrones de l'utilisateur (débit ciblé, contraintes d'équipement).
2.  **`/api/iterations`** : Dédiée à la simulation historique. Ce point d'accès s'appuie sur la bibliothèque **pandas** pour extraire avec précision les séries temporelles du jeu de données original, filtrer les observations valides, et itérer le solveur sur les différents points environnementaux pour restituer des tracés évolutifs.

Côté client, le *frontend* prend la forme d'un unique tableau de bord monolithique développé de façon fonctionnelle avec HTML/JavaScript et embelli via **TailwindCSS**. Cette orientation d'interface réactive élimine la charge liée aux rechargements de pages. L'affichage des données séquentielles et des courbes d'évolution est assuré par l'intégration de la librairie interactive **Chart.js**.

---

### IV. 4. Interface utilisateur

L'implémentation résultante de l'interface graphique prouve la cohésion solide du modèle mathématique lorsqu'il est instancié à travers un écosystème web.

En mode d'**opération statique (ponctuel)**, l'interface démontre une grande flexibilité. L'utilisateur interagit avec des champs de contraintes unitaires imposant par exemple des plafonds de turbinage ajustables (en respectant les capacités empiriques maximales) ou encore l'arrêt virtuel de certaines turbines pour maintenance (indisponibilité). L'algorithme, dès son exécution via l'interface, redistribue en temps réel l'ensemble de la puissance générée en tenant compte des pertes de charge spécifiques à chaque flux. L'écran de contrôle valide avec succès l'exclusion des turbines sélectionnées en assignant des débits de zéro tout en répartissant le quota du reliquat aux autres turbines valides.

En mode de **simulation temporelle (graphiques itératifs)**, l'interface tire directement parti des observations historiques documentées au sein du jeu de données initial. Lors du déclenchement manuel par l'opérateur, cinq tracés indépendants sont générés de manière fluide, traçant l'utilisation hydrodynamique de chacune des cinq turbines. Les axes des ordonnées ($y$) projettent visuellement le débit optimal assigné, réagissant dynamiquement face aux itérations (axe $x$) dictées par les 20 premiers vecteurs cibles (ex: changements météorologiques du débit du fleuve constatés dans l'historique du barrage). Le résultat graphique confirme que la surface d'approximation des fonctions productives s'adapte correctement de manière isolée pour chaque changement d'élévation amont face aux variations du fleuve.
