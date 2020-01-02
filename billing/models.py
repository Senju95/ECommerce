from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, pre_save


from accounts.models import GuestEmail

User = settings.AUTH_USER_MODEL

import stripe
stripe.api_key = "sk_test_STGupFyt4AmMQLqgMSi1ibbK00KyNvSL09"

class BillingProfileManager(models.Manager):
    def new_or_get(self,request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None
        if user.is_authenticated():
            obj, created = self.model.objects.get_or_create(
                                                    user=user, email=user.email)
        elif guest_email_id is not None:
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(
                                                            email=guest_email_obj.email)
        else:
            pass
        return obj, created

class BillingProfile(models.Model):
    user        = models.OneToOneField(User,null=True, blank=True)
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    custumer_id = models.CharField(max_length=120, null=True, blank=True)
    #custumer_id in Stripe or BrainTree

    objects = BillingProfileManager()

    def __str__(self):
        return self.email

    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)

    def get_cards(self):
        return self.card_set.all()
    
    def get_payment_method_url(self):
        return reverse('billing-payment-method')

    @property
    def has_card(self):
        return self.get_cards().exists()

    @property
    def default_card(self):
        return self.get_cards().filter(active=True, default_payment=True).first()

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()

def billing_profile_created_receiver(sender, instance, *args, **kwargs):
    if not instance.custumer_id and instance.email:
        customer = stripe.Customer.create(
            email= instance.email
        )
        instance.custumer_id = customer.id


pre_save.connect(billing_profile_created_receiver, sender=BillingProfile)

def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)


class CartManager(models.Manager):
    def all(self, *args, **kwargs):
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, token):
        if token:
            customer = stripe.Customer.retrieve(billing_profile.custumer_id)
            card_response = customer.sources.create(source=token)
            new_cart = self.model(
               billing_profile=billing_profile,
               stripe_id = card_response.id,
               brand = card_response.brand, 
               country = card_response.country, 
               exp_month = card_response.exp_month, 
               exp_year = card_response.exp_year, 
               last4 = card_response.last4
            )
            new_cart.save()
            return new_cart
        return None

class Card(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile)
    stripe_id           = models.CharField(max_length=120)
    brand               = models.CharField(max_length=120, null=True, blank=True)
    country             = models.CharField(max_length=20, null=True, blank=True)
    exp_month           = models.IntegerField(null=True, blank=True)
    exp_year            = models.IntegerField(null=True, blank=True)
    last4               = models.CharField(max_length=5, null=True, blank=True)
    default_payment     = models.BooleanField(default=True)
    active              = models.BooleanField(default=True)
    timestamp           = models.DateTimeField(auto_now_add=True)

    objects = CartManager()

    def __str__(self):
        return "{} {}".format(self.brand, self.last4)

class ChargeManager(models.Manager):
    def do(self, billing_profile, order_obj, card=None):
        if card is None:
            card = billing_profile.card_set.filter(default_payment=True).first()
        if card is None:
            return False, "No cards available"    
        charge = stripe.Charge.create(
                    amount = int(order_obj.total * 100),
                    currency = "usd",
                    customer = billing_profile.custumer_id,
                    source = card.stripe_id,
                    description = "Charge for a example!",
                    metadata = {"order_id": order_obj.order_id}
                )
        print(charge)
        new_charge_obj = self.model(
            billing_profile     = billing_profile,
            stripe_id           = charge.id,
            paid                = charge.paid,
            refunded            = charge.refunded,
            outcome             = charge.outcome,
            outcome_type        = charge.outcome['type'],
            seller_message      = charge.outcome.get('seller_message'),
            risk_level          = charge.outcome.get('risk_level')
        )
        new_charge_obj.save()
        return new_charge_obj.paid, new_charge_obj.seller_message

class Charge(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile)
    stripe_id           = models.CharField(max_length=120)
    paid                = models.BooleanField(default=False)
    refunded            = models.BooleanField(default=False)
    outcome             = models.TextField(null=True, blank=True)
    outcome_type        = models.CharField(max_length=120, null=True, blank=True)
    seller_message      = models.CharField(max_length=120, null=True, blank=True)
    risk_level          = models.CharField(max_length=120, null=True, blank=True)

    objects = ChargeManager()