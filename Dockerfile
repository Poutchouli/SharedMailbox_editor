# Utilise une image Python légère comme base
FROM python:3.9-slim-buster

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier des exigences et installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie les certificats SSL si ils existent. C'est important pour HTTPS.
# Ces commandes ne produiront pas d'erreur si les fichiers n'existent pas, mais l'app fonctionnera en HTTP.
# Assurez-vous de générer cert.pem et key.pem dans le répertoire de l'application avant de construire l'image.
# COPY cert.pem .
# COPY key.pem .

# Copie le reste de l'application
COPY . .

# Expose le port sur lequel l'application Flask va tourner
EXPOSE 5000

# Commande pour démarrer l'application Flask
# Utilise Gunicorn pour un déploiement plus robuste que le serveur de développement de Flask
# Assurez-vous que Gunicorn peut bien utiliser le contexte SSL.
# Le app.run(ssl_context=...) de Flask prendra le relais du paramètre Gunicorn ici.
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
# Pour Flask avec SSL, on laisse Flask gérer le SSL si les fichiers existent,
# ou on revient au mode simple si ce n'est pas le cas.
# Le CMD sera simplement:
CMD ["python", "app.py"]