from django import forms
from django_countries.fields import CountryField

from allauth.account.forms import SignupForm

payment_choices = (
    ('MTN', 'MTN MOBILE MONEY'),
    ('AIRTEL', 'AIRTEL MONEY')
)

class CheckOut(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'ex: John'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'ex: Doe'
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'placeholder': 'example@gmail.com'
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'ex: Kigali'
    }))
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=payment_choices)
    country = CountryField(blank_label='(select country)').formfield()
    phone_number = forms.IntegerField(widget=forms.TextInput(attrs={
        'placeholder': '+250 780 000 000'
    }))
    save_info = forms.BooleanField(widget=forms.CheckboxInput())


# class SignupForm(forms.ModelForm):
#     names = forms.CharField(max_length=30)
#     email = forms.CharField(max_length=30)
#
#     class Meta:
#         model = AbstractComprehensiveUser
#         fields = (
#             # Field to differentiate from buyer and seller
#             # user sign up
#             'user_type',
#             # Common fields for either buyer and seller
#             'names', 'email',
#             # seller specifc fields
#             'telephone_number', 'address', # etc etc
#         )
#
#
# class BuyerSignupForm(forms.ModelForm):
#     first_name = forms.CharField(max_length=30)
#     last_name = forms.CharField(max_length=30)
#
#     class Meta:
#         model = Buyer
#         fields = ('first_name', 'last_name')
#
#
# class SellerSignupForm(SignupForm):
#     company_name = forms.CharField(max_length=50, required=True, strip=True)
#
#     def save(self, request):
#         user = super(SellerSignupForm, self).save(request)
#         agatike_seller = Seller(
#             seller_person=user,
#             seller_name=self.cleaned_data.get('seller_name')
#         )
#         agatike_seller.save()
#         return agatike_seller.contact_person
