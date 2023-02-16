from flask_pymongo import PyMongo

class Student(PyMongo):
    
    def save_to_db(self, data):
        self.db.students.insert_one(data)
        return {
            'name' : data['name'],
            'surname' : data['surname'],
            'address' : data['address'],
            'contact_number' : data['contact_number']
        }

    def find_student_by_name(self, name):
        result = self.db.students.find_one({'name' : name})
        if result:
            return {
                'name' : result['name'],
                'surname' : result['surname'],
                'address' : result['address'],
                'contact_number' : result['contact_number']
            }
        
        return {"message": "This Student does not exist"}

    def find_students_all(self):
        result = self.db.students.find()
        students = {}
        # index = 1
        for student in result:
            student.pop('_id')
            students[student['name']] = student
            # index += 1

        return students
    
    def delete_from_db(self, name):
        # result = self.db.students.find_one({'name' : name})
        result = self.find_student_by_name(name)
        print(result)
        if 'name' in result:
            self.db.students.delete_one({'name': name})
            return {"message": "This Student is deleted"}
        else:
            return {"message": "This Student does not exist"}