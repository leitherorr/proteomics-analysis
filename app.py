import os
import time
import glob
import pandas as pd
import math




def log2(x):
    return math.log2(x)

from flask import Flask, flash, request, redirect, render_template, url_for, send_file, jsonify
from werkzeug.utils import secure_filename

app=Flask(__name__)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home_menu():
    return render_template('home.html')


@app.route('/tmt')
def upload_form():
    return render_template('upload.html')


@app.route('/isotop')
def upload_isotop():
    return render_template('isotop_upload.html')



# this is the tmt part
@app.route('/tmt', methods=['POST'])

def upload_file():
    
    
    if request.method == 'POST':
        # check if the post request has the file part

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #raw_file = "raw_file"
            #os.rename(filename, raw_file)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')



            #THIS WAS THE OLD WAY
            return redirect(url_for('run_analysis'))


        
            #return redirect(request.url)
            #return app.route('/next')
        else:
            flash('Only .xlsx files are accepted')
            return redirect(request.url)



        
#def upload_name():
    #if request.method == 'POST':


#@app.route('/analysis', methods=['GET'])
#def loading():



    #return render_template('loading.html')



@app.route('/analysis', methods=['GET'])

#def loading():

    #return render_template('loading.html')


def run_analysis():

    flash('Analyzed file will be exported to your downloads folder')
    
    list_of_files = glob.glob('uploads/*', recursive=False) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)

    remove_last = latest_file[:-5]
    slimmed_file = remove_last[8:]

    ##########################################latest_path = "uploads/" + latest_file
    
    #oldFile = "220830_YK267_5uM_24hr.xlsx"
    

    #start of paste
    #hardcoded!!!
    df = pd.read_excel(latest_file)
        #df = pd.read_csv(oldFilePlus)

    df['description'] = df['description'].str.split(' PE=').str[0]
    df[['protein', 'gene']] = df['description'].str.split(' GN=', expand=True)
    df = df.drop('description', axis=1)


    # sort by norm ratio
    df = df.sort_values('norm protein ratio list 2/1')

    # delete spec count < 1
    df_spec = df[df['spec count'] > 1]

    # delete contaminant or reverse


    new_accession = df_spec.copy()
    new_accession["first4access"] = df_spec["accession"]
    new_accession['norm ratio copy'] = (df_spec['norm protein ratio list 2/1'])
    new_accession['norm protein ratio log2'] = new_accession['norm ratio copy'].apply(log2)

    new_accession['first4access2'] = new_accession['first4access'].str.slice(0,4)
    df_spec_rev1 = new_accession[new_accession['first4access2'] != ('Reve')]
    df_spec_rev = df_spec_rev1[df_spec_rev1['first4access2'] != ('cont')]

    del df_spec_rev['norm ratio copy']
    del df_spec_rev["first4access"]
    del df_spec_rev["first4access2"]


    cols = list(df_spec_rev.columns.values)
    #print(cols)
    #print(cols[24])
          
    newOrder = [0, 25, 6, 2, 1, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    cols = [cols[i] for i in newOrder]
    df_spec_rev = df_spec_rev[cols]

    # remove insignificant p values
    statsig = df_spec_rev[df_spec_rev['norm p-value  for 1 and 2'] < 0.05]


    #write to excel

    import xlsxwriter

    outputfile = "exports/" + slimmed_file + "_analyzed.xlsx"

    #user_output_name = oldFile + "_analyzed.xlsx"
    #user_output_name = latest_file + '/' + oldFile + "_analyzed.xlsx"
    #print(user_output_name)

    writer = pd.ExcelWriter(outputfile, engine='xlsxwriter')


    #outputfile = "220830_YK267_5uM_24hr" + "_analyzed.xlsx"

    workbook = writer.book



    workbook = xlsxwriter.Workbook(outputfile, {'constant_memory': True})








    #define specific sheets
    df.to_excel(writer, sheet_name='Raw data', index = False)
    df_spec_rev.to_excel(writer, sheet_name='Curated data', index = False)
    statsig.to_excel(writer, sheet_name='Statistically significant', index = False)

    worksheet = writer.sheets['Curated data']
    worksheet2 = writer.sheets['Statistically significant']

    cell_format = workbook.add_format()
    cell_format.set_bold()
    

    worksheet.set_column('A:D', None, cell_format)
    worksheet2.set_column('A:D', None, cell_format)

    # save the new excel file
    writer.save()
    

    #flash('Analyzed file will be exported to your Downloads folder.')
    #return redirect(url_for('download'))
    return redirect(url_for('download'))








    
    

@app.route('/download')
def download():



    list_of_files = glob.glob('exports/*', recursive=False) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    

    #latest_path = "exports/" + latest_file

    flash("Your analysis file has been exported to your downloads folder.")

    return send_file(latest_file, as_attachment=True) 
    
# end tmt part









#here is the new isotop part

ALLOWED_EXTENSIONS_2 = set(['tsv'])


def allowed_file_2(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_2



@app.route('/isotop', methods=['POST'])

def upload_file_isotop():
    
    
    if request.method == 'POST':
        # check if the post request has the file part

        if 'file_isotop' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file_isotop']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file_2(file.filename):
            filename = secure_filename(file.filename)
            #raw_file = "raw_file"
            #os.rename(filename, raw_file)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')



            #THIS WAS THE OLD WAY
            return redirect(url_for('run_analysis_isotop'))


        
            #return redirect(request.url)
            #return app.route('/next')
        else:
            flash('Only .tsv files are accepted')
            return redirect(request.url)



        
#def upload_name():
    #if request.method == 'POST':


#@app.route('/analysis', methods=['GET'])
#def loading():



    #return render_template('loading.html')



@app.route('/analysis_isotop', methods=['GET'])

#def loading():

    #return render_template('loading.html')


def run_analysis_isotop():

    #flash('Analyzed file will be exported to your downloads folder')
    
    list_of_files = glob.glob('uploads/*', recursive=False) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)

    remove_last = latest_file[:-4]
    slimmed_file = remove_last[8:]

    ##########################################latest_path = "uploads/" + latest_file
    
    #oldFile = "220830_YK267_5uM_24hr.xlsx"
    

    #start of paste
    #hardcoded!!!
    df = pd.read_table(latest_file)
        #df = pd.read_csv(oldFilePlus)




# need to test up to thus far





    # sort by fold change
    df = df.sort_values('fold_change', ascending=False)

    # delete spec count < 1
    df_spec = df.loc[df['run count'] > 1]

    df_spec = df_spec.loc[df_spec['p.value'] != "--"]




    
    
    



    cols = list(df_spec.columns.values)
    
          
    newOrder = [18, 17, 1, 2, 16, 0, 19, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    cols = [cols[i] for i in newOrder]
    df_spec = df_spec[cols]

    # remove insignificant p values
    df_spec ['p.value'] = df_spec ['p.value'].astype(float)
    statsig = df_spec.loc[df_spec['p.value'] < 0.05 ]


    #write to excel

    import xlsxwriter

    outputfile = "exports/" + slimmed_file + "_analyzed.xlsx"

    #user_output_name = oldFile + "_analyzed.xlsx"
    #user_output_name = latest_file + '/' + oldFile + "_analyzed.xlsx"
    #print(user_output_name)

    writer = pd.ExcelWriter(outputfile, engine='xlsxwriter')


    #outputfile = "220830_YK267_5uM_24hr" + "_analyzed.xlsx"

    workbook = writer.book



    workbook = xlsxwriter.Workbook(outputfile, {'constant_memory': True})








    #define specific sheets
    df.to_excel(writer, sheet_name='Raw data', index = False)
    df_spec.to_excel(writer, sheet_name='Curated data', index = False)
    statsig.to_excel(writer, sheet_name='Statistically significant', index = False)

    worksheet = writer.sheets['Curated data']
    worksheet2 = writer.sheets['Statistically significant']

    cell_format = workbook.add_format()
    cell_format.set_bold()
    

    worksheet.set_column('A:D', None, cell_format)
    worksheet2.set_column('A:D', None, cell_format)


    # save the new excel file
    writer.save()
    

    #flash('Analyzed file will be exported to your Downloads folder.')
    #return redirect(url_for('download'))
    return redirect(url_for('download_isotop'))








    
    

@app.route('/isotop/download')
def download_isotop():



    list_of_files = glob.glob('exports/*', recursive=False) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    

    #latest_path = "exports/" + latest_file

    flash("Your analysis file has been exported to your downloads folder.")

    return send_file(latest_file, as_attachment=True) 



# end isotop part

if __name__ == "__main__":
    app.run(host = '127.0.0.1',port = 5000, debug = False)
    
