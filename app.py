from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])     #Allowed Extention
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# For Image Upload
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Valid For Admin
def is_valid_admin(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM admindetails')
    data = cur.fetchall()
    print(data)
    for row in data:
        print(row)
        if row[0] == email and row[1] == password:
            return True
    return False

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


# ADMINLOGIN

@app.route('/adminlogin')
def adminLogin():
    return render_template('adminlogin.html')

@app.route('/adminpanel')
def adminPanel():
    success_code = request.args.get('success_code')
    if (success_code == "200"):
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products')
            itemData = cur.fetchall()
            cur.execute('SELECT categoryId, name FROM categories')
            categoryData = cur.fetchall()
        # itemData = parse(itemData)
        for i in itemData:
            print(i)
        return render_template('adminpanel.html', itemData=itemData, categoryData=categoryData)
    else:
        return render_template_string('''
                                        <div class="error">
                                            <h1>Error Page 404</h1>
                                        </div>
                                      ''')

# ADMINLOGIN - [VALIDATION]

@app.route('/adminvalidation', methods = ['POST', 'GET'])
def adminValidation():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid_admin(email, password):
            session['email'] = email
            return redirect(url_for('adminPanel', success_code=200))
        else:
            error = 'Invalid UserId / Password'
            return render_template('adminlogin.html', error=error)


# ADD SECTION

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryType = request.form['category']

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                categoryId = cur.execute("SELECT categoryId FROM categories WHERE name = ?", [categoryType])
                # print(categoryId.fetchone()[0])
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', [name, price, description, imagename, stock, categoryId.fetchone()[0]])
                conn.commit()
                # conn.rollback()
                msg="added successfully"
            except Exception as e:
                msg="error occured"
                print(e)
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('adminPanel', success_code=200))


# DELETE SECTION

@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route("/removeItem", methods=['GET', 'POST'])
def removeItem():
    # productId = request.args.get('productId')
    if request.method == 'POST':
        productName = request.form['productname']
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM products WHERE name = ?",[productName])
                conn.commit()
                msg = "Deleted successsfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        print(msg)
        return redirect(url_for('adminPanel', success_code=200))
    else:                                                           # FOR DELETE CARDS
        productName = request.args.get('productname')
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM products WHERE name = ?",[productName])
                conn.commit()
                msg = "Deleted successsfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        print(msg)
        return redirect(url_for('adminPanel', success_code=200))


# EDIT & UPDATE SECTION

@app.route('/edit')
def edit():
    return render_template('edit.html')

# Need Edititng Over Here.
@app.route("/editItem", methods=['POST', 'GET']) # Without methods => give Method not allowed with 405
def editItem():
    if request.method == 'POST':
        productName = request.form['productname']
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE name = ?",[productName])
            productData = cur.fetchone()
        conn.close()
        return render_template("edit.html", productData=productData)
    else:                                                               # FOR EDIT CARDS
        productName = request.args.get('productname')
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products WHERE name = ?",[productName])
            productData = cur.fetchone()
        conn.close()
        return render_template("edit.html", productData=productData)

@app.route("/updateProduct", methods=["GET", "POST"])
def updateProduct():
    if request.method == 'POST':
        productId = request.form['productid']
        productName = request.form['productname']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE products SET name = ?, price = ?, description = ?, stock = ? WHERE productId = ?', [productName, price, description, stock, productId])
                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        return redirect(url_for('adminPanel', success_code=200))

    


if __name__ == "__main__":
    app.run(debug=True)