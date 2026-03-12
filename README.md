## Projet : Déploiement Automatisé d’une Application Flask sur AWS avec Terraform

Ce projet met en place une **infrastructure minimale sur AWS** avec **Terraform** :

- une instance EC2 Ubuntu qui héberge une application **Flask** ;
- un bucket **S3** privé pour stocker des fichiers statiques (uploads) ;
- un déploiement **automatisé** : la VM installe Python/Flask et lance l’application au démarrage.

L’objectif est pédagogique : montrer comment automatiser la création d’une VM, d’un stockage cloud et le déploiement d’un backend Flask avec Terraform.

---

### 1. Structure du projet

- `terraform/`
  - `main.tf`
  - `provider.tf`
  - `variables.tf`
  - `outputs.tf`
  - `terraform.tfvars.example`
- `app/`
  - `app.py`
  - `requirements.txt`
  - `config_example.py`
- `provisioning/`
  - `user_data.sh`

---

### 2. Prérequis

- Un compte **AWS** avec droits basiques (EC2, S3, IAM si nécessaire).
- **AWS CLI** installé et configuré (`aws configure`) avec un profil par défaut fonctionnel.
- **Terraform** installé (version récente).
- **Une clé SSH** existante côté client :
  - par exemple `~/.ssh/id_rsa` et `~/.ssh/id_rsa.pub`.

Sous Windows, tu peux utiliser WSL ou Git Bash pour générer/gerer les clés SSH.

---

### 3. Configuration Terraform

1. Crée un fichier `terraform/terraform.tfvars` (non commité) à partir de l’exemple :

```hcl
aws_region       = "eu-west-3"
project_name     = "projet-cloud-flask"
instance_type    = "t2.micro"
public_key_path  = "C:/Users/ton_user/.ssh/id_rsa.pub"
allowed_ssh_cidr = "X.X.X.X/32"     # ton IP publique
allowed_http_cidr = "0.0.0.0/0"     # ou plus restreint si tu préfères
```

2. Adapte :
- la région (`aws_region`) ;
- le chemin vers ta clé publique (`public_key_path`) ;
- les CIDR d’accès SSH/HTTP.

---

### 4. Déploiement de l’infrastructure

Dans le dossier `terraform/` :

```bash
terraform init
terraform plan
terraform apply
```

Confirme l’`apply` lorsque Terraform affiche le plan.

À la fin, Terraform affiche :
- l’**IP publique** de la VM ;
- le **nom du bucket S3** ;
- l’URL HTTP d’accès à l’application.

---

### 5. Tester l’application Flask et le stockage S3

1. **Accès à l’application**
   - Ouvre dans ton navigateur : `http://<ip_publique>` (ou `http://<ip_publique>:80` selon la sortie Terraform).
   - Tu dois voir une page d’accueil simple Flask indiquant le nom du bucket S3.

2. **Upload de fichier**
   - Depuis la page Flask, utilise le formulaire d’upload, ou bien via `curl` :

```bash
curl -F "file=@chemin/vers/fichier.png" http://<ip_publique>/upload
```

3. **Liste des fichiers**
   - Va sur `http://<ip_publique>/files` pour voir la liste des objets présents dans le bucket S3.
   - Vérifie dans la console AWS S3 que les fichiers sont bien créés dans le bucket.

---

### 6. Détruire l’infrastructure

Quand tu as terminé les tests, détruis tout avec :

```bash
cd terraform
terraform destroy
```

Confirme la destruction lorsque Terraform demande validation.

---

### 7. Rapport de projet (idée de contenu)

- Décrire les étapes :
  - préparation de l’environnement Terraform/AWS ;
  - création de la configuration Terraform ;
  - déploiement de la VM, du bucket S3 et de l’appli Flask ;
  - tests d’accès à l’app et au stockage ;
  - destruction de l’infrastructure.
- Ajouter quelques captures d’écran :
  - sortie de `terraform apply` ;
  - console EC2 (instance en running) ;
  - console S3 avec des objets dans le bucket ;
  - navigateur avec la page Flask et un upload réussi.
- Noter les problèmes rencontrés (ports, user_data, IAM, etc.) et comment tu les as résolus.

