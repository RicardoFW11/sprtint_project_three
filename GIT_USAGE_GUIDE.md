# Guía de Uso del Script git.sh

## ¿Qué hace el script git.sh?

El script `git.sh` es una herramienta que automatiza el proceso de commit y push en Git, y **automáticamente configura la cuenta de Git** antes de realizar cualquier operación.

## ⚠️ Importante para Usuarios Compartidos

Este script está configurado específicamente para la cuenta **RicardoFW11**. Si eres otro usuario y quieres usar este script con tu propia cuenta de GitHub, necesitas modificarlo.

## Cómo Personalizar el Script para Tu Cuenta

### Paso 1: Hacer una copia del script
```bash
cp git.sh mi_git.sh
```

### Paso 2: Editar tu copia
Abre `mi_git.sh` y modifica las líneas 5-6:

```bash
# Cambiar estas líneas:
git config user.name "RicardoFW11"
git config user.email "ricardo.fajardo@cgcompass.com"

# Por tus datos:
git config user.name "TU_USUARIO_GITHUB"
git config user.email "tu.email@ejemplo.com"
```

### Paso 3: Dar permisos de ejecución
```bash
chmod +x mi_git.sh
```

### Paso 4: Usar tu script personalizado
```bash
./mi_git.sh
```

## Cómo Usar el Script

1. **Ejecutar el script:**
   ```bash
   ./git.sh
   ```

2. **El script automáticamente:**
   - Configura la cuenta de Git
   - Convierte SSH a HTTPS si es necesario
   - Te pide un mensaje de commit
   - Te pregunta si quieres hacer push a la rama actual

3. **Seguir las instrucciones en pantalla:**
   - Escribir el mensaje del commit
   - Confirmar el push (Y/n)

## Ejemplo de Uso

```bash
$ ./git.sh
Configuring Git account for RicardoFW11...
Git configuration updated successfully!

Enter the commit message:
Added new feature for data processing

You are on branch: main. Do you want to push to this branch? (Y/n)
y

[main abc1234] Added new feature for data processing
 3 files changed, 45 insertions(+), 12 deletions(-)
Enumerating objects: 8, done.
...
To https://github.com/RicardoFW11/sprint_project_two.git
   def5678..abc1234  main -> main
```

## Ventajas del Script

- ✅ **Configuración automática:** No necesitas recordar configurar Git cada vez
- ✅ **Conversión SSH a HTTPS:** Evita problemas de autenticación con claves SSH
- ✅ **Proceso simplificado:** Un solo comando para add, commit y push
- ✅ **Confirmación de seguridad:** Te pregunta antes de hacer push

## Notas Importantes

- El script hace `git add .` automáticamente (agrega todos los archivos modificados)
- Asegúrate de revisar tus cambios antes de ejecutar el script
- Si cancelas el push, los cambios quedan commitados localmente
- El script funciona con cualquier rama, no solo `main`

## Troubleshooting

### Error: "Permission denied"
- Asegúrate de que el script tenga permisos de ejecución: `chmod +x git.sh`

### Error: "remote rejected"
- Verifica que tengas permisos de escritura en el repositorio
- Asegúrate de que tu cuenta de GitHub esté configurada correctamente

### Error: "large files detected"
- Agrega archivos grandes al `.gitignore`
- Usa `git rm --cached archivo_grande` para remover del tracking
