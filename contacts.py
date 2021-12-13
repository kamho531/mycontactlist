# -*- coding: utf-8 -*-
"""
Created on Sat May 15 21:33:17 2021

@author: Kam
"""

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.list import ThreeLineListItem
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ObjectProperty
from kivymd.utils import asynckivy
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

# set the display window size
Window.size = (350, 650)


#sample color palette:
#"Read", "Pink", "Purple", "DeepPurple",
#"Indigo", "Blue", "LightBlue", "Cyan",
#"Teal", "Green", "LightGreen", "Lime",
#"Yellow", "Amber", "Orange", "DeepOrange",
#"Brown", "Gray", "BlueGray"
class MainScreen(Screen):
    pass


class DetailScreen(Screen):
    pass


class EditScreen(Screen):
    pass


# Create the screen manager
sm = ScreenManager()
sm.add_widget(MainScreen(name='main'))
sm.add_widget(DetailScreen(name='detail'))
sm.add_widget(EditScreen(name='edit'))

class ContactListApp(MDApp):
    # declare all variables used
    name = ObjectProperty(None)
    phonenum = ObjectProperty(None)
    email = ObjectProperty(None)
    myfile = ObjectProperty(None)
    old_name = ObjectProperty(None)
    new_name = ObjectProperty(None)
    new_phonenum = ObjectProperty(None)
    new_email = ObjectProperty(None)
    dialog = ObjectProperty(None)

    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Purple"
        
        return Builder.load_file('contacts.kv')   

    # start up process to load the existing contacts from the txt file
    def on_start(self):
        async def on_start():
            with open("contacts.txt", mode="r") as myfile:
                content = myfile.readlines()
                for line in content:
                    name, phonenum, email = line.strip().split(";")
                    mythreelinelistitem = ThreeLineListItem(text=name,
                                                            secondary_text=phonenum,
                                                            tertiary_text=email,
                                                            on_press=self.edit_data)
                    self.root.get_screen('main').ids.container.add_widget(mythreelinelistitem)
        asynckivy.start(on_start())

    # refresh the contact list after add, edit or delete
    def refresh_callback(self, *args):
        def refresh_callback(internal):
            self.on_start()
            self.tick = 0
            
        Clock.schedule_once(refresh_callback, 0)

    # display the contact added
    def show_data(self):
        # to load all input text into a three list item and display in scrollview
        mythreelinelistitem = ThreeLineListItem(text=self.root.get_screen('detail').ids.name_txt.text,
                                                secondary_text=self.root.get_screen('detail').ids.phonenum_txt.text,
                                                tertiary_text=self.root.get_screen('detail').ids.email_txt.text,
                                                on_press=self.edit_data)
        
        self.root.get_screen('main').ids.container.add_widget(mythreelinelistitem)
        # put all input texts in relevant variables                                                
        name = self.root.get_screen('detail').ids.name_txt.text
        phonenum = self.root.get_screen('detail').ids.phonenum_txt.text
        email = self.root.get_screen('detail').ids.email_txt.text
        # to write all variables into a txt file
        with open("contacts.txt", mode="a") as myfile:
            myfile.writelines(f"{name};{phonenum};{email}\n")
            #print("Name: ", name, "\nPhone Number: ", phonenum, "\nEmail: ", email,"\nADDED!")
        
        # clear all input text field 
        self.root.get_screen('detail').ids.name_txt.text = ''
        self.root.get_screen('detail').ids.phonenum_txt.text = ''
        self.root.get_screen('detail').ids.email_txt.text = ''
        
        
        
    def edit_data(self, mythreelinelistitem):
        self.root.transition.direction = 'up'
        self.root.current = 'edit'
        # put the chosen contact info into each text field in edit screen
        self.root.get_screen('edit').ids.edit_name.text = mythreelinelistitem.text
        self.root.get_screen('edit').ids.edit_phonenum.text = mythreelinelistitem.secondary_text
        self.root.get_screen('edit').ids.edit_email.text = mythreelinelistitem.tertiary_text
        # declare a global variable to use in other functions
        global old_name
        old_name = mythreelinelistitem.text
                        
                
    def save_data(self):
        # pass all required info from edit screen into new variables
        new_name =  self.root.get_screen('edit').ids.edit_name.text
        new_phonenum = self.root.get_screen('edit').ids.edit_phonenum.text
        new_email = self.root.get_screen('edit').ids.edit_email.text
        # clear all contacts shown in the scrollview 
        self.root.get_screen('main').ids.container.clear_widgets()
        # read and rewrite all contacts and the edited one with new info from above new variables
        with open("contacts.txt", mode="r") as myfile:
            content = myfile.readlines()
            for lno, line in enumerate(content):
                name, phonenum, email = line.strip().split(";")
                if name == old_name:                    
                        content[lno]=f"{new_name};{new_phonenum};{new_email}\n"
                with open("contacts.txt", mode="w") as myfile:
                    myfile.writelines(content)
                myfile.close()                    
        # refresh the scrollview    
        self.refresh_callback()
		# clear all input text fields                                          
        self.root.get_screen('edit').ids.edit_name.text = ''
        self.root.get_screen('edit').ids.edit_phonenum.text = ''
        self.root.get_screen('edit').ids.edit_email.text = ''
       
    # to display the popup before delete a contact
    def show_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Are you sure?",
                size_hint=(0.6, 0.4),
                buttons=[
                    MDFlatButton(text="Delete", text_color=self.theme_cls.primary_color, on_release=self.delete_data),
                    MDFlatButton(text="Cancel", text_color=self.theme_cls.primary_color, on_release=self.cancel),
                    ],
                )
        self.dialog.open()
       

    def delete_data(self, obj):
        # close the dialog box
        self.dialog.dismiss()
        # clear all contacts in the scrollview first
        self.root.get_screen('main').ids.container.clear_widgets()
        # read the txt file and rewrite all contacts again without the deleted one
        with open("contacts.txt", mode="r") as myfile:
            content = myfile.readlines()
        with open("contacts.txt", mode="w") as myfile:
            for lno, line in enumerate(content):
                name, phonenum, email = line.strip().split(";")
                if name != old_name:
                    myfile.write(line)
        # refresh the scrollview                                                                 
        self.refresh_callback()
        # move down the screen
        self.root.transition.direction = 'down'
        # go to the main screen
        self.root.current = 'main'
		# clear all input text fields                                          
        self.root.get_screen('edit').ids.edit_name.text = ''
        self.root.get_screen('edit').ids.edit_phonenum.text = ''
        self.root.get_screen('edit').ids.edit_email.text = ''


    def cancel(self, obj):
        # to close the dialog box
        self.dialog.dismiss()
        # set the current screen back edit screen
        self.root.current = 'edit'


ContactListApp().run()