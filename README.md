## Projet : Déploiement d’une application Flask sur AWS avec Terraform

Ce projet a été réalisé dans le cadre d’un cours de cloud / DevOps.

L’objectif est de déployer une petite application Flask sur une machine virtuelle dans le cloud (AWS) et d’utiliser un stockage S3 pour garder des fichiers (par exemple des images). Toute l’infrastructure est créée avec Terraform.

L’infrastructure reste volontairement simple pour bien comprendre les bases :

- une instance EC2 (Ubuntu) qui fait tourner Flask ;
- un bucket S3 privé pour stocker les fichiers uploadés ;
- un script de démarrage qui installe Python, Flask et lance l’application.

---

### 1. Structure du projet

A la racine du dépôt, on trouve principalement trois dossiers :

- `terraform/` : tout ce qui concerne l’infrastructure
  - `main.tf` : définition des ressources (EC2, S3, security group, etc.)
  - `provider.tf` : configuration du provider AWS
  - `variables.tf` : variables utilisées dans le projet
  - `outputs.tf` : valeurs affichées à la fin (IP de la VM, nom du bucket…)
  - `terraform.tfvars.example` : exemple de fichier de variables
- `app/` : code de l’application Flask
  - `app.py` : code de l’API Flask (routes, upload de fichiers, etc.)
  - `requirements.txt` : dépendances Python à installer
  - `config_example.py` : petit exemple de configuration
- `provisioning/` : scripts exécutés sur la VM
  - `user_data.sh` : script lancé au démarrage de la machine pour installer et lancer l’application

---

### 2. Prérequis

Pour pouvoir exécuter le projet, il faut :

- un compte **AWS** (avec au minimum l’accès à EC2 et S3) ;
- **AWS CLI** installé et configuré (`aws configure`) ;
- **Terraform** installé sur la machine ;
- une **clé SSH** pour se connecter éventuellement à l’instance EC2
  - par exemple `~/.ssh/id_rsa` et `~/.ssh/id_rsa.pub`.

Sous Windows, on peut utiliser WSL ou Git Bash pour gérer les clés SSH.

---

### 3. Configuration de Terraform

Dans le dossier `terraform/`, il faut créer un fichier `terraform.tfvars` (ce fichier ne doit pas être commité). On peut partir du modèle `terraform.tfvars.example` fourni.

Exemple de contenu :

```hcl
aws_region        = "eu-west-3"
project_name      = "projet-cloud-flask"
instance_type     = "t2.micro"
public_key_path   = "C:/Users/ton_user/.ssh/id_rsa.pub"
allowed_ssh_cidr  = "X.X.X.X/32"
allowed_http_cidr = "0.0.0.0/0"
```

Il faut adapter :

- la région (`aws_region`) ;
- le chemin vers la clé publique SSH (`public_key_path`) ;
- l’adresse IP autorisée en SSH (`allowed_ssh_cidr`) ;
- éventuellement les règles HTTP (`allowed_http_cidr`).

---

### 4. Déploiement de l’infrastructure

Dans un terminal, se placer dans le dossier `terraform/` puis lancer :

```bash
terraform init
terraform plan
terraform apply
```

Terraform affiche un plan des ressources créées. Il faut confirmer l’`apply` pour lancer réellement le déploiement.

A la fin, Terraform affiche plusieurs valeurs, notamment :

- l’IP publique de l’instance EC2 ;
- le nom du bucket S3 ;
- l’URL pour accéder à l’application Flask.

---

### 5. Tests de l’application Flask et de S3

Une fois le déploiement terminé :

1. **Accès à l’application**
   - Ouvrir un navigateur et aller sur `http://<ip_publique>` (l’IP est donnée par Terraform).
   - On doit voir une page de bienvenue simple indiquant le nom du bucket S3 utilisé.

2. **Upload d’un fichier**
   - Utiliser le petit formulaire présent sur la page d’accueil pour envoyer un fichier.
   - On peut aussi tester avec `curl` :

   ```bash
   curl -F "file=@chemin/vers/fichier.png" http://<ip_publique>/upload
   ```

3. **Liste des fichiers**
   - Aller sur `http://<ip_publique>/files` pour voir les fichiers présents dans le bucket S3.
   - Vérifier dans la console AWS S3 que les objets ont bien été créés dans le bucket.

---

### 6. Destruction de l’infrastructure

Quand les tests sont terminés, il faut supprimer les ressources pour ne pas laisser tourner la VM et éviter des coûts inutiles.

Depuis le dossier `terraform/` :

```bash
terraform destroy
```

Terraform affiche la liste des ressources à supprimer. Il faut confirmer pour lancer la destruction.

---

### 7. Idées pour le rapport de projet

Pour le rapport écrit, on peut par exemple :

- décrire les grandes étapes :
  - préparation de l’environnement (installation Terraform, configuration AWS) ;
  - création des fichiers Terraform ;
  - déploiement de l’infrastructure ;
  - tests de l’application Flask et du stockage S3 ;
  - destruction des ressources.
- ajouter quelques captures d’écran :
  - résultat de `terraform apply` ;
  - console EC2 (instance en cours d’exécution) ;
  - console S3 avec les fichiers uploadés ;
  - navigateur montrant la page Flask.
- expliquer les problèmes rencontrés (erreurs Terraform, ports, IAM, etc.) et comment ils ont été corrigés.


