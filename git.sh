#!/bin/bash

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
