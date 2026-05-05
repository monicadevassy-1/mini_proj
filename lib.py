import sqlite3                                               #for work with SQLite databases
import re                                                    #for regex(useful for email/phone validation) 
from datetime import datetime, timedelta                     #for date and days calculation
from tabulate import tabulate                                #for viewing data in tabular form

conn = sqlite3.connect("lib3.db")                            #creates a database file named lib3.db 
cursor = conn.cursor()                                       #creates a cursor to execute SQL queries

#--------------------CREATING TABLES------------------------------------------------------------------------------------------------------------------------------
#********************TABLE 1 Lib_user********************
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Lib_user(
        mid INTEGER PRIMARY KEY AUTOINCREMENT ,
        mname VARCHAR(20) UNIQUE,
        age INTEGER,
        phone TEXT,
        email TEXT,
        password TEXT,
        role INTEGER
    )''')

#********************TABLE 2 Books********************
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books(
        bid INTEGER PRIMARY KEY AUTOINCREMENT,
        bname VARCHAR(20) UNIQUE,
        category TEXT,
        copies INTEGER
        )''')

#********************TABLE 3 Lib_issue********************
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Lib_issue(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mid INTEGER,
        bid INTEGER,
        borrow_date TEXT,
        due_date TEXT,
        return_date TEXT,
        fine INTEGER,
        FOREIGN KEY(mid) REFERENCES Lib_user(mid),
        FOREIGN KEY(bid) REFERENCES Books(bid)
        )''')


#insert or ignore (if already created)  Librarian in Lib_user
cursor.execute('''INSERT OR IGNORE INTO Lib_user (mname, age, phone, email, password, role)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ("Joseph", 37, "4567890123 ", "joseph@gmail.com", "joseph12345", 1))


conn.commit()
conn.close()
print("Database created successfully!")

#-------------------- FUNCTION DEFINITIONS ------------------------------------------------------------------------------------
#--------------------1.REGISTRATION -----------------------------------------------------
def register():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    #taking inputs into fields of 'Registration'
    print("\n********* REGISTRATION *********")

    try:
        mname = input("Enter your name: ")
        #if no value is entered for mname
        if not mname:
            raise ValueError("Name cannot be empty")
        
        age   = int(input("Enter your age: "))
        #if age is negative number
        if age <= 0:
            raise ValueError("Age must be positive")
        
        phone = (input("Enter your phone number: "))
        #checking for length of phone number and type
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Phone must be exactly 10 digits")

        
        email  = input("Enter your email: ")
        #checking if email is present using re expressions and patterns and min.length of email
        pattern=r"([a-z][a-zA-Z0-9$#%^!&*()-+]+)\@([a-z]+)\.([a-z]+)"
        if len(email)<5:
            print("*********Insufficient Length*********")
            return
        elif not re.match(pattern, email):
            raise ValueError("Invalid email format")
        elif re.search(pattern,email):
            pass


        password = input("Enter a password: ")
        #checking if password is within min and max length
        if len(password) < 5 or len(password) > 15:
           raise ValueError("*********Invalid Password*********\n*********length(5-15 chara) *********")
        
        #setting role for members only
        role =2

        #inserting values into Lib_user table
        cursor.execute(''' INSERT INTO Lib_user(mname,age,phone,email,password,role) VAlUES(?,?,?,?,?,?)
            ''', (mname, age,phone,email,password,role))
        conn.commit()

        print('Registration Successfull✅')

    except ValueError as ve:
        print("❌❌❌",ve,"❌❌❌")

    finally:
        conn.close()



#--------------------2.LOG IN -----------------------------------------------------
def login():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    print('\n********* LOG IN  *********')
    try:
        #taking inputs into fields of 'Log In'
        mname    = input('Enter your Username : ')
        password = input('Enter your Password : ')
        #checking if any fields are empty
        if not mname or not password:
            raise ValueError("❌❌ Fields cannot be empty ❌❌")

        #selecting and fetching data from Lib_user Table in db
        cursor.execute('''SELECT mid,mname,role FROM Lib_user WHERE mname = ? AND password = ?
            ''', (mname, password))
        user = cursor.fetchone()
        conn.close()

        #if any data is fetched ,successful login,else failed
        if user:
            print('\nLog in Successfull✅ \nHi,',user[1],"!!!")
            return user
        else:
            print('Log In Failed ❌')
            return None
        
    except ValueError as ve:
        print("❌❌❌",ve,"❌❌❌")
        return None

    finally:
        conn.close()
    
#--------------------3.ADDING BOOKS -----------------------------------------------------
def add_book():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    try:
        bname    = input('Enter the Name of the Book: ')
        category = input('Enter the Category: ')
        copies   = int(input("Enter the No.of Copies: "))
        #checking no.of copies
        if copies < 0:
            raise ValueError("Copies cannot be negative")

        cursor.execute('''INSERT INTO Books(bname,category,copies)VALUES(?,?,?)
            ''', (bname,category,copies))
        conn.commit()
        print("\nNew Book Added 📔")

    except ValueError as ve:
        print("❌❌❌",ve,"❌❌❌")

    finally:
        conn.close()

#--------------------4.VIEWING BOOKS -----------------------------------------------------
def view_books():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    cursor.execute('''SELECT bid, bname, category, copies FROM Books''')
    # retreives data from last executred querry
    data   = cursor.fetchall()

    
    # print(data)
    print("******************* Books available📚: *******************")
    print("-----------------------------------------------------------")
    
    if not data:
        print("No books available.")
    else:
        headers = ["Book ID", "Book Name", "Category", "Copies"]
        print(tabulate(data, headers=headers, tablefmt="grid"))

    conn.close()

#--------------------5.SEARCHING BOOKS -----------------------------------------------------
def search_book():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    bname  =input('Enter the Book name:')

    cursor.execute('''
        SELECT * FROM Books WHERE  bname = ?''', (bname,))

    data  = cursor.fetchone()
    if data:
        print('\n********** Book Found 📗**********\n')
        print(data[3], "copies of", data[1], "are available.")
    else:
        print("Book not found! ❌❌")

    conn.close()

#--------------------6.ISSUING BOOKS -----------------------------------------------------
def issue_book(mid):
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    #show books available in the lib
    view_books()    
    bid   = int(input("Choose a Book from the Library\n Enter the Book id: "))
    cursor.execute('''SELECT * FROM Books WHERE  bid = ?
        ''', (bid,))

    book = cursor.fetchone()
    cursor.execute('''SELECT * FROM Lib_issue WHERE mid = ? AND bid= ? AND return_date IS NULL
        ''', (mid,bid))

    # fetches book according to the mid and bid to check if the bookid has already issued to same mid
    issued = cursor.fetchone() 
    if issued:
        print("*** This Book already issued to you 😶,  Please return it on time!!!! ***")
        return
    else:
        #if entered bid in not available
        if book is None:
            print(" Book not found!  ❌")  
            return
        
        #checking no.of copies
        if book[3]>0:
            borrow_input = input("Enter the Borrowing Date (yyyy/mm/dd):")
            borrow_date  = datetime.strptime(borrow_input, "%Y/%m/%d")#------------------changing str into datetime for easy calcn
            due_date     = borrow_date + timedelta(days=10)#--------------------------------calculating due date using borrowdate
            borrow_str   = borrow_date.strftime("%Y/%m/%d")#------------------------------changing back into str
            due_str      = due_date.strftime("%Y/%m/%d")

            #adding due date into Lib_issue
            cursor.execute('''INSERT INTO Lib_issue(mid, bid, borrow_date, due_date)
                VALUES (?, ?, ?, ?)
                ''', (mid, bid, borrow_str, due_str))

            #reducing the no.of copies
            cursor.execute("""UPDATE Books SET copies = copies-1 WHERE bid = ?
                """, (bid,))
            conn.commit()
            print(" Book is Issued ✅\n Due Date :",due_date) 
            
        else:
            #if bid is present but ,no of copies is 0
            print("No Copies of the Selected Books are Available!!!!!")
    conn.close()

#--------------------7.RETURNING BOOKS -----------------------------------------------------
def return_book(mid):
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    bid    = int(input('Enter your Book id: '))
    #taking borrow_date and due_date from Lib_issue
    cursor.execute('''SELECT borrow_date, due_date FROM Lib_issue WHERE mid = ? AND bid = ? AND return_date IS NULL
        ''', (mid, bid)) #to not allow returning of already returned books
    issued = cursor.fetchone()

    if issued:
        return_date_input = input("Enter Return Date (YYYY/MM/DD): ")
        try:
            return_date = datetime.strptime(return_date_input, "%Y/%m/%d")
            #setting return_date
            cursor.execute('''UPDATE Lib_issue SET return_date = ? WHERE mid = ? AND bid = ? AND return_date IS NULL
                ''', (return_date_input, mid, bid))
            #adding copies
            cursor.execute("""UPDATE Books SET copies = copies + 1 WHERE bid = ?
                """, (bid,))
            
            conn.commit()

            #display return_date
            print('\n*** Book Returned 📔 on', return_date_input, "***")

            #display fine after calculating
            calc_fine(mid, bid, return_date)

        except ValueError:
            print("Invalid date format!(YYYY/MM/DD)")
    else:
        print("This Book is not issued / already returned.")
    conn.close()

#--------------------8.FINE CALCULATION -----------------------------------------------------
def calc_fine(mid, bid, return_date):
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    #setting fine to zero,taking due_date from Lib_issue Table
    fine=0
    cursor.execute('''SELECT due_date FROM Lib_issue WHERE mid = ? AND bid= ?
        ''', (mid,bid))
    issued = cursor.fetchone()

    if issued:
        due_date   = datetime.strptime(issued[0], "%Y/%m/%d")
        #calc. no.of days using timedelta from datatime module
        days_delay = (return_date - due_date).days
        if days_delay>0:
            fine  =  days_delay * 10
    
    #updating fine into Lib_issue Table
    cursor.execute('''UPDATE Lib_issue SET fine = ? WHERE mid = ? AND bid = ? 
            ''', (fine, mid, bid))
    
    conn.commit() 
    #displays fine calculated
    print("Fine is Rs.",fine)
    conn.close()

#--------------------9.REMOVING ISSUED BOOK -----------------------------------------------------
def remove_issue():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    #taking inputs for bid and mid 
    bid = int(input('Enter your Book id: '))
    mid = int(input('Enter your Member id: '))

    #reassuring the remove action
    ch = input('Are you sure you want to remove the issued Book ? (y/n): ')
    if ch == 'y':
        cursor.execute('''DELETE FROM Lib_issue WHERE bid = ? AND mid =? AND return_date IS NULL
            ''', (bid,mid))

        #updating no.of copies after deleting the iss
        cursor.execute("""
        UPDATE Books SET copies = copies+1 WHERE bid = ?
                """, (bid,))
        conn.commit()
        print('\nIssued Book is Removed ❌')
    else:
        print('\nIssued Book is not Removed 👎')
    conn.close()

#--------------------10.UPDATING BOOK DETAILS-----------------------------------------------------
def  update_book():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    #taking inputs for updated data of book
    bid      = int(input('Enter the Book id : '))
    bname    = input('Enter the Updated Book Name : ')
    category = input('Enter the Updated Category : ')
    copies   = int(input('Enter the Updated no.of Copies : '))

    #updating Books table
    cursor.execute('''UPDATE Books SET bname = ?, category = ?, copies = ? WHERE bid = ? 
                   ''', (bname, category, copies,bid))

    conn.commit()
    print('\nBook Details are Updated ✅')
    conn.close()


#--------------------11.REMOVING BOOKS-----------------------------------------------------
def remove_book():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    #taking inputs
    bid = int(input('Enter your Book id: '))
    ch  = input('Are you sure you want to remove this Book ? (y/n): ')

    if ch == 'y':
        cursor.execute(''' DELETE FROM Books WHERE bid = ?''', (bid,))
        conn.commit()
        print('\nBook is Removed ❌')
    else:
        print('\nBook is not Removed 👎')
    conn.close()

#--------------------12.ADDING NEW MEMBERS -----------------------------------------------------
def add_member():
    register()

#--------------------13.REMOVING MEMBERS -----------------------------------------------------   
def remove_member():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    mid = int(input('Enter the Member id: '))
    ch  = input('Are you sure you want to remove this Member ? (y/n): ')

    if ch == 'y':
        #Deleting member from Lib_user using mid
        cursor.execute('''DELETE FROM Lib_user WHERE mid = ?''', (mid,))
        conn.commit()
        print('\nMember is Removed ❌')
    else:
        print('\nMember is not Removed 👎')
    conn.close()
  
#--------------------14.UPDATING MEMBER DETAILS -----------------------------------------------------
def update_member():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    mid   = int(input('Enter the Member id : '))
    mname = input('Enter the Updated Member Name : ')
    age   = input('Enter the Updated Age : ')
    phone = input('Enter the Updated Phone number : ')
    email = input('Enter the Updated Email : ')
    password = input('Enter the Updated Password : ')

    cursor.execute('''UPDATE Lib_user SET mname = ?, age = ?, phone = ?,email = ?,password = ? WHERE mid = ? 
            ''', (mname, age, phone,email,password,mid))

    conn.commit()
    print('\nMember Details are Updated ✅')
    conn.close()

#--------------------15.VIEWING ISSUED BOOKS -----------------------------------------------------
def view_issued():
    conn   = sqlite3.connect("lib3.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT L.mid, B.bname, L.borrow_date, L.due_date FROM Lib_issue L JOIN Books B ON L.bid = B.bid
        WHERE L.return_date IS NULL''')

    data = cursor.fetchall()

    print("******************* Books issued📚: *******************")
    print("----------------------------------------------------------------------------------------")

    if not data:
        print("No books currently issued.")
    else:
        headers = ["Member ID", "Book Name", "Borrow Date", "Due Date"]
        print(tabulate(data, headers=headers, tablefmt="grid"))

    conn.close()


#--------------------MAIN FUNCTIONS---------------------------------------------------------------------------------------------------------------------------

def main1(mid):
    while True:
        print('----------------📖🏫 Welcome to Library🏫 📖----------------')
        print("-------------------  🧢Member's Interface🧢   ----------------")
        try:
            ch = int(input('1.View Books\n2.Search Book\n3.Issue Book\n4.Update Member Details\n5.Return Book\n6.Exit\n Choose your Option :---'))
        except ValueError:
            print("❌ Enter a valid number!")
            continue
        
        if ch == 1:
            view_books()
        elif ch == 2:
            search_book()
        elif ch == 3:
            issue_book(mid)
        elif ch == 4:
            update_member()
        elif ch == 5:
            return_book(mid)
        elif ch == 6:
            return
        else:
            print('Invalid Choice')
def main3():
    while True:
        print('---------------- Welcome to Library ----------------')
        print("----------------  Librarian's Interface 🧑‍🏫 ----------------")
        
        try:
            ch = int(input('1.Add Book\n2.View Books\n3.Update Book\n4.Remove Book\n5.Add Member\n6.Update Member Details \n7.Remove Member \n8.Remove Issued Book \n9.View issued Books \n10.Exit\nChoose your Option : '))
        except ValueError:
            print("❌❌ Enter a valid number!❌❌")
            continue
        
        if ch == 1:
            add_book()
        elif ch == 2:
            view_books()
        elif ch == 3:
            update_book()
        elif ch == 4:
            remove_book()
        elif ch == 5:
            add_member()
        elif ch == 6:
            update_member()
        elif ch == 7:
            remove_member()
        elif ch == 8:
            remove_issue()
        elif ch==9:
            view_issued()
        elif ch==10:
            return
        else:
            print('Invalid Choice')
        
def main2():
    while True:
        print('-----------------🏫 LIBRARY 🏫------------------ \n---------------- Login Page ---------------- \n Select an Option : ')
        try:
            ch = int(input('1.Register (for Members only)\n2.Login\n3.Exit\nChoice is : '))
        except ValueError:
            print("❌ Enter a valid number!")
            continue

        if ch == 1:
            register()
        elif ch == 2:
            user = login()
            if user:
                mid, name, role = user
                if role == 1:
                    main3()
                else:
                    main1(mid)

main2()
