import os
from flask import Flask, request, render_template, send_file, redirect, url_for, jsonify, session
import pandas as pd
import io
import base64
import datetime
import logging
import traceback

app = Flask(__name__)
app.secret_key = os.urandom(24) # Used for session management

# Configuration: Set to True to require authentication credentials
REQUIRE_AUTHENTICATION = False

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.errorhandler(404)
def handle_404_error(e):
    if request.path == '/favicon.ico':
        return '', 404
    logger.warning(f"404 Not Found: {request.path}")
    return render_template('index.html', error="Page non trouvée. Retour à l'accueil."), 404

@app.errorhandler(Exception)
def handle_general_exception(e):
    if hasattr(e, 'code') and e.code == 404:
        return handle_404_error(e)
    
    tb_str = traceback.format_exc()
    logger.error(f"An unhandled exception occurred: {e}", exc_info=True)
    error_log = {
        "timestamp": datetime.datetime.now().isoformat(),
        "level": "ERROR",
        "message": str(e),
        "source_module": "app.py",
        "request_path": request.path,
        "request_method": request.method,
        "traceback": tb_str.splitlines(),
        "error_type": type(e).__name__
    }
    import json
    logger.debug(f"AI_DEBUG_LOG: {json.dumps(error_log, indent=2)}")

    if request.path.startswith('/generate_permission_script'):
        return jsonify(error=f"Une erreur inattendue s'est produite : {str(e)}"), 500
    else:
        # For general errors, try to render the main page with an error message
        return render_template('index.html', error=f"Une erreur inattendue s'est produite : {str(e)}. Veuillez vérifier les logs pour plus de détails."), 500

@app.route('/')
def index():
    """
    Rend la page d'accueil unique. Le JavaScript côté client gérera le contenu dynamique.
    Initial_data est passé pour pré-remplir si l'utilisateur vient d'un upload.
    """
    initial_data = session.pop('initial_data', [])
    filename = session.pop('filename', "Aucun fichier chargé")
    return render_template('index.html', initial_data=initial_data, filename=filename)

@app.route('/favicon.ico')
def favicon():
    """
    Handle favicon requests to prevent 404 errors in logs.
    """
    return '', 204  # No Content response

@app.route('/sample')
def download_sample():
    """
    Télécharge le fichier d'exemple South Park CSV.
    """
    try:
        sample_file_path = os.path.join(os.path.dirname(__file__), 'sample_southpark_permissions.csv')
        if os.path.exists(sample_file_path):
            return send_file(sample_file_path, as_attachment=True, download_name='sample_southpark_permissions.csv', mimetype='text/csv')
        else:
            return render_template('index.html', error="Fichier d'exemple non trouvé. Oh mon Dieu, ils ont tué Kenny!"), 404
    except Exception as e:
        logger.error(f"Error downloading sample file: {str(e)}", exc_info=True)
        return render_template('index.html', error=f"Erreur lors du téléchargement du fichier d'exemple : {str(e)}"), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Gère le téléchargement du fichier CSV, le traite et stocke les données en session
    avant de rediriger vers la page principale.
    """
    try:
        if 'file' not in request.files:
            return render_template('index.html', error="Aucun fichier sélectionné.")
        
        file = request.files['file']
        if file.filename == '' or file.filename is None:
            return render_template('index.html', error="Aucun fichier sélectionné.")
        
        if not file.filename.lower().endswith('.csv'):
            return render_template('index.html', error="Veuillez sélectionner un fichier CSV (.csv).")
        
        if file:
            logger.debug(f"Processing file: {file.filename}")
            
            try:
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    file.seek(0)
                    content = file.read().decode('utf-8-sig')
                except UnicodeDecodeError:
                    try:
                        file.seek(0)
                        content = file.read().decode('latin-1')
                    except UnicodeDecodeError:
                        return render_template('index.html', error="Erreur d'encodage du fichier. Veuillez sauvegarder le fichier en UTF-8.")
            
            file_buffer = io.StringIO(content)
            try:
                df = pd.read_csv(file_buffer, sep=';', encoding='utf-8', on_bad_lines='skip')
            except Exception as csv_error:
                logger.error(f"CSV parsing error: {csv_error}")
                return render_template('index.html', error=f"Erreur lors de la lecture du fichier CSV: {str(csv_error)}. Vérifiez le format du fichier.")
            
            required_cols = ['Identity', 'User', 'AccessRights']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ''
            
            df = df[required_cols]
            df.columns = ['Identity', 'User', 'AccessRights']
            df = df.fillna('')
            
            if df.empty:
                return render_template('index.html', error="Le fichier CSV ne contient aucune donnée valide. Vérifiez que le fichier contient des colonnes 'Identity', 'User', et 'AccessRights' séparées par des points-virgules.")

            data_to_display = df.to_dict(orient='records')
            
            # Store data and filename in session to pass to the main page
            session['initial_data'] = data_to_display
            session['filename'] = file.filename
            
            return redirect(url_for('index'))
        else:
            return render_template('index.html', error="Fichier invalide.")
            
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}", exc_info=True)
        raise e

@app.route('/get_initial_data')
def get_initial_data():
    """
    Endpoint for client-side JavaScript to fetch initial data after an upload or direct access.
    """
    initial_data = session.pop('initial_data', [])
    filename = session.pop('filename', "Aucun fichier chargé")
    return jsonify(initial_data=initial_data, filename=filename)


@app.route('/generate_permission_script', methods=['POST'])
def generate_permission_script():
    """
    Génère un script PowerShell unique consolidant toutes les modifications de permissions.
    Prend en charge une liste d'opérations (add/remove) pour différentes boîtes aux lettres et utilisateurs.
    """
    try:
        data = request.get_json()
        operations = data.get('operations', []) # List of dictionaries, each describing an operation
        username = data.get('username', '')
        password = data.get('password', '')
        domain = data.get('domain', 'admr50.fr')
        auth_enabled = data.get('auth_enabled', False)

        if not operations:
            return jsonify(error="Aucune opération à générer."), 400

        script_content = []
        
        # Unique log file based on timestamp
        log_file_prefix = "ExchangePermissionScript"
        log_file_path = f"$PSScriptRoot\\{log_file_prefix}_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
        
        script_content.append(f"$LogFilePath = '{log_file_path}'\n")
        script_content.append(f"Function Write-Log {{ param([string]$Message, [string]$Type = 'INFO', [string]$ErrorCode = '')\n")
        script_content.append(f"    $Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'\n")
        script_content.append(f"    $LogEntry = \"[$Timestamp]::[$Type]::$Message\"\n")
        script_content.append(f"    if ($ErrorCode) {{ $LogEntry += \"::$ErrorCode\" }}\n")
        script_content.append(f"    Add-Content -Path $LogFilePath -Value $LogEntry\n")
        script_content.append(f"    Write-Host $LogEntry\n")
        script_content.append(f"}}\n\n")

        script_content.append(f"Write-Log -Message 'Début de l''exécution du script consolidé de gestion des permissions.' -Type 'START'\n")
        
        # Authentication setup
        if auth_enabled:
            if not username or not password or not domain:
                 return jsonify(error="Si l'authentification est activée, le nom d'utilisateur, le mot de passe et le domaine sont requis."), 400
            encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
            script_content.append(f"$SecurePassword = ConvertTo-SecureString ( [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{encoded_password}')) ) -AsPlainText -Force\n")
            script_content.append(f"$Credential = New-Object System.Management.Automation.PSCredential ('{username}', $SecurePassword)\n")
            script_content.append(f"Write-Log -Message 'Tentative de connexion à Exchange Online avec les identifiants fournis...' -Type 'INFO'\n")
            script_content.append(f"try {{\n")
            script_content.append(f"    Connect-ExchangeOnline -Credential $Credential -ShowBanner:$false -WarningAction SilentlyContinue -ErrorAction Stop\n")
            script_content.append(f"    Write-Log -Message 'Connecté à Exchange Online.' -Type 'SUCCESS'\n")
            script_content.append(f"}} catch {{ \n")
            script_content.append(f"    $ErrorMessage = $_.Exception.Message\n")
            script_content.append(f"    Write-Log -Message \"Erreur de connexion à Exchange Online. Vérifiez vos identifiants et vos permissions. Erreur: $($ErrorMessage)\" -Type 'ERROR' -ErrorCode 'CONNECT_FAILED'\n")
            script_content.append(f"    Write-Log -Message 'Arrêt du script.' -Type 'FATAL'\n")
            script_content.append(f"    exit 1\n")
            script_content.append(f"}}\n\n")
        else:
            script_content.append(f"Write-Log -Message 'Utilisation de la session Exchange Online actuelle. Assurez-vous d''être connecté manuellement.' -Type 'INFO'\n")
            script_content.append(f"try {{\n")
            script_content.append(f"    $ExistingSession = Get-PSSession | Where-Object {{ $_.ConfigurationName -eq 'Microsoft.Exchange' -and $_.State -eq 'Opened' }}\n")
            script_content.append(f"    if (-not $ExistingSession) {{\n")
            script_content.append(f"        Write-Log -Message 'Aucune session Exchange Online active trouvée. Veuillez vous connecter manuellement (Connect-ExchangeOnline) avant d''exécuter ce script.' -Type 'WARNING' -ErrorCode 'NO_ACTIVE_SESSION'\n")
            script_content.append(f"        # Optionally, you could uncomment the next line to attempt an interactive connection, but it might not work in all automated scenarios.\n")
            script_content.append(f"        # Connect-ExchangeOnline -ShowBanner:$false -WarningAction SilentlyContinue -ErrorAction Stop\n")
            script_content.append(f"        Write-Log -Message 'Arrêt du script en raison de l''absence de session active et d''identifiants non fournis.' -Type 'FATAL'\n")
            script_content.append(f"        exit 1\n")
            script_content.append(f"    }} else {{\n")
            script_content.append(f"        Write-Log -Message 'Session Exchange Online active trouvée.' -Type 'SUCCESS'\n")
            script_content.append(f"    }}\n")
            script_content.append(f"}} catch {{ \n")
            script_content.append(f"    $ErrorMessage = $_.Exception.Message\n")
            script_content.append(f"    Write-Log -Message \"Erreur lors de la vérification ou de la tentative de connexion à Exchange Online. Erreur: $($ErrorMessage)\" -Type 'ERROR' -ErrorCode 'CONNECT_FAILED_SESSION_CHECK'\n")
            script_content.append(f"    Write-Log -Message 'Arrêt du script.' -Type 'FATAL'\n")
            script_content.append(f"    exit 1\n")
            script_content.append(f"}}\n\n")

        script_content.append("# Début des modifications des permissions\n")
        
        for op in operations:
            mailbox_identity = op.get('mailboxIdentity')
            user_target = op.get('userToModify')
            action_type = op.get('actionType')
            access_rights = op.get('accessRights')

            if not all([mailbox_identity, user_target, action_type, access_rights]):
                logger.warning(f"Skipping malformed operation: {op}")
                script_content.append(f"Write-Log -Message \"Avertissement: Opération mal formée ignorée pour la boîte aux lettres '{mailbox_identity}' et l'utilisateur '{user_target}'.\" -Type 'WARNING' -ErrorCode 'MALFORMED_OPERATION'\n")
                continue
            
            script_content.append(f"\n# --- Opération pour {user_target} sur {mailbox_identity} ({action_type.upper()}) ---\n")
            script_content.append(f"$mailboxTarget = '{mailbox_identity}'\n")
            script_content.append(f"$userTarget = '{user_target}'\n")
            script_content.append(f"$accessRightsToApply = @('{', '.join(access_rights)}')\n")
            script_content.append(f"$actionType = '{action_type}'\n\n")

            script_content.append(f"if ($userTarget.ToUpper() -eq 'NT AUTHORITY\\SELF') {{\n")
            script_content.append(f"    Write-Log -Message \"Info: Ignoré: NT AUTHORITY\\SELF n'est pas modifiable pour la boîte aux lettres $($mailboxTarget).\" -Type 'WARNING'\n")
            script_content.append(f"    # Continue to next operation if SELF is encountered\n")
            script_content.append(f"}} else {{\n") # Only execute if not NT AUTHORITY\SELF
            script_content.append(f"    foreach ($right in $accessRightsToApply) {{\n")
            script_content.append(f"        Write-Log -Message \"Traitement de $($actionType) $($right) pour $($userTarget) sur $($mailboxTarget)\" -Type 'INFO'\n")
            script_content.append(f"        try {{\n")
            script_content.append(f"            if ($right -eq 'FullAccess') {{\n")
            script_content.append(f"                if ($actionType -eq 'add') {{\n")
            script_content.append(f"                    Add-MailboxPermission -Identity $mailboxTarget -User $userTarget -AccessRights FullAccess -InheritanceType All -Confirm:$false -ErrorAction Stop\n")
            script_content.append(f"                    Write-Log -Message \"Permission FullAccess ajoutée pour $($userTarget) sur $($mailboxTarget).\" -Type 'SUCCESS'\n")
            script_content.append(f"                }} elseif ($actionType -eq 'remove') {{\n")
            script_content.append(f"                    Remove-MailboxPermission -Identity $mailboxTarget -User $userTarget -AccessRights FullAccess -Confirm:$false -ErrorAction Stop\n")
            script_content.append(f"                    Write-Log -Message \"Permission FullAccess supprimée pour $($userTarget) sur $($mailboxTarget).\" -Type 'SUCCESS'\n")
            script_content.append(f"                }}\n")
            script_content.append(f"            }} elseif ($right -eq 'SendAs') {{\n")
            script_content.append(f"                $MailboxDisplayName = (Get-EXOMailbox -Identity $mailboxTarget -ErrorAction SilentlyContinue | Select-Object -ExpandProperty DisplayName)\n")
            script_content.append(f"                if ($null -ne $MailboxDisplayName) {{\n")
            script_content.append(f"                    if ($actionType -eq 'add') {{\n")
            script_content.append(f"                        Add-RecipientPermission -Identity $MailboxDisplayName -Trustee $userTarget -AccessRights SendAs -Confirm:$false -ErrorAction Stop\n")
            script_content.append(f"                        Write-Log -Message \"Permission SendAs ajoutée pour $($userTarget) sur $($mailboxTarget).\" -Type 'SUCCESS'\n")
            script_content.append(f"                    }} elseif ($actionType -eq 'remove') {{\n")
            script_content.append(f"                        Remove-RecipientPermission -Identity $MailboxDisplayName -Trustee $userTarget -AccessRights SendAs -Confirm:$false -ErrorAction Stop\n")
            script_content.append(f"                        Write-Log -Message \"Permission SendAs supprimée pour $($userTarget) sur $($mailboxTarget).\" -Type 'SUCCESS'\n")
            script_content.append(f"                    }}\n")
            script_content.append(f"                }} else {{\n")
            script_content.append(f"                    Write-Log -Message \"Boîte aux lettres $($mailboxTarget) non trouvée (DisplayName) pour la gestion de la permission SendAs.\" -Type 'WARNING' -ErrorCode 'MAILBOX_NOT_FOUND_SENDAS'\n")
            script_content.append(f"                }}\n")
            script_content.append(f"            }}\n")
            script_content.append(f"}} catch {{ \n")
            script_content.append(f"    $ErrorMessage = $_.Exception.Message\n")
            script_content.append(f"    Write-Log -Message \"Erreur lors de l''opération $($actionType) $($right) pour $($userTarget) sur $($mailboxTarget). Erreur: $($ErrorMessage)\" -Type 'ERROR' -ErrorCode 'PERMISSION_OPERATION_FAILED'\n")
            script_content.append(f"}}\n")
            script_content.append(f"    }}\n")
            script_content.append(f"}}\n") # End of if not NT AUTHORITY\SELF and foreach right
            
        script_content.append("\nWrite-Log -Message 'Toutes les opérations demandées ont été traitées.' -Type 'INFO'\n")
        script_content.append(f"Write-Log -Message 'Déconnexion d''Exchange Online.' -Type 'INFO'\n")
        script_content.append(f"Disconnect-ExchangeOnline -Confirm:$false -WarningAction SilentlyContinue\n")
        script_content.append(f"Write-Log -Message 'Script terminé.' -Type 'END'\n")

        # Instead of sending a file, return the script content as JSON
        return jsonify(script_content="".join(script_content)), 200

    except Exception as e:
        logger.error(f"Error in generate_permission_script: {str(e)}", exc_info=True)
        return jsonify(error=f"Erreur lors de la génération du script : {str(e)}"), 500

if __name__ == '__main__':
    ssl_context = None
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        ssl_context = ('cert.pem', 'key.pem')
        logger.info("Démarrage de l'application avec HTTPS.")
    else:
        logger.warning("ATTENTION: cert.pem ou key.pem introuvable. L'application démarrera en HTTP (non sécurisé).")
        logger.info("Pour activer HTTPS, générez des certificats avec : openssl req -x509 -newkey rsa:496 -nodes -out cert.pem -keyout key.pem -days 365 -subj '/CN=localhost'")
    
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=ssl_context)