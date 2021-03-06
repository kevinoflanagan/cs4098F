import json
import os, sys, tempfile#, nltk
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import pygraphviz as pgv
import graph as test
import time

reload(sys)
sys.setdefaultencoding("utf-8")

CURRENT_DIRECTORY = os.getcwd()
BUCKET_NAME = "temp_folder/"  # directory to store files
BUCKET_PATH = os.path.join(CURRENT_DIRECTORY, BUCKET_NAME)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = BUCKET_PATH
app.config['ALLOWED_EXTENSIONS'] = set(['pml'])


def __init__():
    if not os.path.exists('temp_folder'):
        os.mkdir('temp_folder')


@app.route('/')
def main():
    __init__()

    return render_template('graph.html')


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


#return location of the svg graph file
@app.route('/temp_folder/<filename>' )
def uploaded_file(filename):
    return send_from_directory(BUCKET_PATH, filename)


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files['file']
        if files and allowed_file(files.filename):
            out_data = files.read()
            # global filename
            filename = secure_filename(files.filename)
            # global path
            path = os.path.join(BUCKET_PATH, filename)

            file_handle = open(path, "w")
            # write data to file
            file_handle.write(out_data)
            file_handle.close()

            return render_template("graph.html", output=out_data)
        else:
            return redirect("/")




def flushPath(filename):
    #removes files in temp_folder
    folder = BUCKET_PATH
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            print e


@app.route('/')
@app.route("/pmlcheck", methods=['GET','POST'])
def pmlCheck():
    #if request.method == 'POST':
        text = request.form["text"]

        if text:
            with tempfile.NamedTemporaryFile(mode='w+t', suffix='.pml', delete=False ) as file:#open(path) as file:
                name = file.name
                basename, ext = os.path.splitext(name)
                path = os.path.join(basename + '.pml')

                file.write(text)
                file.flush()
                try:
                    #check for error to avoid dot error later on
                    output_res, error = test.pmlCheckT(name)

                    if error:
                        error = error.strip().replace(name + ':', "Line number ")
                        return render_template('graph.html', result=error, output=text)

                    output_res = output_res.strip().replace(name + ':', "Line number ")#'No Errors Detected'

                    return render_template('graph2.html', result=output_res, output=text)

                except subprocess.CalledProcessError as err:
                    return err.output.decode(), 400


#analysis colored actions
#@app.route('/')
@app.route("/graph", methods=['GET','POST'])
def graphAnalysisColored():
    #if request.method == 'POST':
        text = request.form["input2"]

        if text:
            with tempfile.NamedTemporaryFile(mode='w+t', suffix='.pml', delete=False ) as file:#open(path) as file:
                name = file.name
                basename, ext = os.path.splitext(name)
                path = os.path.join(basename + '.pml')

                file.write(text)
                file.flush()
                try:

                    #check for error to avoid dot error later on
                    output_res, error = test.pmlCheckT(name)

                    if error:
                        error = error.strip().replace(name + ':', "Line number ")
                        return render_template('graph.html', result=error, output=text)

                    finalgraph = test.graph_analysis(pmlfile=name, flag='-n')


                    Graph = pgv.AGraph(finalgraph)
                    filename1 = 'graph'  + time.strftime("%Y%m%d-%H%M%S") +'.svg'
                    Graph.draw(BUCKET_PATH + filename1, prog="dot")


                    output_res = output_res.strip().replace(name + ':', "Line number ")#'No Errors Detected'

                    listFiles = url_for('uploaded_file' , filename=filename1 )

                    return render_template('graph2.html', result=output_res, output=text, imgpath=listFiles, legend='static/fonts/Legends.png')

                except subprocess.CalledProcessError as err:
                    return err.output.decode(), 400

#resource flow
@app.route("/resource", methods=['GET','POST'])
def graphResourceFlow():
    #if request.method == 'POST':
        text = request.form["input1"]

        if text:
            with tempfile.NamedTemporaryFile(mode='w+t', suffix='.pml') as file:#open(path) as file:
                name = file.name
                basename, ext = os.path.splitext(name)
                path = os.path.join(basename + '.pml')

                file.write(text)
                file.flush()
                try:

                    #check for error to avoid dot error later on
                    output_res, error = test.pmlCheckT(name)

                    error = error.strip().replace(name + ':', "Line number ")
                    if error:
                        return render_template('graph.html', result=error, output=text)
                    
                    resourceflow = test.traverse(pmlfile=name, flag='-n')

                    Graph2 = pgv.AGraph(resourceflow)
                    filename2 = 'graph2'  + time.strftime("%Y%m%d-%H%M%S") +'.svg'
                    Graph2.draw(BUCKET_PATH + filename2, prog="dot")
        
                    output_res = output_res.strip().replace(name + ':', "Line number ")#'No Errors Detected'

                    #return graph
                    listFiles = url_for('uploaded_file' , filename= filename2)

                    return render_template('graph2.html', result=output_res, output=text, imgpath=listFiles)

                except subprocess.CalledProcessError as err:
                    return err.output.decode()#, 400


@app.route("/agents", methods=['GET','POST'])
def graphAgentColored():
    #if request.method == 'POST':
        text = request.form["text"]

        if text:
            with tempfile.NamedTemporaryFile(mode='w+t', suffix='.pml') as file:#open(path) as file:
                name = file.name
                basename, ext = os.path.splitext(name)
                path = os.path.join(basename + '.pml')

                file.write(text)
                file.flush()
                try:

                    #check for error to avoid dot error later on
                    output_res,error = test.pmlCheckT(name)

                    if error:
                        error = error.strip().replace(name + ':', "Line number ")
                        return render_template('graph.html', result=error, output=text)
                    
                    agentColored = test.traverse(pmlfile=name, flag='-f')

                    Graph2 = pgv.AGraph(agentColored)
                    filename3 = 'graph'  + time.strftime("%Y%m%d-%H%M%S") +'.svg'
                    Graph2.draw(BUCKET_PATH + filename3, prog="dot")

        
                    output_res = output_res.strip().replace(name + ':', "Line number ")

                    #return graph
                    listFiles = url_for('uploaded_file' , filename= filename3)

                    return render_template('graph2.html', result=output_res, output=text, imgpath=listFiles)

                except subprocess.CalledProcessError as err:
                    return err.output.decode()#, 400



if __name__ == "__main__":
    app.debug = True
    app.run()
