from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, SelectField, IntegerField, TextAreaField, FileField
from wtforms.validators import InputRequired, EqualTo, DataRequired, NumberRange



class RegistrationFrom(FlaskForm):
    user_id = StringField("User id:",
                          validators=[InputRequired()])
    password = PasswordField("Password:",
                             validators=[InputRequired()])
    password2 = PasswordField("Repeat password:",
                              validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    user_id = StringField("User id:", 
                          validators=[InputRequired()])
    password = PasswordField("Password:",
                             validators=[InputRequired()])
    submit = SubmitField("Login")

from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired

class CatalogForm(FlaskForm):
    paint_type = RadioField("Products types", 
                            choices=[
                                ("paint", "Paints"),
                                ("print", "Prints"),
                                ("card", "Cards"), 
                                ("all", "All")
                            ], 
                            default="all", 
                            validators=[DataRequired()])
    search = StringField("Search: ")
    submit = SubmitField("Search")

class PaintForm(FlaskForm):
    paint_size = SelectField("Size", choices=[
        ('500x400mm', '500 x 400mm'),
        ('350x350mm', '350 x 350mm'),
        ('A1','A1'),
        ('A2','A2'),
        ('A3','A3')], validators=[InputRequired()])
    quantity = IntegerField("Quantity",
                            validators=[NumberRange(min=1, max=500, 
                            message="Quantity must be between 1 and 500")], default=1)
    add_to_cart = SubmitField("Add to cart")

class ChangeUserForm(FlaskForm):
    password = PasswordField("Your password:",
                             validators=[InputRequired()])
    newName = StringField("New username:",
                              validators=[InputRequired()])
    change = SubmitField("Change username")

class ChangePasswordForm(FlaskForm):
    oldPassword = PasswordField("Old password:",
                             validators=[InputRequired()])
    newPassword = PasswordField("New password:",
                              validators=[InputRequired()])
    newPassword2 = PasswordField("Repeat new password:",
                              validators=[InputRequired(), EqualTo("newPassword")])
    change = SubmitField("Change password")

class OrderForm(FlaskForm):
    customer_name = StringField('Name', validators=[DataRequired()])
    customer_surname = StringField('Surname', validators=[DataRequired()])
    customer_email = StringField('Email', validators=[DataRequired()])
    address = TextAreaField('Shipping Address', validators=[DataRequired()])
    comments = TextAreaField('Comments') 
    submit = SubmitField('Place Order')

class AddProductForm(FlaskForm):
    paint_name = StringField('Product Name:', validators=[DataRequired()])
    paint_city = StringField('Product City:')
    paint_type = SelectField('Select type:', choices=[('paint', 'Paint'), 
                                                ('print', 'Print'), 
                                                ('card', 'Card')], validators=[DataRequired()])
    paint_description = TextAreaField('Description:', validators=[DataRequired()])
    image = FileField('Upload product image:', validators=[DataRequired()])
    submit = SubmitField('Add Product')


