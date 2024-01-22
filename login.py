import tkinter as tk
from PIL import ImageTk, Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, askdirectory
import re
import random
import sqlite3
import win32api
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import myemail
from io import BytesIO
import subprocess

required_modules = ["Pillow", "pywin32"]

for module in required_modules:
    subprocess.check_call(["pip", "install", module])

data = BytesIO(b'Some data')
bytes_data = data.getvalue()



root=tk.Tk()
root.geometry("500x600")
root.title("(STUDENTS DETAILS MANAGEMENT SYSTEM)")

bg_color="sandybrown"
button="springgreen"

login_student_icon=tk.PhotoImage(file=".\\student.png")
login_admin_icon=tk.PhotoImage(file=".\\admin.png")
add_student_icon=tk.PhotoImage(file=".\\add.png")
add_student_pic_icon=tk.PhotoImage(file=".\\student_profile_img.png")

#########################################------------------------------------#########################################

def init_database():

    connection=sqlite3.connect("students_accounts_db")

    cursor= connection.cursor()

    cursor.execute("""
    create table if not exists data(
    id_number text PRIMARY KEY,
    password text,
    name text,
    age text,
    gender text,
    phone_number text,
    student_class text,
    email text,
    image blob
    )
    """)

    connection.commit()
    connection.close()

#########################################------------------------------------#########################################

def check_id_already_exists(id_number):
    connection=sqlite3.connect("students_accounts_db")

    cursor= connection.cursor()

    cursor.execute(f"""
    SELECT id_number FROM data WHERE id_number = "{id_number}"
    """)

    
    response = cursor.fetchall()
    connection.commit()
    connection.close()

    return response

##################################-----------------------------------############################

def check_valid_password(id_number, password):
    connection=sqlite3.connect("students_accounts_db")
    cursor= connection.cursor()

    cursor.execute("""
    SELECT password FROM data WHERE id_number = %s AND password = %s
    """, (id_number, password))

    connection.commit()
    response = cursor.fetchall()
    connection.close()

    return response

#########################################------------------------------------#########################################

def add_data(id_number ,password ,name ,age ,gender,phone_number,
            student_class,email,pic_data):
    try:
        connection=sqlite3.connect("students_accounts_db")
        cursor= connection.cursor()

        cursor.execute("""
        INSERT INTO data (id_number, password, name, age, gender, phone_number, student_class, email, image) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_number, password, name, age, gender, phone_number, student_class, email, pic_data))

        connection.commit()
    except Exception as e:
        print("An error occured whule inserting data:", e)
    finally:
        connection.close()

#########################################------------------------------------#########################################
def confirmation_box(message):

    answer=tk.BooleanVar()
    answer.set(False)

    def action(ans):
        answer.set(ans)
        confirmation_box_fm.destroy()
    
    confirmation_box_fm=tk.Frame(root,highlightbackground=bg_color, highlightthickness=3)

    message_lb=tk.Label(confirmation_box_fm, text=message, font=("Bold",12))
    message_lb.pack(pady=20)

    cancel_btn=tk.Button(confirmation_box_fm, text="CANCEL", font=("Bold",12),
                         bd=2, bg="green",fg="white", command=lambda:action(False))
    cancel_btn.place(x=50, y=160)

    yes_btn=tk.Button(confirmation_box_fm, text="Yes", font=("Bold",12),
                         bd=2, bg="red",fg="white",command=lambda:action(True))
    yes_btn.place(x=190, y=160, width=80)

    confirmation_box_fm.place(x=100,y=120, width=320,height=220)

    root.wait_window(confirmation_box_fm)
    return answer.get()
#########################################------------------------------------#########################################
def message_box(message):
    message_box_fm=tk.Frame(root,highlightbackground=bg_color, highlightthickness=3)

    close_btn=tk.Button(message_box_fm, text="X", bd=0, font=("Bold", 13), 
                        fg="red", command=lambda: message_box_fm.destroy())
    close_btn.place(x=285,y=5)

    message_lb= tk.Label(message_box_fm, text=message, font=("Bold", 15))
    message_lb.pack(pady=50)

    message_box_fm.place(x=100, y=120, width=320, height=200)

#########################################------------------------------------#########################################

def draw_student_card(student_pic_path, student_data):

    labels="""
ID Number:
Name:
Gender:
Age:
Class:
Contact:
Email:
"""

    
    student_card = Image.open(".\\student_card_frame.png")
    pic = Image.open(student_pic_path).resize((100, 100))


    student_card.paste(pic, (15, 25))

    draw= ImageDraw.Draw(student_card)

    heading_font= ImageFont.truetype("bahnschrift", 18)
    labels_font= ImageFont.truetype("arial", 15)
    data_font= ImageFont.truetype("bahnschrift", 15)

    draw.text(xy=(150,60), text="Student Card", fill=(0,0,0),
              font=heading_font)
    
    draw.multiline_text(xy=(15,120), text=labels, fill=(0,0,0,),
                        font=labels_font, spacing=6)
    
    draw.multiline_text(xy=(95, 120), text=student_data, fill=(0,0,0),
                        font=data_font, spacing=float(8.5))

    return student_card

#########################################------------------------------------#########################################

def student_card_page(student_card_obj, student_id):

    def save_student_card():
        path=askdirectory()
        if path:
            student_card_obj.save(f'{path}/student_card.png')

    def print_student_card():
        path=askdirectory()
        if path:
            student_card_obj.save(f'{path}/student_card.png')
            win32api.ShellExecute(0, "print", f"{path}/student_card.png",
                                  None, ".",0)
            
    def close_page():
        student_card_page_fm.destroy()
        root.update()
        student_login_page()

    student_card_img= ImageTk.PhotoImage(student_card_obj)
    
    student_card_page_fm= tk.Frame(root, highlightbackground=bg_color, 
                                   highlightthickness=3)
    
    heading_lb=tk.Label(student_card_page_fm, text="Student Card",
                         bg=bg_color, fg="white", font=("Bold", 16))
    heading_lb.place(x=0,y=0, width=410)

    close_btn= tk.Button(student_card_page_fm, text="X", bg=bg_color,
                         fg="white", font=("Bold", 13), bd=0,
                         command=close_page)
    close_btn.place(x=370, y=0)

    student_card_lb=tk.Label(student_card_page_fm, image=student_card_img)
    student_card_lb.place(x=50, y=50)

    student_card_lb.image=student_card_img

    save_student_card_btn= tk.Button(student_card_page_fm, text="Save Student Card",
                                     bg="green", fg="white", font=("Bold", 15),
                                     bd=1 ,command=save_student_card)
    save_student_card_btn.place(x=80, y=375)

    print_student_card_btn= tk.Button(student_card_page_fm, text="🖨",
                                     bg="deepskyblue", fg="black", font=("Bold", 18),
                                     bd=1, command=print_student_card)
    print_student_card_btn.place(x=270, y=370)

    student_card_page_fm.place(x=50, y=30, width=400, height=450)

#######################################------------------------------------#########################################
def welcome_page():
    def forward_to_student_login_page():
        welcome_page_fm.destroy()
        root.update()
        student_login_page()
    '''
    def forward_to_admin_login_page():
        welcome_page_fm.destroy()
        root.update()
        admin_login_page()
    '''
    def forward_to_add_account_page():
        welcome_page_fm.destroy()
        root.update()
        add_account_page()

    welcome_page_fm=tk.Frame(root, highlightbackground=bg_color, highlightthickness=3) 

    heading_lb=tk.Label(welcome_page_fm,text="WELCOME TO THE SYSTEM", bg=bg_color, fg="white", font=("Bold",18))
    heading_lb.place(x=0,y=0,width=400,)

    image1 = Image.open(".\\logo1.png")
    test = ImageTk.PhotoImage(image1)
    label1 = tk.Label(welcome_page_fm, image=test)
    label1.image = test
    label1.place(x=135, y=40,width=120,height=100)

    student_login_btn=tk.Button(welcome_page_fm,text="Login student", bg=button,borderwidth=2, relief="solid"
                                ,command=forward_to_student_login_page)
    student_login_btn.place(x=230,y=244,width=100,height=35)
    '''
    admin_login_btn=tk.Button(welcome_page_fm,text="Login admin", bg=button,borderwidth=2, relief="solid"
                              ,command=forward_to_admin_login_page)
    admin_login_btn.place(x=51,y=244,width=100,height=35)

    admin_login_img=tk.Button(welcome_page_fm,image=login_admin_icon, bd=0)
    admin_login_img.place(x=60,y=162)
    '''
    student_login_img=tk.Button(welcome_page_fm,image=login_student_icon, bd=0)
    student_login_img.place(x=240,y=162)

    add_student_btn=tk.Button(welcome_page_fm,text="add new student", 
                              bg=button,borderwidth=2, relief="solid",command=forward_to_add_account_page)
    add_student_btn.place(x=51,y=244,width=100,height=35)

    add_student_img=tk.Button(welcome_page_fm,image=add_student_icon, bd=0)
    add_student_img.place(x=60,y=162)

    welcome_page_fm.pack(pady=30)
    welcome_page_fm.pack_propagate(False)
    welcome_page_fm.configure(width=400, height=430, bg="#f8f8ff")

#########################################------------------------------------#########################################

def sendmail_to_student(email, message , subject):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    username = myemail.email_address
    password = myemail.password

    msg = MIMEMultipart()

    msg["Subject"] = subject
    msg["From"] = username
    msg["To"] = email

    msg.attach(MIMEText(_text=message, _subtype="html"))

    smtp_connection = smtplib.SMTP(host=smtp_server, port=smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(user= username, password=password)

    smtp_connection.sendmail(from_addr=username, to_addrs=email,msg=msg.as_string())
    print("Mail sent successfully")

#########################################------------------------------------#########################################

def forget_password_page():

    def recover_password():
        student_id = student_id_ent.get()
        
        if check_id_already_exists(id_number=student_id):
            print("correct ID")

            connection = sqlite3.connect("students_accounts_db")
            cursor = connection.cursor()
            
            cursor.execute("""
            SELECT password FROM data WHERE id_number = ?
            """, (student_id,))

            results= cursor.fetchall()

            if results:
                recovered_password = results[0][0]
                
            else:
                print("No password found for this ID.")
            
            connection.commit()

            cursor.execute("""
            SELECT email FROM data WHERE id_number = ?
            """, (student_id,))
            email_results = cursor.fetchall()
            if email_results:
                student_email = email_results[0][0]
                
            else:
                print("No email found for this ID.")
            connection.close()

            confirmation = confirmation_box(message=f"""We will Send\nYour Forget Password
        via Your Email Address:
        {student_email}
        Do you Want to Continue?""")
            
            if confirmation:
                msg = f"""<h1>Your Forgeten Password is:</h1>
                <h2>{recovered_password}</h2>
                <p>After remembering, please delete this email for safety reasons.</p>"""
                sendmail_to_student(email=student_email, message=msg,
                                    subject="Password Recovery")

        else:
            print("incorrect ID")
            message_box(message="!Invalid ID Number")

    forget_password_page_fm = tk.Frame(root, highlightbackground=
                                       bg_color, highlightthickness=3)
    heading_lb = tk.Label(forget_password_page_fm, text="⚠ Forgetting Password",
                          font=("bold", 15), bg=bg_color, fg="white")
    heading_lb.place(x=0, y=0, width=350)

    close_btn = tk.Button(forget_password_page_fm, text="X",
                          font=("bold", 13), bg=bg_color, fg="white",
                          bd=0, command=lambda: forget_password_page_fm.destroy())
    close_btn.place(x=320, y=0)

    student_id_lb = tk.Label(forget_password_page_fm, text="Enter Student ID Number.",
                             font=("Bold", 13))
    student_id_lb.place(x=70, y=40)

    student_id_ent = tk.Entry(forget_password_page_fm,
                              font=("Bold", 15), justify=tk.CENTER)
    student_id_ent.place(x=70, y=70, width=180)

    info_lb = tk.Label(forget_password_page_fm,
                       text="""Via Your Email Address
we will Send to You
Your Forgeten Password.""", justify=tk.LEFT)
    info_lb.place(x=75, y=110)

    next_btn = tk.Button(forget_password_page_fm,
                         text="Next", font=("Bold", 13), bg=bg_color,
                         fg="white", command=recover_password)
    next_btn.place(x=130, y=200, width=80)
    
    
    forget_password_page_fm.place(x=75, y=120, width=350, height=250)


#########################################------------------------------------#########################################

def fetch_student_data(query, parameters=None):
    connection = sqlite3.connect("students_accounts_db")
    cursor = connection.cursor()
    if parameters:
        cursor.execute(query, parameters)
    else:
        cursor.execute(query)
    response= cursor.fetchall()

    cursor.close()
    connection.close()
    return response

#########################################------------------------------------#########################################

def student_dashboard(student_id):

    query = """
    SELECT name, age, gender,student_class, phone_number, email FROM data WHERE id_number =?
    """
    get_student_details = fetch_student_data(query, (student_id,))
    query1  = """
    SELECT image FROM data WHERE id_number =?
    """
    get_student_pic = fetch_student_data(query1, (student_id,))

    student_pic = BytesIO(get_student_pic[0][0])

    def logout():

        confirm=confirmation_box(message="Do You Want to\n Logout Your Account?")

        if confirm:
            dashboard_fm.destroy()
            welcome_page()
            root.update()

    def switch(indicator,page):
        home_btn_indicator.config(bg="#c3c3c3")
        student_card_btn_indicator.config(bg="#c3c3c3")
        security_btn_indicator.config(bg="#c3c3c3")
        edit_data_btn_indicator.config(bg="#c3c3c3")
        delete_account_btn_indicator.config(bg="#c3c3c3")

        student_card_btn_indicator.config(bg="red")

        for child in pages_fm.winfo_children():
            child.destroy()
            root.update()

        page()

    dashboard_fm= tk.Frame(root, highlightbackground=bg_color,
                           highlightthickness=3)
    
    options_fm = tk.Frame(dashboard_fm, highlightbackground=bg_color,
                           highlightthickness=2, bg="#c3c3c3")
    
    home_btn = tk.Button(options_fm, text="Home", font=("Bold", 15),
                         fg="red", bg="#c3c3c3", bd=0,
                         command=lambda: 
                         switch(indicator=home_btn_indicator,
                                page=home_page))
    home_btn.place(x=10, y=60)

    home_btn_indicator = tk.Label(options_fm, bg="red")
    home_btn_indicator.place(x=5, y=60, width=3, height=34)


    student_card_btn = tk.Button(options_fm, text="Student\nCard", font=("Bold", 15),
                         fg="red", bg="#c3c3c3", bd=0, justify=tk.LEFT,
                         command=lambda: 
                         switch(indicator=student_card_btn_indicator,
                                page=student_card_page))
    
    student_card_btn.place(x=10, y=105)

    student_card_btn_indicator = tk.Label(options_fm, bg="#c3c3c3")
    student_card_btn_indicator.place(x=5, y=115, width=3, height=40)

    security_btn = tk.Button(options_fm, text="Security", font=("Bold", 15),
                         fg="red", bg="#c3c3c3", bd=0,
                         command=lambda: 
                         switch(indicator=security_btn_indicator,
                         page=security_page))
    security_btn.place(x=10, y=175)

    security_btn_indicator = tk.Label(options_fm, bg="#c3c3c3")
    security_btn_indicator.place(x=5, y=180, width=3, height=30)

    edit_data_btn = tk.Button(options_fm, text="Edit Data", font=("Bold", 15),
                         fg="red", bg="#c3c3c3", bd=0,
                         command=lambda: 
                         switch(indicator=edit_data_btn_indicator,
                         page=edit_data_page))
    edit_data_btn.place(x=10, y=220)

    edit_data_btn_indicator = tk.Label(options_fm, bg="#c3c3c3")
    edit_data_btn_indicator.place(x=5, y=220, width=3, height=30)

    delete_account_btn = tk.Button(options_fm, text="Delete\nAcoount", font=("Bold", 15),
                         fg="red", bg="#c3c3c3", bd=0, justify=tk.LEFT,
                         command=lambda: 
                         switch(indicator=delete_account_btn_indicator,
                         page=delete_account_page))
    delete_account_btn.place(x=10, y=270)

    delete_account_btn_indicator = tk.Label(options_fm, bg="#c3c3c3")
    delete_account_btn_indicator.place(x=5, y=280, width=3, height=40)

    logout_btn = tk.Button(options_fm, text="Log out", font=("Bold", 15),
                         fg="red", bg="#c3c3c3", bd=0,
                         command=logout)
    logout_btn.place(x=10, y=340)

    options_fm.place(x=0, y=0, width=128, height=575)

    def home_page():
        
        student_pic_image_obj = Image.open(student_pic)
        size = 100
        mask = Image.new(mode= "L", size=(size, size))
        
        draw_circle = ImageDraw.Draw(im=mask)
        draw_circle.ellipse(xy=(0,0, size, size), fill=255, outline= True)

        output = ImageOps.fit(image=student_pic_image_obj, size=mask.size,
        centering=(1,1))

        output.putalpha(mask)

        student_picture = ImageTk.PhotoImage(output)

        home_page_fm = tk.Frame(pages_fm)

        student_pic_lb = tk.Label(home_page_fm, image=student_picture)
        student_pic_lb.image = student_picture
        student_pic_lb.place(x=10, y=10)

        hi_lb = tk.Label(home_page_fm, text=f"!Hi {get_student_details[0][0]}",
                         font=("Bold", 15))
        hi_lb.place(x=130, y=50)

        student_details = f"""
Student ID: {student_id}\n
Name: {get_student_details[0][0]}\n
Age: {get_student_details[0][1]}\n 
Gender: {get_student_details[0][2]}\n  
Class: {get_student_details[0][3]}\n 
Contact: {get_student_details[0][4]}\n
Email: {get_student_details[0][5]}
"""

        student_details_lb = tk.Label(home_page_fm,text= student_details,
                                      font=("Bold", 13), justify=tk.LEFT)
        student_details_lb.place(x=20, y=130)

        home_page_fm.pack(fill=tk.BOTH, expand=True)

    def student_card_page():

        student_details = f"""
Student ID: {student_id}
Name: {get_student_details[0][0]}
Age: {get_student_details[0][2]}
Gender: {get_student_details[0][1]}
Class: {get_student_details[0][3]}
Contact: {get_student_details[0][4]}
Email: {get_student_details[0][5]}
"""

        student_card_image_obj = draw_student_card(student_pic_path=student_pic,
                                                   student_data=student_details)

        def save_student_card():
            path=askdirectory()
            if path:
                student_card_image_obj.save(f'{path}/student_card.png')

        def print_student_card():
            path=askdirectory()
            if path:
                student_card_image_obj.save(f'{path}/student_card.png')
                win32api.ShellExecute(0, "print", f"{path}/student_card.png",
                                    None, ".",0)

        student_card_img = ImageTk.PhotoImage(student_card_image_obj)

        student_card_page_fm = tk.Frame(pages_fm)

        card_lb = tk.Label(student_card_page_fm, image=student_card_img)
        card_lb.image = student_card_img
        card_lb.place(x=20, y= 50)

        save_student_card_btn = tk.Button(student_card_page_fm, text="Save Student Card",
                                          font=("Bold",15), bd=1, fg="white", 
                                          bg=bg_color,command=save_student_card)
        save_student_card_btn.place(x=40, y=400)

        print_student_card_btn = tk.Button(student_card_page_fm, text="🖨",
                                           font=("Bold",15), bd=1, fg="white", 
                                           bg=bg_color, command=print_student_card)
        print_student_card_btn.place(x=240, y=400)

        student_card_page_fm.pack(fill=tk.BOTH, expand=True)

    def security_page():

        def set_password():
            if new_password_ent.get() != "":
                
                confirm = confirmation_box(message="Do You Want to Change\nYour Password?")
                
                if confirm:
                    connection = sqlite3.connect("students_accounts_db")

                    cursor = connection.cursor
                    cursor().execute("UPDATE data SET password = '{new_password_ent.get()}' WHERE id_number == '{student_id}'")

                    connection.commit()
                    connection.close()

                    message_box(message="Password Changed Successfully!")

                    current_password_ent.config(state=tk.NORMAL)
                    current_password_ent.delete(0, tk.END)
                    current_password_ent.insert(0, new_password_ent.get())
                    current_password_ent.config(state="readonly")

                    new_password_ent.delete(0, tk.END)

            else:
                message_box(message="New Password is Required\nto change the old one")

        security_page_fm = tk.Frame(pages_fm)

        current_password_lb = tk.Label(security_page_fm, text="Your Current Password",
                                       font=("Bold",12))
        current_password_lb.place(x=80, y=30)

        current_password_ent = tk.Entry(security_page_fm, font=("Bold", 15),
                                        justify=tk.CENTER)
        current_password_ent.place(x=50, y=80)

        student_current_password = fetch_student_data(f"SELECT password FROM data where id_number == '{student_id}'")
        
        current_password_ent.insert(tk.END, student_current_password[0][0])
        current_password_ent.config(state="readonly")

        change_password_lb = tk.Label(security_page_fm, text="Change Password",
                                      font=("Bold", 15), bg="red", fg="white")
        change_password_lb.place(x=30, y=210, width=290)

        new_password_lb = tk.Label(security_page_fm, text="Set New Password", 
                                   font=("Bold",12))
        new_password_lb.place(x=100, y=280)

        new_password_ent = tk.Entry(security_page_fm, font=("Bold", 15),
                                    justify=tk.CENTER)
        new_password_ent.place(x=60, y=330)

        change_password_btn = tk.Button(security_page_fm, text="SET Password",
                                        font=("Bold", 12), bg="green", fg="white",
                                        command=set_password)
        change_password_btn.place(x=110, y=380)

        security_page_fm.pack(fill=tk.BOTH, expand=True)
    
    def edit_data_page():
        edit_data_page_fm = tk.Frame(pages_fm)

        pic_path=tk.StringVar()
        pic_path.set("")

        def open_pic():
            path= askopenfilename()
            if path:
                img=ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
                pic_path.set(path)

                add_pic_btn.config(image=img)
                add_pic_btn.image=img

        def remove_highlight_warning(entry):
            if entry["highlightbackground"]!="grey":
                if entry.get() != "":
                    entry.config(highlightcolor="black",
                                highlightbackground="grey")
                    
        def check_invalid_email(email):
            pattern="^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
            match = re.match(pattern=pattern, string=email)
    
            return match
                    
        def check_inputs():
            nonlocal get_student_details,get_student_pic, student_pic

            if student_name_ent.get() == "":
                student_name_ent.config(highlightcolor="red",
                                        highlightbackground="red")
                student_name_ent.focus()
                message_box(message="Student Full Name is Requierd")

            elif student_age_ent.get() == "":
                student_age_ent.config(highlightcolor="red",
                                        highlightbackground="red")
                student_age_ent.focus()
                message_box(message="Student Age is Requierd")

            elif student_contact_ent.get() == "":
                student_contact_ent.config(highlightcolor="red",
                                        highlightbackground="red")
                student_contact_ent.focus()
                message_box(message="Student Contact Details\n is Requierd") 

            elif student_email_ent.get() == "":
                student_email_ent.config(highlightcolor="red",
                                        highlightbackground="red")
                student_email_ent.focus()
                message_box(message="Student Email ID is Requierd")  
            
            elif not check_invalid_email(email=student_email_ent.get().lower()):
                student_email_ent.config(highlightcolor="red",
                                        highlightbackground="red")
                student_email_ent.focus()
                message_box(message="Please Enter a Valid\nEmail Address")

            else:

                if pic_path.get() != "":
                    new_stdent_picture = Image.open(pic_path.get().resize(100, 100))
                    new_stdent_picture.save("temp_pic.png")
                    
                    with open("temp_pic.png", "rb") as read_new_pic:
                        new_picture_binary = read_new_pic.read()
                        read_new_pic.close()
                    connection = sqlite3.connect("students_accounts_db")
                    cursor = connection.cursor()

                    cursor.execute(f"UPDATE data SET image=? WHERE id_number =='{student_id}'",
                                   [new_picture_binary])

                    connection.commit()
                    connection.close()

                    message_box(message="Data Successfully Updated")

                name = student_name_ent.get()
                age = student_age_ent.get()
                selected_class = select_class_btn.get()
                contact_number = student_contact_ent.get()
                email_address = student_email_ent.get()

                connection = sqlite3.connect("students_accounts_db")
                cursor = connection.cursor()

                cursor.execute(f"""
                UPDATE data SET name='{name}', age='{age}', student_class='{selected_class}',
                phone_number='{contact_number}', email = '{email_address}'
                WHERE id_number == '{student_id}'               
                """)

                connection.commit()
                connection.close()

                query = """
                SELECT name, age, gender,student_class, phone_number, email FROM data WHERE id_number =?
                """
                get_student_details = fetch_student_data(query, (student_id,))
                query1  = """
                SELECT image FROM data WHERE id_number =?
                """
                get_student_pic = fetch_student_data(query1, (student_id,))

                student_pic = BytesIO(get_student_pic[0][0])

                message_box(message="Data Successfully Updated.")


        student_current_pic = ImageTk.PhotoImage(Image.open(student_pic))

        add_pic_section_fm= tk.Frame(edit_data_page_fm, highlightbackground="black", highlightthickness=2)
        add_pic_btn=tk.Button(add_pic_section_fm, image=student_current_pic,bd=0,
                              command=open_pic)
        
        add_pic_btn.image = student_current_pic
        add_pic_btn.pack()

        add_pic_section_fm.place(x=5, y=5, width= 105, height=105)

        student_name_lb=tk.Label(edit_data_page_fm, text="Student Full Name", font=("Bold",10),bg="white")
        student_name_lb.place(x=5,y=130)

        student_name_ent=tk.Entry(edit_data_page_fm, font=("Bold",12), 
                                highlightcolor="black", highlightbackground="grey",highlightthickness=2)
        student_name_ent.place(x=5,y=160, width=180)
        student_name_ent.bind("<KeyRelease>",
                            lambda e: remove_highlight_warning(entry=student_name_ent))

        student_name_ent.insert(tk.END, get_student_details[0][0])


        student_age_lb=tk.Label(edit_data_page_fm, text="Student Age",
                            font=("Bold",10), bg="white")
        student_age_lb.place(x=5, y=210)

        student_age_ent=tk.Entry(edit_data_page_fm, font=("Bold",12), 
                                highlightcolor="black", highlightbackground="grey",highlightthickness=2)
        student_age_ent.place(x=5,y=235, width=180)

        student_age_ent.bind("<KeyRelease>",
                            lambda e: remove_highlight_warning(entry=student_age_ent))

        student_age_ent.insert(tk.END, get_student_details[0][1])


        student_contact_lb=tk.Label(edit_data_page_fm, text="Student Phone Number",
                            font=("Bold",10), bg="white")
        student_contact_lb.place(x=5, y=285)

        student_contact_ent=tk.Entry(edit_data_page_fm, font=("Bold",12), 
                                highlightcolor="black", highlightbackground="grey",highlightthickness=2)
        student_contact_ent.place(x=5,y=310, width=180)

        student_contact_ent.bind("<KeyRelease>",
                            lambda e: remove_highlight_warning(entry=student_contact_ent))

        student_contact_ent.insert(tk.END, get_student_details[0][4])


        student_class_lb=tk.Label(edit_data_page_fm, text="Student Class", 
                                  font=("Bold",12))
        student_class_lb.place(x=5, y=360)

        select_class_btn = Combobox(edit_data_page_fm, font=("Bold", 15),
                                    state="readonly", values=class_list)
        select_class_btn.place(x=5, y=390, width=180, height=30)

        select_class_btn.set(get_student_details[0][3])


        student_email_lb=tk.Label(edit_data_page_fm, text="Student Email ID",
                            font=("Bold",10), bg="white")
        student_email_lb.place(x=5, y=440)

        student_email_ent=tk.Entry(edit_data_page_fm, font=("Bold",12), 
                                highlightcolor="black", highlightbackground="grey",highlightthickness=2)
        student_email_ent.place(x=5,y=470, width=180)

        student_email_ent.bind("<KeyRelease>",
                            lambda e: remove_highlight_warning(entry=student_email_ent))

        student_email_ent.insert(tk.END, get_student_details[0][-1])


        update_data_btn = tk.Button(edit_data_page_fm, text="UPDATE", 
                                    font=("Bold", 15), fg="white", bg="green"
                                    , bd=0, command=check_inputs)
        update_data_btn.place(x=220, y=470, width=85)



        edit_data_page_fm.pack(fill=tk.BOTH, expand=True)

    def delete_account_page():

        def confirm_delete_account():
            confirm = confirmation_box(message="⚠ Do You Want to Delete\nYour Account?")
            if confirm:
                connection = sqlite3.connect("students_accounts_db")
                cursor = connection.cursor()

                cursor.execute(f"""
                DELETE FROM data WHERE id_number == '{student_id}'               
                """)

                connection.commit()
                connection.close()

                dashboard_fm.destroy()
                welcome_page()
                root.update()
                message_box(message="Account Successfully Deleted")

        delete_account_page_fm = tk.Frame(pages_fm)

        delete_account_page_lb = tk.Label(delete_account_page_fm, text="⚠Delete Account",
                             bg="red", fg="white", font=("Bold",15))
        delete_account_page_lb.place(x=30,y=100,width=290)

        delete_account_button = tk.Button(delete_account_page_fm,
                                          text="DELETE Account", bg="red", fg="white",
                                          font=("Bold",13),command=confirm_delete_account)
        delete_account_button.place(x=110, y=200)

        delete_account_page_fm.pack(fill=tk.BOTH, expand=True)

    pages_fm = tk.Frame(dashboard_fm)
    pages_fm.place(x=131, y=5, width=341, height=558)
    home_page()

    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.configure(width=480, height=580)

#########################################------------------------------------#########################################
def student_login_page():
    def forward_to_welcome_page():
        student_login_page_fm.destroy()
        root.update()
        welcome_page()

    def forward_to_forgot_password_page():
        forget_password_page()

    def remove_highlight_warning(entry):
        if entry["highlightbackground"]!="grey":
            if entry.get() != "":
                entry.config(highlightcolor="black",
                             highlightbackground="grey")
    def login_account():
        verify_id_number= check_id_already_exists(id_number=id_number_ent.get())
        
        if verify_id_number:
            id_number=id_number_ent.get()
            student_login_page_fm.destroy()
            student_dashboard(student_id=id_number)
            root.update()

        else:
            print("!oops ID is Incorrect")
            id_number_ent.config(highlightcolor="red",
                             highlightbackground="red")
            
            message_box(message="Please Enter Valid Student ID")
            

    student_login_page_fm=tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    heading_lb=tk.Label(student_login_page_fm,text="Student Login Page", bg=bg_color,fg="white",font=("Bold",18))
    heading_lb.place(x=0,y=0,width=400)

    back_btn=tk.Button(student_login_page_fm,text="⬅",font=("Bold",20), fg="black",bd=0,
                       command=forward_to_welcome_page)
    back_btn.place(x=5,y=40)

    stud_icon_lb=tk.Label(student_login_page_fm,image=login_student_icon)
    stud_icon_lb.place(x=150, y=40)

    id_number_lb=tk.Label(student_login_page_fm, text="ENTER STUDENT ID NUMBER",font=("bold",10))
    id_number_lb.place(x=77, y=173)

    id_number_ent= tk.Entry(student_login_page_fm, font=("Bold", 15), fg="black", 
                        highlightcolor=bg_color,highlightbackground="grey", highlightthickness=2)
    id_number_ent.place(x=80,y=190)
    id_number_ent.bind("<KeyRelease>", lambda e: remove_highlight_warning(entry=id_number_ent))

    password_lb=tk.Label(student_login_page_fm, text="ENTER PASSWORD",font=("bold",10))
    password_lb.place(x=77, y=250)

    password_ent= tk.Entry(student_login_page_fm, font=("Bold", 15), fg="black", 
                        highlightcolor=bg_color,highlightbackground="grey", highlightthickness=2,show="*")
    password_ent.place(x=80,y=270)

    login_btn=tk.Button(student_login_page_fm, text="LogIN",font=("Bold",15),
                        bg="navy", fg="white",width="20",height="1", command=login_account)
    login_btn.place(x=79,y=320)

    forget_password_btn=tk.Button(student_login_page_fm, text="⚠\n Forgot Password?",
                                   fg="dark blue", bd=0, command=forward_to_forgot_password_page)
    forget_password_btn.place(x=140,y=380)

    student_login_page_fm.pack(pady=30)
    student_login_page_fm.pack_propagate(False)
    student_login_page_fm.configure(width=400, height=450, bg="#f8f8ff")

#########################################------------------------------------#########################################
'''
def admin_dashboard():

    def switch(indicator):
        home_btn_indicator.config(bg="#c3c3c3")
        find_student_btn_indicator.config(bg="#c3c3c3")
        announcement_btn_indicator.config(bg="#c3c3c3")

        indicator.config(bg="blue")

    dashboard_fm = tk.Frame(root, highlightbackground=bg_color, 
                            highlightthickness=3)
    
    options_fm = tk.Frame(root, highlightbackground=bg_color, 
                            highlightthickness=2, bg="#c3c3c3")
    
    home_btn= tk.Button(options_fm, text="Home", font=("Bold",15),
                        fg="blue", bg="#c3c3c3", bd=0,
                        command=lambda: switch(indicator=home_btn_indicator))
    home_btn.place(x=10,y=50)

    home_btn_indicator = tk.Label(options_fm, text="", bg="blue")
    home_btn_indicator.place(x=5, y=48, width=3, height=40)

    find_student_btn= tk.Button(options_fm, text="Find\nStudent", font=("Bold",15),
                        fg="blue", bg="#c3c3c3", bd=0, justify=tk.LEFT,
                        command=lambda: switch(indicator=find_student_btn_indicator))
    find_student_btn.place(x=10,y=100)

    find_student_btn_indicator = tk.Label(options_fm, text="", bg="#c3c3c3")
    find_student_btn_indicator.place(x=5, y=108, width=3, height=40)

    announcement_btn= tk.Button(options_fm, text="Announce\n-ment📢", font=("Bold",15),
                        fg="blue", bg="#c3c3c3", bd=0, justify=tk.LEFT,
                        command=lambda: switch(indicator=announcement_btn_indicator))
    announcement_btn.place(x=10,y=170)

    announcement_btn_indicator = tk.Label(options_fm, text="", bg="#c3c3c3")
    announcement_btn_indicator.place(x=5, y=180, width=3, height=40)

    logout_btn= tk.Button(options_fm, text="LogOut", font=("Bold",15),
                        fg="blue", bg="#c3c3c3", bd=0)
    logout_btn.place(x=10,y=240)
    
    options_fm.place(x=0, y=6, width=128, height=575)

    def home_page():

        home_page_fm = tk.Frame(pages_fm)

        admin_icon_lb = tk.Label(home_page_fm, image=login_admin_icon)
        admin_icon_lb.image = login_admin_icon
        admin_icon_lb.place(x=10, y=10)

        hi_lb = tk.Label(home_page_fm, text="!Hi Admin", font=("Bold", 15))
        hi_lb.place(x=120, y=40)

        class_list_lb = tk.Label(home_page_fm, text="Number of Students By class.",
                              font=("Bold", 13), bg=bg_color, fg="white")
        class_list_lb.place(x=2, y=130)

        students_numbers_lb = tk.Label(home_page_fm, text="", font=("Bold", 13),
                                       justify=tk.LEFT)
        students_numbers_lb.place(x=20, y=170)

        for i in class_list:
            result=fetch_student_data(query=f"SELECT COUNT(*) FROM data WHERE student_class == '{i}'")

            students_numbers_lb["text"] += f"{i} Class:    {result[0][0]}\n\n"

            print(i,result)

            home_page_fm.pack(fill=tk.BOTH, expand=True)

    pages_fm = tk.Frame(dashboard_fm)
    pages_fm.place(x=135, y=5, width=350, height=550)

    home_page()
    
    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.configure(width=680, height=580)
'''
#########################################------------------------------------#########################################
'''
def admin_login_page():
    def forward_to_welcome_page():
        admin_login_page_fm.destroy()
        root.update()
        welcome_page()

    def login_account():
        if username_ent.get() == "admin":
            if password_ent.get() == "admin":
                admin_login_page_fm.destroy()
                root.update()
                admin_dashboard()
            else:
                message_box(message="Wrong Password")
        else:
            message_box(message="Wrong Username")

    admin_login_page_fm=tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    heading_lb=tk.Label(admin_login_page_fm,text="Admin Login Page", bg=bg_color,fg="white",font=("Bold",18))
    heading_lb.place(x=0,y=0,width=400)

    back_btn=tk.Button(admin_login_page_fm,text="⬅",font=("Bold",20), fg="black",bd=0,
                       command=forward_to_welcome_page)
    back_btn.place(x=5,y=40)

    stud_icon_lb=tk.Label(admin_login_page_fm,image=login_admin_icon)
    stud_icon_lb.place(x=150, y=40)

    username_lb=tk.Label(admin_login_page_fm, text="ENTER ADMIN USERNAME",font=("bold",10))
    username_lb.place(x=77, y=173)

    username_ent= tk.Entry(admin_login_page_fm, font=("Bold", 15), fg="black", 
                            highlightcolor=bg_color,highlightbackground="grey", highlightthickness=2)
    username_ent.place(x=80,y=190)

    password_lb=tk.Label(admin_login_page_fm, text="ENTER ADMIN PASSWORD",font=("bold",10))
    password_lb.place(x=77, y=250)

    password_ent= tk.Entry(admin_login_page_fm, font=("Bold", 15), fg="black", 
                            highlightcolor=bg_color,highlightbackground="grey", highlightthickness=2,show="*")
    password_ent.place(x=80,y=270)

    login_btn=tk.Button(admin_login_page_fm, text="LogIN",font=("Bold",15),
                            bg="navy", fg="white",width="20",height="1",
                            command=login_account)
    login_btn.place(x=79,y=320)

    forget_password_btn=tk.Button(admin_login_page_fm, text="⚠\n Forgot Password?", fg="dark blue", bd=0)
    forget_password_btn.place(x=140,y=380)

    admin_login_page_fm.pack(pady=30)
    admin_login_page_fm.pack_propagate(False)
    admin_login_page_fm.configure(width=400, height=450, bg="#f8f8ff")
'''
#########################################------------------------------------#########################################

student_gender=tk.StringVar()


class_list=["6-A","6-B","6-C","6-D","7-A","7-B","7-C","7-D","8-A","8-B","8-C","8-D","9-A","9-B","9-C","9-D","10-A","10-B",
            "10-C","10-D","11-A","11-B","11-C","12-A","12-B","12-C",]

def add_account_page():

    pic_path=tk.StringVar()
    pic_path.set("")

    def open_pic():
        path= askopenfilename()

        if path:
            img=ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
            pic_path.set(path)

            add_pic_btn.config(image=img)
            add_pic_btn.image=img

    def forward_to_welcome_page():

        ans=confirmation_box(message="Do You Want To Leave\nRegistration Form?")
        
        if ans:
            add_account_page_fm.destroy()
            root.update()
            welcome_page()

    def remove_highlight_warning(entry):
        if entry["highlightbackground"]!="grey":
            if entry.get() != "":
                entry.config(highlightcolor="black",
                             highlightbackground="grey")
    
    def check_invalid_email(email):
        pattern="^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
        match = re.match(pattern=pattern, string=email)
 
        return match
    
    def generate_id_number():
        generated_id=""

        for i in range(6):

            generated_id += str(random.randint(0,9))

        if not check_id_already_exists(id_number=generated_id):

            print("id number:", generated_id)

            student_id.config(state=tk.NORMAL)
            student_id.delete(0, tk.END)
            student_id.insert(tk.END, generated_id)
            student_id.config(state="readonly")

        else:
            generate_id_number()

    def check_input_validation():
        if student_name_ent.get()=="":
            student_name_ent.config(highlightcolor="red"
                                    ,highlightbackground="red")
            student_name_ent.focus()
            message_box(message="Student Full Name is Required")

        elif student_age_ent.get()=="":
            student_age_ent.config(highlightcolor="red"
                                    ,highlightbackground="red")
            student_age_ent.focus()
            message_box(message="Student Age is Required")

        elif student_contact_ent.get() == "":
            student_contact_ent.config(highlightcolor="red"
                                    ,highlightbackground="red")
            student_contact_ent.focus()
            message_box(message="Student Phone Number is Required")

        elif select_class_btn.get() == "":
            select_class_btn.focus()
            message_box(message="Student Class is Required")

        elif student_email_ent.get() == "":
            student_email_ent.config(highlightcolor="red"
                                    ,highlightbackground="red")
            student_email_ent.focus()
            message_box(message="Student Email ID is Required")

        elif not check_invalid_email(email=student_email_ent.get().lower()):
            student_email_ent.config(highlightcolor="red"
                                    ,highlightbackground="red")
            student_email_ent.focus()
            message_box(message="Please Enter Valid\nEmail ID")

        elif account_password_ent.get() == "":
            account_password_ent.config(highlightcolor="red"
                                    ,highlightbackground="red")
            account_password_ent.focus()
            message_box(message="Password is Required")
        else:

            pic_data=b""

            if pic_path.get() != "":

                resize_pic=Image.open(pic_path.get()).resize((100,100))
                resize_pic.save("temp_pic.png")

                read_data = open("temp_pic.png", "rb")
                pic_data = read_data.read()
                read_data.close()

            else:
                read_data = open(".\\student_profile_img.png", "rb")
                pic_data = read_data.read()
                read_data.close()


            add_data(id_number=student_id.get(),
                     password=account_password_ent.get(),
                     name=student_name_ent.get(),
                     age=student_age_ent.get(),
                     gender=student_gender.get(),
                     phone_number=student_contact_ent.get(),
                     student_class=select_class_btn.get(),
                     email=student_email_ent.get(),
                     pic_data=pic_data)
            
            message_box("Account Created Successfully")
             
            data=f"""
{student_id.get()}
{student_name_ent.get()}
{student_gender.get()}
{student_age_ent.get()}
{select_class_btn.get()}
{student_contact_ent.get()}
{student_email_ent.get()}
"""

            get_student_card=draw_student_card(student_pic_path=pic_path.get(),
                              student_data=data)
            student_card_page(student_card_obj=get_student_card, student_id=student_id.get())

            add_account_page_fm.destroy()
            root.update()

            message_box("Account Created Successfully")
            

    add_account_page_fm=tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    add_pic_section_fm= tk.Frame(add_account_page_fm, highlightbackground="black", highlightthickness=2)
    add_pic_btn=tk.Button(add_pic_section_fm, image=add_student_pic_icon,bd=0, command=open_pic)
    add_pic_btn.pack()

    add_pic_section_fm.place(x=5, y=5, width= 105, height=105)


    student_name_lb=tk.Label(add_account_page_fm, text="Enter Student Full Name", font=("Bold",10),bg="white")
    student_name_lb.place(x=5,y=130)

    student_name_ent=tk.Entry(add_account_page_fm, font=("Bold",12), 
                            highlightcolor="black", highlightbackground="grey",highlightthickness=2)
    student_name_ent.place(x=5,y=160, width=180)
    student_name_ent.bind("<KeyRelease>",
                          lambda e: remove_highlight_warning(entry=student_name_ent))


    student_gender_lb=tk.Label(add_account_page_fm, text="Select Student Gender", font=("Bold", 10),bg="white")
    student_gender_lb.place(x=5, y=210)

    male_gender_btn=tk.Radiobutton(add_account_page_fm, text="MALE",font=("Bold",10),
                                bg="white", variable=student_gender, value="MALE")
    male_gender_btn.place(x=5, y=235)

    female_gender_btn=tk.Radiobutton(add_account_page_fm, text="FEMALE",font=("Bold",10),
                                    bg="white",variable=student_gender,value="FEMALE")
    female_gender_btn.place(x=75, y=235)
    student_gender.set("MALE")


    student_age_lb=tk.Label(add_account_page_fm, text="Enter Student Age",
                            font=("Bold",10), bg="white")
    student_age_lb.place(x=5, y=275)

    student_age_ent=tk.Entry(add_account_page_fm, font=("Bold",12), 
                            highlightcolor="black", highlightbackground="grey",highlightthickness=2)
    student_age_ent.place(x=5,y=305, width=180)

    student_age_ent.bind("<KeyRelease>",
                          lambda e: remove_highlight_warning(entry=student_age_ent))


    student_contact_lb=tk.Label(add_account_page_fm, text="Enter Phone Number",
                            font=("Bold",10), bg="white")
    student_contact_lb.place(x=5, y=360)

    student_contact_ent=tk.Entry(add_account_page_fm, font=("Bold",12), 
                            highlightcolor="black", highlightbackground="grey",highlightthickness=2)
    student_contact_ent.place(x=5,y=390, width=180)

    student_contact_ent.bind("<KeyRelease>",
                          lambda e: remove_highlight_warning(entry=student_contact_ent))


    student_class_lb=tk.Label(add_account_page_fm, text="Select Student Class",
                            font=("Bold",10), bg="white")
    student_class_lb.place(x=5, y=445)

    select_class_btn=Combobox(add_account_page_fm, font=("bold",12), state="readonly", values=class_list)
    select_class_btn.place(x=5,y=475, width=180, height=30)


    student_id_lb= tk.Label(add_account_page_fm, text="Student ID Number:" ,font=("bold",10),bg="white")
    student_id_lb.place(x=240, y=35)

    student_id= tk.Entry(add_account_page_fm,font=("Bold",16),bd=0)
    student_id.place(x=380, y=35, width=80)

    
    student_id.config(state="readonly")

    generate_id_number()

    id_info_lb=tk.Label(add_account_page_fm, text="""Atumatically Generated ID Number!
                    For Student Login!""",justify=tk.LEFT,bg="lightcoral")
    id_info_lb.place(x=240, y=65,width=220)


    student_email_lb=tk.Label(add_account_page_fm, text="Enter Student Email ID",
                            font=("Bold",10), bg="white")
    student_email_lb.place(x=240, y=130)

    student_email_ent=tk.Entry(add_account_page_fm, font=("Bold",12), 
                            highlightcolor="black", highlightbackground="grey",highlightthickness=2)
    student_email_ent.place(x=240,y=160, width=180)

    student_email_ent.bind("<KeyRelease>",
                          lambda e: remove_highlight_warning(entry=student_email_ent))

    email_info_lb=tk.Label(add_account_page_fm, text="""Via Email ID Student Can Recover 
Account! In Case of Forgetten Password 
and Will Get Notifications.""",font=("Bold",8), justify=tk.LEFT)
    email_info_lb.place(x=240, y=200, width=220)


    account_password_lb=tk.Label(add_account_page_fm, text="Create Account Password", font=("Bold", 10),bg="white")
    account_password_lb.place(x=240, y=275)

    account_password_ent=tk.Entry(add_account_page_fm, font=("Bold",12), 
                            highlightcolor="black", highlightbackground="grey",highlightthickness=2)
    account_password_ent.place(x=240,y=307, width=180)

    account_password_ent.bind("<KeyRelease>",
                          lambda e: remove_highlight_warning(entry=account_password_ent))

    account_paasword_info_lb= tk.Label(add_account_page_fm, text="""Via Student Created Password 
And Provided Student ID Number
Student Can Login Account.""", justify=tk.LEFT)
    account_paasword_info_lb.place(x=240,y=345)
    

    home_btn= tk.Button(add_account_page_fm, text="HOME", font=("Bold", 12),
                        bg="red", fg="white", bd=2, command=forward_to_welcome_page)
    home_btn.place(x=240, y=420)


    submit_btn= tk.Button(add_account_page_fm, text="SUBMIT", font=("Bold", 12),
                        bg="green", fg="white", bd=2, command=check_input_validation)
    submit_btn.place(x=360, y=420)



    add_account_page_fm.pack(pady=5)
    add_account_page_fm.pack_propagate(False)
    add_account_page_fm.configure(width=480, height=580, bg="#f8f8ff")

init_database()
welcome_page()
#admin_dashboard()
#admin_login_page()
root.mainloop()
