from django.forms import ModelForm, TextInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import *

class CustomerForm(ModelForm):
	class Meta:
		model = Customer
		fields = ['name', 'phone', 'email','profile_pic']
		labels = {
            'name':'Name',
			'phone':'Phone',
			'email': 'Email',
			'profile_pic': 'Profile Pic',
        }
		widgets = {
            'name': TextInput(attrs={'placeholder':'Enter Name','class':'form-control'}),
			'phone': TextInput(attrs={'placeholder':'Enter Phone','class':'form-control'}),
			'email': TextInput(attrs={'placeholder':'Enter Email','class':'form-control'}),
        }


class OrderForm(ModelForm):
	class Meta:
		model = Order
		fields = '__all__'


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

