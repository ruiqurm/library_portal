from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.core.exceptions import ValidationError
# Register your models here.
admin.site.register(DatabaseSubject)
admin.site.register(DatabaseSource)
admin.site.register(DatabaseCategory)
admin.site.register(Database)
admin.site.register(DatabaseVisit)
admin.site.register(Feedback)
admin.site.register(Announcement)
admin.site.register(AnnouncementVisit)
admin.site.register(MyUser)
admin.site.register(File)

#
# def validate_password_strength(value):
#     """Validates that a password is as least 8 characters long and has at least
#     1 digit and 1 letter.
#     """
#     min_length = 8
#
#     if len(value) < min_length:
#         raise ValidationError("密码至少为8位")
#
#     # check for digit
#     if not any(char.isdigit() for char in value):
#         raise ValidationError('密码至少包含一个数字')
#
#     # check for letter
#     if not any(char.isalpha() for char in value):
#         raise ValidationError('密码至少包含一个字母')
# class UserCreationForm(forms.ModelForm):
#     """A form for creating new users. Includes all the required
#     fields, plus a repeated password."""
#     password1 = forms.CharField(label='密码', widget=forms.PasswordInput,
#                                 min_length=8,max_length=24,
#                                 help_text="长度为8-24,至少包含一个字母和一个数字")
#     password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)
#
#     class Meta:
#         model = MyUser
#         fields = ('username',)
#
#     def clean_password2(self):
#         # Check that the two password entries match
#         password1 = self.cleaned_data.get("password1")
#         validate_password_strength(password1)
#         password2 = self.cleaned_data.get("password2")
#         if password1 and password2 and password1 != password2:
#             raise forms.ValidationError("Passwords don't match")
#         return password2
#
#     def save(self, commit=True):
#         # Save the provided password in hashed format
#         user = super(UserCreationForm, self).save(commit=False)
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user
#
#
# class MyUserAdmin(UserAdmin):
#     # The forms to add and change user instances
#     # form = UserChangeForm
#     add_form = UserCreationForm
#
#     # The fields to be used in displaying the User model.
#     # These override the definitions on the base UserAdmin
#     # that reference specific fields on auth.User.
#     # fieldsets = (
#     #     (None, {'fields': ('username', 'password')}),
#     #     ('Personal info', {'fields': ('date_of_birth',)}),
#     #     ('Permissions', {'fields': ('is_admin',)}),
#     #     ('Important dates', {'fields': ('last_login',)}),
#     # )
#     # add_fieldsets = (
#     #     (None, {
#     #         'classes': ('wide',),
#     #         'fields': ('email', 'date_of_birth', 'password1', 'password2')}
#     #     ),
#     # )
#     # search_fields = ('email',)
#     # ordering = ('email',)
#     # filter_horizontal = ()
#
# # Now register the new UserAdmin...

#
# admin.site.unregister(Group)