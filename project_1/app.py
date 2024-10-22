from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'  # Database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Employee Model for Database
class EmployeeDB(db.Model):
    emp_id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.String(10), nullable=False)  # Change to Date type if needed

# Employee class for BST
class Employee:
    def __init__(self, emp_id, name, position, hire_date):
        self.emp_id = emp_id
        self.name = name
        self.position = position
        self.hire_date = hire_date
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, emp_id, name, position, hire_date):
        # Check for existing employee in the database
        existing_employee = EmployeeDB.query.filter_by(emp_id=emp_id).first()
        if existing_employee:
            return False  # Return False if employee already exists

        new_employee = Employee(emp_id, name, position, hire_date)
        if self.root is None:
            self.root = new_employee
        else:
            self._insert_rec(self.root, new_employee)

        # Save to database
        new_db_employee = EmployeeDB(emp_id=emp_id, name=name, position=position, hire_date=hire_date)
        db.session.add(new_db_employee)
        db.session.commit()
        
        return True  # Return True if insertion is successful

        
    def _insert_rec(self, node, new_employee):
        if new_employee.emp_id < node.emp_id:
            if node.left is None:
                node.left = new_employee
            else:
                self._insert_rec(node.left, new_employee)
        else:
            if node.right is None:
                node.right = new_employee
            else:
                self._insert_rec(node.right, new_employee)

    def inorder(self):
        return self._inorder_rec(self.root)

    def _inorder_rec(self, node):
        if node is None:
            return []
        return self._inorder_rec(node.left) + [node] + self._inorder_rec(node.right)

    def delete(self, emp_id):
        self.root = self._delete_rec(self.root, emp_id)
        # Delete from database
        EmployeeDB.query.filter_by(emp_id=emp_id).delete()
        db.session.commit()

    def _delete_rec(self, node, emp_id):
        if node is None:
            return node
        if emp_id < node.emp_id:
            node.left = self._delete_rec(node.left, emp_id)
        elif emp_id > node.emp_id:
            node.right = self._delete_rec(node.right, emp_id)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            min_larger_node = self._min_value_node(node.right)
            node.emp_id, node.name, node.position, node.hire_date = (
                min_larger_node.emp_id,
                min_larger_node.name,
                min_larger_node.position,
                min_larger_node.hire_date,
            )
            node.right = self._delete_rec(node.right, min_larger_node.emp_id)
        return node

    def _min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def search(self, emp_id):
        return self._search_rec(self.root, emp_id)

    def _search_rec(self, node, emp_id):
        if node is None or node.emp_id == emp_id:
            return node
        if emp_id < node.emp_id:
            return self._search_rec(node.left, emp_id)
        return self._search_rec(node.right)

# Global BST instance
employee_tree = BST()

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    employees = employee_tree.inorder()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    message = ""
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        name = request.form['name']
        position = request.form['position']
        hire_date = request.form['hire_date']
        
        # Insert new employee
        insertion_successful = employee_tree.insert(emp_id, name, position, hire_date)
        if not insertion_successful:
            message = "Employee ID already exists. Please use a different ID."
        else:
            message = "ทำรายการสำเร็จ!"  # Success message in Thai

        return render_template('add.html', message=message)
    
    return render_template('add.html', message=message)



@app.route('/delete/<string:emp_id>', methods=['POST'])
def delete_employee(emp_id):
    employee_tree.delete(emp_id)
    return redirect(url_for('index'))

@app.route('/edit/<string:emp_id>', methods=['GET', 'POST'])
def edit_employee(emp_id):
    employee = employee_tree.search(emp_id)
    if request.method == 'POST':
        employee_tree.delete(emp_id)
        employee_tree.insert(request.form['emp_id'], request.form['name'], request.form['position'], request.form['hire_date'])
        return redirect(url_for('index'))
    return render_template('edit.html', employee=employee)

@app.route('/search', methods=['POST'])
def search_employee():
    emp_id = request.form['emp_id']
    employee = employee_tree.search(emp_id)
    return render_template('search_result.html', employee=employee)

if __name__ == '__main__':
    app.run(debug=True)
