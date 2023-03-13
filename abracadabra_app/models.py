from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

# manager for cutom user model


class UserManger(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        print("extraa",extra_fields)
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        if password:
            user.set_password(password)
            print('user',user.password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        # user.is_admin = True
        user.set_password(password)
        user.save()
        return user        


# custom user model
class CustomUser(AbstractBaseUser):
    last_login=None
    
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    sub_id= models.CharField(max_length=255,null=True)
    social_acc=models.CharField(max_length=255,null=True)
    # stripe_user_id=models.CharField(max_length=255,null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    objects = UserManger()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return True;


class UserSubscription(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subscription_plan=models.CharField(max_length=255)
    subscription_plan_id=models.CharField(max_length=255)
    subscription_plan_price=models.CharField(max_length=255)
    subscription_plan_price_id=models.CharField(max_length=255)
    subscription_status=models.CharField(max_length=50)
    subscription_purchase_date=models.DateTimeField(auto_now_add=True)