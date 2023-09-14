# you will have to pip install matplotlib

import pickle
from enum import Enum
import time
import random
import math
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import visuals

class RafflePage():
   def __init__(self, width = 1200, height = 700):
      self.root = tk.Tk()
      self.root.state('zoomed')
      self.width = width
      self.height = height
      self.root.config(**visuals.RAFFLE_COUNTDOWN_BACKGROUND_CONFIG)
      self.root.geometry(f"{self.width}x{self.height}")
      self.active_raffle_type = RollType.RANDOM
      self.root.protocol("WM_DELETE_WINDOW", self.on_close)
      self.raffleMainloop()

   def on_close(self):
      self.root.destroy()
      plt.close('all')

   def raffleMainloop(self):
      raffleBtn = tk.Button(self.root, text="RAFFLE", command=self.onRaffle, **visuals.RAFFLE_BUTTON_CONFIG)
      raffleBtn.place(relx = 0.2, rely = 0.4, anchor = 'center')

      frame = tk.Frame(self.root)
      frame.place(relx = 0.2, rely = 0.6, anchor = "center")

      opt1 = tk.Button(frame, text="RANDOM", command = self.setOpt1, **visuals.RAFFLE_TYPE_OPTIONS)
      opt1.pack()

      opt2 = tk.Button(frame, text="SCORE BASED", command = self.setOpt2, **visuals.RAFFLE_TYPE_OPTIONS)
      opt2.pack()

      opt3 = tk.Button(frame, text="SCORE BASED LOGARITHMIC", command = self.setOpt3, **visuals.RAFFLE_TYPE_OPTIONS)
      opt3.pack()

      self.updateGraph()

      self.root.mainloop()



   def onRaffle(self):
      for widget in self.root.winfo_children():
         widget.destroy()

      students, pickChances = getRollWeights(self.active_raffle_type, student_array)

      theChosenOne = random.choices(students, weights=pickChances, k=1)[0]
      self.root.config(**visuals.RAFFLE_COUNTDOWN_BACKGROUND_CONFIG)
      nameLabel = tk.Label(self.root, text="3", **visuals.RAFFLE_COUNTDOWN_CONFIG)
      nameLabel.place(relx = 0.5, rely = 0.5, anchor = "center")
      self.root.update()
      time.sleep(1)

      nameLabel.config(text="2")
      self.root.update()
      time.sleep(1)

      nameLabel.config(text="1")
      self.root.update()
      time.sleep(1)

      nameLabel.config(text=theChosenOne)
      self.root.update()

   def setOpt1(self):
      self.active_raffle_type = RollType.RANDOM
      self.updateGraph()

   def setOpt2(self):
      self.active_raffle_type = RollType.SCORE_BASED
      self.updateGraph()

   def setOpt3(self):
      self.active_raffle_type = RollType.SCORE_BASED_LOGARITHMIC
      self.updateGraph()

   def updateGraph(self):
      students, pickChances = getRollWeights(self.active_raffle_type, student_array)
      # Clear the previous graph
      plt.clf()

      fig, ax = plt.subplots()
      ax.set_facecolor("#e3e3e3")
      fig.set_facecolor("#ffffff")

      # Create the column graph on the Matplotlib axis
      ax.bar(students, pickChances, color='#f92672')
      # Add labels and a title
      if self.active_raffle_type == RollType.RANDOM:
         titleText = "RANDOM"
      elif self.active_raffle_type == RollType.SCORE_BASED:
         titleText = "SCORE BASED"
      elif self.active_raffle_type == RollType.SCORE_BASED_LOGARITHMIC:
         titleText = "SCORE BASED LOGARITHMIC"
      else:
         titleText = ""

      ax.set_title(titleText, color = '#f92672')


      plt.xticks(rotation=90)

      ax.tick_params(axis='x', colors='#000000')
      ax.set_yticklabels([])


      font = FontProperties(family='Consolas', size=13, weight='bold')

      for tick_label in ax.get_xticklabels():
         tick_label.set_fontproperties(font)

      ax.spines['top'].set_visible(False)
      ax.spines['right'].set_visible(False)
      ax.spines['bottom'].set_visible(False)
      ax.spines['left'].set_visible(False)

      # Define the vertical position for moving labels upward
      vertical_position = 1

      # Move the x-axis labels upward
      x_label_objs = ax.get_xticklabels()
      for label in x_label_objs:
         label.set_y(vertical_position)

      ax.set_ylim(0, 2 * max(pickChances) if max(pickChances) != 0 else 1)

      canvas = FigureCanvasTkAgg(fig, master=self.root)
      canvas_widget = canvas.get_tk_widget()
      canvas_widget.place(relx = 0.65, rely = 0.5, anchor = "center")



class StudentPage():
   def __init__(self, root , student_instance, width = 500, height = 500):
      self.root = root
      self.root.config(**visuals.RAFFLE_COUNTDOWN_BACKGROUND_CONFIG)
      self.root.state('zoomed')
      self.student = student_instance
      self.width = width
      self.height = height

      self.studentIdToDisplayNext = None

      self.pageMainLoop()

   def pageMainLoop(self):
      self.root.geometry(f"{self.width}x{self.height}")

      nameLbl = tk.Label(self.root, text=f"{self.student.name} {self.student.surname}", **visuals.PROFILE_NAME_CONFIG)
      nameLbl.place(relx = 0.5, rely = 0.5, anchor = 'center')


      PICKABLE_CONFIG = visuals.IS_RAFFLABLE_CONFIG if self.student.pickable else visuals.IS_NOT_RAFFLABLE_CONFIG
      pickableLbl = tk.Label(self.root, text= f"Can Get Raffled", **PICKABLE_CONFIG)
      pickableLbl.place(relx = 0.5, rely = 0.3, anchor = 'center')

      self.pointsLbl = tk.Label(self.root, text = f"Score: {self.student.totalPickScore}", **visuals.PROFILE_SCORE_CONFIG)
      self.pointsLbl.place(relx = 0.5, rely = 0.6, anchor="center")

      frame = tk.Frame(self.root, **visuals.RAFFLE_COUNTDOWN_BACKGROUND_CONFIG)
      frame.place(relx = 0.5, rely = 0.8, anchor = 'center')

      plusButton = tk.Button(frame, command=self.plusPoint, **visuals.PLUS_CONFIG)
      plusButton.grid(row=0, column = 1)

      minusButton = tk.Button(frame, command=self.minusPoint, **visuals.MINUS_CONFIG)
      minusButton.grid(row = 0, column = 0, padx = (0, 4))

      gotoNextStudentBtn = tk.Button(self.root, text="Next >>", command=self.nextStudent, **visuals.NEXT_PREV_BUTTON_CONFIG)
      gotoNextStudentBtn.pack(side=tk.RIGHT, padx = 30)

      gotoPrevStudentBtn = tk.Button(self.root, text="<< Back", command=self.prevStudent, **visuals.NEXT_PREV_BUTTON_CONFIG)
      gotoPrevStudentBtn.pack(side=tk.LEFT, padx = 40)


      self.root.mainloop()


   def plusPoint(self):
      self.student.addGreenPoint()
      self.pointsLbl.config(text=f"Score: {self.student.totalPickScore}")

   def minusPoint(self):
      self.student.addRedPoint()
      self.pointsLbl.config(text=f"Score: {self.student.totalPickScore}")

   def nextStudent(self):
      self.studentIdToDisplayNext = self.student.id + 1
      for widget in self.root.winfo_children():
         widget.destroy()

      self.root.quit()


   def prevStudent(self):
      self.studentIdToDisplayNext = self.student.id - 1
      for widget in self.root.winfo_children():
         widget.destroy()

      self.root.quit()




class MenuEnum(Enum):
   RAFFLE = 1
   ADD_STUDENT = 2
   MANAGE_STUDENTS = 3

class MainMenu():
   def __init__(self, width= 500, height = 500):
      self.root = tk.Tk()
      self.root.state('zoomed')
      self.width = width
      self.height = height
      self.root.config(**visuals.RAFFLE_COUNTDOWN_BACKGROUND_CONFIG)
      self.nextPage = None
      self.root.geometry(f"{self.width}x{self.height}")

      self.menuMainLoop()

   def menuMainLoop(self):

      title = tk.Label(self.root, text="THE RAFFLER", **visuals.MAIN_TITLE_CONFIG)
      title.place(relx = 0.5, rely = 0.2, anchor = "center")
      frame = tk.Frame(self.root)
      frame.place(relx = 0.5, rely = 0.5, anchor = "center")

      raffle = tk.Button(frame, text="RAFFLE", command=self.goRaffle, **visuals.RAFFLE_TYPE_OPTIONS)
      raffle.pack()

      addStdntBtn = tk.Button(frame, text="ADD STUDENT", command=self.goAddStudent, **visuals.RAFFLE_TYPE_OPTIONS)
      addStdntBtn.pack()

      manageStudentsBtn = tk.Button(frame, text="MANAGE STUDENTS", command=self.goManageStudents, **visuals.RAFFLE_TYPE_OPTIONS)
      manageStudentsBtn.pack()

      self.root.mainloop()

   def goRaffle(self):
      self.nextPage = MenuEnum.RAFFLE
      self.root.quit()
      self.root.destroy()

   def goAddStudent(self):
      self.nextPage = MenuEnum.ADD_STUDENT
      self.root.quit()
      self.root.destroy()

   def goManageStudents(self):
      self.nextPage = MenuEnum.MANAGE_STUDENTS
      self.root.quit()
      self.root.destroy()

class AddStudentPage():
   def __init__(self, student_array, width=500, height=500):
      self.root = tk.Tk()
      self.root.config(**visuals.RAFFLE_COUNTDOWN_BACKGROUND_CONFIG)
      self.root.state('zoomed')
      self.student_array = student_array
      self.width = width
      self.height = height

      self.root.geometry(f"{self.width}x{self.height}")

      self.addStudentMainloop()

   def addStudentMainloop(self):
      frame = tk.Frame(self.root, **visuals.RAFFLE_COUNTDOWN_BACKGROUND_CONFIG)
      frame.place(relx=0.5, rely=0.5, anchor="center")

      nameLbl = tk.Label(frame, text="Name: ", **visuals.ADD_STUDENT_LABELS)
      nameLbl.grid(row = 0, column = 0, sticky = 'we', pady=(0, 2))

      self.nameEntry  = tk.Entry(frame, **visuals.ADD_STUDENT_ENTRY)
      self.nameEntry.grid(row = 0, column = 1, sticky = 'nswe', pady=(0, 2), padx = (2, 0))

      surnameLbl = tk.Label(frame, text="Surname: ", **visuals.ADD_STUDENT_LABELS)
      surnameLbl.grid(row=1, column=0, sticky = 'we', pady=(0, 2))

      self.surnameEntry = tk.Entry(frame, **visuals.ADD_STUDENT_ENTRY)
      self.surnameEntry.grid(row=1, column=1, sticky = 'nswe', pady=(0, 2), padx = (2, 0))

      addStudentBtn = tk.Button(frame, text="Add Student" , command=self.addStudent, **visuals.ADD_STUDENT_LABELS)
      addStudentBtn.grid(row = 2, column = 0, columnspan = 2, sticky='we')

      self.root.mainloop()

   def addStudent(self):
      name = self.nameEntry.get()
      surname = self.surnameEntry.get()
      if name == "" or surname == "":
         return
      add_student(name, surname, self.student_array)
      self.root.quit()
      self.root.destroy()


def add_student(name, surname, student_array):
   student = Student(name, surname)
   student_array.append(student)
   save_student_array(student_array)

class Student:
   def __init__(self, name, surname):
      self.name = name
      self.surname = surname
      self.id = len(student_array)
      self.pickable = True
      self.totalPickScore = 0

   def __str__(self):
      return f"Name: {self.name}\nSurname: {self.surname}\nID: {self.id}\nPickable: {self.pickable}" \
         f"\nTotalScore {self.totalPickScore}\n"

   def addGreenPoint(self):
      # reduces the chance of getting picked
      # the lower the better
      self.totalPickScore += 1
      save_student_array(student_array)

   def addRedPoint(self):
      self.totalPickScore -= 1
      save_student_array(student_array)


def save_student_array(student_array):
   with open('students.pkl', 'wb') as file:
      pickle.dump(student_array, file)

def load_student_array():
   try:
      with open('students.pkl', 'rb') as file:
         student_array = pickle.load(file)
         return student_array
   except:
         return []

class RollType(Enum):
      RANDOM = 1
      SCORE_BASED = 2
      SCORE_BASED_LOGARITHMIC = 3

def getRollWeights(roll_type, student_array):
   students = [f"{student.name} {student.surname}" for student in student_array]

   if roll_type == RollType.RANDOM:
      pickChances = [1 for _ in student_array]
      return students, pickChances

   elif roll_type == RollType.SCORE_BASED or roll_type == RollType.SCORE_BASED_LOGARITHMIC:
      pickChances = []
      highestScore = float("-inf")
      for student in student_array:
         if highestScore < student.totalPickScore:
            highestScore = student.totalPickScore
      for student in student_array:
         # the higher the score is the better (lower chance of getting picked)
         # we invert it so that the best score has the lowest chance of getting picked
         # we add the absolute value of the highest score to ensure that all of the weights are positive
         # the smallest number since we invert it is the best score * -1 so if we add the best score to all of the students
         # we have all of them positive
         pickChances.append(((-1)*student.totalPickScore + abs(highestScore) + 1))
      if roll_type == RollType.SCORE_BASED_LOGARITHMIC:
         pickChances = [math.log10(pickChance * 100) for pickChance in pickChances] # play with the values
      return students, pickChances



def wrap_around_index(value, size):
   if size <= 0 or value == None:
      raise ValueError("Invalid Size or idx")

   wrapped_index = value % size

   return wrapped_index

def main():
   global student_array
   student_array = load_student_array()
   while True:
      menu = MainMenu()
      if menu.nextPage == None:
         return

      if menu.nextPage == MenuEnum.RAFFLE:
         RafflePage()
      elif menu.nextPage == MenuEnum.ADD_STUDENT:
         AddStudentPage(student_array)
      elif menu.nextPage == MenuEnum.MANAGE_STUDENTS:
         pageIdx = 0
         root = tk.Tk() # group root window for all student pages
         while True:
            cPage = StudentPage(root, student_array[pageIdx])
            if cPage.studentIdToDisplayNext == None:
               break
            pageIdx = wrap_around_index(cPage.studentIdToDisplayNext, len(student_array))


if __name__ == "__main__":
   main()