from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
db = SQLAlchemy(app)

class Employee(db.Model):
    emp_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    hire_date = db.Column(db.String(10), nullable=False)

# ใช้ app.app_context() เพื่อสร้างบริบท
with app.app_context():
    db.create_all()  # สร้างตารางในฐานข้อมูล

@app.route('/')
def index():
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['POST'])
def add_employee():
    emp_id = request.form['emp_id']
    name = request.form['name']
    position = request.form['position']
    hire_date = request.form['hire_date']
    new_employee = Employee(emp_id=emp_id, name=name, position=position, hire_date=hire_date)
    db.session.add(new_employee)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<string:emp_id>')
def delete_employee(emp_id):
    employee = Employee.query.get(emp_id)
    if employee:
        db.session.delete(employee)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<string:emp_id>', methods=['GET', 'POST'])
def edit_employee(emp_id):
    employee = Employee.query.get(emp_id)
    if request.method == 'POST':
        employee.emp_id = request.form['emp_id']
        employee.name = request.form['name']
        employee.position = request.form['position']
        employee.hire_date = request.form['hire_date']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', employee=employee)

if __name__ == '__main__':
    app.run(debug=True)
