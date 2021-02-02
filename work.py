from flask import Flask, render_template, url_for, flash, request, redirect
from flask_mysqldb import MySQL
import hashlib, uuid, os
from pathlib import Path
#pour importer les fichiers
from werkzeug.utils import secure_filename
import requests
import requests
import http.client,time


app = Flask(__name__)
app.secret_key = 'hello'
"""
#variable pour télecharger nos fichiers
uploads_dir = os.path.join(work.instance_path, 'uploads')
os.makedirs(uploads_dir, exists_ok=True)"""
#deuxième methodes  upload contient le chemin et allowed les exentions
UPLOAD_FOLDER = '/dos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'xlsx', 'jpg', 'jpeg', 'docx'}

#variable de connexion à mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'd@ve1234'
app.config['MYSQL_DB'] = 'dave'



mysql = MySQL(app)
#mysql.init_app(app)

#focntion de verifcation de l'extension du fichier
def allowed_file(filename):

    return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/acceuil')
def acceuil():
   
    return render_template('formpage.html')
"""
# être connecter à une session
@app.route('/session')
def session():
    if 'login' in session :
        use = session ['login']

        return render_template('projet.html')

    return "Session out" """

#se connecter à un compte utilisateur
@app.route('/connexion', methods=['GET','POST'])
def connexion():
    if request.method == "POST":
        user = request.form['login']
        passw = request.form['passwor']
        # avoir le curseur dans BD
        #cur = mysql.get_db().cursor()
        passwh = hashlib.sha256(str(passw).encode("utf-8")).hexdigest()
        
        cur = mysql.connection.cursor()
        cur.execute("select * from utilisateur where username =%s and password = %s",(user,passwh))
        result = cur.fetchone()
        if result :

            #return render_template('projet.html',use=user)
            return redirect(url_for('projet'))
        
        else :
            return ("BAD PASSWORD")


        cur.close()
        
    return render_template('connexion.html')

@app.errorhandler(404)
def page_not_found(error):
    return "Url Invalide", 404




#route pour deposer les dossiers de validation
@app.route('/projet',methods=['GET','POST'])
def projet():
    cur = mysql.connection.cursor()
    if request.method == "POST" :
        namechefprojet = request.form['namechefprojet']
        descrip = request.form['descproj']
        date = request.form['date']
        fichier = UPLOAD_FOLDER 
        fich = request.files["files"]
        fich1 = request.files["files1"]
        
        
        # Si aucun fichier n'est selectionné
        if fich.filename == '' and fich.filename == '':
            flash('No selected file')
            return "aucun fifichier selectionner"
        
        
        
        #enregistrer le fichier
        if fich and fich1 and allowed_file(fich.filename):
            #pour le premier fichier
            filename = secure_filename(fich.filename)
            save_proj = namechefprojet+'_'+descrip+'_'+filename
            fich.save(os.path.join('dos', save_proj))

            #pour le deuxième fichier
            filename = secure_filename(fich1.filename)
            save_proj = namechefprojet+'_'+descrip+'_'+filename
            fich1.save(os.path.join('dos', save_proj))

            
            cur.execute("INSERT INTO projet(chefprojet,description ,publication ,repertoire) VALUES (%s, %s, %s, %s)", (namechefprojet, descrip,date,fichier))
            mysql.connection.commit()
            cur.close()
            return "fichier download"
        
        #si l'extension du fichier n'est pas pris en compte 
        if fich.filename != ALLOWED_EXTENSIONS and fich1.filename != ALLOWED_EXTENSIONS:
            flash('No selected file')
            return "l'éxtension n'est pas prise en compte"
        #filename = secure_filename(fich)
        """
        fich.save(os.path.join(app.config[UPLOAD_FOLDER],filename))
        cur.execute("INSERT INTO user(chefprojet,description ,publication ,repertoire) VALUES (%s, %s, %s, %s)", (chefp, descrip,date,fichier))
        mysql.connection.commit()
        cur.close()
            
        return "enregistrement non effectuer" """
 
    return render_template('projet.html')

# créer un compte utilisateur
@app.route('/compte', methods=['GET','POST'])
def compte():
    cur = mysql.connection.cursor()
    if request.method == "POST" :
        username = request.form['newuser']
        passw = request.form['passw']
        passw1 = request.form['password1']
        passhash = hashlib.sha256(str(passw1).encode("utf-8")).hexdigest()
        
        cur.execute("select * from utilisateur where username =%s ",[username])
        #cur.execute("select * from user where username= %s ",(username))
        verif = cur.fetchone()
        if not verif :
            #verification de la correspondance du mot de passe
            if passw1 == passw :
                cur.execute("INSERT INTO utilisateur (username, password) VALUES (%s, %s)", (username, passhash))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('connexion'))
            
            else :
                return "le mot de passe n'est pas correcte"

        else :
            return "cet utilisateur existe déja"   
    
    return render_template('compte.html')

@app.route('/test')
def test():
    return render_template('helo.html')

#demande de congés
@app.route('/conges', methods=['GET','POST'])
def conge():

    if request.method == "POST" :

        # RECUPERER LES VARIABLES DU FORMULAIRE
        nom = request.form['nomco']
        prenom = request.form["prenomc"]
        jour = request.form["conge"]
        depart = request.form["datedepart"]
        service = request.form["service"]
        poste = request.form["poste"]

        def demarer_arreter():
            #envoyer les données a camunda
            url = "http://localhost:8080/engine-rest/process-definition/key/conges/submit-form"

            payload="{\r\n    \"variables\":\r\n    {\r\n        \"nom\": {\"value\":\""+nom+ "\", \"type\":\"String\"},\r\n        \"prenom\": {\"value\":\""+prenom+ "\", \"type\":\"String\"},\r\n        \"jours\": {\"value\":\""+str(jour)+ "\", \"type\":\"Long\"},\r\n        \"DateDepart\":{\"value\":\""+depart+ "\" , \"type\":\"String\"},\r\n        \"service\":{\"value\":\""+poste+ "\"  , \"type\":\"String\"},\r\n        \"poste\":{\"value\":\""+service+ "\"  , \"type\":\"String\"}\r\n        \r\n    }\r\n}"

            headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            # recuperation de la reponse de camunda au format json
            A = (response.json())
            # concaténation du formation json en chaine de carectère
            B= str(A)
            fich = open("not.txt","a")
            fich.write(B)
            print("script effectuer")
            fich.close()

            #recuperer de l'id de l'instance en cours du processus 
            fih = open("not.txt","r+")
            fich = fih.readline()
            
            fich = str(fich)

            B = fich.find("id")
            C = fich.find("definitionId")
            D = fich[B:C]

            E = D[6:]
            F = E[:-4]

            print("la variable finale est : ",F)

            fih.truncate(0)
            fih.close()

            time.sleep(5)

            # recuperer l'id du processus dans camunda  
            ul = "http://localhost:8080/engine-rest/task?assigned=true&assignee=ac&executionId="

            url = ul + F
            payload = ''
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            G = (response.json())

            H = str(G)
            
            fich = open("not1.txt","a")
            fich.write(H)
            fich.close()
            print("script effectuer")

            time.sleep(5)

            # terminer le processus
            fih = open("not1.txt","r+")
            fich = fih.readline()

            fich1 = str(fich)

            I = fich1.find("id")
            J = fich1.find("name")
            K = fich1[I:J]
            L = K[6:]
            M = L[:-4]

            print("le nouveau contenu est ", M)
            fih.truncate(0)
            fih.close()

            u = "http://localhost:8080/engine-rest/task/"
            l = "/complete"
            url = u + M + l 

            payload="{\r\n  \"variables\": {\r\n    \"approver\": {\"value\":\"ac\",\"type\":\"String\"}\r\n  }\r\n}"
            headers = {
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print("tout est ok") 

        demarer_arreter()
        return "Votre demande a été prise en compte"

    return render_template('conges.html')

   

    
#initialiser l'application
if __name__=="__main__" :
    app.run(debug=True)