# Script to start the Flask application using Docker for Windows PowerShell

# Navigate to the directory where the script is located
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Definition)

Write-Host "🐳 Vérification de Docker..." -ForegroundColor Blue
try {
    docker --version | Out-Null
    Write-Host "✅ Docker est disponible" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas installé ou démarré" -ForegroundColor Red
    Write-Host "Veuillez installer Docker Desktop et le démarrer avant de continuer." -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host "🏗️  Construction et démarrage du conteneur Docker..." -ForegroundColor Blue
try {
    # Arrêter les conteneurs existants si ils existent
    docker-compose down 2>$null
    
    # Construire et démarrer l'application
    docker-compose up --build -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Application démarrée avec succès !" -ForegroundColor Green
        Write-Host "🌐 L'application est accessible à l'adresse :" -ForegroundColor Yellow
        Write-Host "   http://localhost:5000" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📋 Commandes utiles :" -ForegroundColor Yellow
        Write-Host "   • Voir les logs: docker-compose logs -f" -ForegroundColor Gray
        Write-Host "   • Arrêter l'app: docker-compose down" -ForegroundColor Gray
        Write-Host "   • Redémarrer: docker-compose restart" -ForegroundColor Gray
        
        # Optionnel : ouvrir le navigateur
        $openBrowser = Read-Host "Voulez-vous ouvrir l'application dans le navigateur ? (y/N)"
        if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
            Start-Process "http://localhost:5000"
        }
    } else {
        Write-Host "❌ Erreur lors du démarrage de l'application" -ForegroundColor Red
        Write-Host "Vérifiez les logs avec: docker-compose logs" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erreur lors de l'exécution de Docker Compose: $_" -ForegroundColor Red
    Write-Host "Vérifiez que Docker Desktop est démarré et que vous êtes dans le bon répertoire." -ForegroundColor Yellow
}