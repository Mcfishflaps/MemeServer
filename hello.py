import os
import random
from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'static'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memes.db'
db = SQLAlchemy(app)

class Meme(db.Model):
   __tablename__ = 'meme'

   #keys
   id = db.Column('id',db.Integer,primary_key = True)
   visual_id = db.Column(db.Integer, db.ForeignKey("memevisual.id"))
   sound_id = db.Column(db.Integer, db.ForeignKey("memesound.id"))
   toptext_id = db.Column(db.Integer, db.ForeignKey("memetext.id"))
   bottomtext_id = db.Column(db.Integer, db.ForeignKey("memetext.id"))

   #relationships
   visual = relationship("MemeVisual")
   sound = relationship("MemeSound")
   toptext = relationship("MemeText", foreign_keys = [toptext_id])
   bottomtext = relationship("MemeText", foreign_keys = [bottomtext_id])

class MemeVisual(db.Model):
   __tablename__ = 'memevisual'
   id = db.Column('id', db.Integer, primary_key = True)
   fileName = db.Column('fileName',db.String(100))

class MemeSound(db.Model):
   __tablename__ = 'memesound'
   id = db.Column('id',db.Integer, primary_key = True)
   fileName = db.Column('fileName',db.String(100))
   meme = relationship("Meme", uselist=False, back_populates="sound_id")

class MemeText(db.Model):
   __tablename__ = 'memetext'
   id = db.Column('id',db.Integer, primary_key = True)
   memeText = db.Column('memeText',db.String(50))
   position = db.Column(db.Boolean)
   
def index():
   return render_template('index.html')

def login():
   return render_template('login.html')

def memeForm():
   return render_template('memeForm.html')

def deathRoll():
   return render_template('deathRolling.html')

app.add_url_rule('/','index',index)
app.add_url_rule('/login', 'login', login)
app.add_url_rule('/submit', 'memeForm', memeForm)
app.add_url_rule('/deathRoll','deathRoll',deathRoll)

@app.route('/erDuSej/<fuckerName>')
def erDuSej(fuckerName):
   return render_template('userpage.html', fuckerName = fuckerName)

@app.route('/randomMeme')
def randomMeme():
   randomMeme = getRandom()
   if len(randomMeme) == 1:
      return render_template('randomMeme.html', visual = randomMeme[0])
   else:
      return render_template('randomMeme.html', visual = randomMeme[0], sound = randomMeme[1])

@app.route('/requestMeme')
def memeRequest():
   memes = getRandom()

   

   if len(memes) == 1:
      parts = memes[0].split('.')
       
      return parts[len(parts) - 1]+ "___" + readFileAsBase64(memes[0]) 
   else:
      visualParts = memes[0].split('.')
      soundParts = memes[1].split('.')
      
      return visualParts[len(visualParts) - 1]+ "___" + readFileAsBase64(memes[0]) + "___" + soundParts[len(soundParts) - 1]+ "___" + readFileAsBase64(memes[1])


@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name

@app.route('/erDuSej_request',methods = ['POST','GET'])
def erDuSej_request():
   if request.method == 'POST':
      user = request.form['nm']
      return redirect(url_for('erDuSej',fuckerName = user))
   else:
      user = request.args.get('nm')
      return redirect(url_for('erDuSej',fuckerName = user))

@app.route('/login_request',methods = ['POST', 'GET'])
def login_request():
   if request.method == 'POST':
      user = request.form['nm']
      return redirect(url_for('success',name = user))
   else:
      user = request.args.get('nm')
      return redirect(url_for('success',name = user))

@app.route('/upload', methods = ['POST'])
def upload_file():
   count = getCount()

   if 'soundFile' in request.files:
      sFile = request.files['soundFile']   
      sFile.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(str(count) + sFile.filename)))
   
   vFile = request.files['visualFile']
   vFile.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(str(count) + vFile.filename)))

   incrementCount(count)
   return 'Din meme sutter nu paa serveren'

def readFileAsBase64(memeName):
   file = open(UPLOAD_FOLDER + '/' + memeName)
   based64 = base64.b64encode(file.read())
   file.close()
   return based64

def getCount():
   file = open("count.txt", "r")
   count = int(file.readline()) 
   file.close()
   return count

def incrementCount(count):
   file = open("count.txt","w")
   file.write(str(count + 1))
   file.close()

def getRandom():

   id = str(random.randint(0, getCount() - 1))
   dir = os.listdir(UPLOAD_FOLDER + "/")
   filesFound = [name for name in dir if name.startswith(id)]
   amountFound = len(filesFound)
   if (amountFound == 0 or amountFound > 2):
      return ["error.png"]
   else:
      print(filesFound)
      return filesFound

if __name__ == '__main__':
   app.run(host = '0.0.0.0',port = 80,debug = True)