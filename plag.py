import os
from flask import Flask, request, render_template,redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import re
import math
import language_tool_python
app = Flask("__name__")
app.config['UPLOAD_FOLDER'] = 'uploads/'
ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def wordcount(filename, find_word):
    file = open(app.config['UPLOAD_FOLDER'] + filename, 'r').read()
    count = 0
    words = file.split()
    for word in words:
        if(word == find_word):
            count += 1
    return count
q = ""
@app.route('/grammar',methods=['POST'])
def grammar():
	if request.method=='POST':
		inputQuery = request.form['query']
		my_tool=language_tool_python.LanguageTool('en-US')
		my_matches=my_tool.check(inputQuery)
		myMistakes=[]
		myCorrections=[]
		startPositions=[]
		endPositions=[]
		for rules in my_matches:
			if len(rules.replacements)>0:
				startPositions.append(rules.offset)
				endPositions.append(rules.errorLength + rules.offset)
				myMistakes.append(inputQuery[rules.offset: rules.errorLength + rules.offset])
				myCorrections.append(rules.replacements[0])
		my_NewText = list(inputQuery)
		for n in range(len(startPositions)):  
			for i in range(len(inputQuery)):
				my_NewText[startPositions[n]] = myCorrections[n]
				if (i > startPositions[n] and i < endPositions[n]):
					my_NewText[i] = ""
		my_NewText = "".join(my_NewText)
		return render_template('grammar.html',output=my_matches,my_NewText=my_NewText)
	return render_template('grammar.html',output="")
@app.route('/checkcount', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        word = request.form['word']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(app.config['UPLOAD_FOLDER'] + filename)
            count = str(wordcount(filename, word))
            os.remove(app.config['UPLOAD_FOLDER'] + filename)
            return render_template('checkCount.html',
                                   filename = filename,
                                   word = word,
                                   count = count)

    return render_template('checkCount.html', count = None)
@app.route('/grammar')
def loadgrammar():
	return render_template('grammar.html',query="")
@app.route("/login")
def loadlogin():
	return render_template('login.html', query="")
@app.route("/choose")
def loadchoose():
	return render_template('choose.html', query="")
@app.route("/checkcount")
def loadcheckCount():
	return render_template('checkCount.html', query="")
@app.route("/")
def loadPage():
	return render_template('index.html', query="")

@app.route("/", methods=['POST'])
def cosineSimilarity():
	try:
		universalSetOfUniqueWords = []
		matchPercentage = 0
    	
		####################################################################################################
		
		inputQuery = request.form['query']
		lowercaseQuery = inputQuery.lower()
    	
		queryWordList = re.sub("[^\w]", " ",lowercaseQuery).split()			#Replace punctuation by space and split
		# queryWordList = map(str, queryWordList)					#This was causing divide by zero error
    	
		for word in queryWordList:
			if word not in universalSetOfUniqueWords:
				universalSetOfUniqueWords.append(word)
    	
		####################################################################################################
    	
		fd = open("database1.txt", "r")
		database1 = fd.read().lower()
    	
		databaseWordList = re.sub("[^\w]", " ",database1).split()	#Replace punctuation by space and split
		# databaseWordList = map(str, databaseWordList)			#And this also leads to divide by zero error
    	
		for word in databaseWordList:
			if word not in universalSetOfUniqueWords:
				universalSetOfUniqueWords.append(word)
    	
		####################################################################################################
    	
		queryTF = []
		databaseTF = []
    	
		for word in universalSetOfUniqueWords:
			queryTfCounter = 0
			databaseTfCounter = 0
    	
			for word2 in queryWordList:
				if word == word2:
					queryTfCounter += 1
			queryTF.append(queryTfCounter)
    	
			for word2 in databaseWordList:
				if word == word2:
					databaseTfCounter += 1
			databaseTF.append(databaseTfCounter)
    	
		dotProduct = 0
		for i in range (len(queryTF)):
			dotProduct += queryTF[i]*databaseTF[i]
    	
		queryVectorMagnitude = 0
		for i in range (len(queryTF)):
			queryVectorMagnitude += queryTF[i]**2
		queryVectorMagnitude = math.sqrt(queryVectorMagnitude)
    	
		databaseVectorMagnitude = 0
		for i in range (len(databaseTF)):
			databaseVectorMagnitude += databaseTF[i]**2
		databaseVectorMagnitude = math.sqrt(databaseVectorMagnitude)
    	
		matchPercentage = (float)(dotProduct / (queryVectorMagnitude * databaseVectorMagnitude))*100
    	
		'''
		print queryWordList
		print
		print databaseWordList
    	
    	
		print queryTF
		print
		print databaseTF
		'''
    	
		output = "Input query text matches %0.02f%% with database."%matchPercentage
    	
		return render_template('index.html', query=inputQuery, output=output)
	except Exception as e:
		output = "Please Enter Valid Data"
		return render_template('index.html', query=inputQuery, output=output)

if __name__ == "__main__":
    if(not os.path.isdir(app.config['UPLOAD_FOLDER'])):
        os.makedirs(app.config['UPLOAD_FOLDER']) #Create upload-folder if it does not exist

    app.run(host='localhost', debug = True) # Start the app