# Script to set up the new SharedMailbox_editor repository

Write-Host "Setting up SharedMailbox_editor repository..." -ForegroundColor Blue

# Remove existing git configuration
if (Test-Path ".git") {
    Write-Host "Removing old git configuration..." -ForegroundColor Yellow
    Remove-Item ".git" -Recurse -Force
}

# Initialize new git repository
Write-Host "Initializing new git repository..." -ForegroundColor Green
git init

# Set up remote origin
Write-Host "Setting up remote origin..." -ForegroundColor Green
git remote add origin https://github.com/Poutchouli/SharedMailbox_editor.git

# Add all files
Write-Host "Adding all files..." -ForegroundColor Green
git add .

# Initial commit
Write-Host "Creating initial commit..." -ForegroundColor Green
git commit -m "Initial commit: SharedMailbox Editor - Professional shared mailbox permissions management system"

Write-Host "Repository setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Repository 'SharedMailbox_editor' created on GitHub - DONE" -ForegroundColor Gray
Write-Host "2. Run: git push -u origin main" -ForegroundColor Gray
Write-Host "3. Set up branch protection rules if needed" -ForegroundColor Gray
Write-Host ""
Write-Host "Repository will be available at:" -ForegroundColor Cyan
Write-Host "   https://github.com/Poutchouli/SharedMailbox_editor" -ForegroundColor Cyan
