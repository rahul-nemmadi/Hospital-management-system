from flask import flash,Flask,render_template,redirect,url_for,jsonify,request,session,flash,abort
from flask_mysqldb import MySQL
from flask_session import Session
from datetime import datetime
from datetime import date
from key import *
from sdmail import sendmail
from tokenreset import token
from itsdangerous import URLSafeTimedSerializer

app=Flask(__name__)
app.secret_key=secret_key
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='PMS'
app.config["SESSION_TYPE"] = "filesystem"
mysql=MySQL(app)
Session(app)
@app.route('/')
def welcome():
    return render_template('Adminpage.html')
@app.route('/registration',methods=['GET','POST'])
def register():
    if request.method=="POST":
        cursor=mysql.connection.cursor()
        user_id=request.form['id']    
        cursor.execute('SELECT user_id from admin')
        data=cursor.fetchall()
        cursor.close()
        if (user_id,) in data:
            flash('user Id already exists')
            return render_template('Registration.html')
        name=request.form['name']
        gender=request.form['gender']
        email_id=request.form['email']
        designation=request.form['designation']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from admin where name=%s',[name])
        count=cursor.fetchone()[0]
        cursor.execute('select count(*) from admin where email_id=%s',[email_id])
        count1=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            flash('username already in use')
            return render_template('Registration.html')
        elif count1==1:
            flash('Email already in use')
            return render_template('Registration.html')
        data={'id':user_id,'name':name,'password':password,'email_id':email_id,'designation':designation,'gender':gender}
        subject='Email Confirmation'
        body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('confirm',token=token(data),_external=True)}"
        sendmail(to=email_id,subject=subject,body=body)
        flash('Confirmation link sent to mail')
        return redirect(url_for('welcome'))
    return render_template('Registration.html')


@app.route('/confirm/<token>')
def confirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
        #print(e)
        return 'Link Expired register again'
    else:
        cursor=mysql.connection.cursor()
        name=data['name']
        cursor.execute('select count(*) from admin where name=%s',[name])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('welcome'))
        else:
            cursor.execute('insert into admin values(%s,%s,%s,%s,%s,%s)',[data['id'], data['name'],data['gender'],data['email_id'],data['designation'],data['password']])
            mysql.connection.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('welcome'))


'''@app.route('/forgotpassword',methods=('GET', 'POST'))
def forgotpassword():
    if request.method=='POST':
        id1 = request.form['id']
        cursor=mysql.connection.cursor() 
        cursor.execute('select user_id from admin') 
        deta=cursor.fetchall()
        if (id1,) in deta:
            cursor.execute('select email_id from admin where user_id=%s',[id1])
            data=cursor.fetchone()[0]
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the passwword using-\{request.host+url_for("resetpwd",token=token(id1,300))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your registered mail id')
            return redirect(url_for('admin'))
        else:
            flash('user does not exits')
    return render_template('forgot.html')

@app.route('/resetpwd/<token>',methods=('GET', 'POST'))
def resetpwd(token):
    try:
        s=Serializer(app.config['SECRET_KEY'])
        id1=s.loads(token)['user']
        if request.method=='POST':
            npwd = request.form['npassword']
            cpwd = request.form['cpassword']
            if npwd == cpwd:
                cursor=mysql.connection.cursor()
                cursor.execute('update admin set password=%s where user_id=%s',[npwd,id1])
                mysql.connection.commit()
                cursor.close()
                return 'Password reset Successfull'
            else:
                return 'Password does not matched try again'
        return render_template('newpassword.html')
    except Exception as e:
        abort(410,description='reset link expired')'''

@app.route('/forget',methods=['GET','POST'])
def forgotpassword():
    if request.method=='POST':
        email=request.form['email']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from admin where email_id=%s',[email])
        count=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            cursor=mysql.connection.cursor()
            cursor.execute('SELECT email_id from admin where email_id=%s',[email])
            status=cursor.fetchone()[0]
            cursor.close()
            subject='Forget Password'
            confirm_link=url_for('reset',token=token(email,salt2),_external=True)
            body=f"Use this link to reset your password-\n\n{confirm_link}"
            sendmail(to=email,body=body,subject=subject)
            flash('Reset link sent check your email')
            return redirect(url_for('admin'))
        else:
            flash('Invalid email id')
            return render_template('forgot.html')
    return render_template('forgot.html')


@app.route('/reset/<token>',methods=['GET','POST'])
def reset(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        email=serializer.loads(token,salt=salt2,max_age=180)
        print(email)
    except :
        #print(e)
        abort(404,'Link Expired')
    else:
        if request.method=='POST':
            newpassword=request.form['npassword']
            confirmpassword=request.form['cpassword']
            if newpassword==confirmpassword:
                cursor=mysql.connection.cursor()
                cursor.execute('update admin set password=%s where email_id=%s',[newpassword,email])
                mysql.connection.commit()
                flash('Reset Successful')
                return redirect(url_for('welcome'))
            else:
                flash('Passwords mismatched')
                return render_template('newpassword.html')
        return render_template('newpassword.html')  



@app.route('/login',methods=['GET','POST'])
def admin():
    if session.get('user'):
        return redirect(url_for('adminhome')) 
    if request.method=="POST":
        user=request.form['user']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT user_id from admin')
        users=cursor.fetchall()            
        password=request.form['password']
        cursor.execute('select password from admin where user_id=%s',[user])
        data=cursor.fetchone()
        cursor.close() 
        if (user,) in users:
            if password==data[0]:
                session['user']=user
                return redirect(url_for('adminhome'))
            else:
                flash('Invalid Password')
                return render_template('login.html')
        else:
            flash('Invalid user id')
            return render_template('login.html')      
    return render_template('login.html')
@app.route('/home')
def adminhome():
    if session.get('user'):
        return render_template('Home.html')
    return redirect(url_for('admin'))
@app.route('/checkin',methods=['GET','POST'])
def checkin():
    details=None
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from patients')
    data=cursor.fetchall()
    data1=request.args.get('name') if request.args.get('name') else 'empty'
    print(data1)
    cursor.execute('SELECT * from patients where mobileNumber=%s',[data1])
    details=cursor.fetchone()
    cursor.execute('SELECT * from records')
    std_records=cursor.fetchall()
    cursor.close()
    if request.method=='POST':
        cursor=mysql.connection.cursor()
        Id2=request.form['empCode']
        today=date.today()
        day=today.day
        month=today.month
        year=today.year
        today_date=datetime.strptime(f'{year}-{month}-{day}','%Y-%m-%d')
        date_today=datetime.strftime(today_date,'%Y-%m-%d')
        fullname=request.form['studid']
        if Id2=="" or fullname=="":
            flash('Select The patient mobile no first')
        else:
            cursor=mysql.connection.cursor()
            cursor.execute('insert into records(name,mobilenumber,date) values(%s,%s,%s)',[Id2,fullname,date_today])
            mysql.connection.commit()
            cursor.execute('SELECT * from records')
            std_records=cursor.fetchall()
            cursor.close()
    return render_template('Check in-page.html',data1=data1,data=data,details=details,std_records=std_records)
@app.route('/addpatient',methods=['GET','POST'])
def addpatient():
    cursor=mysql.connection.cursor()
    cursor.execute('select * from patients')
    data=cursor.fetchall()
    if request.method=="POST":
        name=request.form['name']
        mobileNumber=request.form['mobileNumber']
        Address=request.form['address']
        age=request.form['age']
        cursor=mysql.connection.cursor()
        cursor.execute('insert ignore into patients values(%s,%s,%s,%s)',[name,mobileNumber,Address,age])
        mysql.connection.commit()
        cursor.close()
        cursor=mysql.connection.cursor()
        cursor.execute('select * from patients')
        data=cursor.fetchall()
        cursor.close()
        return render_template('Student Record.html',data=data)
    return render_template('Student Record.html',data=data)
@app.route('/checkoutupdate/<id1>')
def checkoutupdate(id1):
    cursor=mysql.connection.cursor()
    cursor.execute('update records set checkout=current_timestamp() where Id=%s',[id1])
    mysql.connection.commit()
    return redirect(url_for('checkin'))
@app.route('/checkinupdat/<id1>')
def checkinupdate(id1):
    cursor=mysql.connection.cursor()
    cursor.execute('update records set checkin=current_timestamp() where Id=%s',[id1])
    mysql.connection.commit()
    return redirect(url_for('checkin'))
@app.route('/doctor/<id1>',methods=['GET','POST'])
def doctor(id1):
    if request.method=="POST":
        doctor=request.form['doctor']
        visit=request.form['visit']
        time=request.form['time']
        cursor=mysql.connection.cursor()
        cursor.execute('update records set doctor=%s,purpose=%s,appointmenttime=%s where id=%s',[doctor,visit,time,id1])
        mysql.connection.commit()
        return redirect(url_for('checkin'))
    return render_template('AssignDoctor.html')
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))
@app.route('/test',methods=['GET','POST'])
def test():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT mobileNumber from patients')
        data=cursor.fetchall()
        cursor.execute('SELECT * from test')
        details=cursor.fetchall()
        cursor.close()
        if request.method=="POST":
            number=request.form['name']
            tname=request.form['tname']
            toutcome=request.form['toutcome']
            cursor=mysql.connection.cursor()
            cursor.execute('SELECT Name from patients where mobileNumber=%s',[number])
            name=cursor.fetchone()[0]
            cursor.execute('insert into test(mobilenumber,Name,testname,testresult) values(%s,%s,%s,%s)',[number,name,tname,toutcome])
            mysql.connection.commit()
            cursor.execute('SELECT * from test')
            details=cursor.fetchall()
            cursor.close()
        return render_template('test.html',data=data,details=details)
    return redirect(url_for('admin'))
app.run(debug=True)

#cmo@codegnan.com---