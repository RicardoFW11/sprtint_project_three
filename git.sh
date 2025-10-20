#!/bin/bash

# Configurar automáticamente la cuenta de Git para RicardoFW11
echo "Configuring Git account for RicardoFW11..."
git config user.name "RicardoFW11"
git config user.email "ricardo.fajardo@cgcompass.com"

# Verificar que el remote esté configurado correctamente (HTTPS en lugar de SSH)
current_remote=$(git remote get-url origin)
if [[ $current_remote == git@github.com:* ]]; then
    echo "Converting SSH remote to HTTPS..."
    repo_path=$(echo $current_remote | sed 's/git@github.com://' | sed 's/.git$//')
    git remote set-url origin "https://github.com/$repo_path.git"
fi

echo "Git configuration updated successfully!"
echo ""

# Pregunta por el comentario del commit
echo "Enter the commit message:"
read commitMessage

# Obtiene la rama actual
currentBranch=$(git rev-parse --abbrev-ref HEAD)

# Pide confirmación para hacer push a la rama actual
echo "You are on branch: $currentBranch. Do you want to push to this branch? (Y/n)"
read confirmation

confirmation=${confirmation:-y}

if [[ $confirmation != "y" ]]; then
    echo "Push cancelled."
    exit 1
fi

# Agrega todos los archivos modificados
git add .

# Hace el commit con el mensaje proporcionado
git commit -m "$commitMessage"

# Hace push a la rama actual
git push origin $currentBranch
