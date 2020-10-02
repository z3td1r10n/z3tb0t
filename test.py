class Student():
    def __init__(self, age:int, name:str, grant:bool):
        self.age = age
        self.name = name
        self.grant = grant

ivanov = Student(int(input()), input(), bool(input()))

print( str(ivanov.age) + ' ' + str(ivanov.name) + ' ' + str(ivanov.grant))
